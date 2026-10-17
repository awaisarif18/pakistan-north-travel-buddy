# Retrieval evaluation

## Current results

| Metric | Actual result |
|---|---|
| Verified answerable questions | 20 |
| Hit@5 | 1.0000 |
| MRR@10 | 0.9667 |
| Verified multi-fact questions | 5 |
| CompleteEvidence@5 | 1.0000 |
| Failed retrieval questions | 0 |

Successfully retrieved verified questions: 20. Retrieval errors: 0.
Scores require verified labels and a successful retrieval for every verified answerable question.
Draft labels are excluded. These results do not measure answer correctness.

## Method

Model: `gemini-embedding-2`, 3072 dimensions; cosine search, top 10.
Hit@5 = questions with at least one gold chunk in ranks 1-5 / verified answerable questions.
MRR@10 = mean of 1 / first gold rank in ranks 1-10, or zero when no gold chunk appears.
CompleteEvidence@5 = fraction of verified multi-fact questions with at least one top-five chunk from EVERY required evidence group.
IDs within a group are alternatives; all groups are required. One chunk may satisfy multiple groups when the reviewed labels allow it.
Hit@5 and MRR@10 use the first matching gold chunk, so they do not establish complete evidence coverage.
CSV retrieved IDs, pages, and distances are parallel lists ordered from rank 1 to rank 10.

## Failures and next steps

No Hit@5 failures in the evaluated questions.

### Gold evidence below rank one

- q07: How do you reach Ratti Gali Lake from its base camp, and how long is that final leg? First gold rank: 3. Top three: `p053-054-a26a1670d604;p072-074-249d8c96c2fc;p064-065-eeaf0cd09563`.

### Multi-fact evidence coverage

| Question | CompleteEvidence@5 | Missing evidence groups |
|---|---|---|
| q16 | 1 | `[]` |
| q17 | 1 | `[]` |
| q18 | 1 | `[]` |
| q19 | 1 | `[]` |
| q20 | 1 | `[]` |

Inspect missed evidence and question wording before changing retrieval. No reranker or hybrid search is implemented.
If retrieval errors occur, rerun using cached query embeddings before interpreting the aggregate scores.

## Unanswerable questions

Excluded from retrieval metrics. This script never calls Gemini answer generation.
Ask these questions in the chatbot and inspect refusals separately; label approval alone does not verify refusal behavior.

- q21: What will the weather in Hunza be tomorrow?
- q22: How many seats are available on the next NATCO bus from Islamabad to Skardu right now?
- q23: What is the guest Wi-Fi password at Serena Shigar Fort?
- q24: What is the fare for a direct train from Islamabad to Skardu?
- q25: What are the exact GPS coordinates of Monday Lake?

## Gold label review

Verification statuses below record label approval. Only verified answerable questions enter retrieval scores.
The reference answers and supporting excerpts are retained for inspection. Future label changes require review before rescoring.

