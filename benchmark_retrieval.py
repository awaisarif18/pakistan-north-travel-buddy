"""Development comparison, frozen settings, then one final held-out comparison."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from unittest.mock import patch

from langsmith import tracing_context

import rag
from eval_data import load_questions, source_hash
from eval_metrics import RETRIEVAL_EVALUATORS
from hybrid_report import multi_passage_complete, multi_passage_coverage, retrieval_latency, write_comparison
from langsmith_eval import export_results, langsmith_client, upload_verified
from retrieval import SETTINGS
from verify_migration import fingerprint
from workflow import open_retriever

METHODS = ("dense", "bm25", "hybrid")


def code_hashes():
    files = ["retrieval.py", "workflow.py", "rag.py", "hybrid_report.py", "benchmark_retrieval.py", "eval_metrics.py"]
    return {name: hashlib.sha256((rag.ROOT / name).read_bytes()).hexdigest() for name in files}


def prepare_vectors(questions, directory):
    records = []
    with rag.gemini_client() as client:
        for q in questions:
            cache_path = rag.DATA_DIR / "query_embeddings.json"
            cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
            key = hashlib.sha256(json.dumps([rag.INDEX_CONFIG, q["question"]], sort_keys=True).encode()).hexdigest()
            start = time.perf_counter()
            vector = rag.query_embedding(client, q["question"])
            assert len(vector) == rag.DIMENSIONS
            records.append({"id": q["id"], "already_cached": key in cache,
                            "preparation_ms": (time.perf_counter() - start) * 1000})
            (directory / "query_preparation.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
            print(f"Query vector ready: {q['id']} ({'cached' if key in cache else 'new'})", flush=True)
            if key not in cache:
                time.sleep(1)
    return records


def compare(split, group):
    directory = group / split
    directory.mkdir(exist_ok=False)
    questions = load_questions("harder", split, require_verified=True)
    sync = upload_verified("harder", split)
    client = langsmith_client()
    remote = sorted(client.list_examples(dataset_name=sync["dataset"], splits=[split]), key=lambda e: e.outputs["id"])
    assert [e.outputs["id"] for e in remote] == sorted(q["id"] for q in questions)
    prepare_vectors(questions, directory)
    collection = rag.open_collection()
    assert collection.count() == 49
    initial_fingerprint = fingerprint(collection)
    all_records, experiments = {}, []
    for method in METHODS:
        start = time.perf_counter()
        retriever = open_retriever(k=10, mode=method)
        startup_ms = (time.perf_counter() - start) * 1000
        warmup = load_questions("harder", "dev", require_verified=True)[0]["question"]
        with tracing_context(enabled=False), patch.object(rag, "embed", side_effect=AssertionError("Uncached query during timed run")):
            retriever.invoke(warmup)  # Warmup is always a development query, never a held-out question.
        records = {}

        def target(inputs):
            q = next(q for q in questions if q["question"] == inputs["question"])
            if q["id"] in records:
                raise ValueError("A query was already executed for this method; refusing a repeated benchmark.")
            try:
                start = time.perf_counter()
                # Exclude trace/experiment upload overhead from the measured retrieval call.
                with tracing_context(enabled=False):
                    documents = retriever.invoke(q["question"])
                elapsed = (time.perf_counter() - start) * 1000
                output = {"retrieved_ids": [d.id for d in documents], "retrieval_latency_ms": elapsed,
                          "retrieved_pages": [d.metadata for d in documents],
                          "retrieved_evidence": [{"id": d.id, "text": d.page_content, "metadata": d.metadata} for d in documents]}
                assert len(output["retrieved_ids"]) == len(set(output["retrieved_ids"]))
                if method == "dense":
                    old = rag.retrieve(collection, None, q["question"], top_k=10)
                    assert output["retrieved_ids"] == [d["id"] for d in old], "v1 dense ranking differs"
                    assert all(d.page_content == previous["text"] and d.metadata == previous["metadata"]
                               for d, previous in zip(documents, old)), "v1 dense evidence differs"
                    output["v1_dense_parity"] = True
            except Exception as error:
                output = {"retrieved_ids": [], "error": type(error).__name__}
            records[q["id"]] = output
            (directory / f"{method}_raw.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return output

        prefix = f"{group.name}-{split}-{method}"
        metadata = {"method": method, "split": split, "settings": SETTINGS, "code_hashes": code_hashes(),
                    "source_sha256": source_hash("harder"), "index_fingerprint": initial_fingerprint,
                    "startup_ms": startup_ms, "k": 10, "latency": "one invoke, warm query cache, no trace overhead",
                    "generation_enabled": False, "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
        with tracing_context(enabled=True), patch.object(rag, "embed", side_effect=AssertionError("Embedding forbidden during comparison")):
            experiment = client.evaluate(target, data=remote, experiment_prefix=prefix,
                                         evaluators=RETRIEVAL_EVALUATORS + [multi_passage_coverage, multi_passage_complete, retrieval_latency],
                                         metadata=metadata, max_concurrency=1, num_repetitions=1)
            list(experiment)
        assert len(records) == len(questions), "Missing actual retrieval outputs"
        all_records[method] = records
        relative = str(group.relative_to(rag.ROOT / "evals/experiments") / split / method)
        export_results(questions, records, relative, metadata)
        info = {"method": method, "name": experiment.experiment_name,
                "url": experiment.url, "startup_ms": startup_ms}
        experiments.append(info)
        (directory / "experiments.json").write_text(json.dumps(experiments, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(info), flush=True)
    assert fingerprint(collection) == initial_fingerprint, "Stored vectors/text/metadata changed"
    return write_comparison(directory, questions, all_records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["dev", "freeze", "held_out"])
    parser.add_argument("--group", required=True, help="Existing/new benchmark directory name; no path separators.")
    args = parser.parse_args()
    if not args.group.replace("-", "").isalnum():
        parser.error("Use a simple alphanumeric/hyphen group name.")
    group = rag.ROOT / "evals/experiments" / args.group
    if args.action == "freeze":
        dev = json.loads((group / "dev/aggregate.json").read_text(encoding="utf-8"))
        if any(dev[method][key] is None for method in METHODS for key in ["hit_at1", "hit_at5", "mrr_at10", "complete_evidence_at5"]):
            raise ValueError("Resolve development errors before freezing.")
        # Predeclared choice: complete evidence, Hit@5, MRR, Hit@1; dense wins exact ties.
        preference = {"dense": 2, "hybrid": 1, "bm25": 0}
        selected = max(METHODS, key=lambda m: tuple(dev[m][key] for key in ["complete_evidence_at5", "hit_at5", "mrr_at10", "hit_at1"]) + (preference[m],))
        frozen = {"settings": SETTINGS, "code_hashes": code_hashes(), "source_sha256": source_hash("harder"),
                  "selected_from_dev": selected, "created_utc": datetime.now(timezone.utc).isoformat(),
                  "selection_rule": "CompleteEvidence@5, Hit@5, MRR@10, Hit@1; ties dense > hybrid > bm25"}
        with (group / "frozen_settings.json").open("x", encoding="utf-8") as file:
            json.dump(frozen, file, indent=2)
        print(json.dumps(frozen, indent=2))
        return
    if args.action == "held_out":
        frozen = json.loads((group / "frozen_settings.json").read_text(encoding="utf-8"))
        assert frozen["settings"] == SETTINGS and frozen["code_hashes"] == code_hashes()
        assert frozen["source_sha256"] == source_hash("harder")
        with (group / "held_out_started.json").open("x", encoding="utf-8") as file:
            json.dump({"started_utc": datetime.now(timezone.utc).isoformat(), "frozen_settings": frozen}, file, indent=2)
    else:
        group.mkdir(parents=True, exist_ok=False)
    # Open only a private copy so Chroma cannot mutate the deployment snapshot.
    runtime = rag.DATA_DIR / "hybrid-checks" / args.group
    if not runtime.exists():
        shutil.copytree(rag.DB_PATH, runtime / "chroma")
    with patch.object(rag, "DB_PATH", runtime / "chroma"):
        print(json.dumps(compare("dev" if args.action == "dev" else "held_out", group), indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"Benchmark stopped: {type(error).__name__}. Existing outputs are retained; no secrets logged.")
