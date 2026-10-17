# Paired retrieval comparison

| Method | hit_at1 | hit_at5 | mrr_at10 | complete_evidence_at5 | multi_passage_coverage_at5 | multi_passage_complete_at5 | Median ms | Mean ms | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dense | 0.9375 | 1.0000 | 0.9688 | 0.9677 | 0.9706 | 0.9412 | 58.655 | 60.660 | 0 |
| bm25 | 0.8750 | 1.0000 | 0.9323 | 0.9355 | 0.9412 | 0.8824 | 0.839 | 0.872 | 0 |
| hybrid | 0.9375 | 1.0000 | 0.9635 | 0.9677 | 0.9706 | 0.9412 | 58.479 | 60.305 | 0 |

Unanswerable cases have rankings and latency but no retrieval-accuracy score or refusal assessment.
Multi-passage scores require at least two evidence groups; an empty subset is N/A.
Denominators: `{"hit_at1": 32, "hit_at5": 32, "mrr_at10": 32, "complete_evidence_at5": 31, "multi_passage_coverage_at5": 17, "multi_passage_complete_at5": 17}`.

## Per-query changes relative to dense

| ID | Method | MRR delta | CompleteEvidence delta | Actual top five |
|---|---|---:|---:|---|
| h08 | bm25 | +0.5000 | 0 | `p016-018-ca83b3ddd819, p018-020-73083763654d, p080-081-4717074613d0, p026-028-3af709bd9d8f, p078-080-77062c50650d` |
| h08 | hybrid | +0.5000 | 0 | `p016-018-ca83b3ddd819, p018-020-73083763654d, p026-028-3af709bd9d8f, p080-081-4717074613d0, p083-085-e588f14f58f1` |
| h17 | bm25 | -0.5000 | 0 | `p090-092-d469daea2cf5, p033-035-97d114c1c3a8, p047-049-8dc49f1b20f2, p058-060-fa9822ff4f99, p049-051-51be39ff7ee4` |
| h20 | bm25 | -0.6667 | -1 | `p032-033-d33bd27c781e, p014-016-b439f2d5f7da, p026-028-3af709bd9d8f, p076-078-8491e93c619d, p030-032-e38247495869` |
| h20 | hybrid | -0.6667 | 0 | `p032-033-d33bd27c781e, p076-078-8491e93c619d, p026-028-3af709bd9d8f, p040-042-e594be504c6e, p022-024-9d656b3640ce` |
| h36 | bm25 | -0.5000 | 0 | `p090-092-d469daea2cf5, p074-076-784ce56e21b3, p067-069-ead8a5550d3a, p054-057-7e1519e0731e, p076-078-8491e93c619d` |

## Incomplete or missed evidence

- h20 (bm25): Hit@5=1, CompleteEvidence@5=0. Gold `["p040-042-e594be504c6e", "p026-028-3af709bd9d8f"]`; top five `p032-033-d33bd27c781e, p014-016-b439f2d5f7da, p026-028-3af709bd9d8f, p076-078-8491e93c619d, p030-032-e38247495869`.
- h36 (dense): Hit@5=1, CompleteEvidence@5=0. Gold `["p072-074-249d8c96c2fc", "p074-076-784ce56e21b3"]`; top five `p074-076-784ce56e21b3, p078-080-77062c50650d, p076-078-8491e93c619d, p071-072-cc358ad79e0e, p069-070-ef7a401bc920`.
- h36 (bm25): Hit@5=1, CompleteEvidence@5=0. Gold `["p072-074-249d8c96c2fc", "p074-076-784ce56e21b3"]`; top five `p090-092-d469daea2cf5, p074-076-784ce56e21b3, p067-069-ead8a5550d3a, p054-057-7e1519e0731e, p076-078-8491e93c619d`.
- h36 (hybrid): Hit@5=1, CompleteEvidence@5=0. Gold `["p072-074-249d8c96c2fc", "p074-076-784ce56e21b3"]`; top five `p074-076-784ce56e21b3, p076-078-8491e93c619d, p071-072-cc358ad79e0e, p067-069-ead8a5550d3a, p090-092-d469daea2cf5`.
