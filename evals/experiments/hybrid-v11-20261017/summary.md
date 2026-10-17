# v1.1 dense, BM25, and hybrid benchmark

## Decision and chronology

Dense remains the default. All three methods tied on development accuracy, so the predeclared tie rule selected dense before the held-out comparison. No retrieval settings were tuned after observing held-out results. Only one BM25/RRF configuration was evaluated; this was a baseline comparison rather than a parameter sweep.

Settings frozen at `2026-10-17T15:43:09.401756+00:00`. The [freeze manifest](frozen_settings.json) records code/data hashes, parameters, and the development-only selection. The [held-out start marker](held_out_started.json) was created afterward and prevents repeating the final comparison in this group.

## Measured scores

Development: 8 answerable and 2 unanswerable questions. Every method scored Hit@1 = Hit@5 = MRR@10 = 1.0000 on 8 cases and CompleteEvidence@5 = 1.0000 on 7 eligible cases. Multi-passage coverage is N/A: no development question requires two evidence groups.

Held-out: 32 answerable and 8 unanswerable questions. Scores below use 32 cases for Hit/MRR, 31 for CompleteEvidence@5, and 17 two-group cases for multi-passage metrics.

| Method | Hit@1 | Hit@5 | MRR@10 | CompleteEvidence@5 | Multi-passage group coverage@5 | Multi-passage complete@5 | Median ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| dense | 0.9375 | 1.0000 | 0.9688 | 0.9677 | 0.9706 | 0.9412 | 58.655 |
| bm25 | 0.8750 | 1.0000 | 0.9323 | 0.9355 | 0.9412 | 0.8824 | 0.839 |
| hybrid | 0.9375 | 1.0000 | 0.9635 | 0.9677 | 0.9706 | 0.9412 | 58.479 |

Dense and hybrid completed 30/31 eligible evidence cases and 16/17 multi-passage cases, covering 33/34 required multi-passage groups. BM25 completed 29/31 and 15/17, covering 32/34 groups. Retrieval errors: zero in all six experiments. All 150 method/query pairs have actual top-ten IDs and physical-page metadata.

## Retrieval configuration and metrics

Each method receives the exact approved question string. Conversation history,
query rewriting, and answer generation are excluded from this retrieval-only
comparison, so they cannot change the queries between methods.

- Dense uses the unchanged Gemini query-prefix/configuration/cache adapter and original cosine Chroma ranking.
- BM25Okapi uses k1=1.5, b=0.75, epsilon=0.25; Unicode alphanumeric tokenization and case folding; no stemming or stopwords. Only positive-score passages are returned. Text is loaded from Chroma, not extraction artifacts.
- Hybrid uses equal-weight Reciprocal Rank Fusion over 20 candidates per method: sum of 1/(60+rank), one-based ranks, original chunk-ID deduplication and ID tie-breaking. Top ten are scored; the chatbot uses top five.
- Hit@1/5 checks any gold chunk; MRR@10 uses the first gold rank. Existing CompleteEvidence@5 checks every required evidence group.
- Multi-passage coverage@5 averages the fraction of required groups covered only for cases with at least two groups. Multi-passage complete@5 requires all groups on that same subset. One-group multi-fact questions do not count as multi-passage successes.
- Unanswerable questions have rankings and latency measurements but are excluded from retrieval-accuracy metrics. No answers or refusal scores were generated in this benchmark.

## Per-query regressions and improvements

| Question | Dense gold ranks | BM25 gold ranks | Hybrid gold ranks | Observation |
|---|---|---|---|---|
| h08, Ginani/Shandur | 2 | 1 | 1 | Keyword matching and fusion improve first-evidence rank. |
| h17, Hareen Bhaag versus Kho Nagar | 1, 2 | 3, 2 | 1, 2 | BM25 puts the closing correction summary first; both real evidence groups still reach top five. |
| h20, Gondogoro La versus Snow Lake | 1, 3 | 6, 3 | 4, 3 | BM25 loses complete top-five coverage. Fusion recovers both groups but demotes the first gold to rank 3. |
| h36, Izmis versus Sheitan Gawt | 6, 1 | >10, 2 | 9, 1 | All methods omit one required group from top five. Hit@5 alone hides this failure. |
| h40, Shah Jinali-Thui versus Zani | 2, 3 | 2, 4 | 2, 3 | Every method finds both groups; none places the first gold at rank 1. |

The general closing-summary chunk `p090-092-d469daea2cf5` mentions multiple corrected destination names. It outranks the actual supporting sections for BM25 on h17 and h36. This observation follows inspection of the saved rankings and summary text; it did not trigger stopword changes, reranking, or any other held-out tuning. Exact top-ten IDs, pages, gold groups, deltas, and misses are in the [held-out paired CSV](held_out/comparison.csv) and [generated failure report](held_out/summary.md).

## Latency and API use

Latency is one sequential warm-query-cache retriever invocation per question/method on the local Windows development environment. It includes query-cache file reads and retrieval/fusion, excludes initialization, query-vector preparation, baseline-parity queries, trace upload, and experiment feedback. There were no repeated timing trials, random-order runs, or cloud measurements. Negative cases are included in latency.

| Split | Method | Median ms | Mean ms | Initialization ms |
|---|---|---:|---:|---:|
| dev | dense | 28.854 | 29.708 | 590.152 |
| dev | bm25 | 0.745 | 0.771 | 31.069 |
| dev | hybrid | 31.287 | 31.327 | 615.563 |
| held_out | dense | 58.655 | 60.660 | 678.442 |
| held_out | bm25 | 0.839 | 0.872 | 35.411 |
| held_out | hybrid | 58.479 | 60.305 | 714.864 |

