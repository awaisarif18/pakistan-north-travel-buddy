# v1.1 harder dataset: independent review

50 reviewed questions: 40 answerable and 10 unanswerable. All labels independently approved and verified.
Development: 8 answerable + 2 unanswerable. Held-out: 32 answerable + 8 unanswerable.
Dataset synchronization is separate from evaluation. No new benchmark has been run or scored.
Gold chunk IDs are disjoint between splits; questions still share one PDF and related topics.
The dataset is multi-fact-heavy: 38/40 answerable questions are multi_fact; 21 have one required evidence group and 17 have at least two.
Keep aggregate CompleteEvidence@5 and plan a separate multi-passage result restricted to questions requiring at least two distinct evidence groups. One-group coverage does not demonstrate multi-passage retrieval.
After the requested split rebalance, all 17 two-group questions are held-out. The development multi-passage subgroup is empty; report it as unavailable, not zero or a passing score.
Review reference completeness, exact supporting pages, excerpt relevance, evidence groups, and negative-case scope.
Verification records explicit user approval after source-consistency checks; references remain frozen.

<details><summary>h01 | held_out | According to the guide, what registration deadline, yearly per-category limit, and flight-height ceiling should a resident drone owner note, and is Khunjerab an exception?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: The guide says register with PCAA within 15 days of purchase, up to three drones per category per calendar year, and fly no higher than 400 ft above ground; Khunjerab is a complete no-fly zone.

Gold chunks: `p003-004-421772785019`. Physical PDF pages: [3, 4].

Required groups: `[["p003-004-421772785019"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p003-004-421772785019` | physical pages [3, 4]

> Registration: drones must be registered with the PCAA (Pakistan Civil Aviation Authority) — as a resident, you're required to register within 15 days
>
> of purchase, and can register up to 3 drones per category per calendar year.

`p003-004-421772785019` | physical pages [4]

> Altitude/operation limits: max 400ft above ground level, visual line of sight required, daylight only unless specially authorized. Hard no-fly zones: military installations, sensitive infrastructure, and border areas — Khunjerab Pass specifically is a complete no-fly zone since it's a border crossing, directly relevant since it's a common add-on to a Hunza trip. Site-specific permission needed: flying over Altit Fort or Baltit Fort in Hunza requires prior permission from the AC/DC (Assistant/Deputy Commissioner) office in Hunza/Aliabad — worth arranging ahead if you want aerial shots of either fort specifically.

</details>

<details><summary>h02 | held_out | For an ID checkpoint followed by a remote jeep-track trek, which original riding documents should I carry and how is a local guide usually arranged?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: Carry original CNIC, bike registration book and driving licence. Hire a jeep with driver at the last accessible town; the driver guides or connects visitors to a local porter/guide.

Gold chunks: `p004-006-bcd9fec8929a, p016-018-ca83b3ddd819`. Physical PDF pages: [5, 16, 17].

Required groups: `[["p004-006-bcd9fec8929a"], ["p016-018-ca83b3ddd819"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p004-006-bcd9fec8929a` | physical pages [5]

> Always carry: original CNIC (not a photo of it — checkpoints in AJK and near the LOC specifically ask for the original), your bike's registration book, and your driving license. KKH, Neelum, and Astore/Deosai routes all have periodic checkpoints where these get checked.

`p016-018-ca83b3ddd819` | physical pages [16, 17]

> Jeep hire: this is genuinely how "local guide" works for most of the remote spots in this document — you hire a jeep with driver in the last accessible
>
> town (Thal, Utror, Sassi, Bilamik, Madaglasht, etc.), and the driver either guides you directly or connects you with a local porter/guide on arrival. There's no separate "book a guide in advance" infrastructure for most of these places outside the big-name treks (K2, Rakaposhi, Fairy Meadows) that the tour operators above run as formal packages.

</details>

<details><summary>h03 | dev | Match these side-valley turnoffs to their last main-road fuel hubs: Chapursan, Naltar, and Hushe.</summary>

Status: **verified**. Category: `exact_route`. Region: `practical`.

Reference: Sost for Chapursan, Nomal for Naltar, and Khaplu for Hushe; do not assume fuel beyond the turnoff.

