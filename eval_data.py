"""Dataset loading, review gates, and LangSmith example conversion."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASETS = {"baseline": ROOT / "evals/questions.json", "harder": ROOT / "evals/questions_v1_1.json"}
REFERENCE_FIELDS = ("id", "answerable", "category", "reference_answer", "gold_chunk_ids", "gold_pages",
                    "gold_evidence", "required_evidence_groups", "verification_status")


def load_questions(dataset, split=None, *, require_verified=False):
    questions = json.loads(DATASETS[dataset].read_text(encoding="utf-8"))
    questions = [{"split": "baseline", **q} for q in questions]
    expected = {"baseline": (25, 20), "harder": (50, 40)}[dataset]
    if (len(questions), sum(q["answerable"] is True for q in questions)) != expected:
        raise ValueError("Dataset size/answerability differs from the declared benchmark.")
    if dataset == "harder":
        counts = [(sum(q["split"] == split for q in questions),
                   sum(q["split"] == split and q["answerable"] is True for q in questions))
                  for split in ["dev", "held_out"]]
        if counts != [(10, 8), (40, 32)]:
            raise ValueError("Expected 8+2 development and 32+8 held-out cases.")
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)) or len({q["question"].casefold() for q in questions}) != len(questions):
        raise ValueError("Question IDs and text must be unique.")
    for q in questions:
        if q["verification_status"] not in {"verified", "needs_review"} or not isinstance(q["answerable"], bool):
            raise ValueError(f"Invalid status or answerability for {q['id']}.")
        gold = set(q["gold_chunk_ids"])
        if q["answerable"]:
            if not gold or not q["reference_answer"] or not q["gold_evidence"]:
                raise ValueError(f"Missing evidence for {q['id']}.")
            if {e["chunk_id"] for e in q["gold_evidence"]} != gold:
                raise ValueError(f"Evidence IDs differ from gold IDs for {q['id']}.")
            if any(not e["quote"] or not e["pages"] for e in q["gold_evidence"]):
                raise ValueError(f"Empty evidence for {q['id']}.")
            if set(q["gold_pages"]) != {page for e in q["gold_evidence"] for page in e["pages"]}:
                raise ValueError(f"Gold pages differ from supporting excerpts for {q['id']}.")
        elif gold or q["gold_pages"] or q["gold_evidence"] or q["reference_answer"] is not None:
            raise ValueError(f"Unanswerable question has positive evidence: {q['id']}.")
        if q["category"] == "multi_fact" and not q.get("required_evidence_groups"):
            raise ValueError(f"Missing evidence groups for {q['id']}.")
        if any(not group or not set(group) <= gold for group in q.get("required_evidence_groups", [])):
            raise ValueError(f"Invalid evidence group for {q['id']}.")
    selected = [q for q in questions if split is None or q["split"] == split]
    if not selected:
        raise ValueError("No questions in the selected split.")
    pending = [q["id"] for q in selected if q["verification_status"] != "verified"]
    if require_verified and pending:
        raise ValueError("Independent gold-label approval required before import/evaluation: " + ", ".join(pending))
    return selected


def as_example(question, source_hash):
    reference = {key: question.get(key, []) if key == "required_evidence_groups" else question[key]
                 for key in REFERENCE_FIELDS}
    return {"inputs": {"question": question["question"]}, "outputs": reference,
            "metadata": {"question_id": question["id"], "split": question["split"],
                         "verification_status": question["verification_status"], "source_sha256": source_hash},
            "split": question["split"]}


def source_hash(dataset):
    data = json.loads(DATASETS[dataset].read_text(encoding="utf-8"))
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def prepare_exports():
    baseline = load_questions("baseline", require_verified=True)
    export = ROOT / "evals/langsmith_baseline.jsonl"
    export.write_text("".join(json.dumps(as_example(q, source_hash("baseline")), ensure_ascii=False) + "\n"
                              for q in baseline), encoding="utf-8")
    draft = load_questions("harder")
    multi_fact = [q for q in draft if q["answerable"] and q["category"] == "multi_fact"]
    single_group = sum(len(q["required_evidence_groups"]) == 1 for q in multi_fact)
    approved = all(q["verification_status"] == "verified" for q in draft)
    lines = ["# v1.1 harder dataset: independent review", "",
             ("50 reviewed questions: 40 answerable and 10 unanswerable. All labels independently approved and verified."
              if approved else "50 new draft questions: 40 answerable and 10 unanswerable. Labels require independent approval."),
             "Development: 8 answerable + 2 unanswerable. Held-out: 32 answerable + 8 unanswerable.",
             "Dataset synchronization is separate from evaluation. No new benchmark has been run or scored.",
             "Gold chunk IDs are disjoint between splits; questions still share one PDF and related topics.",
             f"The dataset is multi-fact-heavy: {len(multi_fact)}/40 answerable questions are multi_fact; "
             f"{single_group} have one required evidence group and {len(multi_fact) - single_group} have at least two.",
             "Keep aggregate CompleteEvidence@5 and plan a separate multi-passage result restricted to questions "
             "requiring at least two distinct evidence groups. One-group coverage does not demonstrate multi-passage retrieval.",
             "After the requested split rebalance, all 17 two-group questions are held-out. The development "
             "multi-passage subgroup is empty; report it as unavailable, not zero or a passing score.",
             "Review reference completeness, exact supporting pages, excerpt relevance, evidence groups, and negative-case scope.",
             ("Verification records explicit user approval after source-consistency checks; references remain frozen."
              if approved else "After independent approval, update verification_status in questions_v1_1.json. Do not infer approval from matching text."), ""]
    for q in draft:
        lines.extend([f"<details><summary>{q['id']} | {q['split']} | {q['question']}</summary>", "",
                      f"Status: **{q['verification_status']}**. Category: `{q['category']}`. Region: `{q['region']}`.", "",
                      f"Reference: {q['reference_answer'] or 'Unsupported; refuse using the PDF-only contract.'}", "",
                      f"Gold chunks: `{', '.join(q['gold_chunk_ids']) or 'None'}`. Physical PDF pages: {q['gold_pages']}.", "",
                      f"Required groups: `{json.dumps(q['required_evidence_groups'])}`.", "", q['review_notes'], ""])
        for e in q["gold_evidence"]:
            lines.extend([f"`{e['chunk_id']}` | physical pages {e['pages']}", "",
                          "> " + e["quote"].replace("\n", "\n> "), ""])
        lines.extend(["</details>", ""])
    review = "\n".join(line.rstrip() for line in "\n".join(lines).splitlines())
    (ROOT / "evals/review_v1_1.md").write_text(review + "\n", encoding="utf-8")
    return {"verified_baseline_exported": len(baseline), "draft_questions": len(draft),
            "draft_verified": sum(q["verification_status"] == "verified" for q in draft)}
