# Future research gaps

These are research tasks, not reasons to reject a useful recommendation. Scenic
destinations may suit couples or families through explained inference. A missing
comfort rating does not disqualify a destination. No new web facts were added to
the profiles, PDF, index or evaluation references.

## Already in the PDF

- [x] Add Miacher Kho's approximately 30-minute walk from parking and scenery,
  physical p35, chunk `p033-035-97d114c1c3a8`. Added to the draft Hunza/Nagar
  profile with explicit Nagar scope; this is not step-free certification.
- [x] Add the named Fairy Meadows cabin, twin-share and meal example, p53,
  `p051-053-ff8a6c292dbc`. Added as a guide estimate, not verified comfort/privacy.
- [ ] Consider Hunza budget guesthouses and shared-bathroom qualification,
  p20-21, `p020-022-8d8b2710273b`, for meaningful budget/amenity comparisons.
- [ ] Consider Chapursan homestays, `p026-028-3af709bd9d8f`, and Shigar's heritage
  hotel, `p040-042-e594be504c6e`. These illustrate discovery outside the initial
  12 profiles; neither should be excluded for lacking a profile.
- [ ] Add selected destination-specific seasons, trek durations, guide advice
  and lighter local activities when useful. Preserve local scope instead of
  assigning one difficulty or season to a whole region.
- [ ] Reuse existing emergency/fuel/transport advice when relevant. The PDF has
  emergency contacts; the gap is destination-specific access to assistance,
  not a complete absence of safety information.

## Not documented sufficiently in the available guide

The reviewed guide does not provide the following dependable comparison data.
This is absence of documented evidence, not proof that a facility does not exist.

- [ ] Couples: property-specific privacy, room setting/noise, private bathroom
  details and quieter activity options. A honeymoon marketing label is optional.
- [ ] Families: family/connecting rooms, cot/extra-bed arrangements, child-suitable
  activities with age/effort information and supervised facilities where relevant.
- [ ] Limited mobility: measured walking distances, gradients/surfaces, steps,
  parking-to-entrance access, rest stops, toilets and accessible rooms/bathrooms.
  Road arrival or a chairlift alone does not answer these questions.
- [ ] Comfort: property-specific heating, reliable hot water/power, meals and
  room arrangements. Hunza category-level bathroom/hot-water information exists,
  but it is not a property-by-property inventory.
- [ ] Relaxation/beginner travel: comparable exertion, rest opportunities,
  overnight arrangements and approach effort. Do not equate beginner-friendly
  with no walking, no altitude exposure or guaranteed comfort.
- [ ] Budgets: comparable per-person/per-room and per-day bases, inclusions,
  group size and observation date. Existing scattered guide prices cannot
  establish a reliable all-inclusive moderate-budget total for every region.

## Requires current verification

Use official/operator sources as research leads, not automatically trusted PDF
evidence. Record the specific page/contact, observation date, scope and source
version; review before adding any factual claim. No forms or bookings were submitted.

| Information | Source to consult | Limit |
|---|---|---|
| Forecasts and weather warnings | [Pakistan Meteorological Department](https://pmd.gov.pk/) links to its [live platform](https://weather.gov.pk/) | A forecast does not certify trail or road access. |
| Highway advisories | [NHMP travel advisory](https://beta.nhmp.gov.pk/TA/Public/ViewTravel.aspx) | Coverage is not every local mountain/jeep road. Homepage fetch timed out during this review. |
| Regional notices, local contacts and seasonal access | [GB Tourism Department](https://visitgilgitbaltistan.gov.pk/) and [KPCTA Visit KP](https://kptourism.com/visit) | Confirm dates and exact destination; a tourism description is not a current opening notice. |
| Hotel rooms, amenities, rates and availability | Property's own site/reservations team, for example [Serena Khaplu Palace](https://www.serenahotels.com/khaplu-palace) | Verify the actual room and dates; marketing language does not certify accessibility/privacy. |
| Flights, timetables and fares | Airline/operator's own booking channel, for example [PIA](https://www.piac.com.pk/) | PIA page was search-visible but direct fetch returned 403; no live schedule was verified. |
| Local transfers, parking, permits and last-mile conditions | Relevant district/tourism authority and named local operator/property | Ask about the exact route/date/vehicle. Do not generalize a statement to an entire valley. |

These source links were checked on 2026-10-22 solely to identify verification
channels. No current forecast, permission, tariff or availability claim was imported.

## Minimal expansion contract

The catalog keeps stable destination `id` values independent of source wording
and chunk IDs. Each fact has a free-form `attribute`, exact `quote` and heading
`context`, a named `subject` and `scope_note`, original chunk/page references,
`chunk_sha256`, and a `source_version` key. Root `source_versions` records the
document fingerprint and `source_type`. Unknowns remain descriptive, not a
required-completeness checklist. Current records are owner-verified for the controlled development pilot only;
this is not approval of current travel accuracy or production readiness.

For a future PDF edition, add a source-version record and update/add only affected
facts and references against its reviewed indexed passages. Keep destination IDs
stable. The current workflow needs no new intent routes, destination lookup rules,
comparison code or model. Existing chunk fingerprints still detect stale evidence;
the document hash is provenance, not a requirement to ship the PDF at runtime.

Optional future source types/URIs can be recorded in the registry without treating
them as PDF facts. This does **not** implement web ingestion or non-PDF citations.
Such sources would first need reviewed stored passages and an appropriate source
display adapter; the intent/retrieval/comparison graph need not be rewritten.
Do not edit/rebuild the protected original index as part of these reference updates.
