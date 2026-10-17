# Trip planner development review

Review date: 2026-10-18, Asia/Karachi. Branch: `feature/v1.1-langgraph`.

Three controlled synthetic preference sets exercise Hunza by motorbike, local Skardu sightseeing by car, and an unrealistic one-day winter round trip. The coding assistant compared outputs with retrieved passages and original physical PDF text. No LLM judge, held-out benchmark, or public-user data was used. These are manual development observations, not a general itinerary accuracy score.

## Workflow and API usage

The planner uses benchmark-selected dense retrieval. Three deterministic queries each retrieve the top five; unique passages are interleaved and capped at 12. One Gemini 3.5 Flash Lite invocation generates structured output, then Python validates day numbers and source IDs and attaches physical PDF page ranges. Unsupported and partial plans are valid outcomes. Trip days include outward and return travel.

| Run | Generation attempts | Query embeddings | Observation |
|---|---:|---:|---|
| Initial, all three cases | 3 | 9 | Hunza over-refused; Skardu assumed a jeep excursion; unrealistic trip declined. |
| Revised prompt, same cases | 3 | 0 | Hunza supplied days but compressed a three-day trek; Skardu vehicle issue corrected. |
| Focused trek correction, Hunza only | 1 | 0 | Three trek days restored with separate outward/return travel. |
| Total | 7 | 9 | No document embedding or retrieval-benchmark calls. |

Both failed drafts were retained. The fixes changed planner instructions, not embeddings, queries or retrieval algorithms. The original 49-vector database was untouched; real checks opened a copied snapshot under ignored `data/planner-checks/`. Later checks reused all query embeddings. Generation invocations made one attempt, with no automated repair/retry loop.

## Final observations

| Case | Result | Generation seconds | Whole-workflow seconds |
|---|---|---:|---:|
| trip01 | reviewed_pass_with_limits | 4.753 | 6.230 |
| trip02 | reviewed_pass_with_limits | 3.274 | 4.071 |
| trip03 | reviewed_pass | 1.956 | 2.755 |

Latency measures a single LangChain generation invocation, including formatting and SDK overhead. Workflow latency also includes retrieval. Runs are not statistically comparable speed benchmarks. Skardu and the unrealistic-trip results predate the final trek-specific prompt addition and were not regenerated again.

## trip01: Gilgit to Hunza

5 total days; Motorbike; Budget; July; interests: Nature, Trekking.

Review: `reviewed_pass_with_limits`. The recheck now allocates two ascent days and one descent day to Rakaposhi, keeps outward/return riding separate, and includes source-supported guesthouse/camp, season and fuel guidance. It remains a partial suggested outline because exact local riding timings and total costs are not established. No current road-opening guarantee is made.

[Development trace](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b79-cb8b-7c42-9557-f417f1ab2a2e/run/01a14b79-cb8b-7c42-9557-f417f1ab2a2e?start_time=2026-10-17T20%3A07%3A15.595090%2B00%3A00)

Plan status: `partial`.

This partial trip plan starts in Gilgit and heads toward Hunza for a 5-day journey in July using a motorbike, focusing on nature and trekking within budget constraints. [PDF pages 20-22; PDF pages 18-20; PDF pages 1-3]

### Day 1: Arrival in Gilgit & Travel to Hunza

Ride from Gilgit northward along the Karakoram Highway toward Karimabad/Hunza, enjoying the scenic mountain views. [PDF pages 6-8; PDF pages 18-20]

Settle into a budget guesthouse in Karimabad or Aliabad, which typically offers simple rooms and breakfast. [PDF pages 20-22; PDF pages 18-20; PDF pages 8-10]

### Day 2: Minapin to Hapakun (Rakaposhi Trek Day 1)

Take a short ride from Hunza down to Minapin village, the starting point for the Rakaposhi Base Camp trek. [PDF pages 20-22]

Trek on the straightforward trail from Minapin to Hapakun campsite, taking in the surrounding nature. [PDF pages 20-22]

### Day 3: Hapakun to Tagaphari / Rakaposhi Base Camp (Trek Day 2)

Continue the trek from Hapakun upward to Tagaphari at Rakaposhi Base Camp, sitting around 4,150m altitude. [PDF pages 20-22]

Stay overnight at the camp utilizing local tent and meal support options. [PDF pages 20-22]

### Day 4: Descent to Minapin & Return to Hunza

Descend from Rakaposhi Base Camp back down to Minapin village following the recommended multi-day trekking pace. [PDF pages 20-22]