| ID | Category | Question | Gold chunks | PDF pages | Reference answer | Status |
|---|---|---|---|---|---|---|
| q01 | direct | Where should I refuel before traveling to Khunjerab Pass? | p006-008-4850ae1f4334 | 7 | Fill up completely in Sost before the round trip to Khunjerab; the guide reports no fuel along that stretch. | verified |
| q02 | direct | What is the best season for Rakaposhi Base Camp? | p020-022-8d8b2710273b | 22 | June to September. | verified |
| q03 | direct | What fare range does the guide give for NATCO buses from Islamabad/Rawalpindi to Skardu? | p037-039-63413879f3c2, p010-014-0aced0690245 | 11, 38 | Approximately PKR 4,630–5,500 depending on bus class. | verified |
| q04 | direct | During which months does Deosai close to vehicles because of snow? | p039-040-154eaa1a99b3, p008-010-a7bee3da530b | 10, 40 | Roughly November through May. | verified |
| q05 | direct | What is the minimum motorcycle engine size allowed into Minimarg according to the guide? | p049-051-51be39ff7ee4 | 50 | At least 150cc; smaller motorcycles are turned away. | verified |
| q06 | direct | What vehicle does the guide recommend for the final section to the Naltar lakes? | p057-058-1e3220f30d27 | 57 | A local 4x4 jeep; using a personal bike or vehicle is not advisable on the final rocky section. | verified |
| q07 | direct | How do you reach Ratti Gali Lake from its base camp, and how long is that final leg? | p064-065-eeaf0cd09563 | 64 | Hike from base camp, approximately 40 minutes to two hours. | verified |
| q08 | direct | How long is the trek to Kandol Lake after the jeep journey to Utror? | p072-074-249d8c96c2fc | 72 | About three to four hours. | verified |
| q09 | direct | Which three valleys make up the Kalash Valleys group in this guide? | p081-083-d64cf441cb82 | 81, 82 | Bumburet, Rumbur, and Birir. | verified |
| q10 | direct | How much water should I carry for the Miranjani round trip? | p087-088-8428f4e31885 | 88 | At least 1.5 litres because the trail has no water source. | verified |
| q11 | paraphrased | I am riding over Babusar toward Chilas. Where should I top up, and how long is the stretch without a petrol pump? | p006-008-4850ae1f4334 | 7 | Fill up in Naran; there is no pump after Batakundi through Babusar to Chilas, roughly 90–100 km. | verified |
| q12 | paraphrased | What nightly budget does the guide suggest for a basic guesthouse in Hunza? | p020-022-8d8b2710273b | 20 | Approximately PKR 1,500–3,500 per night for a simple room. | verified |
| q13 | paraphrased | Which village is the road gateway for approaching Kutwal Lake from Gilgit? | p058-060-fa9822ff4f99 | 58 | Sassi village on the Gilgit–Skardu road. | verified |
| q14 | paraphrased | What is the Chitrali broth made by slowly cooking lamb or goat bones called? | p080-081-4717074613d0 | 80 | Shorba. | verified |
| q15 | paraphrased | Is there somewhere to shelter and get water when camping at Dagri Bangla? | p088-090-7fe56cb01062 | 89 | The guide describes a proper shelter and a nearby stream. | verified |
| q16 | multi_fact | Compare the seasons and elevations of Rakaposhi Base Camp and Rush Lake. | p020-022-8d8b2710273b, p022-024-9d656b3640ce | 21, 22, 23 | Both are recommended June–September; Rakaposhi Base Camp is about 4,150 m, while Rush Lake is over 4,700 m. | verified |
| q17 | multi_fact | How can I reach Skardu from Islamabad by public bus, and when does Deosai close to vehicles? | p037-039-63413879f3c2, p010-014-0aced0690245, p039-040-154eaa1a99b3, p008-010-a7bee3da530b | 10, 11, 38, 40 | NATCO operates direct buses, around PKR 4,630–5,500; Deosai closes roughly November–May. | verified |
| q18 | multi_fact | Can I use a 125cc bike for Minimarg and the jeep track to Fairy Meadows, and what alternatives does the guide suggest? | p049-051-51be39ff7ee4, p051-053-ff8a6c292dbc | 50, 52 | A 125cc bike is below Minimarg’s 150cc threshold; use a 4x4 or a 150cc+ motorcycle. For Fairy Meadows, leave the bike at Raikot Bridge or Chilas and take the local jeep service, then hike. | verified |
| q19 | multi_fact | Compare the final access to the Naltar lakes with the approach to Kandol Lake from Kalam. | p057-058-1e3220f30d27, p072-074-249d8c96c2fc | 57, 72 | Naltar lakes require a separate 4x4 leg beyond Naltar Bala. Kandol involves a jeep to Utror, then a three-to-four-hour trek. | verified |
| q20 | multi_fact | What water and overnight arrangements does the guide describe for Miranjani and Dagri Bangla? | p087-088-8428f4e31885, p088-090-7fe56cb01062 | 88, 89 | Miranjani has no trail water source, so carry at least 1.5 litres for a round trip; Dagri Bangla has a shelter and nearby stream for an overnight camp. | verified |
| q21 | unanswerable | What will the weather in Hunza be tomorrow? | None | None | Not available in the PDF | verified |
| q22 | unanswerable | How many seats are available on the next NATCO bus from Islamabad to Skardu right now? | None | None | Not available in the PDF | verified |
| q23 | unanswerable | What is the guest Wi-Fi password at Serena Shigar Fort? | None | None | Not available in the PDF | verified |
| q24 | unanswerable | What is the fare for a direct train from Islamabad to Skardu? | None | None | Not available in the PDF | verified |
| q25 | unanswerable | What are the exact GPS coordinates of Monday Lake? | None | None | Not available in the PDF | verified |

### Supporting excerpts for manual verification

<details><summary>q01: Where should I refuel before traveling to Khunjerab Pass?</summary>

`p006-008-4850ae1f4334`, physical PDF pages [7].

> Sost → Khunjerab Pass (~75-90km one-way) has no fuel whatsoever — this is a there-and-back stretch from Sost for most riders (day trip up to the pass and back), so fill up completely in Sost before making the run.

</details>

