# v1.1.0 — Conversational RAG & AI Trip Planning

Conversational RAG and personalized trip planning, built on the original
49-vector document index. Published at the owner's explicit direction with
the remaining hosted verification limits recorded below.

Live application: https://pakistan-north-travel-ai.streamlit.app/

## What's New in v1.1.0

- LangChain interfaces for Gemini, prompts, structured answers, documents, and retrieval.
- LangGraph chat with session-scoped memory, four-exchange follow-up rewriting, validated source IDs, and PDF page citations.
- Gemini 3.5 Flash Lite for all text generation. Gemini Embedding 2 and the original 49-vector Chroma index are preserved.
- Dense, BM25, and hybrid RRF retrieval. Dense remains the default selected before held-out evaluation.
- Reviewed development/held-out datasets, deterministic retrieval metrics, local exports, and optional LangSmith development experiments/traces. Public-user tracing stays off.
- Shared API budgets, rolling session allowances, cooldown, concurrency protection, Pacific-day accounting, and friendly 429 handling.
- Configurable Google Forms feedback and early-tester consent links, without automatic prompt/history transfer.
- Personalized trip outlines with day cards, source evidence, preference validation, shared quotas, and explicit missing-information handling.
- Literal currency rendering in answers, source passages, and itineraries; prices no longer become accidental LaTeX.
- Motorbike motorway-access guard: a static source citation cannot establish current vehicle eligibility. Unverified motorway routing produces partial guidance without a committed day schedule.

## Recorded retrieval results

| Held-out method | Hit@1 | Hit@5 | MRR@10 | CompleteEvidence@5 | Median ms |
|---|---:|---:|---:|---:|---:|
| Dense | 0.9375 | 1.0000 | 0.9688 | 0.9677 | 58.655 |
| BM25 | 0.8750 | 1.0000 | 0.9323 | 0.9355 | 0.839 |
| Hybrid | 0.9375 | 1.0000 | 0.9635 | 0.9677 | 58.479 |

Scores use 32 answerable held-out questions and 31 eligible complete-evidence
cases. Development results tied; the frozen tie-break selected dense. All
methods missed a required top-five evidence group for h36; BM25 also missed
complete coverage for h20. Small curated samples and single cached latency
measurements do not establish statistical superiority.

Historical v1.0 results remain unchanged: Hit@5 1.0000, MRR@10 0.9667, and
CompleteEvidence@5 1.0000 on the original dataset. Different datasets are not a
valid before/after accuracy comparison.

## Verification and limits

The seven conversation scenarios, usage safeguards, and planner integration
checks pass with mocked Gemini calls. Real planner reviews retained failed
drafts, corrected compressed trekking/vehicle assumptions, and produced useful
partial outlines plus a refusal to fill an unrealistic trip. Local-car transport
guidance now explicitly states the limits of current road/access evidence.
Automatic checks do not certify real-world itinerary feasibility. A clean Linux
Python 3.12.3 runtime loaded all 49 vectors and rendered chat/planner screens
without the original PDF, `.env`, or development files, using placeholder
Streamlit Secrets and zero Gemini calls. This is not a hosted restart test.

Session defaults are 3 chats and 1 plan per rolling hour, a 12-second cooldown,
700-character chat input, and 2 concurrent workflows. Shared generation budgets
are 10/minute and 300/Pacific day; embedding budgets are separate at 30/minute
and 300/Pacific day. Process restarts, multiple replicas, and new browser sessions
limit enforcement. No authentication or durable quota store is included.

The form owner intentionally requires Name. General feedback does not require
email, and future invitations require explicit consent. Owner verification of
Google Forms collection/sign-in and consent routing remains necessary.

## Deployment notes and roadmap

Keep Python 3.12, `app.py`, the existing theme, and the complete bundled Chroma
snapshot. Set `GEMINI_API_KEY` through Streamlit Secrets; keep
`GEMINI_CHAT_MODEL="gemini-3.5-flash-lite"`,
`GEMINI_EMBEDDING_MODEL="gemini-embedding-2"`, and `LANGSMITH_TRACING="false"`.
The PDF and ingestion artifacts are not runtime dependencies.

Prices and travel conditions may be outdated. Future work should broaden
independent evaluations, strengthen itinerary feasibility checks, and add
durable account quotas only when needed. Live bookings/weather, authentication,
neural reranking, and email automation are not implemented.

The approved feature commit was merged into `main` and the existing Streamlit
application updated. The owner confirmed that the Chat and Plan a Trip interface
loads correctly. Owner screenshots also confirm supported chat, follow-up
continuity, unsupported-weather refusal, and a partial planner result. They
exposed currency rendering and an unverified motorbike motorway route; focused
corrections pass mocked checks and await hosted retesting. Quotas, links, and
responsive layout still need owner-assisted verification. These checks are not
claimed as passed; the owner explicitly requested publication at this stage.
The audit's browser remained on a loading screen. The original `v1.0.0` tag and
evaluation artifacts are preserved. No rollback was performed.
