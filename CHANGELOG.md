# Changelog

## v1.3.0 - Destination recommendation BETA

- Add intent-aware destination discovery, comparisons and preference refinement to Chat.
- Reuse bounded LangGraph memory, dense retrieval, reviewed non-exclusive profiles and original PDF citations.
- Separate recommendation information requests from final answers; deduplicate source quotations and preserve source-only fallbacks.
- Enable the owner-approved beta by default, with `ENABLE_RECOMMENDATIONS` retained as an explicit override.
- Add a visible beta caution and a frozen, curated development baseline for future model comparisons.
- Keep the models, 49-vector index, planner, historical benchmarks, quotas and production tracing settings unchanged.

The original recommendation gate was not met: 3/6 overall passes, 4/6 fully useful
and aligned, 2/2 factual controls passed. Known effort/access errors are accepted
beta limitations, not fixed defects. See [release notes](docs/RELEASE_v1.3.0.md).

## v1.2.0 - Answer quality and planner usability

Useful partial plans, more flexible citations, bounded evidence selection,
graceful failures and the interface-owned alpha notice.
[Published release](https://github.com/awaisarif18/pakistan-north-travel-buddy/releases/tag/v1.2.0).

## v1.1.0 - Conversational RAG and trip planning

LangChain/LangGraph, session memory, retrieval comparisons, development LangSmith,
Flash Lite generation, quota safeguards, feedback and personalized trip planning.
[Release notes](docs/RELEASE_v1.1.0.md).

## v1.0.0 - Initial RAG MVP

PDF extraction, prebuilt Chroma, source-cited chat, reviewed retrieval evaluation
and public Streamlit deployment. Historical scores remain unchanged.
