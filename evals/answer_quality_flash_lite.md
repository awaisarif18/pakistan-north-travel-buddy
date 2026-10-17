# Flash Lite answer-quality smoke review

Date: 2026-10-17. Branch: `feature/v1.1-langgraph`. Model: `gemini-3.5-flash-lite`.

Three real generation calls used the existing LangGraph prompt, native structured responses, and Python citation validation. The audited top-five passage IDs from the prior Gemini 3.8 review were replayed from a temporary copy of the 49-vector Chroma collection. No retrieval benchmark, new query embedding, document embedding, or LangSmith upload was run. The original index was not opened or modified by this smoke check.

The coding assistant checked the responses against original physical PDF pages and stored metadata. No additional LLM judge was used. Existing 3.8 outputs were reused for comparison; no 3.8 calls were made.

| Check | Actual result |
|---|---|
| Supported factual answers | 2/2 passed |
| Requested-fact completeness | 2/2 passed |
| Citation support | 2/2 passed |
| Unsupported refusal | 1/1 passed, no citations |
| Flash Lite generation attempts | 3 |
| Embedding attempts | 0 |
| Original Chroma vectors | 49, unchanged |

This small smoke sample does not establish equivalent model quality across all questions or replace the historical 10-case answer review. No substantive regression was observed on these three cases.

## Recorded responses

### q01: Where should I refuel before traveling to Khunjerab Pass?

> Before traveling to Khunjerab Pass, you should fill up completely in Sost, which is the last Pakistani town before the border and has reliable fuel. The stretch from Sost to Khunjerab Pass has no fuel whatsoever, making complete fill-ups in Sost essential for the round-trip run. [PDF pages 6-8]

Review status: `reviewed_pass`. The core fuel advice and its page 6-8 citation match physical PDF page 7. Flash Lite omits the optional 75-90 km distance and earlier Karimabad/Aliabad advice included by 3.8. The requested refueling answer remains complete.

Cited chunks: `p006-008-4850ae1f4334`.

Original physical PDF pages checked: 7.

Recorded Gemini 3.8 comparison:

> Before traveling to Khunjerab Pass, you should fill up completely in Sost, as it is the last Pakistani town before the border with reliable fuel and your final opportunity to refuel. The 75- to 90-kilometer one-way stretch from Sost to Khunjerab Pass has no fuel available at all. Earlier along the route, it is also recommended to fill up in Karimabad or Aliabad before heading up-valley toward Sost and Khunjerab, as Passu has limited options. [PDF pages 6-8]

### q17: How can I reach Skardu from Islamabad by public bus, and when does Deosai close to vehicles?

> You can reach Skardu from Islamabad or Rawalpindi via NATCO, which runs direct public buses to Skardu with daily departures around 2:00 PM. Fares range from approximately PKR 4,630 to 5,500 depending on the bus class, and the trip takes about 12 to 14 hours. [PDF pages 37-39; PDF pages 10-14]
>
> Deosai National Park closes to vehicles roughly from November to May due to snow. [PDF pages 39-40]

Review status: `reviewed_pass`. All requested facts are supported: direct NATCO service, daily roughly 2 pm departure, PKR 4,630-5,500 by class, 12-14 hours, and November-May Deosai vehicle closure. Same substantive coverage and source chunks as the recorded 3.8 answer.

Cited chunks: `p037-039-63413879f3c2`, `p010-014-0aced0690245`, `p039-040-154eaa1a99b3`.

Original physical PDF pages checked: 11, 38, 40.

Recorded Gemini 3.8 comparison:

> To travel from Islamabad to Skardu by public bus, NATCO operates direct services departing daily around 2:00 pm. Estimated fares range from PKR 4,630 to 5,500 depending on the bus class, and the journey takes approximately 12 to 14 hours. [PDF pages 37-39; PDF pages 10-14]
>
> Deosai National Park closes to vehicles due to snow roughly from November to May. [PDF pages 39-40]

### q21: What will the weather in Hunza be tomorrow?

> I couldn't find that information in the PDF.

Review status: `reviewed_pass`. Correct refusal of tomorrow's live weather; same fixed refusal as 3.8, with no fabricated citations.

Cited chunks: none.

Recorded Gemini 3.8 comparison:

> I couldn't find that information in the PDF.

## Differences and limitations

Flash Lite gave a shorter q01 answer, omitting optional route distance and earlier fuel-stop guidance. It retained the necessary Sost/round-trip/no-fuel advice. The multi-fact answer preserved the same requested facts and citations. The unsupported-weather refusal was identical. The unchanged interface still shows the warning about outdated prices, schedules, and travel conditions.

No latency or cost comparison was measured, and there were no repeat samples. Ambiguous rewriting was covered by mocked regression checks and the preceding one-call Flash Lite rewrite test, not a new real multi-turn benchmark. No production model switch, push, or deployment occurred.
