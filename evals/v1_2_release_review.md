# v1.2 release review

Date: 2026-10-18. Functional reference: `0f144c2`. These are development
observations, not a new retrieval benchmark or current travel advice.

## Scope and acceptance

The shipping batch uses ordinary S1…Sn passage citations, independent paragraph
filtering, useful unscheduled options and a fixed alpha notice. Experimental
paragraph-reference schemas, title/quotation matching and investigation runners
are retained locally and excluded from the release. Major unsupported access,
route or duration claims remain unacceptable. Minor omissions, alternate names
and imperfect list coverage do not invalidate otherwise useful content.

The original 49-vector index, embedding prefix/dimensions, dense ranking,
planner queries, historical datasets/results, quotas and production tracing
opt-out are preserved. A copied index has the same logical fingerprint
`394c832e5e8bee68fa9f85fca85d97421081139d29838e162be5fe30e2c21dc6`.
Original dirty index files remained unchanged and are excluded from staging.

## Offline checks

Commands, all with real API calls and uploads blocked or mocked:

```powershell
.venv-v1.1/Scripts/python.exe verify_conversation.py
.venv-v1.1/Scripts/python.exe verify_planner.py
.venv-v1.1/Scripts/python.exe verify_usage.py
.venv-v1.1/Scripts/python.exe verify_quota_windows.py
.venv-v1.1/Scripts/python.exe verify_simplification.py
```

- Seven conversation scenarios passed, including follow-ups, destination switch,
  reset, isolated sessions and reruns without duplicate messages/calls.
- Planner graph, repeated guidance, citation filtering, normal complete plans,
  optional jeep transfer, partial options, invalid day sequencing, quota and UI
  checks passed. Invalid independent options do not discard valid siblings.
- Malformed rewrites use the original question without retrying. Provider and
  timeout failures stop before retrieval or answer generation. Incomplete JSON
  is rejected and never displayed as a complete itinerary.
- Session, concurrency, actual-attempt budgets, friendly 429 handling and Pacific
  23/25-hour daily windows passed mocked checks. No quota policy changed.
- The original embedding adapter and graph checks passed against synthetic data
  and a disposable index copy. The full historical evaluation was not rerun.
- Six saved chat rankings retained all reviewed available facts after bounded
  evidence selection; d03 gained Bashkargol geography. Availability is not proof
  that a newly generated answer will use it correctly.
- Desktop and 390px local browser previews displayed chat, complete day cards,
  partial options, source controls, currency and wrapping alpha notices. These
  previews used explicitly synthetic fixtures, not real itinerary evaluations.
- The unchanged saved baseline payloads also passed the new mechanical parsing/
  rendering path. This does not relabel their historical factual errors as correct.

## Four real saved-evidence generations

Each case ran once with the existing Gemini 3.5 Flash Lite model. Retrieval
replayed saved actual rankings/passages; this is **not** an end-to-end retrieval
test. Planner cap remained 2,400 tokens. No retries or tuning-and-rerunning.

| Case | Actual result and source review | Remaining limitations |
|---|---|---|
| d01, lakes in Swat | Lake list with stored citations to pages 72–78. Jag Banda, Gabin Jaba and Chukail Banda were not classified as lakes. | Sarbanda was omitted, so this run does not establish explicit ambiguity handling. Some places and qualifications were omitted. |
| d07, Islamabad–Swat, six days, Motorbike, July, Trekking/Nature | Partial result, no committed schedule. Three independent options survived: Gabin Jaba/Daral, Kandol/Spin Khwar, Mastij. Pages 72–76 support the Lalkoo driving endpoint, subsequent trekking, 6–8h Daral option, 3–4h Kandol approach, another 2–3h for Spin Khwar and connector-guide advice. | Free-text limitations overstated why the entire schedule was unavailable. The final Python display layer drops all such uncited model explanations and uses app-owned notices. A Lahore bus alternative is irrelevant; fuel guidance is incomplete. |
| d09, Kalam–Utror, three days, Motorbike, July | Partial three-card outline. The jeep leg is explicitly named, Kandol's 3–4h trek and connector-guide advice are retained, and the motorbike preference is preserved. Separate alternatives/options remain available. | Return-day detail and explicit transfer acceptance/parking arrangements are weak. Season citations include another region and do not establish a specific Utror season. These are not current-access assurances. |
| d12, local Skardu, three days, Car, August | Partial outline with three day cards: city/fort/desert, Kachura lakes, Satpara/cuisine. Core facts match pages 37–39. Deosai is an unscheduled 4x4 option, not a sedan route. | An Islamabad flight alternative is irrelevant. The uncited explanation that three days preclude regional excursions is dropped by the final display layer. Full road suitability, distances to every stop and real-world feasibility are not established. |

The model's free-text limitations are retained in local raw results as observed
failures. They are used only as an incompleteness signal in production. Final
display validation was replayed offline against the same four responses, without
changing their generation prompts or making additional calls. No generic
semantic fact checker is claimed. Valid source IDs still require human review
of the claims and qualifications they accompany.

| Case | Finish | Input tokens | Output tokens |
|---|---|---:|---:|
| d01 | STOP | 3,149 | 352 |
| d07 | STOP | 7,662 | 1,746 |
| d09 | STOP | 7,568 | 1,194 |
| d12 | STOP | 6,263 | 1,161 |

SDK-boundary accounting: **4 generation attempts, 0 query embeddings, 0 document
embeddings, 0 uploads**. Exact raw outputs, selected passages, prompts and finish
metadata are preserved in ignored local artifacts. None of these outputs is an
independent held-out result. Historical v1.0/v1.1 scores are unchanged.

## Hosted gate and limitations

The separate rollout reserve is at most two generation attempts and four new
query embeddings. Actual hosted observations and accounting belong in the
[v1.2 release notes](https://github.com/awaisarif18/pakistan-north-travel-buddy/releases/tag/v1.2.0)
after the deployment gate. Provider attempts are not directly observable through
the browser; distinguish completed workflows from conservative attempt bounds.

A hosted cold restart, comprehensive mobile-device coverage, unseen-case quality
and itinerary feasibility are not established. The static guide may itself contain
errors or outdated information. No new accuracy or safety guarantee is claimed.