<details><summary>q02: What is the best season for Rakaposhi Base Camp?</summary>

`p020-022-8d8b2710273b`, physical PDF pages [22].

> Season: June–September ideal. Local transport in: A public minibus runs Gilgit → Minapin daily, leaving around 3pm, roughly 2 hours.

</details>

<details><summary>q03: What fare range does the guide give for NATCO buses from Islamabad/Rawalpindi to Skardu?</summary>

`p037-039-63413879f3c2`, physical PDF pages [38].

> By local bus: NATCO runs Islamabad/Rawalpindi → Skardu directly, fares around PKR 4,630–5,500 depending on bus class, with buses departing daily around 2pm and the trip taking the same 12–14 hours as the drive.

`p010-014-0aced0690245`, physical PDF pages [11].

> Operator | Route | Fare (PKR) | Notes
> NATCO | Islamabad → Gilgit | ~3,760 | Government- run, oldest operator on the KKH
> NATCO | Islamabad → Hunza | ~5,040 | 
> NATCO | Islamabad → Skardu | ~4,630- 5,500 | Daily ~2pm departure
> Faisal Movers | Islamabad → Hunza | ~4,500- 5,000 | Gilgit terminal: 0311-1224488, near NATCO terminal, Shahr- e-Quaid-e-Azam
> Faisal Movers | Islamabad → Naran | ~2,800- 3,400 | ~7.5 hrs, Yutong executive mini
> Faisal Movers | Islamabad → Kaghan | ~3,400 | 
> Faisal Movers | Lahore → Naran | ~4,000 | 
> Faisal Movers | Multan → Naran | ~5,400 | 

</details>

<details><summary>q04: During which months does Deosai close to vehicles because of snow?</summary>

`p039-040-154eaa1a99b3`, physical PDF pages [40].

> Wildlife/season: Himalayan brown bears, golden eagles, wildflowers May–July, golden landscape August–September. Nights are freezing even in summer — pack proper thermal gear regardless of the season. The park closes to vehicles roughly November–May due to snow.

`p008-010-a7bee3da530b`, physical PDF pages [10].

> Deosai's road closes to vehicles roughly November-May

</details>

<details><summary>q05: What is the minimum motorcycle engine size allowed into Minimarg according to the guide?</summary>

`p049-051-51be39ff7ee4`, physical PDF pages [50].

> Correction — Minimarg bike rules: My earlier note that motorbikes aren't permitted was wrong. The actual rule: minimum 150cc bikes are allowed into Minimarg — it's bikes under 150cc and regular cars that get turned away; you need either a 4x4 jeep or a 150cc+ bike. This matters directly for you — your Yamaha YBR 125 is a 125cc, under that threshold, so it wouldn't qualify for entry on this specific stretch even though it's fine for the rest of the route to Astore, Rama Meadows, and the broader Deosai/Astore road network. The zone is still militarized and NOC-gated regardless of vehicle: get the NOC from the Assistant Commissioner's office at the start of Rama Road near the Astore lorry depot — bring your bike/car number and CNIC, they'll type and stamp three copies on the spot, then hand copies over at the Army Mess checkpoint on Deosai Road. If you ride the YBR out there, plan to leave it in Astore and go the last stretch by jeep or a rented/borrowed 150cc+ bike.

</details>

<details><summary>q06: What vehicle does the guide recommend for the final section to the Naltar lakes?</summary>

`p057-058-1e3220f30d27`, physical PDF pages [57].

> Route: Gilgit → Nomal village (turn off the KKH) → Naltar Bala (Upper Naltar), about 34-40km, 1.5-2 hours. The road to Naltar Bala itself is manageable; the lakes beyond require a separate 4x4 jeep leg — old Willys jeeps with reinforced suspension are the standard local vehicle for this stretch, and taking your own vehicle (bike included) isn't advisable for the final rocky, boulder-strewn section.

</details>

<details><summary>q07: How do you reach Ratti Gali Lake from its base camp, and how long is that final leg?</summary>

`p064-065-eeaf0cd09563`, physical PDF pages [64].

> Ratti Gali Lake: About 106-120km from Muzaffarabad via Dowarian, 3,683-3,698m. Jeep to base camp (PKR 5,000-7,000 round trip) then a 40- minute to 2-hour hike to the lake itself. Moderate, beginner-friendly.

</details>

<details><summary>q08: How long is the trek to Kandol Lake after the jeep journey to Utror?</summary>

`p072-074-249d8c96c2fc`, physical PDF pages [72].

