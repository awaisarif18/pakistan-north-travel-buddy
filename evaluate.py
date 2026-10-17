"""Evaluate verified gold labels only. Draft labels never produce scores."""

import csv
import json
from pathlib import Path
import time

from google.genai import errors

from rag import INDEX_CONFIG, gemini_client, open_collection, retrieve

EVAL_DIR = Path(__file__).resolve().parent / "evals"
FIELDS = ["id", "question", "category", "answerable", "verification_status", "status",
          "gold_chunk_ids", "gold_pages", "retrieved_ids", "retrieved_pages",
          "first_relevant_rank", "hit_at5", "reciprocal_rank", "retrieved_distances",
          "required_evidence_groups", "complete_evidence_at5", "missing_evidence_groups"]


def retrieval_scores(retrieved_ids, gold_ids):
    rank = next((i for i, chunk_id in enumerate(retrieved_ids[:10], 1) if chunk_id in gold_ids), None)
    return rank, int(rank is not None and rank <= 5), 1 / rank if rank else 0.0


def complete_evidence_score(retrieved_ids, groups):
    if not groups:
        raise ValueError("CompleteEvidence@5 requires nonempty evidence groups.")
    top_five = set(retrieved_ids[:5])
    missing = [group for group in groups if not top_five.intersection(group)]
    return int(not missing), missing


