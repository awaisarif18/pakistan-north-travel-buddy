# Pakistan North Tours AI

A document-grounded AI travel assistant built using Retrieval-Augmented Generation (RAG), Gemini, ChromaDB, and Streamlit.

The application retrieves information from a 92-page Northern Pakistan travel guide and generates answers with supporting PDF citations.

**v1.1 development branch:** `feature/v1.1-langgraph` migrates the local chatbot
to LangChain and LangGraph, with session-scoped conversational memory. The live demo, `main`, and tag `v1.0.0`
remain on the stable v1.0 implementation. This migration has not been deployed.

## Live demo and source code

**[Open the live demo](https://pakistan-north-travel-ai.streamlit.app/)** · **[View the source on GitHub](https://github.com/awaisarif18/pakistan-north-travel-buddy)**

## Technology badges

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-API-4285F4)
![Streamlit](https://img.shields.io/badge/Streamlit-Community_Cloud-FF4B4B?logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Persistent_index-58644B)
![RAG](https://img.shields.io/badge/RAG-Evaluated-2C6653)

## Application screenshot

![Pakistan North Tours AI — Application Screenshot](assets/demo.png)

## Features

- Processes the 92-page guide with PyMuPDF into 49 text chunks with physical PDF page metadata.
- Uses Gemini Embedding 2 at 3,072 dimensions and persistent ChromaDB cosine search to retrieve the top five passages.
- Generates concise answers with Gemini 3.8 Flash. Python validates selected source identifiers and attaches page citations from stored metadata.
- Exposes retrieved passages in expandable source cards and refuses questions unsupported by the supplied evidence.
- Provides a responsive Streamlit chat interface with six example prompts, conversation display, and a reset option.
- Caches query embeddings to avoid repeat embedding calls for identical questions and configuration.
- Includes a reviewed 25-question retrieval dataset, three retrieval metrics, and a separate recorded answer-quality review.
- Runs publicly on Streamlit Community Cloud using a bundled prebuilt index, without ingestion at startup.

Ask about routes, trekking seasons, transport, fuel stops, costs, and facilities.
For example: "Where should I refuel before traveling to Khunjerab Pass?"
The live v1.0 demo requires explicit destinations in each question. On this
v1.1 branch, follow-ups can resolve the current destination from the last four
exchanges. Answers still use retrieved PDF evidence rather than conversation
history as a source.

## RAG architecture

```mermaid
flowchart LR
    P[92-page PDF] --> X[PyMuPDF extraction and chunking]
    X --> E[Gemini document embeddings, once]
    E --> C[(Persistent ChromaDB: 49 vectors)]
    Q[User question] --> PQ[Prepare question]
    PQ --> F{Ambiguous follow-up?}
    F -->|No| QE[Verified cached Gemini query embedding adapter]
    F -->|Yes| W[Rewrite using four recent exchanges]
    H[Session-owned in-memory graph state] --> W
    W --> QE
    QE --> C
    C --> R[Top five passages]
    R --> G[LangChain prompt and structured Gemini answer]
    G --> V[Validate source IDs and add PDF citations]
    V --> UI[Streamlit answer and source evidence]
    V --> H
```

Chunks contain approximately 400-697 estimated tokens, with paragraph overlap
where practical. `rag.py` checks the indexed embedding model, dimensions, and
retrieval-format version before use. Documents and questions share
`gemini-embedding-2` and 3,072 dimensions, with document/query-specific prefixes.

The model selects source IDs rather than inventing page numbers. The application
validates those IDs and appends page ranges from the retrieved metadata. This
checks citation references, not the truth of every generated statement.

`workflow.py` compiles typed state into this LangGraph workflow:
`START → prepare_question → optional rewrite_question → retrieve_evidence → generate_grounded_answer → validate_citations → END`.
Retrieval uses LangChain `Document` objects and a similarity retriever over the
existing Chroma collection. The embedding adapter delegates to v1.0's exact
query-prefix, dimension, cache-key, and cache-write implementation in `rag.py`.
It blocks document embedding. The original `rag.py`, ingestion, and evaluator
remain intact as the migration reference. There are no agents, tools, or loops.
Each Streamlit session owns an `InMemorySaver`, graph, and random thread ID.
Completed graph turns are the sole chat-history source. Reruns read state;
they do not replay prior questions. New conversation replaces the graph and
thread, and server/session loss clears memory. Only stateless clients are cached
across sessions. The original question stays visible, while retrieval and
generation use the resolved standalone query. Generation receives no history.

Run the small controlled memory checks, with no Gemini calls:

```powershell
.\.venv-v1.1\Scripts\python.exe verify_conversation.py
# Optional: upload synthetic development traces, never public-user conversations.
.\.venv-v1.1\Scripts\python.exe verify_conversation.py --trace
```

See the [conversation review](evals/conversation_review.md) for seven scenario
results, live Gemini spot checks, citation checks, and limitations. This does
not run the approved held-out benchmark or change historical retrieval scores.

## Technology stack

| Component | Technology |
|---|---|
| Runtime | Python 3.12 deployment configuration |
| PDF extraction | PyMuPDF 1.28.2 |
| Embeddings | `gemini-embedding-2`, 3,072 dimensions |
| Vector storage | ChromaDB 1.5.9, persistent cosine index |
| Answer generation | `gemini-3.8-flash` |
| Gemini client | Official `google-genai` SDK 2.20.0 on this branch; v1.0 retains 1.75.0 |
| LangChain interfaces | langchain-core 1.6.12 |
| Gemini integration | langchain-google-genai 4.4.2 |
| Chroma integration | langchain-chroma 1.1.0 |
| Workflow | langgraph 1.2.16 |
| Transitive tracing dependency | langsmith 0.14.11; optional tracing through environment settings |
| Interface | Streamlit 1.66.0, custom CSS, native chat components |
| Local configuration | python-dotenv 1.2.4 |
| Hosting | GitHub and Streamlit Community Cloud |

The development branch uses LangChain Core and provider integrations directly.
The top-level `langchain` agent package is unnecessary for this workflow and is
not installed. The Gemini integration requires the SDK upgrade; the separate
local v1.1 virtual environment preserves the working v1.0 environment.

Optional LangSmith tracing reads `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, and
`LANGSMITH_PROJECT` from your private environment. The template defaults to
`LANGSMITH_TRACING=false`; development commands require an explicit `--trace`
or `--langsmith` flag to upload traces/results. Streamlit calls the workflow
with tracing forced off, even if the environment flag is true. Keep real
tracing keys private, like the Gemini key. No tracing configuration was
deployed to the live v1.0 app.

## Evaluation methodology and results

The following audited v1.0 results and original evaluation files are preserved.
Migration parity is recorded separately below; these scores were not overwritten.

The curated dataset contains 10 direct factual questions, five paraphrased
questions, five multi-fact questions, and five unanswerable questions. Gold
chunk IDs and physical PDF pages were independently checked against the source
and approved before all 25 labels were marked `verified`. The reviewed labels
include alternative Deosai evidence for q04/q17 and required evidence groups
for q16-q20.

| Metric | Result |
|---|---|
| PDF pages | 92 |
| Document chunks | 49 |
| Evaluation questions | 25 |
| Verified answerable questions | 20 |
| Hit@5 | 1.0000 (20/20) |
| MRR@10 | 0.9667 |
| CompleteEvidence@5 | 1.0000 (5/5) |
| Retrieval errors | 0 |

The baseline evaluator retrieves the top ten chunks using semantic search and
cached query embeddings, independently of answer generation:

- **Hit@5:** fraction of verified answerable questions with at least one gold chunk in ranks 1-5.
- **MRR@10:** mean reciprocal rank of the first gold chunk in ranks 1-10; a miss contributes zero.
- **CompleteEvidence@5:** fraction of the five verified multi-fact questions with at least one top-five chunk from every `required_evidence_groups` group. IDs within a group are alternatives, every group is required, and a shared chunk may satisfy multiple groups where the reviewed labels allow it.

Only the 20 verified answerable questions enter Hit@5 and MRR@10. Complete
evidence coverage is measured separately because a single matching gold chunk
does not establish that all facts were retrieved. Aggregate scores require
successful retrieval for every eligible question; unverified labels are excluded.
The CSV preserves rank-ordered IDs, page ranges, distances, first-gold ranks,
and missing evidence groups.

There were no Hit@5 misses or incomplete multi-fact evidence groups. Nineteen
questions retrieved gold evidence at rank one. q07, about the hike from Ratti
Gali base camp, retrieved its gold chunk at rank three behind passages about
other treks. MRR@10 is therefore `(19 + 1/3) / 20 = 0.9667`.

### Separate answer-quality review

**5/5 supported answers passed** the recorded factual-consistency, completeness,
and citation-support review. **5/5 unanswerable questions were appropriately
refused** without fabricated citations. The ten-response review included a
multi-fact question, eight newly generated answers, and two reused saved outputs.
Evidence was compared directly with the PDF; no LLM judge or evaluation framework
was added.

These are actual observations on a small, curated dataset, not a held-out
benchmark or a guarantee of universal accuracy. Retrieval metrics do not measure
answer correctness. The earlier five retrieval smoke queries are not formal
evaluation scores, and refusal behavior has not been tested broadly or adversarially.

Review the evidence and methodology:

- [Verified questions and gold labels](evals/questions.json)
- [Per-question retrieval rankings and scores](evals/results.csv)
- [Evaluation summary and supporting excerpts](evals/summary.md)
- [Recorded answer-quality review](evals/answer_quality.md)
- [Full development process and technical report](docs/PROJECT_REPORT.md)

### v1.1 migration verification

All 25 verified questions matched the v1.0 top-ten ordering, chunk text, page
metadata, and cosine distances exactly. Maximum distance difference was `0.0`.
The 20 archived answerable-question rankings also matched, and top-five
retriever results matched each baseline prefix. The collection still contains
49 vectors. The deployed index files, original backend, labels, and evaluation
reports remain unchanged. See [per-question parity results](evals/v1_1_parity.csv).

Four fresh LangChain/LangGraph answer checks covered q01, q17, q21, and q25.
The two supported answers matched the PDF, including multi-fact evidence for
Skardu transport and Deosai closure; both unsupported questions refused without
citations. These selected checks do not replace the original ten-answer review.
Graph order, invalid citation rejection, cached embedding request formatting,
and Streamlit startup/submit/reset passed focused checks. No document embeddings
or real query embeddings were generated during verification.

### LangSmith tracing and the approved v1.1 datasets

The private LangSmith dataset `pakistan-north-v1-verified-25` contains the existing
25 verified references. [Its local JSONL export](evals/langsmith_baseline.jsonl)
retains labels, answers, gold IDs/pages, and excerpts. Importing it did not run
retrieval or recalculate the historical scores.

The [50-question reviewed benchmark](evals/questions_v1_1.json) has 40 answerable and
10 unanswerable questions. Review it in the [expandable gold-evidence sheet](evals/review_v1_1.md).
Development has 8 answerable + 2 unanswerable questions; held-out has 32 + 8.
All 50 labels are `verified` after independent review and explicit user approval.
The private LangSmith datasets `north-tours-v1-1-dev` and
`north-tours-v1-1-heldout` contain 10 and 40 examples respectively. Remote
inputs, reference outputs, metadata, and split membership match the approved
local dataset. Gold chunk IDs are disjoint between splits,
but all questions still use the same PDF and share topics with the old benchmark.
Neither import nor evaluation accepts unverified labels. No harder-set scores
or answer-quality scores have been generated.

The benchmark is intentionally multi-fact-heavy: 38/40 answerable questions are
`multi_fact`. Of those, 21 have one required evidence group and 17 have two.
Keep aggregate CompleteEvidence@5, but also plan a separate multi-passage
result restricted to questions requiring at least two distinct evidence groups.
One-chunk multi-fact coverage does not demonstrate multi-passage retrieval.
These subgroup results are planned, not measured; the v1.0 scores above remain unchanged.
All 17 two-group cases are held-out after the requested split rebalance. The
development multi-passage subgroup is empty and should be reported as unavailable.

Development commands use the existing `.env` without printing credentials:

```powershell
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py prepare
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py upload --dataset baseline
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py upload --dataset harder --split dev
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py upload --dataset harder --split held_out
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py ask --trace --question "What does the guide say about Patundas access?"
```

`prepare` is local-only. Upload is idempotent and refuses mismatched remote
references instead of overwriting them. `ask --trace` explicitly sends that
development question, retrieved passages, and generated answer to the configured
LangSmith project; it is not used by the public chat interface. Missing tracing
credentials cause a clear configuration error.

For a separately authorized future run, these commands evaluate the development
split locally or create a LangSmith experiment with the same local exports.
Synchronization did not run either benchmark:

```powershell
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py evaluate --dataset harder --split dev --allow-query-embeddings
.\.venv-v1.1\Scripts\python.exe langsmith_eval.py evaluate --dataset harder --split dev --langsmith --allow-query-embeddings
```

`--split held_out` explicitly selects the held-out cases. Keep them out of
tuning until development decisions are frozen. `--answers` additionally opts
into one generation request per question, including negative cases. Without
it, negatives are unscored and do not trigger retrieval. Cached query vectors
are reused; `--allow-query-embeddings` explicitly allows missing query vectors,
never document re-embedding. No LLM judge is implemented or automatically run.

Code-based evaluators report Hit@1, Hit@5, MRR@10 and CompleteEvidence@5 for
eligible verified positives. CompleteEvidence@5 uses reviewed evidence groups;
unanswerable cases are excluded. Any run error withholds aggregate scores.
Answer mode adds structural citation validity and strict fixed-refusal checks.
Answer correctness and groundedness remain unscored until manual PDF review;
valid citation syntax alone is not evidence of semantic support.

In [LangSmith](https://smith.langchain.com/), open **Tracing** and select your
`LANGSMITH_PROJECT` to inspect node, retriever, and model spans. A synthetic trace
named `synthetic-dev-trace-no-gemini` was verified with a mocked Gemini response.
For future experiments, open **Datasets & Experiments**, choose the dataset and
experiment, and inspect per-example scores, actual outputs, references, and traces.
Experiment prefixes default to `v11-<dataset>-<split>-dense-k10-<UTC timestamp>` and record
commit/model/source metadata. CSV and Markdown exports go to
`evals/experiments/<experiment-name>/`; they never overwrite the original files.
LangSmith may append a unique suffix to the experiment prefix; local exports use the prefix.
Manual correctness/groundedness fields and reviewer notes are left blank for review.
See Stage 9 of the [project report](docs/PROJECT_REPORT.md) for formulas, API usage,
privacy checks, and limitations.

## Local installation and usage

For this existing workspace, run v1.1 in its separate environment:

```powershell
git switch feature/v1.1-langgraph
python -m venv .venv-v1.1
.\.venv-v1.1\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-v1.1\Scripts\python.exe verify_migration.py
.\.venv-v1.1\Scripts\python.exe -m streamlit run app.py
```

Keep an existing `.venv-v1.1` rather than recreating it. This local environment
is excluded through `.git/info/exclude`. `verify_migration.py` requires the
existing local `data/query_embeddings.json` cache for all 25 questions and fails
before making embedding requests if any entry is missing. It tests a copied
index, never the deployed snapshot. Optional `--live` generates at most four
answers and reuses saved migration outputs when code/model/question match;
it makes no new calls on a matching rerun. Manual answer review is still needed.

General setup for a fresh checkout follows. The live `main` branch still has
v1.0's requirements; install the requirements from whichever branch you run.

The complete index is included in the repository. The source PDF and extraction
files are not needed to run the chatbot. Python 3.12 matches the deployment
configuration; development also used Python 3.13.7 on Windows.

```bash
git clone https://github.com/awaisarif18/pakistan-north-travel-buddy.git
cd pakistan-north-travel-buddy
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the pinned dependencies and copy `.env.example` to `.env` if it does
not already exist. Keep existing environment files and credentials when continuing
local work.

```bash
python -m pip install -r requirements.txt
```

Configure `.env` privately:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_CHAT_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
```

Launch the chatbot:

```bash
python -m streamlit run app.py
```

Open the printed local URL, normally `http://localhost:8501`. Use an example
prompt, inspect the source evidence, or reset the conversation. The app warns
that prices, schedules, and travel conditions in the guide may have changed.

### Optional ingestion and evaluation commands

Use the existing index for normal operation. To reproduce extraction locally,
provide an authorized `pakistan-north-tours-final.pdf` in the project root:

```bash
python ingest.py
python ingest.py --embed
```

The first command writes `data/pages.json` and `data/chunks.json` without API
calls. The second reads those chunks, persists vectors, and skips IDs already
stored with matching text and metadata. Do not regenerate the document vectors
for an ordinary checkout or app restart. Changing the embedding configuration
requires a separately reviewed rebuild.

```bash
python rag.py
python evaluate.py
```

`rag.py` runs the five retrieval smoke questions, prints top-three chunk IDs and
pages, and saves top-five passages to `data/retrieval_results.json`.
`evaluate.py` uses the verified labels and existing index, reuses available
query embeddings, and writes `evals/results.csv` and `evals/summary.md` without
generating answers. Missing cached query embeddings require Gemini API calls;
the cache is not published. The saved results can be reviewed without rerunning
either command. Neither command is part of app startup.

## Deployment architecture

```mermaid
flowchart LR
    GH[Public GitHub repository, main] --> SC[Streamlit Community Cloud, app.py]
    SC --> C[(Bundled local ChromaDB, 49 vectors)]
    SC --> G[Gemini API: query embeddings and answers]
    S[Private Streamlit Cloud Secrets] --> SC
```

The [live application](https://pakistan-north-travel-ai.streamlit.app/) runs on
Streamlit Community Cloud from this public repository's `main` branch, using
`app.py`, the pinned `requirements.txt`, and the Python 3.12 deployment
configuration. The existing theme and `ui.css` ship with the app.

The full `data/chroma/` snapshot contains five files totaling 3,229,860 bytes,
including SQLite and the UUID-named binary-index directory. It stores all 49
document vectors, extracted passages, and page metadata. Publication of this
source-containing index was explicitly approved. The wider `data/` ignore rule
remains; the original PDF, extraction JSON, query cache, `.env`, `.venv`, and
`.streamlit/secrets.toml` are excluded.

Configure the following root-level keys privately in Streamlit Cloud Secrets:

```toml
GEMINI_API_KEY = "your-private-key"
GEMINI_CHAT_MODEL = "gemini-3.8-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-2"
```

The app opens the repository-relative prebuilt index without ingestion or
document embedding at startup. It requires no original PDF, hosted database,
or connection to the development PC. Query caches and session history are
disposable; losing them does not remove the bundled document vectors.

Clean-copy startup and Linux Python 3.12 compatibility checks loaded all 49
vectors without the PDF or temporary extraction files. A hosted cold restart
has not been independently verified. Push intended application changes to
`main` for Streamlit to update the deployment; manage secrets through Cloud
settings and review any replacement index separately. See Streamlit's
[deployment settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
and [secrets documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Limitations

- The static guide may contain outdated or incorrect travel information. The app does not verify current prices, weather, schedules, availability, or road conditions, and does not book hotels or transport.
- Some chunks span destinations or page boundaries. Citations identify stored page ranges rather than exact sentences, and valid source IDs alone do not prove every claim is supported.
- Lower-ranked passages can be irrelevant. The small curated evaluation set includes earlier smoke questions and related facts, so its scores should not be generalized to all questions.
- The live v1.0 demo has display-only history. This v1.1 branch uses volatile conversational memory with four-exchange rewrite context; heuristic follow-up detection can miss unusual wording. Name the destination when resolution is unclear. Hybrid retrieval and reranking are not implemented.
- Query caching and session storage are designed for a demo, not concurrent production workloads. Gemini access and quota are required; Cloud restarts may clear caches and sessions.
- Some CSS uses Streamlit DOM hooks and should be checked when upgrading Streamlit. A hosted cold restart and broad adversarial refusal testing have not been independently verified.

## Future improvements

- Add unseen questions across more regions and expand the manual answer/refusal review.
- Investigate q07's lower-ranked evidence before considering changes to retrieval.
- Refine exact-page citations or chunk boundaries if new evaluation failures justify it.
- Expand conversation coverage before extending memory behavior. Consider hybrid search or reranking only when measured needs justify the added complexity.

The [project report](docs/PROJECT_REPORT.md) preserves the development stages,
recorded problems and solutions, evaluation methodology, and deployment evidence.