Return by motorbike back to Hunza to rest and sample local culinary specialties like Chapshoro. [PDF pages 6-8; PDF pages 20-22]

### Day 5: Hunza Exploration & Return to Gilgit

Spend time exploring local sights or securing fuel before making the return trip down the corridor back to Gilgit. [PDF pages 6-8; PDF pages 18-20]

### Transport

Travel is planned via motorbike on the Karakoram Highway, with local van or shared transport options also available between Gilgit and Karimabad. [PDF pages 18-20; PDF pages 1-3]

### Accommodation

Budget guesthouses in Hunza cost roughly PKR 1,500 to 3,500 per night for simple rooms, often including breakfast. [PDF pages 20-22]

Along the Rakaposhi trek route, local camps offer tent, sleeping bag, and meals for about $15 per day. [PDF pages 20-22]

### Budget

Currency conversion rates approximate PKR 278 to US$1, and budget guesthouses and basic camp options keep daily spending low. [PDF pages 20-22; PDF pages 1-3]

### Season

July falls squarely within the ideal June to September season for both traveling the KKH corridor and undertaking regional treks like Rakaposhi Base Camp. [PDF pages 20-22; PDF pages 26-28; PDF pages 18-20]

### Safety

Watch for early symptoms of altitude sickness such as headaches above 3,300m, and do not continue ascending if symptoms persist. [PDF pages 1-3]

Top off fuel at reliable hubs like Gilgit and Karimabad/Aliabad, as stretches farther north have limited options. [PDF pages 6-8]

### Missing information

- Exact hourly schedules and precise total trip expenses are omitted due to lack of itemized hour-by-hour source data.
- Only a partial itinerary is presented to strictly follow the guide's required 3-day duration for the Rakaposhi Base Camp trek within the 5-day overall limit.

Cited chunk IDs: `p018-020-73083763654d`, `p001-003-dc2f8ea7a907`, `p020-022-8d8b2710273b`, `p026-028-3af709bd9d8f`, `p006-008-4850ae1f4334`, `p008-010-a7bee3da530b`.

## trip02: Skardu to Skardu

3 total days; Car; Mid-range; August; interests: Sightseeing, Culture.

Review: `reviewed_pass_with_limits`. Relevant local sightseeing, supported fort/lake/hotel facts and valid sources; the 4x4-only Deosai day was removed. Some transport guidance unnecessarily discusses Islamabad despite departure in Skardu. Daily grouping remains a suggestion, not verified travel feasibility.

[Development trace](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b78-ee21-72c2-9b3e-6defc2e21ca9/run/01a14b78-ee21-72c2-9b3e-6defc2e21ca9?start_time=2026-10-17T20%3A06%3A18.913201%2B00%3A00)

Plan status: `partial`.

This 3-day mid-range itinerary focuses on sightseeing and cultural exploration in Skardu during August, utilizing a car for transport. [PDF pages 37-39]

### Day 1: Skardu Arrival & Cultural Sights

Arrive in Skardu and get settled. Explore Kharpocho Fort overlooking the Indus and Shigar rivers, and visit the Katpana Cold Desert. [PDF pages 37-39]

### Day 2: Lakes & Waterfalls near Skardu

Visit Upper and Lower Kachura Lakes, and Satpara Lake. Alternatively, explore Manthoka Waterfall along the Kargil-Skardu road. [PDF pages 37-39; PDF pages 42-44]

### Day 3: Shigar Valley Day Trip & Departure

Take a short drive to Shigar town to see the 17th-century Shigar Fort and the 14th-century Amburiq Mosque before concluding the trip in Skardu. [PDF pages 40-42]

### Transport

Reaching Skardu from Islamabad by air takes about 1 to 1 hour and 10 minutes, with flights prone to weather cancellations. Alternatively, the road distance of 630 to 700 km takes 12 to 14 hours via the Skardu Road (S-1), which is mostly paved and smooth. NATCO also runs direct buses taking 12 to 14 hours. [PDF pages 37-39]

### Accommodation

Mid-range hotels in Skardu generally run roughly PKR 14,000 to 30,800 per night, while budget guesthouses are available in the city center. [PDF pages 37-39]

### Budget

Mid-range accommodation ranges from PKR 14,000 to 30,800 per night. Carry enough cash as ATMs are limited beyond Skardu, and local expenses are cash transactions. [PDF pages 37-39; PDF pages 8-10]

### Season

August is during the summer season, which offers good conditions for sightseeing and exploring the region. [PDF pages 37-39; PDF pages 39-40]

