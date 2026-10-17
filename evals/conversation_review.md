# v1.1 conversation-memory review

The seven controlled scenarios passed with deterministic model/retrieval
fixtures. These checks exercise the actual graph and Streamlit app, but do not
measure Gemini's semantic accuracy. A separate live Gemini dialogue completed
five answers before a rate-limit error interrupted the next rewrite. No
held-out benchmark or historical retrieval evaluation was run.

## Controlled results

| Scenario | Result | Observed behavior |
|---|---|---|
| Follow-up destination resolution | Pass | After Rakaposhi Base Camp, the season query resolves to Rakaposhi. |
| Accommodation follow-up | Pass | Nearby accommodation retains Rakaposhi as the destination. |
| Cost follow-up | Pass | Cost remains attached to the Rakaposhi conversation. |
| Switching destinations | Pass | An explicit Skardu question is unchanged; the next season follow-up resolves to Skardu. |
| Clear conversation | Pass | A new saver and thread have no previous turns. A contextless follow-up stays unresolved rather than inheriting the old destination. |
| Unrelated standalone question | Pass | The Khunjerab refueling question is passed through byte-for-byte, including surrounding whitespace, without a rewrite call. |
| Two-session separation | Pass | Two threads retain separate histories; two Streamlit sessions also own different graphs, savers, and IDs. |

The Streamlit AppTest additionally confirmed the original follow-up text stays
visible, a plain rerun makes no additional retrieval/model call and appends no
turn, and New conversation replaces the saver/thread and empties the view.
The maximum observed rewrite context was four completed exchanges.

Original citation-validation checks passed. Invalid or missing source IDs and
empty supported paragraphs still raise errors; a failed citation check commits
no completed turn, and recovery appends exactly one turn. Unsupported fixture
requests receive the original fixed refusal. Answer-generation inputs contain
only the resolved question and PDF excerpts, with no conversation history.
With ambient `LANGSMITH_TRACING=true`, the frontend's explicit `trace=False`
still disabled tracing inside retrieval and generation, with no trace upload.

Run these checks locally without Gemini or Chroma access:

```powershell
.\.venv-v1.1\Scripts\python.exe verify_conversation.py
# Optional synthetic development trace upload:
.\.venv-v1.1\Scripts\python.exe verify_conversation.py --trace
```

## Live Gemini spot check

The real configured `gemini-3.8-flash` model and existing embedding adapter were
used with a copied 49-vector index and copied query cache. Outputs were saved
after each successful turn under ignored `data/conversation-checks/live.json`.
The five answers below were manually compared with their cited source chunks;
all five passed that recorded source-support review. This is a small spot
check, not a new benchmark score or a guarantee of universal factual accuracy.

| Turn | Original question | Actual retrieval query | Observed answer and citations |
|---|---|---|---|
| 1 | Tell me about Rakaposhi Base Camp. | Unchanged | Minapin/Hapakun/Tagaphari route, elevation, duration, season, costs, and optional Diran extension. PDF pages 20-22 and 30-32. |
| 2 | What's the best season? | What is the best season to trek to Rakaposhi Base Camp? | June through September. PDF pages 20-22. |
| 3 | What about accommodation nearby? | What accommodation options are available near Rakaposhi Base Camp? | Campsites, tent/sleeping bag/meals around PKR 4,200/day, gear rental around PKR 3,000/night. PDF pages 20-22. |
| 4 | How much would that cost? | How much does accommodation or camping cost along the Rakaposhi Base Camp trek? | The same camp/gear estimates and organized packages around US$1,000+. PDF pages 20-22. |
| 5 | Tell me about Skardu. | Unchanged | Skardu landmarks, transport, accommodation, food, and surrounding valleys/treks. PDF pages 37-39, 39-40, 40-42, and 42-44. |

Relevant source IDs include `p020-022-8d8b2710273b`,
`p030-032-e38247495869`, `p037-039-63413879f3c2`,
`p039-040-154eaa1a99b3`, `p040-042-e594be504c6e`, and
`p042-044-232729beb314`. Every returned citation ID belonged to that turn's
retrieved evidence, and displayed pages matched its stored metadata.

Turn 6, another "What's the best season?" after Skardu, stopped with
`GoogleRateLimitError` during rewriting. The live post-switch follow-up,
unrelated standalone turn, second-session turn, live refusal, and live reset
steps were therefore not completed. Their controlled/AppTest checks passed;
they must not be described as live Gemini passes. No further live retry was
started after the error.

The live trace recorded nine model spans: eight successful calls, comprising
five answers and three rewrites, and one failed rewrite span. SDK HTTP retries
may add attempts; their exact count, token billing, and costs were not measured.
Five new query vectors were cached only in the isolated test copy. There were
zero document-embedding calls. The copied index fingerprint remained the
verified 49-vector fingerprint:

`394c832e5e8bee68fa9f85fca85d97421081139d29838e162be5fe30e2c21dc6`

## Development traces

- [Seven controlled scenarios](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14a76-d3d4-76b3-91d0-011da7c04acc/run/01a14a76-d3d4-76b3-91d0-011da7c04acc).
- [Partial live dialogue and rate-limit failure](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/r/01a14a77-b972-7a30-852a-dd5b2b60dcc8).

These are private workspace links requiring LangSmith access. Traces contain
controlled development inputs only. The live trace inputs, outputs, metadata,
and errors were checked for configured credential values; none were found.
Public-chat tracing remains explicitly disabled.

## Limitations and preservation

- Memory is session/process-local. Reloads that lose the Streamlit session, restarts, and New conversation discard it. There is no user database.
- Rewriting sees four recent exchanges and truncated answer text. Older context can be lost; heuristic detection can miss unusual follow-ups or route a clear question through the rewriter, which is instructed to leave it unchanged.
- Rewriting can add one Gemini call and a new cached query embedding. Model rate limits can interrupt a turn; failed turns are absent from completed chat history.
- The full visible conversation and checkpoint snapshots remain in RAM until reset/session disposal. This is suitable for short portfolio-demo chats, not unlimited histories.
- Controlled tests do not establish broad semantic accuracy. Live post-switch follow-up/refusal checks remain limited by the observed rate limit.

The original index files, document embeddings, production query cache, v1.0
results, and approved v1.1 evaluation labels retained their pre-change hashes.
The stylesheet, theme, models, dependencies, ingestion, retrieval adapter, and
historical evaluation logic were preserved. No push or deployment occurred.