> Route: Kalam → Utror (jeep, ~1 hour) → cross a bridge → trek up the valley, 3-4 hours to Kandol Lake, with Spin Khwar (a smaller, less-visited lake) another 2-3 hours beyond/near Kandol — often done together as one long day or overnight.

</details>

<details><summary>q09: Which three valleys make up the Kalash Valleys group in this guide?</summary>

`p081-083-d64cf441cb82`, physical PDF pages [81].

> Kalash Valleys (Bumburet, Rumbur, Birir)

`p081-083-d64cf441cb82`, physical PDF pages [82].

> Distances from Chitral specifically: Bumburet ~40km, Birir ~34km, Rumbur ~32km, all on jeepable roads.

</details>

<details><summary>q10: How much water should I carry for the Miranjani round trip?</summary>

`p087-088-8428f4e31885`, physical PDF pages [88].

> Practical note: no water source on the trail itself — carry at least 1.5L round trip.

</details>

<details><summary>q11: I am riding over Babusar toward Chilas. Where should I top up, and how long is the stretch without a petrol pump?</summary>

`p006-008-4850ae1f4334`, physical PDF pages [7].

> Fill your tank in Naran — there is no petrol pump after Batakundi (12km past Naran), all the way over Babusar Top and down to Chilas — that's roughly 90-100km with nothing.

</details>

<details><summary>q12: What nightly budget does the guide suggest for a basic guesthouse in Hunza?</summary>

`p020-022-8d8b2710273b`, physical PDF pages [20].

> Budget guesthouses: PKR 1,500–3,500/night, simple rooms, often shared bathroom, breakfast

</details>

<details><summary>q13: Which village is the road gateway for approaching Kutwal Lake from Gilgit?</summary>

`p058-060-fa9822ff4f99`, physical PDF pages [58].

> Route: Gilgit → Sassi village (on the Gilgit-Skardu road, roughly 53-66km / about 1 hour), then a 4x4 jeep track further into the valley, then trek in. Sassi

</details>

<details><summary>q14: What is the Chitrali broth made by slowly cooking lamb or goat bones called?</summary>

`p080-081-4717074613d0`, physical PDF pages [80].

> Shorba — slow-cooked lamb/goat bone broth with dried tomato and wild herbs, the valley's

</details>

<details><summary>q15: Is there somewhere to shelter and get water when camping at Dagri Bangla?</summary>

`p088-090-7fe56cb01062`, physical PDF pages [89].

> Camping: A proper shelter exists at Dagri Bangla with a nearby stream for water — genuinely set up for an overnight rather than requiring you to bring full camping infrastructure.

</details>

<details><summary>q16: Compare the seasons and elevations of Rakaposhi Base Camp and Rush Lake.</summary>

Required evidence groups: `[["p020-022-8d8b2710273b"], ["p022-024-9d656b3640ce"]]`.

`p020-022-8d8b2710273b`, physical PDF pages [21].

> Distance/elevation: About 26 km round trip with roughly 1,500m of elevation gain/loss if done as a rushed single day — not recommended. Base camp itself sits around 4,150m, reached via a

`p020-022-8d8b2710273b`, physical PDF pages [22].

> Season: June–September ideal. Local transport in: A public minibus runs Gilgit → Minapin daily, leaving around 3pm, roughly 2 hours.

`p022-024-9d656b3640ce`, physical PDF pages [23].

> What it is: Rush Lake sits over 4,700m — Pakistan's highest lake, reached by crossing the Bualtar and Barpu glaciers.

`p022-024-9d656b3640ce`, physical PDF pages [23].

> Season: June–September.

</details>

<details><summary>q17: How can I reach Skardu from Islamabad by public bus, and when does Deosai close to vehicles?</summary>

Required evidence groups: `[["p037-039-63413879f3c2", "p010-014-0aced0690245"], ["p039-040-154eaa1a99b3", "p008-010-a7bee3da530b"]]`.

`p037-039-63413879f3c2`, physical PDF pages [38].

> By local bus: NATCO runs Islamabad/Rawalpindi → Skardu directly, fares around PKR 4,630–5,500 depending on bus class, with buses departing daily around 2pm and the trip taking the same 12–14 hours as the drive.

`p010-014-0aced0690245`, physical PDF pages [11].

