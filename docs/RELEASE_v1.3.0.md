# v1.3.0 - Intent-aware destination recommendations BETA

Live application: https://pakistan-north-travel-ai.streamlit.app/

This is an owner-approved BETA release of destination recommendation expansion.
The original development acceptance target was not met. Publication records that
product decision and the observed limitations; it does not turn failures into passes.

## Capabilities

- PDF-grounded factual answers with metadata-derived page citations.
- Intent-aware destination discovery, conditional recommendations and comparisons.
- Session-specific conversation memory, preference retention and refinement.
- At most two targeted searches and one final comparison, using the existing dense index and reviewed non-exclusive profiles.
- Original passage evidence, scope annotations and unknowns kept distinct from inferred suitability.
- Recommendation requests discard provisional drafts. Failed expansion retains inspectable source passages without raw JSON or automatic retries.
- Existing itinerary planner, quota/provider protections, feedback and privacy behavior.

## Final frozen development results

| Case | Overall |
|---|---|
| r01 honeymoon | PASS |
| r02 wife follow-up | PARTIAL |
| r04 peaceful family holiday | PASS |
| r05 parents/minimal walking | PARTIAL |
| r10 Hunza vs Skardu | PASS |
| r11 very-little-walking follow-up | FAIL |
| r13 Rakaposhi season | PASS |
| r15 Khunjerab refuelling | PASS |

Recommendation quality: **3/6 full passes**. Fully useful and preference-aligned:
**4/6**, below the required five. Factual controls: **2/2 passed**. No unnecessary
complete refusals. This is one curated development cohort, not an independent
held-out benchmark or proof of general travel suitability.

Actual usage: 11 generation attempts and four new query embeddings, all successful;
eight cache hits, zero retries, document embeddings or trace uploads. All model
completions had STOP metadata. Minimum provider spacing was 60.301 seconds;
summed provider latency was 74.610 seconds, excluding pauses.

The [curated evaluation baseline](../evals/v1_3_development_baseline.json) preserves
exact questions, final answers, routing, selected sources, prompt snapshots,
runtime fingerprints, configuration and usage. Private raw traces stay local.

## Known limitations

- Travel-effort preferences can be violated. r11 offered Buskochi for very little
  walking while omitting its documented 3–4-hour round trip; r05 stated that
  duration but still recommended it for minimal walking. Source: PDF pages
  33–35, `p033-035-97d114c1c3a8`.
- r11 dropped the active Skardu comparison after omitting the new walking
  preference from structured preferences, despite receiving conversation history.
- r02 reused overbroad altitude reassurance from pages 87–88,
  `p087-088-8428f4e31885`. General guide wording does not certify individual tolerance.
- Valid source IDs do not prove every inference. Walking distances, accessibility,
  facilities, current roads and accommodation/transport availability need confirmation.
- Topic-switch classification and preference extraction remain model-dependent.
- Qualified advice from documented terrain or required 4x4 transport is reasonable;
  a jeep journey alone does not prove rough roads, and a driver does not prove little walking.

The interface identifies recommendations as BETA and preserves the existing alpha
caution. There are no live weather, booking or road-condition integrations.

## Configuration and verification boundaries

Models remain `gemini-3.5-flash-lite` and `gemini-embedding-2` with 3,072-dimensional
embeddings. Dense remains default. The original 49 vectors, historical evaluations,
planner, source contract and usage budgets are unchanged. No new API key is needed.

`ENABLE_RECOMMENDATIONS=true` is the release default. In Streamlit Cloud Secrets:

```toml
ENABLE_RECOMMENDATIONS = "true"
```

An explicit false overrides the default. Restart/clear cached resources after
changing it. Keep production LangSmith tracing disabled.

Release verification passed 60 existing non-graphical recommendation checks,
five portable contract/configuration tests, seven conversation scenarios and
existing quota/concurrency, citation, planner and text-rendering checks. The
portable suite passed on Windows Python 3.13 and an isolated Python 3.12.14
environment; the exact pinned requirements resolved and pip check passed.
Three AppTest-based local tests were deliberately excluded. No new Gemini
evaluation, embedding call, trace upload or graphical test was performed. GitHub publication does not independently verify Streamlit's deployed
commit, Cloud override or UI. The owner performs hosted visual testing.

## Rollback and future work

Previous production main: `97dea039d254c3be07073983501f2c8390f5c85f`.
Previous release: [v1.2.0](https://github.com/awaisarif18/pakistan-north-travel-buddy/releases/tag/v1.2.0).
Use a normal revert commit for code rollback; do not reset history or move tags.
The flag can explicitly disable expansion without changing models or data.

Future model comparisons should reuse this frozen development baseline, record
new model/configuration and actual calls, and review claim support separately
from citation validity. Preserve historical results and reserve independent cases.