### Safety

Mountain flights are subject to weather cancellations, so avoid tight schedules. Carry ID when traveling near checkpoints like Manthoka Waterfall. [PDF pages 37-39; PDF pages 42-44]

### Missing information

- Exact total costs cannot be calculated due to variable flight and food prices.
- Excursions requiring 4x4 vehicles such as Deosai National Park are noted as separate jeep requirements and are not included in the committed standard car itinerary.

Cited chunk IDs: `p037-039-63413879f3c2`, `p008-010-a7bee3da530b`, `p039-040-154eaa1a99b3`, `p042-044-232729beb314`, `p040-042-e594be504c6e`.

## trip03: Islamabad to Hunza

1 total days; Motorbike; Budget; January; interests: Nature.

Review: `reviewed_pass`. No day schedule was invented; the cited 14-20 hours of one-way riding and multi-day recommendation establish why the one-day round trip is unsupported.

[Development trace](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b78-fe09-75f2-b196-54192d1ca273/run/01a14b78-fe09-75f2-b196-54192d1ca273?start_time=2026-10-17T20%3A06%3A22.985342%2B00%3A00)

Plan status: `partial`.

An Islamabad to Hunza trip by motorbike in January is highly infeasible and unsupported by seasonal road conditions and travel time realities. [PDF pages 18-20]

### Season

The year-round route on the Karakoram Highway (Islamabad to Gilgit to Hunza) is the only option outside summer, but a one-day trip is impossible as actual road time is 14 to 20 hours. [PDF pages 18-20]

### Transport

Traveling by motorbike over a 600-650 km mountain corridor in January requires planning 2 to 3 days of riding, making a 1-day trip completely unrealistic. [PDF pages 18-20]

### Missing information

- A 1-day duration from Islamabad to Hunza is completely infeasible given the 14-20 hours of actual road time required.
- January travel falls outside the summer season for many regional activities, and winter conditions on the Karakoram Highway demand a multi-day itinerary rather than a single day.
- The retrieved guide evidence does not provide enough accommodation detail.
- The retrieved guide evidence does not provide enough budget detail.
- The retrieved guide evidence does not provide enough safety detail.
- The available evidence does not establish a full itinerary for all requested days.

Cited chunk IDs: `p018-020-73083763654d`.

## Source checks and limitations

Physical PDF pages checked include 1-3 for source context and altitude cautions, 7 for fuel, 19-22 for Hunza access/budget/Rakaposhi duration and season, 38 for Skardu lodging/city sights, 39-40 for Deosai vehicle/season restrictions, 41-42 for Shigar, and 43 for Manthoka. Source identifiers and page ranges derive from the original stored metadata. A valid citation ID does not mechanically prove factual support or route feasibility.

All three final observations are partial plans. The Hunza recheck respects the guide's two days up/one day down. Skardu avoids assuming a 4x4 vehicle but still has extra origin-irrelevant transport prose. Costs are guide estimates with an unchanged outdated-information notice. Daily ordering is a proposed schedule assembled from source facts, not evidence of current access, hotel availability, or guaranteed timing. No live travel APIs are used.

The first and second draft failures show that structured output and source-ID validation alone do not ensure itinerary feasibility. The prompt now explicitly preserves recommended trek duration and avoids blanket seasonal access guarantees, but this is not a deterministic route solver. Other routes and wording still need user review. No claim of comprehensive planner correctness is made.

## Feedback and tester integration

Both sidebar actions use exactly `https://forms.gle/5McdABdSnigwwdNz5`, configurable with `FEEDBACK_FORM_URL`. Native links append no prompts, chat history, trip preferences, email, identifiers, or keys. The form was fetched read-only, returned HTTP 200, and no response was submitted.

The public form data shows explicit Yes/No tester consent and a privacy notice. Yes routes to an Email Collection section; No routes to submit. The email field is marked optional. The form currently requires a Name field for general feedback, which this app does not collect itself. Owner checks remain necessary: confirm automatic Google email collection is disabled, no sign-in requirement exists, No can submit without an email, Yes shows the email section, and the linked Sheet/invitation list is handled only under the stated consent. No tester responses or email addresses are sent to LangSmith.

## Executed mocked checks

`verify_planner.py` passed graph, quota and Streamlit UI groups. It exercised both exact form links, no URL prefill, invalid input before quota charge, structured Hunza/Skardu/partial/unsupported fixtures, invalid citation/day rejection, planner quota, shared model capacity, no rerun duplicate, separate sessions, preservation of quota after clear, feedback accessibility under session/global quota exhaustion, and production trace opt-out even with ambient tracing enabled. Synthetic fixture output validates integration, not real itinerary quality.

