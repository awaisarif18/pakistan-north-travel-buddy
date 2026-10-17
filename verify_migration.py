"""Cached retrieval parity and focused graph checks; --live adds four answer calls."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.runnables import RunnableLambda

import rag
from workflow import (VerifiedEmbeddings, build_workflow, chat_model,
                      open_retriever, prepare_question, validate_citations)


def fingerprint(collection):
    stored = collection.get(include=["documents", "metadatas", "embeddings"])
    rows = sorted(zip(stored["ids"], stored["documents"], stored["metadatas"], stored["embeddings"].tolist()))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def check_adapter(output):
    response = SimpleNamespace(embeddings=[SimpleNamespace(values=[0.0] * rag.DIMENSIONS)])
    client = Mock()
    client.models.embed_content.return_value = response
    cache_dir = Path(tempfile.mkdtemp(prefix="cache-", dir=output))
    question = "  adapter cache contract check  "
    with patch.object(rag, "DATA_DIR", cache_dir):
        adapter = VerifiedEmbeddings(client)
        assert adapter.embed_query(question) == adapter.embed_query(question)
        assert client.models.embed_content.call_count == 1
        request = client.models.embed_content.call_args.kwargs
        assert request["model"] == rag.EMBEDDING_MODEL
        assert request["contents"] == f"task: search result | query: {question}"
        assert request["config"].output_dimensionality == 3072
        key = hashlib.sha256(json.dumps([rag.INDEX_CONFIG, question], sort_keys=True).encode()).hexdigest()
        assert list(json.loads((cache_dir / "query_embeddings.json").read_text())) == [key]
        try:
            adapter.embed_documents(["Do not re-embed"])
        except ValueError:
            pass
        else:
            raise AssertionError("Document embedding must be blocked.")


def check_graph(documents):
    payload = {"answerable": True, "paragraphs": [{"text": "Supported fixture.", "sources": ["S1"]}]}
    chat = Mock()
    chat.with_structured_output.return_value = RunnableLambda(lambda _: payload)
    graph = build_workflow(RunnableLambda(lambda _: documents), chat)
    question = "  preserve exact question  "
    events = list(graph.stream({"question": question}))
    assert [next(iter(event)) for event in events] == [
        "prepare_question", "retrieve_evidence", "generate_grounded_answer", "validate_citations"]
    sources = {"S1": {"id": documents[0].id, "metadata": documents[0].metadata}}
    assert events[-1]["validate_citations"]["answer"] == rag.format_answer(payload, sources)
    assert prepare_question({"question": question})["question"] == question
    try:
        prepare_question({"question": "  "})
    except ValueError:
        pass
    else:
        raise AssertionError("Blank question accepted.")
    for paragraphs in [[], [{"text": "Unsupported", "sources": []}],
                       [{"text": "Unsupported", "sources": ["S99"]}]]:
        try:
            validate_citations({"matches": list(sources.values()),
                                "payload": {"answerable": True, "paragraphs": paragraphs}})
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid citations accepted.")
    empty_chat = Mock()
    result = build_workflow(RunnableLambda(lambda _: []), empty_chat).invoke({"question": "Missing?"})
    assert result["answer"] == {"text": rag.NOT_FOUND, "answerable": False, "cited_ids": []}
    empty_chat.with_structured_output.assert_not_called()


def compare_rankings(questions, collection, retriever):
    rows = []
    saved = {row["id"]: row for row in csv.DictReader((rag.ROOT / "evals/results.csv").open(encoding="utf-8"))}
    for question in questions:
        old = rag.retrieve(collection, None, question["question"], top_k=10)
        new = retriever.vectorstore.similarity_search_with_score(question["question"], k=10)
        new_ids = [doc.id for doc, _ in new]
        assert new_ids == [match["id"] for match in old], question["id"]
        assert all(doc.metadata == match["metadata"] and doc.page_content == match["text"]
                   for (doc, _), match in zip(new, old)), question["id"]
        delta = max(abs(distance - match["distance"]) for (_, distance), match in zip(new, old))
        assert delta == 0, (question["id"], delta)
        top_five = retriever.invoke(question["question"])
        assert [doc.id for doc in top_five] == new_ids[:5], question["id"]
        archived = saved[question["id"]]["retrieved_ids"]
        if archived:
            assert new_ids == archived.split(";"), (question["id"], "archived ranking differs")
        rows.append({"id": question["id"], "question": question["question"], "parity": "pass",
                     "old_top10": ";".join(match["id"] for match in old), "new_top10": ";".join(new_ids),
                     "maximum_distance_delta": delta, "metadata_and_text_match": True})
    return rows


def live_checks(questions, retriever, output):
    path = output / "answers.json"
    results = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    graph = build_workflow(retriever, chat_model())
    code_hash = hashlib.sha256((rag.ROOT / "workflow.py").read_bytes()).hexdigest()
    for question_id in ["q01", "q17", "q21", "q25"]:
        question = next(q for q in questions if q["id"] == question_id)
        saved = next((row for row in results if row["id"] == question_id), None)
        if saved:
            if (saved["question"] != question["question"] or saved.get("model") != rag.CHAT_MODEL
                    or saved.get("workflow_sha256") != code_hash):
                raise ValueError("Saved migration answers are from different code/configuration; review them before another paid check.")
            assert saved["answer"]["answerable"] == question["answerable"], question_id
            continue
        state = graph.invoke({"question": question["question"]})
        results.append({"id": question_id, "question": question["question"], "expected_answerable": question["answerable"],
                        "answer": state["answer"], "matches": state["matches"], "model": rag.CHAT_MODEL,
                        "workflow_sha256": code_hash, "review_status": "needs_manual_review"})
        path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        assert state["answer"]["answerable"] == question["answerable"], question_id
    return len(results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Generate up to four answers, reusing saved migration outputs.")
    args = parser.parse_args()
    output = rag.DATA_DIR / "v1.1-checks"
    output.mkdir(exist_ok=True)
    original_files = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in rag.DB_PATH.rglob("*") if p.is_file()}
    protected = [rag.ROOT / name for name in ["rag.py", "evals/questions.json", "evals/results.csv", "evals/summary.md", "evals/answer_quality.md"]]
    hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    questions = json.loads((rag.ROOT / "evals/questions.json").read_text(encoding="utf-8"))
    assert len(questions) == 25 and all(q["verification_status"] == "verified" for q in questions)
    cache = json.loads((rag.DATA_DIR / "query_embeddings.json").read_text())
    for q in questions:
        key = hashlib.sha256(json.dumps([rag.INDEX_CONFIG, q["question"]], sort_keys=True).encode()).hexdigest()
        if key not in cache:
            raise ValueError(f"Missing cached query for {q['id']}; verification will not make embedding calls.")
    copy = Path(tempfile.mkdtemp(prefix="index-", dir=output)) / "chroma"
    shutil.copytree(rag.DB_PATH, copy)
    rag.DB_PATH = copy
    collection = rag.open_collection()
    before = fingerprint(collection)
    assert collection.count() == 49
    check_adapter(output)
    with patch.object(rag, "embed", side_effect=AssertionError("Unexpected embedding API call")):
        retriever = open_retriever()
        rows = compare_rankings(questions, collection, retriever)
        baseline_path = output / "baseline.json"
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            assert before == baseline["collection_fingerprint"]
            assert [row["old_top10"] for row in rows] == [
                ";".join(match["id"] for match in row["matches"]) for row in baseline["results"]]
        check_graph(retriever.invoke(questions[0]["question"]))
        answer_count = live_checks(questions, retriever, output) if args.live else 0
    assert fingerprint(collection) == before
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == value for p, value in original_files.items())
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == value for p, value in hashes.items())
    with (rag.ROOT / "evals/v1_1_parity.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {"questions": len(rows), "ranking_matches": len(rows), "vectors": collection.count(),
              "maximum_distance_delta": max(row["maximum_distance_delta"] for row in rows),
              "collection_fingerprint": before, "original_index_and_evaluations_unchanged": True,
              "real_embedding_calls": 0, "graph_and_citation_checks": "pass", "live_answer_outputs": answer_count}
    (output / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
