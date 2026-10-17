"""Deterministic LangSmith feedback. Semantic answer quality stays manual."""

import re

from rag import NOT_FOUND, page_label


RETRIEVAL_KEYS = ("hit_at1", "hit_at5", "mrr_at10", "complete_evidence_at5")


def retrieval_scores(outputs, reference):
    """None means excluded/unscored, never a retrieval miss or a zero score."""
    excluded = dict.fromkeys(RETRIEVAL_KEYS)
    if reference.get("verification_status") != "verified" or not reference.get("answerable"):
        return excluded
    if outputs.get("error"):
        return excluded
    ids = outputs["retrieved_ids"][:10]
    if len(ids) != len(set(ids)):
        raise ValueError("Retrieved IDs must be unique and rank ordered.")
    gold = set(reference["gold_chunk_ids"])
    if not gold:
        raise ValueError("Verified answerable references require gold chunks.")
    rank = next((i for i, chunk_id in enumerate(ids, 1) if chunk_id in gold), None)
    scores = {"hit_at1": int(rank == 1), "hit_at5": int(rank is not None and rank <= 5),
              "mrr_at10": 1 / rank if rank else 0.0, "complete_evidence_at5": None}
    groups = reference.get("required_evidence_groups", [])
    if reference.get("category") == "multi_fact" and not groups:
        raise ValueError("Multi-fact references require reviewed evidence groups.")
    if groups:
        if any(not group or not set(group) <= gold for group in groups):
            raise ValueError("Each evidence group must contain valid gold alternatives.")
        scores["complete_evidence_at5"] = int(all(set(ids[:5]).intersection(group) for group in groups))
    return scores


def _retrieval_feedback(key, outputs, reference_outputs):
    score = retrieval_scores(outputs, reference_outputs)[key]
    return {"key": key, "score": score,
            "comment": "Verified retrieval evidence only; None means excluded or unavailable."}


def hit_at1(outputs, reference_outputs):
    return _retrieval_feedback("hit_at1", outputs, reference_outputs)


def hit_at5(outputs, reference_outputs):
    return _retrieval_feedback("hit_at5", outputs, reference_outputs)


def mrr_at10(outputs, reference_outputs):
    return _retrieval_feedback("mrr_at10", outputs, reference_outputs)


def complete_evidence_at5(outputs, reference_outputs):
    return _retrieval_feedback("complete_evidence_at5", outputs, reference_outputs)


def citation_validity(outputs):
    answer = outputs.get("answer")
    if answer is None or outputs.get("error"):
        return {"key": "citation_validity", "score": None, "comment": "No generated answer to check."}
    cited = answer.get("cited_ids", [])
    markers = re.findall(r"\[(PDF [^\]]+)\]", answer.get("text", ""))
    if answer.get("answerable") is False:
        valid = not cited and not markers and answer.get("text") == NOT_FOUND
    elif answer.get("answerable") is True:
        sources = {m["id"]: m for m in outputs.get("matches", [])}
        valid = bool(cited) and set(cited) <= sources.keys()
        if valid:
            expected = {page_label(sources[chunk_id]["metadata"]) for chunk_id in cited}
            displayed = {label for marker in markers for label in marker.split("; ")}
            valid = expected == displayed
    else:
        valid = False
    return {"key": "citation_validity", "score": int(valid),
            "comment": "Checks retrieved IDs and stored page labels, not factual support."}


def appropriate_refusal(outputs, reference_outputs):
    if (reference_outputs.get("verification_status") != "verified"
            or reference_outputs.get("answerable") or "answer" not in outputs or outputs.get("error")):
        return {"key": "appropriate_refusal", "score": None, "comment": "Not an eligible negative answer."}
    answer = outputs["answer"]
    valid = (answer.get("answerable") is False and answer.get("text") == NOT_FOUND
             and not answer.get("cited_ids"))
    return {"key": "appropriate_refusal", "score": int(valid),
            "comment": "Strict fixed-refusal contract; broader semantics need manual review."}


def answer_correctness(outputs, reference_outputs):
    return {"key": "answer_correctness", "score": None,
            "comment": "Manual review against reference answer and original PDF required."}


def groundedness(outputs, reference_outputs):
    return {"key": "groundedness", "score": None,
            "comment": "Manual claim-by-claim review against the retrieved passages required."}


RETRIEVAL_EVALUATORS = [hit_at1, hit_at5, mrr_at10, complete_evidence_at5]
ANSWER_EVALUATORS = [citation_validity, appropriate_refusal, answer_correctness, groundedness]