> Operator | Route | Fare (PKR) | Notes
> NATCO | Islamabad → Gilgit | ~3,760 | Government- run, oldest operator on the KKH
> NATCO | Islamabad → Hunza | ~5,040 | 
> NATCO | Islamabad → Skardu | ~4,630- 5,500 | Daily ~2pm departure
> Faisal Movers | Islamabad → Hunza | ~4,500- 5,000 | Gilgit terminal: 0311-1224488, near NATCO terminal, Shahr- e-Quaid-e-Azam
> Faisal Movers | Islamabad → Naran | ~2,800- 3,400 | ~7.5 hrs, Yutong executive mini
> Faisal Movers | Islamabad → Kaghan | ~3,400 | 
> Faisal Movers | Lahore → Naran | ~4,000 | 
> Faisal Movers | Multan → Naran | ~5,400 | 

`p039-040-154eaa1a99b3`, physical PDF pages [40].

> Wildlife/season: Himalayan brown bears, golden eagles, wildflowers May–July, golden landscape August–September. Nights are freezing even in summer — pack proper thermal gear regardless of the season. The park closes to vehicles roughly November–May due to snow.

`p008-010-a7bee3da530b`, physical PDF pages [10].

> Deosai's road closes to vehicles roughly November-May

</details>

<details><summary>q18: Can I use a 125cc bike for Minimarg and the jeep track to Fairy Meadows, and what alternatives does the guide suggest?</summary>

Required evidence groups: `[["p049-051-51be39ff7ee4"], ["p051-053-ff8a6c292dbc"]]`.

`p049-051-51be39ff7ee4`, physical PDF pages [50].

> Correction — Minimarg bike rules: My earlier note that motorbikes aren't permitted was wrong. The actual rule: minimum 150cc bikes are allowed into Minimarg — it's bikes under 150cc and regular cars that get turned away; you need either a 4x4 jeep or a 150cc+ bike. This matters directly for you — your Yamaha YBR 125 is a 125cc, under that threshold, so it wouldn't qualify for entry on this specific stretch even though it's fine for the rest of the route to Astore, Rama Meadows, and the broader Deosai/Astore road network. The zone is still militarized and NOC-gated regardless of vehicle: get the NOC from the Assistant Commissioner's office at the start of Rama Road near the Astore lorry depot — bring your bike/car number and CNIC, they'll type and stamp three copies on the spot, then hand copies over at the Army Mess checkpoint on Deosai Road. If you ride the YBR out there, plan to leave it in Astore and go the last stretch by jeep or a rented/borrowed 150cc+ bike.

`p051-053-ff8a6c292dbc`, physical PDF pages [52].

> Route: Islamabad → Raikot Bridge on the KKH (~540km, 10-12 hours) → 4x4 jeep from Raikot Bridge to Tattu village (15-16km, 90-120 min on a narrow single-lane track, PKR 12,000-15,000 per jeep for up to 6 people) → trek 3-5.5km on foot (2- 3 hours) to Fairy Meadows.

`p051-053-ff8a6c292dbc`, physical PDF pages [52].

> This jeep track is genuinely not bike territory — narrow, one-lane, and normally driven only by experienced local jeep drivers; leave the bike at Raikot Bridge or Chilas and go in by the local jeep service.

</details>

<details><summary>q19: Compare the final access to the Naltar lakes with the approach to Kandol Lake from Kalam.</summary>

Required evidence groups: `[["p057-058-1e3220f30d27"], ["p072-074-249d8c96c2fc"]]`.

`p057-058-1e3220f30d27`, physical PDF pages [57].

> Route: Gilgit → Nomal village (turn off the KKH) → Naltar Bala (Upper Naltar), about 34-40km, 1.5-2 hours. The road to Naltar Bala itself is manageable; the lakes beyond require a separate 4x4 jeep leg — old Willys jeeps with reinforced suspension are the standard local vehicle for this stretch, and taking your own vehicle (bike included) isn't advisable for the final rocky, boulder-strewn section.

`p072-074-249d8c96c2fc`, physical PDF pages [72].

> Route: Kalam → Utror (jeep, ~1 hour) → cross a bridge → trek up the valley, 3-4 hours to Kandol Lake, with Spin Khwar (a smaller, less-visited lake) another 2-3 hours beyond/near Kandol — often done together as one long day or overnight.

</details>

<details><summary>q20: What water and overnight arrangements does the guide describe for Miranjani and Dagri Bangla?</summary>

Required evidence groups: `[["p087-088-8428f4e31885"], ["p088-090-7fe56cb01062"]]`.

`p087-088-8428f4e31885`, physical PDF pages [88].

> Practical note: no water source on the trail itself — carry at least 1.5L round trip.

`p088-090-7fe56cb01062`, physical PDF pages [89].

> Camping: A proper shelter exists at Dagri Bangla with a nearby stream for water — genuinely set up for an overnight rather than requiring you to bring full camping infrastructure.

</details>