Existing `verify_usage.py` and all seven `verify_conversation.py` scenarios also passed. All mocked suites used zero real Gemini calls. LangSmith tracing was enabled only for the controlled real checks; the public app explicitly disables it.

## Development traces

Seven traces were inspected remotely: all expected graph nodes and one generation span per trace were present, with zero technical trace errors and no configured secret values found. Deterministic citation-ID checks and manual review statuses were attached as feedback. Technical success is separate from the recorded quality failures. Traces are private workspace links, not publicly shared experiments. No new LangSmith dataset or full benchmark was launched. To inspect them, open each link while signed in, expand the five graph nodes, inspect the three retriever calls and single Gemini generation, then compare cited passages with this manual review.

- [live_results.json: trip01](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b77-c01d-7d52-8d32-5ddbdfea310b/run/01a14b77-c01d-7d52-8d32-5ddbdfea310b?start_time=2026-10-17T20%3A05%3A01.597738%2B00%3A00)
- [live_results.json: trip02](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b77-d84d-74d2-abe4-6bcf8771bf7e/run/01a14b77-d84d-74d2-abe4-6bcf8771bf7e?start_time=2026-10-17T20%3A05%3A07.789381%2B00%3A00)
- [live_results.json: trip03](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b77-ef4f-7c21-9b33-568befa2e5a7/run/01a14b77-ef4f-7c21-9b33-568befa2e5a7?start_time=2026-10-17T20%3A05%3A13.679355%2B00%3A00)
- [live_results_revised.json: trip01](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b78-d4d4-7073-af9c-4028461ab940/run/01a14b78-d4d4-7073-af9c-4028461ab940?start_time=2026-10-17T20%3A06%3A12.436578%2B00%3A00)
- [live_results_revised.json: trip02](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b78-ee21-72c2-9b3e-6defc2e21ca9/run/01a14b78-ee21-72c2-9b3e-6defc2e21ca9?start_time=2026-10-17T20%3A06%3A18.913201%2B00%3A00)
- [live_results_revised.json: trip03](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b78-fe09-75f2-b196-54192d1ca273/run/01a14b78-fe09-75f2-b196-54192d1ca273?start_time=2026-10-17T20%3A06%3A22.985342%2B00%3A00)
- [live_results_trek-fix.json: trip01](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14b79-cb8b-7c42-9557-f417f1ab2a2e/run/01a14b79-cb8b-7c42-9557-f417f1ab2a2e?start_time=2026-10-17T20%3A07%3A15.595090%2B00%3A00)

Raw controlled outputs and verification details remain in ignored `data/planner-checks/`. No merge, push or deployment occurred.

## v1.1.0 release-audit transport correction

The release audit added an explicit instruction to scope transport to the
chosen origin and made one focused Skardu generation using the same cached
queries. It omitted Islamabad flights/buses, but still asserted standard-car
suitability of local paved routes without sufficient evidence. That raw response
was not accepted as a grounded transport recommendation.

A narrow presentation guard now applies to Car plans whose departure and
destination are the same city. It replaces the generated transport paragraph
with this fixed limitation, leaving sourced day cards unchanged:

> This static guide does not establish current driving conditions or confirm standard-car suitability for every local leg. Confirm access locally; any timings in the day cards are guide estimates.

The saved native payload was replayed through citation validation after the
correction. Day cards were unchanged, source IDs remained valid, and the broad
paving claim was absent. The focused generation took 4.262 seconds. This is a
transport-wording correction, not a guarantee of route feasibility.

Release-audit usage: **1 generation attempt, 0 embeddings**. Cumulative planner
review usage including the earlier runs: **8 generation attempts, 9 query
embeddings, 0 document embeddings**. No full benchmark or LLM judge was run.

[Focused development trace](https://smith.langchain.com/o/4d91b86f-05f1-485a-8951-e7f155770270/projects/p/9b5551ae-bd76-4eaf-b098-4726f36611ee/trace/01a14ba4-c3d0-7200-9ffa-7cbd4b276158/run/01a14ba4-c3d0-7200-9ffa-7cbd4b276158)

The form owner explicitly chose to retain required Name entry. Describe the
external form as general feedback without an email requirement, not fully
anonymous feedback. Tester email/consent and admin-setting owner checks remain
as documented above. No app-side personal-information collection was added.