Gold chunks: `p008-010-a7bee3da530b`. Physical PDF pages: [9].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p008-010-a7bee3da530b` | physical pages [9]

> The general pattern across every remote jeep-track valley on this list (Chapursan, Shimshal, Naltar, Bilamik/Thorsay, Madaglasht, Hushe): fuel exists in the last KKH/main-road town before the turnoff (Sost for Chapursan, Karimabad/Shishkat area for Shimshal, Nomal for Naltar, the Skardu-road towns for Bilamik, Chitral town for Madaglasht, Khaplu for Hushe) and nowhere beyond it. Treat every side-valley turnoff in this entire document as "last fuel here" unless a specific entry says otherwise.

</details>

<details><summary>h04 | dev | Why should a rider avoid relying on a national SIM or an ATM after leaving the main GB towns, and which regional mobile network does the guide prefer?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: SCOM generally has the best coverage in GB; national networks become patchy off main roads. ATMs are concentrated in Gilgit, Skardu, Hunza, Chitral and Mingora, while remote jeep hire, guesthouses and guides mostly take cash.

Gold chunks: `p008-010-a7bee3da530b`. Physical PDF pages: [9, 10].

Required groups: `[["p008-010-a7bee3da530b"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p008-010-a7bee3da530b` | physical pages [9]

> SIM/network: SCOM is Gilgit-Baltistan's own network and generally has the best coverage in- region — already noted for Neelum specifically but worth knowing as a general rule across GB, not just AJK. Major national networks (Jazz, Zong, Telenor, Ufone) have patchy coverage once you're off the KKH/main roads, and several specific spots in this document (Chapursan, Hushe past Saicho, most

`p008-010-a7bee3da530b` | physical pages [10]

> Cash: ATMs exist in Gilgit, Skardu, Hunza (Karimabad/Aliabad), Chitral town, and Mingora — not much beyond that. Carry enough cash for each region's leg before heading into the valleys; jeep hire, guesthouses, and local guides are almost entirely cash transactions.

</details>

<details><summary>h05 | held_out | In the transport table, compare the listed Islamabad-to-Naran Faisal Movers fare with NATCO's Islamabad-to-Gilgit fare and Naran journey time.</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: Faisal Movers to Naran is about PKR 2,800-3,400 and 7.5 hours; NATCO to Gilgit is about PKR 3,760. These are guide estimates.

Gold chunks: `p010-014-0aced0690245`. Physical PDF pages: [11].

Required groups: `[["p010-014-0aced0690245"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p010-014-0aced0690245` | physical pages [11]

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

<details><summary>h06 | held_out | If my bike needs replacing in Naran, who is the named GS150 rental/repair contact and what evidence should I record before accepting any rental bike?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: Abdul Samad in Naran rents Suzuki GS150s and does repairs. Film a full walk-around including chain, fairings, tyres and dents to document pre-existing damage.

Gold chunks: `p014-016-b439f2d5f7da`. Physical PDF pages: [15, 16].

Required groups: `[["p014-016-b439f2d5f7da"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p014-016-b439f2d5f7da` | physical pages [15]

> Naran specifically — Abdul Samad: 03009484055 / 03436097256 — rents Suzuki GS150s and does repairs, based in Naran itself. Genuinely useful if something goes wrong with the YBR on the Kaghan leg, or if you want a second bike for anyone riding with you. Keran, Neelum Valley — Jani Bhai: 0355 6318104 — bike mechanic on the Keran-to-Kel road, just past the hotels. Covers the whole Neelum leg (Ratti Gali, Arang Kel, Kel are all on this same road). General rental hubs (confirmed by multiple independent sources, not just one operator's marketing): Gilgit has bike shops around the Jutial area; Hunza's rental shops cluster in Aliabad; Skardu also has rental options, mostly 125cc- 250cc bikes. North Bikers Pakistan and Gilgit Bikers are two other named operators covering the same Hunza/Skardu/KKH territory, though I don't have verified phone numbers for those two specifically.

`p014-016-b439f2d5f7da` | physical pages [15, 16]

> Before you take a rental: film a full walk-around of the bike first — chain, fairings, tyres, dents — so
>
> you're not blamed for pre-existing damage at return.

</details>

<details><summary>h07 | held_out | Where in Islamabad can I obtain tents, stoves and ice axes, and what repair supplies does the guide recommend taking beyond the main towns?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: Ascender Outdoors at F-11/1, Ali Market, Islamabad rents trekking equipment. Carry basic tools and a spare tube beyond main-town mechanic/fuel hubs.

Gold chunks: `p016-018-ca83b3ddd819`. Physical PDF pages: [16].

Required groups: `[["p016-018-ca83b3ddd819"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p016-018-ca83b3ddd819` | physical pages [16]

> Gear rental in Islamabad: Ascender Outdoors — trekking gear sales and rental (tents, sleeping bags, stoves, crampons, ice axes), F-11/1, Ali Market, Islamabad, +92 333 9980903, info@ascender.pk. Worth stocking up here before heading north rather than counting on finding gear in-valley.

`p016-018-ca83b3ddd819` | physical pages [16]

> Mechanics/fuel beyond bike rental shops: every KKH town (Mansehra, Besham, Chilas, Gilgit, Karimabad) and every Swat/Kaghan hub (Mingora, Balakot, Naran, Kalam) has basic mechanics and fuel — mechanics are available in main towns only, so carry basic tools and a spare tube past those points. Past the last town before a jeep track, you're relying on the jeep driver's own mechanical knowledge, which is generally solid since their vehicles take a beating daily.

</details>

<details><summary>h08 | held_out | Which festival is associated with Hunza and Nagar's wheat harvest, when is it held, and how does accommodation at the Shandur Polo Festival differ?</summary>

Status: **verified**. Category: `multi_fact`. Region: `practical`.

Reference: Ginani is in late June/early July in Hunza and Nagar; Shandur's July 7-9 polo festival has tent-camping-only accommodation and needs advance planning.

Gold chunks: `p016-018-ca83b3ddd819`. Physical PDF pages: [17].

Required groups: `[["p016-018-ca83b3ddd819"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p016-018-ca83b3ddd819` | physical pages [17]

> Ginani — late June/early July, Hunza and Nagar's wheat-harvest festival: orchards, traditional dress, Shina/Burushaski songs, and harissa (a meat-and- wheat dish).

`p016-018-ca83b3ddd819` | physical pages [17]

> Shandur Polo Festival — 3,700m, the world's highest polo ground, Gilgit vs. Chitral in a free- flowing traditional format dating to 1936, held July 7-9 — accommodation is tent-camping only, book/plan well ahead. Genuinely one of the most spectacular single events on this whole list if the timing works.

</details>

<details><summary>h09 | dev | What is the exact per-litre petrol price being charged at Nomal right now?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h10 | dev | Reserve a hotel room in Sost for tonight and give me the confirmed booking number.</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h11 | held_out | I want to approach Tagaphari without a private vehicle. What daily public connection reaches Minapin from Gilgit, and which intermediate campsite is on the base-camp trail?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Hunza`.

Reference: A public minibus leaves Gilgit for Minapin around 3 pm daily and takes roughly two hours. The trail runs Minapin to Hapakun campsite to Tagaphari/Rakaposhi Base Camp.

Gold chunks: `p020-022-8d8b2710273b`. Physical PDF pages: [21, 22].

Required groups: `[["p020-022-8d8b2710273b"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p020-022-8d8b2710273b` | physical pages [21]

> Start point: Minapin village (~70 km from Gilgit, short detour off the KKH) — bike-accessible all the way. Route: Minapin → Hapakun campsite → Tagaphari (Rakaposhi Base Camp), optionally on to Diran Base Camp.

`p020-022-8d8b2710273b` | physical pages [22]

> Season: June–September ideal. Local transport in: A public minibus runs Gilgit → Minapin daily, leaving around 3pm, roughly 2 hours.

</details>

<details><summary>h12 | held_out | For Patundas, which starting lake and glacier crossing are involved, and through whose village must guide/portering arrangements be made?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Gojal`.

Reference: Start at Borith Lake, pass Passugar and cross Passu/White Glacier via Luzhdur to Patundas. Ghulkin villagers hold exclusive portering rights; arrange a guide through Ghulkin or Al-Rahim Hotel near Gulmit, ideally a day ahead.

Gold chunks: `p022-024-9d656b3640ce`. Physical PDF pages: [23, 24].

Required groups: `[["p022-024-9d656b3640ce"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p022-024-9d656b3640ce` | physical pages [23]

> Start point: Borith Lake (near Passu/Hussaini) — bike-accessible to Borith Lake, then on foot. Route: Borith Lake → Passugar → cross Passu (White) Glacier → Luzhdur/Lazhdar camp → Patundas Meadows.

`p022-024-9d656b3640ce` | physical pages [24]

> Guide/access note: Patundas is the property of Ghulkin villagers who hold exclusive portering rights — arrange a guide a day in advance through Ghulkin, or via the Al-Rahim Hotel on the KKH near Gulmit.

</details>

<details><summary>h13 | held_out | Contrast the Karambar Lake road approach via Ishkoman with the standard endpoints of the Snow Lake-Hispar La traverse; are they both simple Hunza return walks?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Hunza_Baltistan`.

Reference: Karambar's GB approach is Gilgit-Ishkoman-Chatorkhand followed by a three-to-four-day trek, with the road ending well before the lake. Snow Lake usually crosses from Askole on the Skardu side to Hispar on the Hunza/Nagar side, roughly 190 km and 12 trekking days; neither is a simple Hunza return walk.

Gold chunks: `p024-026-a464334daa72, p026-028-3af709bd9d8f`. Physical PDF pages: [24, 25, 26].

Required groups: `[["p024-026-a464334daa72"], ["p026-028-3af709bd9d8f"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p024-026-a464334daa72` | physical pages [24]

> What it is: A high-altitude glacial lake at 4,272m in Ishkoman Valley, Ghizer District — Pakistan's 2nd highest lake, sitting near the Afghan border. This one straddles the Chitral and Gilgit-Baltistan approach — genuinely remote either way. Route from Hunza/Gilgit side: Gilgit → Ishkoman Valley → Chatorkhand (~250 km, 8–10 hours by

`p024-026-a464334daa72` | physical pages [25]

> Transport realism: road ends well before the lake; expect shared jeeps and hitchhiking for the approach, not your bike, past Chatorkhand/Immit.

`p026-028-3af709bd9d8f` | physical pages [26]

> Two directions: Most groups start from Askole (Skardu side) and finish in Hispar village (Hunza/Nagar side), or occasionally the reverse.

`p026-028-3af709bd9d8f` | physical pages [26]

> Distance/duration: About 190 km total, 12 days classic itinerary, though full trips including travel run around 3 weeks door to door, with 12 days of high-altitude trekking.

`p024-026-a464334daa72` | physical pages [25]

> road), then a 3–4 day trek covering roughly 30–35 km to the lake. Alternative (Chitral side): Chitral → Mastuj (~3 hrs) → jeep to Lashkargaz (~6 hrs) → trek in, crossing both Karambar Pass and Darkot Pass to reach 4,694m at the highest point.

</details>

<details><summary>h14 | held_out | Separate summit climbing from a base-camp add-on: what experience does Spantik require, and what does the Rakaposhi-to-Diran Base Camp excursion involve?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Hunza_Nagar`.

Reference: Spantik is an AD technical climb with prior high-altitude mountaineering and preferably 6,000 m experience. Diran Base Camp can be an approximately five-hour return add-on from Rakaposhi Base Camp across the crevassed Katchelly Glacier, ideally with a guide; it is not the Diran summit climb.

Gold chunks: `p028-030-6c22e017412e, p030-032-e38247495869`. Physical PDF pages: [30].

Required groups: `[["p028-030-6c22e017412e"], ["p030-032-e38247495869"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p028-030-6c22e017412e` | physical pages [30]

> Difficulty: Graded AD (technical), requiring prior high-altitude mountaineering experience — this is a real climb, not a trek. Previous 6,000m experience is strongly recommended.

`p030-032-e38247495869` | physical pages [30]

> Base camp trek only: A round trip from Rakaposhi Base Camp to Diran Base Camp and back takes about 5 hours, crossing the Katchelly Glacier with some genuinely deep crevasses to navigate — this

</details>

<details><summary>h15 | held_out | A guide says Yashperth and Patundas both involve glaciers. Which meadow is Yashperth, which glacier belongs to each route, and is Patundas a self-guided crossing?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Gojal`.

Reference: Yashperth refers to Yashpirt on the Batura Glacier trek, approached via Borith Lake and Yunzben. Patundas crosses Passu/White Glacier; it needs a local guide's route knowledge, rather than a self-guided crossing.

Gold chunks: `p032-033-d33bd27c781e, p022-024-9d656b3640ce`. Physical PDF pages: [23, 24, 33].

Required groups: `[["p032-033-d33bd27c781e"], ["p022-024-9d656b3640ce"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p032-033-d33bd27c781e` | physical pages [33]

> What it is: the trek you had listed as "Yashperth" is Yashpirt — a beautiful high meadow with shepherd huts at around 3,400–3,630m, with views of the Batura peaks, the Batura icefall, and Distaghil Sar (7,885m). Route: Borith Lake → Yunzben (11.5km, 6–7 hrs) → across the Batura Glacier → Yashpirt (5.7km, 6– 7 hrs). The Batura Glacier itself is around 57–65km long — one of the longest outside the polar regions.

`p022-024-9d656b3640ce` | physical pages [23]

> Start point: Borith Lake (near Passu/Hussaini) — bike-accessible to Borith Lake, then on foot. Route: Borith Lake → Passugar → cross Passu (White) Glacier → Luzhdur/Lazhdar camp → Patundas Meadows.

`p022-024-9d656b3640ce` | physical pages [24]

> Days: Typically done as a 3-day trek (lower camp → Patundas → back). Difficulty: A mandatory glacier crossing that needs a local guide's route knowledge — not technical, but not something to freelance. The climb from lower camp to Patundas gains around 700m in just a couple of kilometers of steep switchbacks above 3,500m.

</details>

<details><summary>h16 | held_out | For a light outing, distinguish Buskochi/Baskochi Top from Miacher Kho Meadows by starting village and walking commitment.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Hunza_Nagar`.

Reference: Buskochi begins at Shishkat near Attabad and is about a three-to-four-hour round trip. Kho Meadows lies above Miacher in Nagar, reached via Nagar-Minapin-Miacher, with about a 30-minute walk from parking.

Gold chunks: `p033-035-97d114c1c3a8`. Physical PDF pages: [34, 35].

Required groups: `[["p033-035-97d114c1c3a8"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p033-035-97d114c1c3a8` | physical pages [34]

> Start point: Shishkat village (near Attabad Lake) — bike-accessible.

`p033-035-97d114c1c3a8` | physical pages [34]

> Route: A 3–4 hour round trip through light forest and traditional Gojal farmland, up to panoramic views of Attabad Lake and the surrounding villages. Difficulty: Easy — a "hidden gem for those who love nature without the burn," good for a late start, sunset trek, or mellow day with local guides.

`p033-035-97d114c1c3a8` | physical pages [35]

> What it is: "Kho Nagar Valley" from your original list is Miacher Kho Meadows (also just called Kho Meadows), a meadow above Miacher village in Nagar Valley — genuinely in Region 1's territory, not Kohistan as I'd first guessed while researching Region 4. Route: Gilgit → Nagar → Minapin → Miacher village → Kho Meadows, about 3-4 hours total from Gilgit City. A short ~30 minute walk from the parking area up to the meadow itself.

</details>

<details><summary>h17 | held_out | Are Hareen Bhaag and Kho Nagar two names for the same meadow? Give the resolved identity and access corridor of each.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Nagar_Rondu`.

Reference: No. Hareen/Hiraan Bhaag is Thorsay Meadows in Bilamik, Rondu, approached from Skardu through Dambudas/Bilamik. Kho Nagar is Miacher Kho Meadows in Nagar, approached via Gilgit-Nagar-Minapin-Miacher.

Gold chunks: `p047-049-8dc49f1b20f2, p033-035-97d114c1c3a8`. Physical PDF pages: [35, 47, 48].

Required groups: `[["p047-049-8dc49f1b20f2"], ["p033-035-97d114c1c3a8"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p047-049-8dc49f1b20f2` | physical pages [47]

> These two spellings from your original list are the same place: Thorsay Meadows, in Bilamik, Rondu District.

`p047-049-8dc49f1b20f2` | physical pages [48]

> Route: Skardu → Dambudas → Bilamik, about 2 hours by road/jeep, or about 80km from Skardu via the Baltistan Highway (JSR), starting from the South Suspension Bridge, roughly 2 hours on a 4x4 jeep track. A tour operator itinerary describes it as a 4-5 hour jeep trek from Skardu to reach camping at the meadows — treat the shorter and longer figures as reflecting different exact routes/vehicles rather than a contradiction.

`p033-035-97d114c1c3a8` | physical pages [35]

> What it is: "Kho Nagar Valley" from your original list is Miacher Kho Meadows (also just called Kho Meadows), a meadow above Miacher village in Nagar Valley — genuinely in Region 1's territory, not Kohistan as I'd first guessed while researching Region 4. Route: Gilgit → Nagar → Minapin → Miacher village → Kho Meadows, about 3-4 hours total from Gilgit City. A short ~30 minute walk from the parking area up to the meadow itself.

</details>

<details><summary>h18 | held_out | For a fly-in Skardu trip followed by a Hushe trek, why allow flight-schedule slack and where does mobile coverage disappear on the trekking approach?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Skardu_Hushe`.

Reference: Skardu flights are generally morning departures and weather cancellations are common, so avoid a tight schedule. Hushe has patchy signal, with no mobile signal beyond Saicho junction.

Gold chunks: `p037-039-63413879f3c2, p044-045-87c4ea0777e3`. Physical PDF pages: [37, 44].

Required groups: `[["p037-039-63413879f3c2"], ["p044-045-87c4ea0777e3"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p037-039-63413879f3c2` | physical pages [37]

> By air: PIA, Airblue, and AirSial all fly Islamabad → Skardu (KDU) direct, about 1–1h10m in the air, roughly 24 weekly departures between them. Fares run roughly PKR 12,000–45,000 one-way depending on timing and season — book early, this route sells out fast in peak season (Eid, summer holidays). Flights are almost always morning departures since mountain visibility is best early, and weather cancellations are common — don't book it on a tight schedule.

`p044-045-87c4ea0777e3` | physical pages [44]

> Hushe is to Baltistan's technical trekking what Minapin is to Hunza's — one road-end village feeding several serious objectives. Route in: Skardu → jeep via Khaplu, Machulo, Kanday, Khaney → Hushe (the highest permanent village in the area, ~3,050m). All multi-day treks above the village require a CKNP trekking permit, issued at the Skardu CKNP office; porters are hired directly from Hushe through the village porters' association. Homestays and one or two basic guesthouses exist in the village itself; everything above it is tent camping. Mobile signal is patchy in Hushe and nonexistent past Saicho junction — same vlogging- connectivity note as Chapursan in Region 1.

</details>

<details><summary>h19 | dev | For Sheosar Lake, compare the approach from Skardu with Astore through Chilum, and list the three Pani crossings in their plateau order.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Deosai`.

Reference: The Skardu route goes via Sadpara and Ali Malik Pass; the Astore/Chilum approach is the smoother option, about four hours by jeep on semi-metalled road. The plateau order is Shatung Pani, Bara Pani, then Kala Pani before Sheosar.

Gold chunks: `p039-040-154eaa1a99b3`. Physical PDF pages: [39, 40].

Required groups: `[["p039-040-154eaa1a99b3"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p039-040-154eaa1a99b3` | physical pages [39]

> Route from Skardu: Skardu → Sadpara Lake/Dam → Ali Malik Pass → Deosai entrance, about 30– 40km, 1.5–2 hours by 4x4 (a sedan will not survive this road — jeep is not optional). Park entry fee is around PKR 100–300/person.

`p039-040-154eaa1a99b3` | physical pages [39]

> Sheosar Lake: At 4,250m, one of the highest- altitude lakes in the world, about 75–85km from Skardu depending on route, reachable via Skardu (jeep, few hours, or a 2-day trek) or via Astore through Chilum (about 4 hours jeep on semi- metalled road) — the Astore approach is the smoother, paved-road option if you're coming from that side instead. Key waypoints along the plateau: Sadpara Lake → Ali Malik Pass → Shatung Pani (first stream

`p039-040-154eaa1a99b3` | physical pages [40]

> crossing) → Bara Pani (main crossing, has glamping) → Kala Pani (last crossing before Astore side) → Sheosar Lake. Bari-La Lake: A high pass/lake at 4,721m linking Deosai to the Gultari-Shigo Shigar area, historically connecting Skardu and Shingo/Shigar. The road (jeep only, high-clearance 4x4 essential) is only open about 2–3 months, July–September, starting the trek portion from Shigar and spanning about 38km.

</details>

<details><summary>h20 | held_out | If I want a traverse rather than retracing Baltoro, where does crossing Gondogoro La take me, what technical gear is listed, and how does Snow Lake's usual finish differ?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Baltistan_Hunza`.

Reference: Gondogoro La leads from the K2/Concordia route into Hushe Valley; crampons, climbing harness and carabiner are listed, with fixed ropes available in July-August for a fee. Snow Lake-Hispar La usually finishes at Hispar village on the Hunza/Nagar side.

Gold chunks: `p040-042-e594be504c6e, p026-028-3af709bd9d8f`. Physical PDF pages: [26, 40, 41].

Required groups: `[["p040-042-e594be504c6e"], ["p026-028-3af709bd9d8f"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p040-042-e594be504c6e` | physical pages [40]

> Route: Skardu → jeep to Askole (last village, ~7 hours), then on foot: Jhola → Paiju (rest day) →

`p040-042-e594be504c6e` | physical pages [41]

> Khoburtse → Urdukas → Goro II → Concordia → K2 Base Camp, then either return the same way or cross Gondogoro La (5,585m) down into Hushe Valley.

`p040-042-e594be504c6e` | physical pages [41]

> Gear/guide: A guide, porter, and CKNP permit are mandatory; crossing Gondogoro La needs crampons, a climbing harness, and a carabiner, with fixed ropes available July–August for a fee (~PKR 28,000 for up to 2 people).

`p026-028-3af709bd9d8f` | physical pages [26]

> Two directions: Most groups start from Askole (Skardu side) and finish in Hispar village (Hunza/Nagar side), or occasionally the reverse.

</details>

<details><summary>h21 | dev | Keep the Khaplu and Kharmang outings straight: where is Sogha/Crystal Lake, how is it reached locally, and why should the Manthoka visitor carry ID?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Khaplu_Kharmang`.

Reference: Sogha/Crystal Lake is at Saling near Khaplu, about seven km from town, reachable by a 15-25-minute jeep leg or 1.5-hour trek from the nearby village. Manthoka is on the Kargil-Skardu road toward the LOC and has a checkpoint, so carry ID.

Gold chunks: `p042-044-232729beb314`. Physical PDF pages: [42, 43].

Required groups: `[["p042-044-232729beb314"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p042-044-232729beb314` | physical pages [42]

> Sogha Lake (Crystal Lake): In Saling village near Khaplu — reachable by jeep (15–25 min) or a 1.5- hour trek from the nearby village, about 7km from Khaplu town.

`p042-044-232729beb314` | physical pages [43]

> Local transport: A full day driver around Khaplu runs about PKR 1,000, and the return drive to Skardu with stops at Machlu Valley, Sogha Lake, Saling, and Manthoka Waterfall runs about PKR 6,000 — a good way to bundle several of these in one day if you're not on the bike for this stretch.

`p042-044-232729beb314` | physical pages [43]

> Manthoka Waterfall: About 80km / 2-3 hours from Skardu on the Kargil-Skardu road, roughly 180 feet high. There's a checkpoint here since the road continues toward the Line of Control — carry ID. Crossed via a bouncy wooden bridge on metal cables; expect to get wet from the spray.

</details>

<details><summary>h22 | held_out | For a K6/K7 Base Camp outing from Hushe, where is the trekking permit issued, who supplies porters, and does the base-camp route itself require technical climbing?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Hushe`.

Reference: Get the CKNP trekking permit from the Skardu CKNP office; hire porters through Hushe's village porters' association. The Charakusa/K6-K7 base-camp trek takes about eight to ten days and requires no technical climbing for the base camp itself.

Gold chunks: `p044-045-87c4ea0777e3`. Physical PDF pages: [44].

Required groups: `[["p044-045-87c4ea0777e3"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p044-045-87c4ea0777e3` | physical pages [44]

> Hushe is to Baltistan's technical trekking what Minapin is to Hunza's — one road-end village feeding several serious objectives. Route in: Skardu → jeep via Khaplu, Machulo, Kanday, Khaney → Hushe (the highest permanent village in the area, ~3,050m). All multi-day treks above the village require a CKNP trekking permit, issued at the Skardu CKNP office; porters are hired directly from Hushe through the village porters' association. Homestays and one or two basic guesthouses exist in the village itself; everything above it is tent camping. Mobile signal is patchy in Hushe and nonexistent past Saicho junction — same vlogging- connectivity note as Chapursan in Region 1.

`p044-045-87c4ea0777e3` | physical pages [44]

> K6/K7 Base Camp Trek (Charakusa Valley) — this covers "Charkusa Valley Husha" from your original list too: Hushe → Saicho (4-5 hrs) → across the Charakusa Glacier → K6/K7 Base Camp at 4,550- 4,600m. 8-10 days total, no technical climbing needed for the base camp itself — genuinely one of the more accessible "serious" treks in this whole region, similar difficulty tier to Patundas in Hunza. K6 stands 7,282m, K7 stands 6,934m, and you'll

</details>

<details><summary>h23 | held_out | Thalle La and Banak/Branak Khund are easy to mix up. Which valleys does each connect and which is explicitly described as requiring rope, crampons and an ice axe?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Baltistan_Astore`.

Reference: Thalle La links the Shigar Valley with the Khaplu/Hushe area via Bauma Lungma; Banak/Branak Khund runs from Shagarthang on the Skardu side to Gutumsar in Astore and is the difficult route explicitly requiring rope, crampons and ice axe.

Gold chunks: `p045-047-ab32139ef98f`. Physical PDF pages: [46].

Required groups: `[["p045-047-ab32139ef98f"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p045-047-ab32139ef98f` | physical pages [46]

> Connects Shigar Valley to Khaplu/Hushe area, running along the Central Karakoram National Park boundary. The route splits into two passes: Tusserpo La (5,084m, infrequently crossed) and the easier Thallee La (4,572m), both eventually reaching Shigar Valley via Bauma Lungma. A cultural-and-trekking route valued as much for connecting two distinct valley cultures as for the scenery itself.

`p045-047-ab32139ef98f` | physical pages [46]

> Shagarthang is a valley on the Skardu side that also serves as a Deosai access point (4-6 day treks reach the Deosai plains from here), and it's also the starting point for the Banak Pass Trek (also called Branak Khund): Shagarthang (Skardu) → Banak Pass → Gutumsar in Astore Valley, a genuinely difficult route needing rope, crampons, and ice axe — for experienced trekkers only. This is the entry that covers "Shagarthang Trek" from your original list.

</details>

<details><summary>h24 | held_out | For shorter mountain-view alternatives near Baltistan, compare Moses Peak via Barah Broq with Marsur Rock in terms of elevation, glacier travel and outing length.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Baltistan`.

Reference: Barah Broq is around 4,300 m with an optional day hike to Moses Peak at 5,350 m for a K2 view and no glacier travel. Marsur Rock near Hussainabad is around 3,300-3,737 m, a half-day hike with about 600 m gain after a short drive, suitable as a single-day outing.

Gold chunks: `p045-047-ab32139ef98f, p047-049-8dc49f1b20f2`. Physical PDF pages: [47].

Required groups: `[["p045-047-ab32139ef98f"], ["p047-049-8dc49f1b20f2"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p045-047-ab32139ef98f` | physical pages [47]

> Starts from Barah village (Khaplu District, known for apricot orchards), ascends through a gorge to Barah Broq at 4,300m with two alpine lakes ("Blue Lake"), with an optional day-hike to Moses Peak at 5,350m for a K2 viewpoint. Considered the shortest K2-viewpoint trek in the region — a good alternative if the full K2 Base Camp commitment isn't realistic but you still want to see it. No glacier travel required, unlike most K2-area routes.

`p047-049-8dc49f1b20f2` | physical pages [47]

> A sloping rock formation near Hussainabad village, discovered/popularized in 2018, often compared to Norway's Trolltunga, sitting around 3,300-3,737m. About 30-45 min drive from Skardu/Shigar/Khaplu to the trailhead, then a half-day hike with roughly 600m of elevation gain — a genuinely easy, single- day add-on with views over Skardu city, the Indus River, and the Cold Desert.

</details>

<details><summary>h25 | held_out | For a Minimarg permit followed by a Rama outing, which Astore office handles the NOC, how many copies are made, where are copies surrendered, and what jeep leg is described for Rama?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Astore`.

Reference: The Assistant Commissioner's office at the start of Rama Road near Astore lorry depot makes three stamped NOC copies using CNIC and vehicle number; copies go to the Army Mess checkpoint on Deosai Road. Rama Meadows/Lake is about 10-13 km from Astore, roughly 1h40 by jeep on a rough 4x4-only road.

Gold chunks: `p049-051-51be39ff7ee4, p051-053-ff8a6c292dbc`. Physical PDF pages: [50, 51].

Required groups: `[["p049-051-51be39ff7ee4"], ["p051-053-ff8a6c292dbc"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p049-051-51be39ff7ee4` | physical pages [50]

> Correction — Minimarg bike rules: My earlier note that motorbikes aren't permitted was wrong. The actual rule: minimum 150cc bikes are allowed into Minimarg — it's bikes under 150cc and regular cars that get turned away; you need either a 4x4 jeep or a 150cc+ bike. This matters directly for you — your Yamaha YBR 125 is a 125cc, under that threshold, so it wouldn't qualify for entry on this specific stretch even though it's fine for the rest of the route to Astore, Rama Meadows, and the broader Deosai/Astore road network. The zone is still militarized and NOC-gated regardless of vehicle: get the NOC from the Assistant Commissioner's office at the start of Rama Road near the Astore lorry depot — bring your bike/car number and CNIC, they'll type and stamp three copies on the spot, then hand copies over at the Army Mess checkpoint on Deosai Road. If you ride the YBR out there, plan to leave it in Astore and go the last stretch by jeep or a rented/borrowed 150cc+ bike.

`p051-053-ff8a6c292dbc` | physical pages [51]

> What's there: Astore itself sits at about 2,600m (8,500ft), 60km from Gilgit, serving mainly as a jumping-off base. Rama Meadows/Lake is about 10-13km from Astore, roughly 1h40 by jeep on a rough 4x4-only road — a popular easy add-on for camping and stargazing, not on your original list by name but effectively part of the same trip since it's this close to Astore.

</details>

<details><summary>h26 | held_out | Distinguish the Tattu and Tarashing approaches to Nanga Parbat: what transport-to-walking sequence and trek duration does the guide give for each?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Nanga_Parbat`.

Reference: For Fairy Meadows, take a local 4x4 from Raikot Bridge to Tattu, 90-120 minutes, then walk two to three hours to Fairy Meadows. For the Rupal side, jeep from Astore to Tarashing in about two hours, then trek via Tarashing Glacier's lateral moraine and Rupal village toward Herligkoffer Base Camp, a three-to-four-day round trip from Tarashing.

Gold chunks: `p051-053-ff8a6c292dbc, p053-054-a26a1670d604`. Physical PDF pages: [52, 53].

Required groups: `[["p051-053-ff8a6c292dbc"], ["p053-054-a26a1670d604"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p051-053-ff8a6c292dbc` | physical pages [52]

> Route: Islamabad → Raikot Bridge on the KKH (~540km, 10-12 hours) → 4x4 jeep from Raikot Bridge to Tattu village (15-16km, 90-120 min on a narrow single-lane track, PKR 12,000-15,000 per jeep for up to 6 people) → trek 3-5.5km on foot (2- 3 hours) to Fairy Meadows.

`p053-054-a26a1670d604` | physical pages [53]

> Route: Astore → Tarashing village (~30km, 2 hours by rough unpaved jeep road, last village in Rupal Valley) → trek in via the Tarashing Glacier's lateral moraine → Rupal village → Herligkoffer Base Camp (also called Rupal Base Camp, named after German mountaineer Karl Herligkoffer).

`p053-054-a26a1670d604` | physical pages [53]

> Distance/elevation: About 26-30km round trip from Tarashing, 3-4 days, reaching Herligkoffer Base Camp at ~3,500-3,550m — Tarashing itself sits at 2,900-2,911m.

</details>

<details><summary>h27 | dev | What uncertainties should I retain, rather than smooth over, when planning Morro Meadows and Takhto Sar in Palas Valley?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Kohistan`.

Reference: Morro access-village names and route details vary; reported walks are roughly 7-8 km with about 1,900 m gain and three to seven hours. The guide lacks firm distance/elevation figures for Takhto Sar, so final logistics need local confirmation rather than invented measurements.

Gold chunks: `p054-057-7e1519e0731e`. Physical PDF pages: [56].

Required groups: `[["p054-057-7e1519e0731e"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p054-057-7e1519e0731e` | physical pages [56]

> Morro (Morro/Morroo) Meadows: From Pattan, a jeep track leads to the village of Khalyar/Shiryal/Mudu (sources vary on the exact village name and route details — this is a genuinely under-documented area), then a trek of roughly 7- 8km with about 1,900m of cumulative elevation gain, taking 3-7 hours depending on the exact route and source. Locals are described as helpful with guiding and porters, though this is not a formal tourism setup — expect to arrange things informally on arrival rather than booking anything in advance.

`p054-057-7e1519e0731e` | physical pages [56]

> Takhto Lake (also called Takhto Sar Lake): Also in the Palas Valley cluster, described as one of the least-explored alpine lakes in Pakistan — visited by at least one Pakistani motorbike tour operator specifically as an exploratory trip, which tells you how off the beaten path this still is. I couldn't find hard distance/elevation figures for this one specifically; treat it as bundled with the Morro Meadows trip into the same general Palas Valley area, and expect to figure out final logistics locally.

</details>

<details><summary>h28 | held_out | Match Bashkiri I, II and III to the Naltar lake names, and explain the spacing and color description of the first two.</summary>

Status: **verified**. Category: `difficult_paraphrase`. Region: `Naltar`.

Reference: Bashkiri I is Satrangi, the seven-colored lake whose hues come from moss and underwater vegetation. Bashkiri II is Blue Lake, about one km from Satrangi; Bashkiri III is Feroza Lake.

Gold chunks: `p057-058-1e3220f30d27`. Physical PDF pages: [58].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p057-058-1e3220f30d27` | physical pages [58]

> The lakes: Collectively called the Naltar Lakes or Bashkiri Lakes — Satrangi Lake (Bashkiri I, the famous "seven-colored" one, named for the mix of hues from moss and underwater vegetation), Blue Lake (Bashkiri II, 1km from Satrangi), and Feroza Lake (Bashkiri III), roughly 12-17km from Naltar Bala depending on source.

</details>

<details><summary>h29 | held_out | Nomal and Sassi are not interchangeable gateways. Which lake valley does each serve, and how does the final access to Naltar Lakes differ from reaching Kutwal Lake?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Gilgit`.

Reference: Nomal is the turnoff toward Naltar Bala, beyond which the Naltar lakes require a separate rough 4x4 leg. Sassi is the Gilgit-Skardu-road gateway for Haramosh/Kutwal; after jeep access, Kutwal entails roughly two to three days of one-way trekking via Iskere.

Gold chunks: `p057-058-1e3220f30d27, p058-060-fa9822ff4f99`. Physical PDF pages: [57, 58, 59].

Required groups: `[["p057-058-1e3220f30d27"], ["p058-060-fa9822ff4f99"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p057-058-1e3220f30d27` | physical pages [57]

> Route: Gilgit → Nomal village (turn off the KKH) → Naltar Bala (Upper Naltar), about 34-40km, 1.5-2 hours. The road to Naltar Bala itself is manageable; the lakes beyond require a separate 4x4 jeep leg — old Willys jeeps with reinforced suspension are the standard local vehicle for this stretch, and taking your own vehicle (bike included) isn't advisable for the final rocky, boulder-strewn section.

`p058-060-fa9822ff4f99` | physical pages [58]

> Route: Gilgit → Sassi village (on the Gilgit-Skardu road, roughly 53-66km / about 1 hour), then a 4x4 jeep track further into the valley, then trek in. Sassi

`p058-060-fa9822ff4f99` | physical pages [59]

> Distance/elevation: Kutwal Lake sits at roughly 3,300-3,310m, reached via 2-3 days of trekking one-way from Sassi, typically via Iskere village first (4-5 hours) then on to the lake (5-6 hours). Difficulty: Moderate — genuinely suitable for beginners with basic fitness, no technical sections. A good "next step up" trek, comparable in accessibility to Rakaposhi Base Camp in Region 1.

</details>

<details><summary>h30 | held_out | Contrast Musa ka Musalla's Shinkiari route with Chamra Peak's Shingri Top route: what are the main stages, and which limitation concerns water versus glacier ropes?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Mansehra_Kaghan`.

Reference: Musa ka Musalla goes Shinkiari-Manda Gucha-Jachha-Dhor-Khori/Gali-summit, usually three to four days, with water only in the first quarter. Chamra goes via Shingri Top at 3,800 m and forward base camp around 4,000 m to its 4,670 m summit; operators fix ropes on the glacier section.

Gold chunks: `p062-063-cf8d655b6812, p067-069-ead8a5550d3a`. Physical PDF pages: [63, 67].

Required groups: `[["p062-063-cf8d655b6812"], ["p067-069-ead8a5550d3a"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p062-063-cf8d655b6812` | physical pages [63]

> Musa ka Musalla (deferred from Region 3): 4,060- 4,080m, at the junction of Siran Valley and Kaghan Valley, in Mansehra District — technically its own trek rather than a Kaghan-proper destination. Standard route: Shinkiari → Manda Gucha → Jachha → Dhor → Khori/Gali → summit, typically 3-4 days, though a faster single-day push exists from Balakot with about 1,800m elevation gain in one push if you're already acclimatized. There's a shrine at the summit associated with a shepherd named Musa. Water is only available in the first quarter of the trek — carry enough.

`p067-069-ead8a5550d3a` | physical pages [67]

> What it is: A 4,670m peak in Naran Valley — genuinely Kaghan-region, not Neelum as I'd guessed while flagging it earlier. Route: Islamabad → Kagan Valley (overnight drive) → jeep to Shingri Top (3,800m, overnight) → trek to forward base camp (4,000m) → summit push to Chamra Peak (4,670m) with fixed ropes on the glacier section → back down to Shingri Top → return to Islamabad via Balakot. 4 days total. Difficulty: Technical enough that operators fix ropes on the glacier for the summit push — this is a

</details>

<details><summary>h31 | held_out | Compare the roadheads for Ratti Gali and Chitta Katta: which gateway/jeep stop and final walking stages does the guide describe?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Neelum`.

Reference: Ratti Gali is approached via Dowarian with a jeep to base camp, then a 40-minute to two-hour hike. Chitta Katta is in Shounter Valley and is approached from Kel by about 20 km of jeep travel to Domel/Domail followed by a five-km trek, commonly a four-day camping trip.

Gold chunks: `p064-065-eeaf0cd09563`. Physical PDF pages: [64, 65].

Required groups: `[["p064-065-eeaf0cd09563"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p064-065-eeaf0cd09563` | physical pages [64]

> Ratti Gali Lake: About 106-120km from Muzaffarabad via Dowarian, 3,683-3,698m. Jeep to base camp (PKR 5,000-7,000 round trip) then a 40- minute to 2-hour hike to the lake itself. Moderate, beginner-friendly.

`p064-065-eeaf0cd09563` | physical pages [64]

> Chitta Katta Lake: In Shounter Valley, Tehsil Sharda, at 4,100m/13,500ft — reached from Kel via a ~20km jeep ride to Domel/Domail then a 5km

`p064-065-eeaf0cd09563` | physical pages [65]

> trek, typically run as a 4-day round trip with camping. Sits near Mount Hari Parbat, sacred to some Hindu visitors historically (associated with Lord Shiva/Kailash). Described as "a junction of Neelum, Naran, and Skardu" geographically and notably close to the Indian-administered Kashmir border.

</details>

<details><summary>h32 | dev | Could I substitute a Pakistan-side Neel Fairy/Haveli outing for Gurez or Satsar without changing border arrangements? Identify the access difference documented in the guide.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Kashmir`.

Reference: Neel Fairy is in Forward Kahuta, Haveli, AJK, approached via Rawalakot-Haveli-Bashan/Suli and a final two-to-three-hour hike. Gurez and Satsar are listed across the LOC in Indian-administered Kashmir, approached from Srinagar/Razdan or Sonamarg/Naranag respectively, not by a Pakistan-side road trip.

Gold chunks: `p065-067-d4e1efea674e`. Physical PDF pages: [65, 66, 67].

Required groups: `[["p065-067-d4e1efea674e"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p065-067-d4e1efea674e` | physical pages [65]

> What it is: In Forward Kahuta, Haveli District, Azad Kashmir — genuinely Pakistan-administered (not to

`p065-067-d4e1efea674e` | physical pages [66]

> Gurez Valley (and Tulail Valley) — Bandipora District, J&K, India, about 123km from Srinagar, reached via Razdan Pass.

`p065-067-d4e1efea674e` | physical pages [67]

> Satsar Mala Lakes — Ganderbal District, J&K, India, part of the Kashmir Great Lakes Trek, reached from Sonamarg or Naranag.

</details>

<details><summary>h33 | held_out | Gunnar Sar/Gujjar Sar and Chamra Peak were assigned to different areas in earlier notes. How does the corrected guide distinguish their starting area, trip duration and route character?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Kaghan_Astore_Kashmir`.

Reference: Chamra is a four-day technical Naran/Kaghan objective via Shingri Top with a glacier summit section. Gunnar Sar is probably Gujjar Sar, a six-day Astore-to-Kashmir/Neelum traverse from Gorikot via Damni and other lakes with a Taobat-side detour, not a simple Naran peak hike.

Gold chunks: `p067-069-ead8a5550d3a`. Physical PDF pages: [67, 68].

Required groups: `[["p067-069-ead8a5550d3a"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p067-069-ead8a5550d3a` | physical pages [67]

> What it is: A 4,670m peak in Naran Valley — genuinely Kaghan-region, not Neelum as I'd guessed while flagging it earlier. Route: Islamabad → Kagan Valley (overnight drive) → jeep to Shingri Top (3,800m, overnight) → trek to forward base camp (4,000m) → summit push to Chamra Peak (4,670m) with fixed ropes on the glacier section → back down to Shingri Top → return to Islamabad via Balakot. 4 days total. Difficulty: Technical enough that operators fix ropes on the glacier for the summit push — this is a

`p067-069-ead8a5550d3a` | physical pages [68]

> What it is: A pass connecting Astore to the Kashmir/Neelum (Taobat) side, threading past a cluster of little-known lakes: Damni Lake, Dhiman Lake, Gujjar Sar Lake, Adhra Lake, Dalia Lake, and Arwa Lake — the pass itself and Adhra/Dalia Lakes sit above 4,000m, with views of Kashmir on one side and Astore on the other from the top. Route: Islamabad → Astore (Gorikot camp) → trek to Damni Lake on the Kashmir-Astore border, past two waterfalls and a "seven lakes" area → explore Gujjar Sar/Damni/Dhiman Lakes → cross Gujjar Sar Pass with a short detour toward the Taobat side of Kashmir → Adhra and Dalia Lakes (4,000m+) → Arwa Lake → descend to Shardu → Chilas or Besal → Naran → Babusar Pass → Islamabad. 6 days total, genuinely covers ground between two regions on this list in one trip.

</details>

<details><summary>h34 | dev | After reaching Thal, spell out the staged journey to Katora Lake through Takki Banda and Jahaz Banda, including overnight location and facilities I should not assume at the lake.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Upper_Dir`.

Reference: Jeep from Thal to Taki/Takki Banda for about 1.5 hours, then walk three to five hours to Jahaz Banda Meadows for camping and another three to four hours to Katora Lake. Do not expect electricity or real food options at the lake; carry supplies, power bank and flashlight.

Gold chunks: `p071-072-cc358ad79e0e`. Physical PDF pages: [71, 72].

Required groups: `[["p071-072-cc358ad79e0e"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p071-072-cc358ad79e0e` | physical pages [71]

> Route: Islamabad → Swat Motorway to Chakdara → N-45 through Timergara and Dir → Thal (last town for normal vehicles), ~370-460km, 8-10 hours → jeep from Thal to Taki/Takki Banda, 16km rough track, ~1.5 hours, PKR 5,000 one-way or PKR 10,000-12,000 round trip with overnight → trek 3-5 hours to Jahaz Banda Meadows (camping) → further 3-4 hours to Katora Lake.

`p071-072-cc358ad79e0e` | physical pages [72]

> Practical note: no electricity or real food options at Katora Lake itself — carry supplies, and bring a power bank and flashlight. This is genuinely remote-feeling despite being a well-known name.

</details>

<details><summary>h35 | held_out | A photographer has confused Spin Khwar with Kooh Lake. Which connector needs a guide, and which separate lake uses the Blue Water Point approach and early-morning color window?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Swat`.

Reference: The Kandol-to-Spin-Khwar connector is the one for which a guide is specifically recommended. Kooh is Andrab Lake in Anakar Valley, reached via Blue Water Point with a seven-to-eight-hour return trek; arrive around 9-10 am for the color contrast.

Gold chunks: `p072-074-249d8c96c2fc`. Physical PDF pages: [72, 74].

Required groups: `[["p072-074-249d8c96c2fc"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p072-074-249d8c96c2fc` | physical pages [72]

> What it's like: Large green-shaded lake surrounded by snow-covered mountains, often compared to a smaller Saiful Muluk but far less crowded. Moderate-to-difficult day hike, doable without a

`p072-074-249d8c96c2fc` | physical pages [74]

> Andrab Lake ("Kooh Lake"): 10,800-11,000ft in Anakar Valley near Kalam, known for visibly shifting from blue to jade-green as the light changes through the day. Route: Kalam Bazaar → jeep 30-45 min to Blue Water Point, Ankar village → 7-8 hour return trek. Arrive by 9-10am for the best color contrast if photography is the goal.

</details>

<details><summary>h36 | held_out | Izmis and Sheitan Gawt were previously misplaced. Name each actual Swat gateway and compare the walking commitment and camping requirement.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Swat`.

Reference: Izmis is in the Utror cluster, with jeep access to Loypanrghalay and about three to six hours of trekking. Sheitan Gawt is above Kedam near Bahrain, a 12-15-hour trek with no guesthouses en route, so camping is mandatory.

Gold chunks: `p072-074-249d8c96c2fc, p074-076-784ce56e21b3`. Physical PDF pages: [73, 75].

Required groups: `[["p072-074-249d8c96c2fc"], ["p074-076-784ce56e21b3"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p072-074-249d8c96c2fc` | physical pages [73]

> Izmis Lake: Southwest of Utror valley, above the treeline — "Izmis" means "caves" in Kohistani, named for natural caves around the lake. Jeep from Utror to Loypanrghalay, then a 3-6 hour trek (one source gives a 13km trail from an 11,230ft start point).

`p074-076-784ce56e21b3` | physical pages [75]

> Sheitan Gawt (Shaitan Gwat) Lake: Considered the largest lake in Swat, 13,500ft, in alpine pastures above Kedam village near Bahrain. A genuinely long trek — 12-15 hours depending on pace, no guesthouses en route so camping is mandatory, and locals in Kedam itself weren't always well- informed on the route when one trekking blog visited — this is a genuinely under-visited lake even by Swat's already-remote standards. Route in starts via Kedam, just past Bahrain on the Kalam road.

</details>

<details><summary>h37 | held_out | Distinguish Zamalo Lakes from the Golen-Bashkargol-Kumrat traverse by starting area, high point/lake elevation and sensible trip shape.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Swat_Chitral_Dir`.

Reference: Zamalo starts at Paloga, climbs to Jaba at 3,700 m then to lake 3 around 4,300 m, and is better paced as a three-day out-and-back with a return to the parked vehicle. The Chitral-Dir traverse crosses Thallo Pass at 4,180 m via Bashkargol Lake at 3,652 m and is generally six to seven days with full camping/guide support.

Gold chunks: `p076-078-8491e93c619d`. Physical PDF pages: [76, 77, 78].

Required groups: `[["p076-078-8491e93c619d"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p076-078-8491e93c619d` | physical pages [76]

> What it is: A multi-day traverse starting in the Golen Gol valley of Chitral, crossing Thalo/Thallo Pass (4,180m), passing Bashkargol Lake, and ending in Kumrat Valley — a genuine Chitral-to-Dir crossing, one of the more remote and less- documented multi-day routes on your entire list. Route/days: Thal → Jandrai (gateway village) → Kala Chashma → Shahzore Banda → Zaghi Chatt Lake (camp) → cross Thallo Pass → Bashkargol

`p076-078-8491e93c619d` | physical pages [76]

> Bashkargol Lake detail: confirmed at 3,652m, a large lake in Chitral district described as looking like a shore or sea in the evening and a still mirror in the morning, about 24km from Sor Laspur settlement on a rugged, steep trail — this is the lake at the heart of this traverse, and can also be reached directly from Sor Laspur without the full Kumrat-side crossing if you just want the lake itself.

`p076-078-8491e93c619d` | physical pages [77]

> Route: Paloga village (~2,500m, just short of Mahodand) → steep, all-ascent trek to Jaba/Jabba summer settlement at the base of Falaksar Peak (3,700m) — a demanding 1,200m single-day climb, with a possible camping spot partway up at the edge of the forest if you'd rather split it over two days.

`p076-078-8491e93c619d` | physical pages [77]

> The lakes: From Jaba, 3-4 more hours to the first three lakes. Zamalo Lake 3 is the biggest and most striking, at 4,300m — a further 600m climb from Jaba. A few more lakes exist above the third one for those with time and stamina to push further.

`p076-078-8491e93c619d` | physical pages [78]

> Difficulty: Genuinely tough for a weekend trek — one trekking account describes doing the whole out-and-back (Paloga → Jaba → lakes → back to Paloga) in essentially two hard days, which they don't recommend unless time-constrained like they were. A 3-day pace with the forest-edge camping option is more sensible.

</details>

<details><summary>h38 | held_out | When comparing an old Chitral road report with a newer one, what did the Lowari Tunnel replace, and how should I distinguish the tunnel route from the old summer pass crossing?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Chitral`.

Reference: The Lowari Tunnel, opened in 2017 with combined length about 10.4 km, replaced the old Lowari Pass on the Dir-Drosh-Chitral route. The tunnel is the default, whereas the 3,118 m old pass is a rough scenic alternative usable in summer, described as July-September.

Gold chunks: `p078-080-77062c50650d, p080-081-4717074613d0`. Physical PDF pages: [79, 80].

Required groups: `[["p078-080-77062c50650d"], ["p080-081-4717074613d0"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p078-080-77062c50650d` | physical pages [79]

> By air: PIA flies Islamabad → Chitral in about 50 minutes, May-October mainly, schedules genuinely shift with Hindu Kush weather and visibility — always have a road backup plan. By bike/road: Islamabad → M-1 → Swat Motorway/Sher Khan interchange → Chakdara → Timergara → Dir → Lowari Tunnel → Drosh → Chitral, about 400-500km, 9-14 hours depending on source and stops. The Lowari Tunnel (10.4km combined length, opened 2017) replaced the old Lowari Pass and cut what used to be a 14-16 hour journey down significantly — this is a genuinely transformed route compared to older trip reports you might find online.

`p080-081-4717074613d0` | physical pages [80]

> The old pass sits at 3,118m and is only usable in summer — some jeep operators and locals still cross it directly (a rough but scenic alternative) when the tunnel is congested or for the views themselves, July-September only. The tunnel is now the default for anyone not specifically chasing the pass-crossing experience.

</details>

<details><summary>h39 | dev | If choosing among Bumburet, Rumbur and Birir for easier visitor infrastructure, which valley is most developed and what road/accommodation evidence supports that choice?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Kalash`.

Reference: Bumburet has the most reliable/developed road and over 30 hotels. Rumbur and Birir have narrower, steeper, more weather-exposed tracks and roughly six and five hotels respectively, so Bumburet is the most set up for visitors in the guide.

Gold chunks: `p081-083-d64cf441cb82`. Physical PDF pages: [81, 82].

Required groups: `[["p081-083-d64cf441cb82"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p081-083-d64cf441cb82` | physical pages [81]

> Route from Chitral: Chitral → Ayun (turn-off village) → jeep track into whichever valley, about 35-45km total, 2-3 hours. Bumburet's road is the most reliable/developed; Rumbur and Birir's tracks are narrower, steeper, and more weather-exposed.

`p081-083-d64cf441cb82` | physical pages [82]

> Accommodation: Chitral town has 40+ hotels; Bumburet has 30+, mostly smaller; Rumbur about 6, Birir about 5 — Bumburet is clearly the most set up for visitors of the three.

</details>

<details><summary>h40 | held_out | Are the Shah Jinali-Thui crossing and Zani/Zain Pass the same Chitral-to-GB itinerary? Give the linked valleys for the first and the mountain approach for the second.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Chitral_Ghizer`.

Reference: No. Shah Jinali links Rich Gol/Turikho to Yarkhun and Thui continues into Yasin Valley, Ghizer, crossing the Hoghost Bar/Aghost Bar Glacier. Zani/Zain is on Uthul-Zani-Shagrom near the Tirich Glacier, part of the Tirich Mir Base Camp approach.

Gold chunks: `p083-085-e588f14f58f1, p085-087-881e3768251c`. Physical PDF pages: [84, 85].

Required groups: `[["p083-085-e588f14f58f1"], ["p085-087-881e3768251c"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p083-085-e588f14f58f1` | physical pages [84]

> What it is: A combined trek in the Hindu Raj range crossing from Upper Chitral into Gilgit-Baltistan — Shah Jinali Pass (called "the King's Polo Ground" locally, 4,259m) connects Rich Gol/Turikho valley with Yarkhun, and Thui Pass (4,499m-4,500m) continues on from Yarkhun into the Yasin Valley, Ghizer District. Route: Chitral → Turikho/Rich Gol valley (jeep) → trek through Shah Jinali Pass → down into Yarkhun valley → cross the Hoghost Bar/Aghost Bar Glacier → Thui Pass → descend into Yasin Valley → jeep to Gilgit. Genuinely one continuous multi-day traverse rather than two separate day trips. Difficulty: Moderately challenging — the two glacier/pass crossings are the demanding sections, otherwise gentle alpine meadow walking; Thui Pass "is just passable" and needs stamina and good health rather than technical climbing skill.

`p085-087-881e3768251c` | physical pages [85]

> What it is: A 3,840-3,886m pass on the Tirich Mir Base Camp trek route, on the Uthul → Zani Pass → Shagrom stretch near the foot of the Tirich Glacier (matching what I found while researching Region 4's misattribution).

`p085-087-881e3768251c` | physical pages [85]

> Context: Tirich Mir (7,708m) is the highest peak in the Hindu Kush and dominates the Chitral skyline — Zani Pass is part of the approach trek toward its base camp rather than a standalone destination, so plan it as one leg of a longer Tirich Mir-area trip if it interests you, not a there-and-back day trip.

</details>

<details><summary>h41 | held_out | For the revived Munro Trail, identify the original endpoints and two familiar forest/top landmarks, and distinguish the complete trek from the shorter Shinkiari option.</summary>

Status: **verified**. Category: `multi_fact`. Region: `Siran_Kaghan`.

Reference: The original horse trail links Kund in Siran Valley with Kamal Ban near Naran, passing Sharan Forest and Manshi Top. The full trail is 66 km and multi-day; Shinkiari to Kund Bangla is an approximately 20-km day-hike section.

Gold chunks: `p088-090-7fe56cb01062, p090-092-d469daea2cf5`. Physical PDF pages: [90, 91].

Required groups: `[["p088-090-7fe56cb01062"], ["p090-092-d469daea2cf5"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p088-090-7fe56cb01062` | physical pages [90]

> What it is: A 66km British-era trail built 1900-1905 by A.V. Munro, a Forest Conservator in British India, originally a horse trail connecting Kund (Siran Valley) to Kamal Ban near Naran (Kaghan Valley) — recently revived and expanded by the KP Forest Department with new tourist facilities.

`p088-090-7fe56cb01062` | physical pages [90]

> Genuinely nice connection to your visited list: the trail passes directly through Sharan Forest and Manshi Top — both already on your visited list from the Kaghan region. So you've technically already stood on part of this trail without necessarily doing the full thing. Route: Kund Bangla (2,250m, Siran side) → Galya/Darbei → Nadi Bangla → Naga Forest → Mala Meadows → Sharan Forest → Manshi Top → Kamal Ban Forest (Kaghan side).

`p090-092-d469daea2cf5` | physical pages [91]

> either — similar to how the Gujjar Sar Pass and Golen-Bashkargol-Kumrat traverse bridged other regions earlier in this document. Difficulty: Described as one of the more challenging trails in the Mansehra area — the full 66km is a multi-day undertaking, though shorter day-hike sections (like Shinkiari to Kund Bangla, ~20km) are doable on their own.

</details>

<details><summary>h42 | held_out | Which Lalazar is actually on the Nathiagali-Mushkpuri trail, and how does the guide compare Miranjani with Mushkpuri for length, crowds and winter snow?</summary>

Status: **verified**. Category: `multi_fact`. Region: `Galliyat`.

Reference: It is the small Lalazar wildlife park near Nathiagali, not the Lalazar meadows near Naran. Miranjani is the longer, less crowded and higher hike, so it retains more winter snow than Mushkpuri.

Gold chunks: `p088-090-7fe56cb01062, p087-088-8428f4e31885`. Physical PDF pages: [88, 89].

Required groups: `[["p088-090-7fe56cb01062"], ["p087-088-8428f4e31885"]]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

`p088-090-7fe56cb01062` | physical pages [89]

> Important distinction: this is a different, smaller Lalazar from the famous Lalazar meadows near Naran in Kaghan Valley (already touched on in Region 5) — don't confuse the two when researching further.

`p088-090-7fe56cb01062` | physical pages [89]

> What it is: A small wildlife park at about 9,000ft, sitting right on the Nathiagali-to-Mushkpuri trail — about 1km up from Nathiagali, which you'd have passed on the way to Mushkpuri already if you took that specific route.

`p087-088-8428f4e31885` | physical pages [88]

> Comparison to Mushkpuri (which you've done): Miranjani is the longer hike of the two but noticeably less crowded; it's also higher, so it holds more snow in winter.

</details>

<details><summary>h43 | held_out | Is Lowari Tunnel open to vehicles at this exact minute after today's storm?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h44 | held_out | Which Islamabad-Skardu flights were cancelled this morning and what is the next confirmed boarding time?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h45 | held_out | Are two shared jeep seats available from Nomal to the Naltar lakes in the next thirty minutes?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h46 | held_out | Give the measured SCOM download speed in Chapursan tonight in Mbps.</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h47 | held_out | What is the confirmed maximum water depth of Takhto Sar Lake in metres?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h48 | held_out | List every landslide reported on the Jaglot-Skardu road in the past two hours.</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h49 | held_out | Give independently confirmed GPS coordinates for the lake named Sheerin Maidon, without substituting Batura Lake.</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>

<details><summary>h50 | held_out | What exact dates have officials confirmed for next year's Choimus festival?</summary>

Status: **verified**. Category: `unanswerable`. Region: `cross_region`.

Reference: Unsupported; refuse using the PDF-only contract.

Gold chunks: `None`. Physical PDF pages: [].

Required groups: `[]`.

Independently reviewed and explicitly approved by the user. Local source, page, split, and evidence-group validation passed.

</details>