BM25 is much faster in this run. Dense versus hybrid timing differences are too small and noisy to interpret. Dense timings also differ between the dev and held-out processes, so compare methods within each split and do not infer an intrinsic twofold slowdown. Cold-cache Gemini request latency is excluded and can dominate actual chatbot response time.

Fifty previously uncached query vectors were generated once: 10 development and 40 held-out, then reused by dense, hybrid, warmups, and baseline checks. Preparation measured about 13.011 seconds for dev and 51.996 seconds for held-out, excluding deliberate one-second pacing after each new vector. No document embedding, answer generation, LLM judge, or repeated final benchmark was run. Exact HTTP retries, billed tokens, and costs were not measured.

## LangSmith experiments

| Split | Dense | BM25 | Hybrid |
|---|---|---|---|
| dev | [Dense](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/4ebe7bdf-7581-4fa5-bf0b-d266e2e326c5/compare?selectedSessions=e8c86f88-7688-42b0-8539-0d79c28c06c8) | [BM25](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/4ebe7bdf-7581-4fa5-bf0b-d266e2e326c5/compare?selectedSessions=5e5a7a8d-1df4-4b50-87a9-be1fb0ddbb2f) | [Hybrid](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/4ebe7bdf-7581-4fa5-bf0b-d266e2e326c5/compare?selectedSessions=de84f89c-f313-4340-a67c-0c0a61fd07f7) |
| held_out | [Dense](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/f3e1e871-fbdd-4fd2-bc38-93fb63b6a089/compare?selectedSessions=fef096b2-d7e8-49b2-b18f-e5787271fe9d) | [BM25](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/f3e1e871-fbdd-4fd2-bc38-93fb63b6a089/compare?selectedSessions=f54885cc-e890-4605-b6cd-b9cc26fcbdd8) | [Hybrid](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/datasets/f3e1e871-fbdd-4fd2-bc38-93fb63b6a089/compare?selectedSessions=c029b2ed-4f9b-4331-a30d-9286ac6b11cd) |

These private workspace links require LangSmith access. Experiments use `north-tours-v1-1-dev` and `north-tours-v1-1-heldout`, with exact approved references verified before execution. Root experiment outputs include actual rankings, source metadata and measured latency. Inner retriever tracing is disabled during timing to exclude upload overhead. Public-user tracing stays off.

Server read-back confirmed all 150 target outputs have the same ranked IDs and
page metadata as the local exports. LangSmith stores h20's reciprocal-rank
feedback as 0.3333 rather than full-precision 1/3. Its held-out BM25/hybrid MRR
averages are consequently about 0.00000104 below the local full-precision
values; the reported four-decimal results agree. LangSmith feedback-item counts
also include unscored examples, so use the eligible denominators stated above.
Configured secret values were absent from the checked trace payloads.

## Comparison with v1.0 and limitations

Dense top-ten IDs, text, and page metadata matched the preserved `rag.retrieve` implementation for all 50 queries. This is a valid paired ranking-parity check on the same index, queries, and embeddings. The index still contains 49 original vectors with its verified logical fingerprint; benchmark operations opened only a private index copy.

Historical v1.0 scores remain Hit@5 1.0000, MRR@10 0.9667, and CompleteEvidence@5 1.0000 on the original curated dataset. They were neither rerun nor overwritten. Comparing those scores numerically to the new dataset would confound different questions and denominators. The original implementation also uses Gemini Embedding 2, rather than an older or weaker embedding model.

The new benchmark is still too small to establish configuration superiority confidently: eight answerable dev cases, no multi-passage dev cases, 32 answerable held-out cases, 17 multi-passage cases, one PDF, and related facts from earlier work. One held-out question changes Hit@1 by 3.125 percentage points; one multi-passage case changes complete coverage by about 5.88 points. All methods saturate Hit@5. The tiny MRR difference between dense and hybrid is not evidence of statistical significance. No confidence intervals or significance tests were performed.

Dense remains the development-frozen default. BM25 is available as a fast offline lexical mode; hybrid is available for comparison, but showed no demonstrated aggregate accuracy gain here. No post-held-out tuning was performed. A new independent test set would be needed to evaluate future changes.

## Local use

```powershell
# Select dense, bm25, or hybrid in .env, then restart the app.
.\.venv-v1.1\Scripts\python.exe -m streamlit run app.py
```

The recorded run used these commands in order. Do not rerun the final held-out phase or delete its guard to tune against it.

```powershell
.\.venv-v1.1\Scripts\python.exe benchmark_retrieval.py dev --group hybrid-v11-20261017
.\.venv-v1.1\Scripts\python.exe benchmark_retrieval.py freeze --group hybrid-v11-20261017
.\.venv-v1.1\Scripts\python.exe benchmark_retrieval.py held_out --group hybrid-v11-20261017
```

Implementation files: `retrieval.py`, `workflow.py`, `benchmark_retrieval.py`, and `hybrid_report.py`. The app selects a retriever with `RETRIEVAL_MODE`; its UI and conversational-memory/citation workflow remain intact. No commit, push, or deployment was performed for this milestone.

References: [rank-bm25 implementation](https://github.com/dorianbrown/rank_bm25), [RRF paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf), and [LangSmith evaluation](https://docs.langchain.com/langsmith/evaluate-llm-application).
