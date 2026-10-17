# hybrid-v11-20261017\dev\bm25

Metadata: `{"method": "bm25", "split": "dev", "settings": {"bm25_k1": 1.5, "bm25_b": 0.75, "bm25_epsilon": 0.25, "tokenizer": "unicode-alphanumeric-casefold-v1", "stopwords": false, "rrf_constant": 60, "candidate_k": 20, "weights": [1, 1], "tie_break": "chunk_id", "lexical_positive_scores_only": true}, "code_hashes": {"retrieval.py": "464a89710efc927ebeba58f7c95735724af4ab944af4333f74d4a5b02c917ad2", "workflow.py": "377f1e53b06435c7539687fb4b800924f41d09c3494ce6b2becf5411ebfed40d", "rag.py": "8d6ab90897f45fe53f1ff1602360ace1a256994bd7ace1efdad42dfff23322fc", "hybrid_report.py": "fd953eb07d8acf3f8bc901f1c6b48c1e314f81445b64cc412da3c3fac0715b1a", "benchmark_retrieval.py": "9dbe8eedb3d4cce0bf78b3b3e84f80d556bd81a7fdb68ce9125b747cc29d8eaf", "eval_metrics.py": "df977911939ad78e30bb8f8e1d2152f4085a2438099bcdcc34c2dad480a05dcb"}, "source_sha256": "65c5c2cd22a1ad1529603a5fbe8e0493ffd7f9da04d807e7b28fd6351186ae56", "index_fingerprint": "394c832e5e8bee68fa9f85fca85d97421081139d29838e162be5fe30e2c21dc6", "startup_ms": 31.06889999980922, "k": 10, "latency": "one invoke, warm query cache, no trace overhead", "generation_enabled": false, "commit": "85696f0d2c43bed57c1a4eaca2ef757a2c0e88c5"}`.

Questions: 10. Errors: 0. No LLM judge was used.

| Metric | Result | Scored questions |
|---|---|---|
| hit_at1 | 1.0000 | 8 |
| hit_at5 | 1.0000 | 8 |
| mrr_at10 | 1.0000 | 8 |
| complete_evidence_at5 | 1.0000 | 7 |

Unanswerable questions are excluded from retrieval scores. Any error withholds aggregates.
Citation validity is structural only. Answer correctness and groundedness remain manual and unscored.
Review generated answers, retrieved passages, refusals, and any chat/top-ten prefix mismatch in results.csv.

## Retrieval misses and errors

