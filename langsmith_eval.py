"""Explicit development tracing, verified dataset upload, and code-only evaluation."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
from uuid import uuid5

from langsmith import Client, tracing_context
from langsmith.utils import LangSmithNotFoundError

from eval_data import ROOT, as_example, load_questions, prepare_exports, source_hash
from eval_metrics import ANSWER_EVALUATORS, RETRIEVAL_EVALUATORS, RETRIEVAL_KEYS, retrieval_scores
import rag
from workflow import build_workflow, chat_model, open_retriever, run_question

NAMES = {"baseline": "pakistan-north-v1-verified-25",
         "harder": {"dev": "north-tours-v1-1-dev", "held_out": "north-tours-v1-1-heldout"}}


def langsmith_client():
    key, project = os.getenv("LANGSMITH_API_KEY", "").strip(), os.getenv("LANGSMITH_PROJECT", "").strip()
    if not key or key.startswith("your") or not project:
        raise ValueError("Configure private LANGSMITH_API_KEY and LANGSMITH_PROJECT in .env first.")
    return Client(api_key=key)


def upload_verified(dataset, split=None):
    if dataset == "harder" and split not in NAMES["harder"]:
        raise ValueError("Select --split dev or --split held_out for the separate v1.1 datasets.")
    if dataset == "baseline" and split not in {None, "baseline"}:
        raise ValueError("The historical dataset only has the baseline split.")
    questions = load_questions(dataset, split, require_verified=True)  # Gate before client/network access.
    split = split or "baseline"
    name = NAMES[dataset][split] if dataset == "harder" else NAMES[dataset]
    digest = source_hash(dataset)
    client = langsmith_client()
    try:
        remote = client.read_dataset(dataset_name=name)
    except LangSmithNotFoundError:
        remote = client.create_dataset(name, description="Reviewed PDF evidence; original scores are not recalculated.",
                                       metadata={"source_sha256": digest, "label_status": "verified"})
    if (remote.metadata or {}).get("source_sha256") != digest:
        raise ValueError("Remote dataset differs from this reviewed snapshot. Use a versioned dataset; do not overwrite it.")
    existing = {str(e.id): e for e in client.list_examples(dataset_id=remote.id)}
    expected = {}
    for q in questions:
        example = as_example(q, digest)
        example["id"] = str(uuid5(remote.id, q["id"]))
        expected[example["id"]] = example
    if not set(existing) <= set(expected):
        raise ValueError("Unexpected remote examples found; inspect the dataset before proceeding.")
    for example_id, prior in existing.items():
        example = expected[example_id]
        if (prior.inputs != example["inputs"] or prior.outputs != example["outputs"]
                or any((prior.metadata or {}).get(k) != v for k, v in example["metadata"].items())):
            raise ValueError("A remote example differs from reviewed local labels; no overwrite performed.")
    pending = [example for example_id, example in expected.items() if example_id not in existing]
    if pending:
        client.create_examples(dataset_id=remote.id, examples=pending)
    saved = {str(e.id): e for e in client.list_examples(dataset_id=remote.id)}
    if set(saved) != set(expected):
        raise ValueError("Remote example count/IDs differ after synchronization.")
    for example_id, example in expected.items():
        actual = saved[example_id]
        if (actual.inputs != example["inputs"] or actual.outputs != example["outputs"]
                or any((actual.metadata or {}).get(k) != v for k, v in example["metadata"].items())):
            raise ValueError("Remote reference or metadata verification failed after synchronization.")
    split_ids = {str(e.id) for e in client.list_examples(dataset_id=remote.id, splits=[split])}
    if split_ids != set(expected) or set(client.list_dataset_splits(dataset_id=remote.id)) != {split}:
        raise ValueError("Remote split membership differs from the approved local split.")
    return {"dataset": remote.name, "id": str(remote.id), "url": remote.url,
            "examples": len(saved), "created_examples": len(pending), "split": split,
            "verification_status": "verified", "local_remote_match": True}


def check_query_budget(questions, args):
    path = rag.DATA_DIR / "query_embeddings.json"
    cache = json.loads(path.read_text()) if path.exists() else {}
    missing = 0
    for q in questions:
        if q["answerable"] or args.answers:
            key = hashlib.sha256(json.dumps([rag.INDEX_CONFIG, q["question"]], sort_keys=True).encode()).hexdigest()
            missing += key not in cache
    if missing and not args.allow_query_embeddings:
        raise ValueError(f"{missing} uncached questions need Gemini query vectors. Opt in with --allow-query-embeddings.")
    return missing


def evaluation_target(questions, args):
    references = {q["question"]: q for q in questions}
    retriever = open_retriever(k=10)
    known = set(retriever.vectorstore.get(include=[])["ids"])
    if any(not set(q["gold_chunk_ids"]) <= known for q in questions):
        raise ValueError("Gold evidence contains IDs missing from the existing index.")
    graph = build_workflow(open_retriever(), chat_model()) if args.answers else None
    records = {}

    def target(inputs):
        q = references[inputs["question"]]
        trace = args.trace or args.langsmith
        try:
            with tracing_context(enabled=trace):
                if not q["answerable"] and not args.answers:
                    outputs = {"retrieved_ids": [], "status": "negative_requires_answer_review"}
                else:
                    docs = retriever.invoke(q["question"])
                    outputs = {"retrieved_ids": [doc.id for doc in docs],
                               "retrieved_evidence": [{"id": doc.id, "text": doc.page_content,
                                                       "metadata": doc.metadata} for doc in docs]}
                    if graph is not None:
                        state = run_question(graph, q["question"], trace=trace)
                        outputs.update(answer=state["answer"], matches=state["matches"],
                                       chat_top5_matches_metric_prefix=[m["id"] for m in state["matches"]] == outputs["retrieved_ids"][:5])
            records[q["id"]] = outputs
            return outputs
        except Exception as error:
            # Export failure types, never credential-bearing HTTP exception text.
            outputs = {"error": type(error).__name__, "retrieved_ids": []}
            records[q["id"]] = outputs
            return outputs

    return target, records


def export_results(questions, records, name, metadata):
    directory = ROOT / "evals/experiments" / name
    directory.mkdir(parents=True, exist_ok=False)
    rows = []
    for q in questions:
        outputs = records.get(q["id"], {"error": "NoResult"})
        scores = retrieval_scores(outputs, q)
        review = {result["key"]: result["score"] for evaluator in ANSWER_EVALUATORS
                  for result in [evaluator(outputs) if evaluator.__name__ == "citation_validity" else evaluator(outputs, q)]}
        rows.append({"id": q["id"], "question": q["question"], "split": q["split"], "answerable": q["answerable"],
                     "reference_answer": q["reference_answer"], "status": outputs.get("error", "completed"),
                     **scores, **review, "human_review_status": "needs_review" if "answer" in outputs else "not_generated",
                     "reviewer_notes": "", "gold_ids": json.dumps(q["gold_chunk_ids"]), "gold_pages": json.dumps(q["gold_pages"]),
                     "required_evidence_groups": json.dumps(q.get("required_evidence_groups", [])),
                     "gold_evidence": json.dumps(q["gold_evidence"], ensure_ascii=False),
                     "actual_outputs": json.dumps(outputs, ensure_ascii=False)})
    with (directory / "results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    errors = sum("error" in records.get(q["id"], {"error": "NoResult"}) for q in questions)
    lines = [f"# {name}", "", f"Metadata: `{json.dumps(metadata)}`.", "",
             f"Questions: {len(rows)}. Errors: {errors}. No LLM judge was used.", "",
             "| Metric | Result | Scored questions |", "|---|---|---|"]
    for key in RETRIEVAL_KEYS:
        eligible = [r[key] for r in rows if r[key] is not None]
        value = f"{sum(eligible) / len(eligible):.4f}" if eligible and not errors else "Not calculated"
        lines.append(f"| {key} | {value} | {len(eligible)} |")
    lines.extend(["", "Unanswerable questions are excluded from retrieval scores. Any error withholds aggregates.",
                  "Citation validity is structural only. Answer correctness and groundedness remain manual and unscored.",
                  "Review generated answers, retrieved passages, refusals, and any chat/top-ten prefix mismatch in results.csv.", "",
                  "## Retrieval misses and errors", ""])
    lines.extend(f"- {r['id']}: {r['question']} Status: {r['status']}. Gold: `{r['gold_ids']}`. Actual: `{r['actual_outputs']}`."
                 for r in rows if r["status"] != "completed" or r["hit_at5"] == 0 or r["complete_evidence_at5"] == 0)
    (directory / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(directory)


def evaluate(args):
    split = args.split or ("dev" if args.dataset == "harder" else "baseline")
    questions = load_questions(args.dataset, split, require_verified=True)
    budget = check_query_budget(questions, args)
    if args.trace or args.langsmith:
        langsmith_client()  # Validate credentials before any Gemini request.
    name = args.experiment or f"v11-{args.dataset}-{split}-dense-k10-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,100}", name):
        raise ValueError("Experiment names must be simple filenames without path separators.")
    if (ROOT / "evals/experiments" / name).exists():
        raise ValueError("Choose a new experiment name; existing exports are never overwritten.")
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = {"commit": commit, "source_sha256": source_hash(args.dataset), "split": split,
                "embedding_model": rag.EMBEDDING_MODEL, "chat_model": rag.CHAT_MODEL,
                "uncached_queries_before_run": budget, "answer_generation_enabled": args.answers}
    target, records = evaluation_target(questions, args)
    with tracing_context(enabled=args.trace or args.langsmith):
        if args.langsmith:
            # Upload/select only verified references. Each target runs once, sequentially.
            uploaded = upload_verified(args.dataset, split)
            client = langsmith_client()
            remote = list(client.list_examples(dataset_name=uploaded["dataset"], splits=[split]))
            if {e.inputs["question"] for e in remote} != {q["question"] for q in questions}:
                raise ValueError("Remote split differs from the selected local questions.")
            experiment = client.evaluate(target, data=remote, experiment_prefix=name,
                                         evaluators=RETRIEVAL_EVALUATORS + (ANSWER_EVALUATORS if args.answers else []),
                                         metadata=metadata, max_concurrency=1, num_repetitions=1)
            list(experiment)  # Export the recorded outputs; never run target a second time.
        else:
            for q in questions:
                target({"question": q["question"]})
    return {"exports": export_results(questions, records, name, metadata), "questions": len(questions)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "upload", "evaluate", "ask"])
    parser.add_argument("--dataset", choices=list(NAMES), default="harder")
    parser.add_argument("--split", choices=["dev", "held_out", "baseline"])
    parser.add_argument("--experiment")
    parser.add_argument("--question")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--langsmith", action="store_true", help="Upload experiment results, not public-user chat.")
    parser.add_argument("--answers", action="store_true", help="Opt into one answer-generation request per question.")
    parser.add_argument("--allow-query-embeddings", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            result = prepare_exports()
        elif args.action == "upload":
            result = upload_verified(args.dataset, args.split)
        elif args.action == "evaluate":
            result = evaluate(args)
        else:
            if not args.question:
                raise ValueError("ask requires --question.")
            state = run_question(build_workflow(open_retriever(), chat_model()), args.question, trace=args.trace)
            result = state["answer"]
        print(json.dumps(result, ensure_ascii=True, indent=2))
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    except Exception as error:
        parser.exit(1, f"Operation failed: {type(error).__name__}. Check credentials, region/endpoint, and permissions privately.\n")


if __name__ == "__main__":
    main()
