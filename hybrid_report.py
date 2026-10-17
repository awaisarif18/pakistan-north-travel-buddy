"""Deterministic feedback and paired reports for the hybrid comparison."""

import csv
import json
from statistics import mean, median

from eval_metrics import RETRIEVAL_KEYS, retrieval_scores

METRICS = (*RETRIEVAL_KEYS, "multi_passage_coverage_at5", "multi_passage_complete_at5")


def group_coverage(outputs, reference):
    groups = reference.get("required_evidence_groups", [])
    if (reference.get("verification_status") != "verified" or not reference.get("answerable")
            or outputs.get("error") or len(groups) < 2):
        return None
    retrieved = set(outputs["retrieved_ids"][:5])
    return sum(bool(retrieved.intersection(group)) for group in groups) / len(groups)


def multi_passage_coverage(outputs, reference_outputs):
    return {"key": "multi_passage_coverage_at5", "score": group_coverage(outputs, reference_outputs),
            "comment": "Fraction of required groups covered, only on cases with at least two groups."}


def multi_passage_complete(outputs, reference_outputs):
    coverage = group_coverage(outputs, reference_outputs)
    return {"key": "multi_passage_complete_at5", "score": None if coverage is None else int(coverage == 1),
            "comment": "All required groups covered; only multi-passage cases are eligible."}


def retrieval_latency(outputs):
    return {"key": "retrieval_latency_ms", "score": outputs.get("retrieval_latency_ms"),
            "comment": "One warm-query-cache invoke; excludes startup, vector preparation, and experiment upload."}


def write_comparison(directory, questions, records):
    rows = []
    for q in questions:
        dense = retrieval_scores(records["dense"][q["id"]], q)
        for method, outputs in records.items():
            actual = outputs[q["id"]]
            scores = retrieval_scores(actual, q)
            coverage = group_coverage(actual, q)
            rows.append({"id": q["id"], "question": q["question"], "answerable": q["answerable"],
                         "method": method, **scores, "multi_passage_coverage_at5": coverage,
                         "multi_passage_complete_at5": None if coverage is None else int(coverage == 1),
                         "retrieval_latency_ms": actual.get("retrieval_latency_ms"),
                         "mrr_delta_vs_dense": None if scores["mrr_at10"] is None else scores["mrr_at10"] - dense["mrr_at10"],
                         "complete_delta_vs_dense": None if scores["complete_evidence_at5"] is None else scores["complete_evidence_at5"] - dense["complete_evidence_at5"],
                         "gold_ids": json.dumps(q["gold_chunk_ids"]), "gold_pages": json.dumps(q["gold_pages"]),
                         "required_groups": json.dumps(q["required_evidence_groups"]),
                         "retrieved_ids": json.dumps(actual["retrieved_ids"]),
                         "retrieved_pages": json.dumps(actual.get("retrieved_pages", [])),
                         "v1_dense_parity": actual.get("v1_dense_parity"), "error": actual.get("error", "")})
    with (directory / "comparison.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {}
    lines = ["# Paired retrieval comparison", "", "| Method | " + " | ".join(METRICS) + " | Median ms | Mean ms | Errors |",
             "|---|" + "---:|" * (len(METRICS) + 3)]
    for method in records:
        selected = [r for r in rows if r["method"] == method]
        errors = sum(bool(r["error"]) for r in selected)
        values = {metric: [r[metric] for r in selected if r[metric] is not None] for metric in METRICS}
        scores = {metric: mean(value) if value and not errors else None for metric, value in values.items()}
        times = [r["retrieval_latency_ms"] for r in selected if r["retrieval_latency_ms"] is not None]
        scores.update(median_latency_ms=median(times) if times else None,
                      mean_latency_ms=mean(times) if times else None, errors=errors,
                      denominators={key: len(value) for key, value in values.items()})
        summary[method] = scores
        display = ["N/A" if scores[key] is None else f"{scores[key]:.4f}" for key in METRICS]
        lines.append(f"| {method} | " + " | ".join(display) + f" | {scores['median_latency_ms']:.3f} | {scores['mean_latency_ms']:.3f} | {errors} |")
    lines.extend(["", "Unanswerable cases have rankings and latency but no retrieval-accuracy score or refusal assessment.",
                  "Multi-passage scores require at least two evidence groups; an empty subset is N/A.",
                  f"Denominators: `{json.dumps(summary['dense']['denominators'])}`.", "",
                  "## Per-query changes relative to dense", "",
                  "| ID | Method | MRR delta | CompleteEvidence delta | Actual top five |", "|---|---|---:|---:|---|"])
    for row in rows:
        if row["method"] == "dense" or row["mrr_delta_vs_dense"] is None:
            continue
        if row["mrr_delta_vs_dense"] or row["complete_delta_vs_dense"]:
            lines.append(f"| {row['id']} | {row['method']} | {row['mrr_delta_vs_dense']:+.4f} | "
                         f"{row['complete_delta_vs_dense']} | `{', '.join(json.loads(row['retrieved_ids'])[:5])}` |")
    lines.extend(["", "## Incomplete or missed evidence", ""])
    lines.extend(f"- {r['id']} ({r['method']}): Hit@5={r['hit_at5']}, CompleteEvidence@5={r['complete_evidence_at5']}. "
                 f"Gold `{r['gold_ids']}`; top five `{', '.join(json.loads(r['retrieved_ids'])[:5])}`."
                 for r in rows if r["error"] or r["hit_at5"] == 0 or r["complete_evidence_at5"] == 0)
    (directory / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (directory / "aggregate.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