def validate_questions(questions, collection):
    ids = [question["id"] for question in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Evaluation question IDs must be unique.")
    known = set(collection.get(include=[])["ids"])
    for question in questions:
        if question["verification_status"] not in {"needs_review", "verified"}:
            raise ValueError(f"{question['id']}: use needs_review or verified.")
        if not isinstance(question["answerable"], bool):
            raise ValueError(f"{question['id']}: answerable must be true or false.")
        gold = set(question["gold_chunk_ids"])
        if question["answerable"] and (not gold or not gold <= known):
            raise ValueError(f"{question['id']}: supporting chunks are missing from the index.")
        if not question["answerable"] and gold:
            raise ValueError(f"{question['id']}: unanswerable questions must have no gold chunks.")
        if question["answerable"] and question["category"] == "multi_fact":
            groups = question.get("required_evidence_groups")
            if not isinstance(groups, list) or not groups:
                raise ValueError(f"{question['id']}: missing reviewed required_evidence_groups.")
            for group in groups:
                if (not isinstance(group, list) or not group
                        or not all(isinstance(chunk_id, str) and chunk_id in gold for chunk_id in group)):
                    raise ValueError(f"{question['id']}: each evidence group must be a nonempty list of gold chunk IDs.")


def evaluate(questions, collection):
    rows, client = [], None
    try:
        for question in questions:
            row = {key: question[key] for key in FIELDS[:5]}
            row.update(gold_chunk_ids=";".join(question["gold_chunk_ids"]),
                       gold_pages=";".join(map(str, question["gold_pages"])),
                       status="needs_review", retrieved_ids="", retrieved_pages="",
                       first_relevant_rank="", hit_at5="", reciprocal_rank="", retrieved_distances="",
                       required_evidence_groups=json.dumps(question.get("required_evidence_groups", [])),
                       complete_evidence_at5="", missing_evidence_groups="")
            if question["verification_status"] == "verified" and not question["answerable"]:
                row["status"] = "unanswerable_manual_review"
            elif question["verification_status"] == "verified":
                if client is None:
                    client = gemini_client()
                try:
                    matches = retrieve(collection, client, question["question"], top_k=10)
                    rank, hit, rr = retrieval_scores([m["id"] for m in matches], question["gold_chunk_ids"])
                    row.update(status="evaluated", first_relevant_rank=rank or "not_in_top10",
                               hit_at5=hit, reciprocal_rank=rr,
                               retrieved_ids=";".join(m["id"] for m in matches),
                               retrieved_distances=";".join(str(m["distance"]) for m in matches),
                               retrieved_pages=";".join(f"{m['metadata']['page_start']}-{m['metadata']['page_end']}" for m in matches))
                    if question["category"] == "multi_fact":
                        coverage, missing = complete_evidence_score(
                            [m["id"] for m in matches], question["required_evidence_groups"])
                        row.update(complete_evidence_at5=coverage, missing_evidence_groups=json.dumps(missing))
                except (errors.APIError, ValueError):
                    row["status"] = "retrieval_error"
                time.sleep(1)
            rows.append(row)
    finally:
        if client is not None:
            client.close()
    return rows


def save_results(rows, questions):
    with (EVAL_DIR / "results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    verified = sum(q["answerable"] and q["verification_status"] == "verified" for q in questions)
    scored = [row for row in rows if row["status"] == "evaluated"]
    failures = [row for row in scored if not row["hit_at5"]]
    errors_count = sum(row["status"] == "retrieval_error" for row in rows)
    complete = verified > 0 and len(scored) == verified
    hit = f"{sum(row['hit_at5'] for row in scored) / verified:.4f}" if complete else "Not calculated"
    mrr = f"{sum(row['reciprocal_rank'] for row in scored) / verified:.4f}" if complete else "Not calculated"
    multi = [row for row in scored if row["category"] == "multi_fact"]
    multi_count = sum(q["answerable"] and q["category"] == "multi_fact"
                      and q["verification_status"] == "verified" for q in questions)
    coverage_ready = multi_count > 0 and len(multi) == multi_count
    coverage = (f"{sum(row['complete_evidence_at5'] for row in multi) / multi_count:.4f}"
                if coverage_ready else "Not calculated")
    lines = ["# Retrieval evaluation", "", "## Current results", "",
             "| Metric | Actual result |", "|---|---|",
             f"| Verified answerable questions | {verified} |",
             f"| Hit@5 | {hit} |", f"| MRR@10 | {mrr} |",
             f"| Verified multi-fact questions | {multi_count} |",
             f"| CompleteEvidence@5 | {coverage} |",
             f"| Failed retrieval questions | {len(failures) if complete else 'Not calculated'} |", "",
             f"Successfully retrieved verified questions: {len(scored)}. Retrieval errors: {errors_count}.",
             "Scores require verified labels and a successful retrieval for every verified answerable question.",
             "Draft labels are excluded. These results do not measure answer correctness.", "",
             "## Method", "",
             f"Model: `{INDEX_CONFIG['embedding_model']}`, {INDEX_CONFIG['dimensions']} dimensions; cosine search, top 10.",
             "Hit@5 = questions with at least one gold chunk in ranks 1-5 / verified answerable questions.",
             "MRR@10 = mean of 1 / first gold rank in ranks 1-10, or zero when no gold chunk appears.",
             "CompleteEvidence@5 = fraction of verified multi-fact questions with at least one top-five chunk from EVERY required evidence group.",
             "IDs within a group are alternatives; all groups are required. One chunk may satisfy multiple groups when the reviewed labels allow it.",
             "Hit@5 and MRR@10 use the first matching gold chunk, so they do not establish complete evidence coverage.",
             "CSV retrieved IDs, pages, and distances are parallel lists ordered from rank 1 to rank 10.", "",
             "## Failures and next steps", ""]
    if failures:
        for row in failures:
            lines.append(f"- {row['id']}: {row['question']} Expected `{row['gold_chunk_ids']}`. Retrieved `{row['retrieved_ids']}`.")
    else:
        lines.append("No evaluated Hit@5 failures to list yet." if not scored else "No Hit@5 failures in the evaluated questions.")
    lines.extend(["", "### Gold evidence below rank one", ""])
    lower_ranked = [row for row in scored if str(row["first_relevant_rank"]) != "1"]
    for row in lower_ranked:
        lines.append(f"- {row['id']}: {row['question']} First gold rank: {row['first_relevant_rank']}. "
                     f"Top three: `{';'.join(row['retrieved_ids'].split(';')[:3])}`.")
    if scored and not lower_ranked:
        lines.append("Every evaluated question retrieved gold evidence at rank one.")
    lines.extend(["", "### Multi-fact evidence coverage", "",
                  "| Question | CompleteEvidence@5 | Missing evidence groups |",
                  "|---|---|---|"])
    for row in multi:
        lines.append(f"| {row['id']} | {row['complete_evidence_at5']} | `{row['missing_evidence_groups']}` |")
    for row in multi:
        if not row["complete_evidence_at5"]:
            lines.append(f"\n- {row['id']}: {row['question']} Top five: `{';'.join(row['retrieved_ids'].split(';')[:5])}`. Missing groups: `{row['missing_evidence_groups']}`.")
    lines.extend(["", "Inspect missed evidence and question wording before changing retrieval. No reranker or hybrid search is implemented.",
                  "If retrieval errors occur, rerun using cached query embeddings before interpreting the aggregate scores.", "",
                  "## Unanswerable questions", "",
                  "Excluded from retrieval metrics. This script never calls Gemini answer generation.",
                  "Ask these questions in the chatbot and inspect refusals separately; label approval alone does not verify refusal behavior.", ""])
    lines.extend(f"- {q['id']}: {q['question']}" for q in questions if not q["answerable"])
    lines.extend(["", "## Gold label review", "",
                  "Verification statuses below record label approval. Only verified answerable questions enter retrieval scores.",
                  "The reference answers and supporting excerpts are retained for inspection. Future label changes require review before rescoring.", "",
                  "| ID | Category | Question | Gold chunks | PDF pages | Reference answer | Status |",
                  "|---|---|---|---|---|---|---|"])
    escape = lambda text: str(text or "Not available in the PDF").replace("|", "\\|").replace("\n", " ")
    for q in questions:
        lines.append("| " + " | ".join(escape(value) for value in [
            q["id"], q["category"], q["question"], ", ".join(q["gold_chunk_ids"]) or "None",
            ", ".join(map(str, q["gold_pages"])) or "None", q["reference_answer"], q["verification_status"],
        ]) + " |")
    lines.extend(["", "### Supporting excerpts for manual verification", ""])
    for q in questions:
        if not q["answerable"]:
            continue
        lines.extend([f"<details><summary>{q['id']}: {escape(q['question'])}</summary>", ""])
        if q.get("required_evidence_groups"):
            lines.extend([f"Required evidence groups: `{json.dumps(q['required_evidence_groups'])}`.", ""])
        for evidence in q["gold_evidence"]:
            lines.extend([f"`{evidence['chunk_id']}`, physical PDF pages {evidence['pages']}.", "",
                          "> " + evidence["quote"].replace("\n", "\n> "), ""])
        lines.extend(["</details>", ""])
    (EVAL_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Verified answerable: {verified}; evaluated: {len(scored)}; Hit@5: {hit}; MRR@10: {mrr}; CompleteEvidence@5: {coverage}")


def main():
    questions = json.loads((EVAL_DIR / "questions.json").read_text(encoding="utf-8"))
    collection = open_collection()
    validate_questions(questions, collection)
    rows = evaluate(questions, collection)
    save_results(rows, questions)
    print(f"Results: {EVAL_DIR / 'results.csv'}; review: {EVAL_DIR / 'summary.md'}")
    if any(row["status"] == "retrieval_error" for row in rows):
        raise SystemExit("Some retrievals failed. Check Gemini quota/access and rerun before reporting scores.")


if __name__ == "__main__":
    main()
