# Paired retrieval comparison

| Method | hit_at1 | hit_at5 | mrr_at10 | complete_evidence_at5 | multi_passage_coverage_at5 | multi_passage_complete_at5 | Median ms | Mean ms | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dense | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | 28.854 | 29.708 | 0 |
| bm25 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | 0.745 | 0.771 | 0 |
| hybrid | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | 31.287 | 31.327 | 0 |

Unanswerable cases have rankings and latency but no retrieval-accuracy score or refusal assessment.
Multi-passage scores require at least two evidence groups; an empty subset is N/A.
Denominators: `{"hit_at1": 8, "hit_at5": 8, "mrr_at10": 8, "complete_evidence_at5": 7, "multi_passage_coverage_at5": 0, "multi_passage_complete_at5": 0}`.

## Per-query changes relative to dense

| ID | Method | MRR delta | CompleteEvidence delta | Actual top five |
|---|---|---:|---:|---|

## Incomplete or missed evidence

