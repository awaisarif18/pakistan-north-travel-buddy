# Answer quality: manual source review

Review date: 2026-10-17. Model: `gemini-3.8-flash`. Reviewer: coding assistant comparing answers directly with the original PDF and stored source metadata. No additional LLM judge or evaluation framework was used.

Five representative answerable cases cover fuel, Skardu transport, Neelum trekking, Chitrali food, and a multi-fact transport/Deosai question. All five existing negative cases q21-q25 are included.

Eight answers were generated in this run. Matching saved chatbot outputs for q01 and q21 were reused with their provenance disclosed to avoid duplicate generation calls. Answerable cases reused audited top-five passages without rerunning retrieval evaluations. Four newly tested negative questions used normal chatbot retrieval and added four query embeddings; no document embedding was regenerated.

| Observation | Result |
|---|---|
| Answerable factual consistency with PDF | 5/5 pass |
| Answerable completeness for requested facts | 5/5 pass |
| Answerable citation support | 5/5 pass |
| Appropriate refusal of unanswerable questions | 5/5 pass |
| Failures observed | 0 |

These are observations on ten selected responses, including two saved outputs. They are not a general answer-accuracy or safety guarantee. No stochastic repeat runs were performed. The audited retrieval metrics and artifacts were not rerun or changed.

The page ranges are accurate to the stored chunks but often broader than the exact source sentence. All five negative answers used the fixed refusal without fabricated citations. The application displays its existing warning about outdated prices, schedules, and conditions.

## Responses and source checks

### q01: Where should I refuel before traveling to Khunjerab Pass?

Origin: Saved earlier chatbot output, same model and prompt; no new generation call.

> Before traveling to Khunjerab Pass, you should fill up completely in Sost, as it is the last Pakistani town before the border with reliable fuel and your final opportunity to refuel. The 75- to 90-kilometer one-way stretch from Sost to Khunjerab Pass has no fuel available at all. Earlier along the route, it is also recommended to fill up in Karimabad or Aliabad before heading up-valley toward Sost and Khunjerab, as Passu has limited options. [PDF pages 6-8]

Review status: **pass**. Factual consistency: pass; completeness: pass; citation support/refusal: pass.

Source page 7 confirms Sost as the last fuel stop, no fuel on the 75-90 km one-way leg, and limited Passu options. The extra Karimabad/Aliabad guidance is also supported.

Original physical PDF pages inspected: 7.

Cited chunk metadata:

- `p006-008-4850ae1f4334`: PDF pages 6-8.

### q03: What fare range does the guide give for NATCO buses from Islamabad/Rawalpindi to Skardu?

Origin: New generation using saved top-five evaluation passages.

> The guide estimates that direct NATCO bus fares from Islamabad/Rawalpindi to Skardu range from approximately PKR 4,630 to PKR 5,500, depending on the bus class. [PDF pages 37-39; PDF pages 10-14]

Review status: **pass**. Factual consistency: pass; completeness: pass; citation support/refusal: pass.

The page 11 table and page 38 prose both give PKR 4,630-5,500. The answer includes the bus-class qualification and calls the fare an estimate.

Original physical PDF pages inspected: 11, 38.

Cited chunk metadata:

- `p037-039-63413879f3c2`: PDF pages 37-39.
- `p010-014-0aced0690245`: PDF pages 10-14.

### q07: How do you reach Ratti Gali Lake from its base camp, and how long is that final leg?

Origin: New generation using saved top-five evaluation passages.

> From its base camp, Ratti Gali Lake is reached by hiking. This final leg takes approximately 40 minutes to 2 hours and is considered a moderate, beginner-friendly hike. [PDF pages 64-65]

Review status: **pass**. Factual consistency: pass; completeness: pass; citation support/refusal: pass.

Page 64 specifies a 40-minute to two-hour hike after the base camp and calls it moderate/beginner-friendly. Both requested facts are present despite the gold passage ranking third in the audited retrieval.

Original physical PDF pages inspected: 64.

Cited chunk metadata:

- `p064-065-eeaf0cd09563`: PDF pages 64-65.

### q14: What is the Chitrali broth made by slowly cooking lamb or goat bones called?

Origin: New generation using saved top-five evaluation passages.

> The slow-cooked lamb or goat bone broth is called Shorba. Prepared with dried tomato and wild herbs, it serves as the foundational dish of the valley and is eaten at events ranging from weddings to everyday dinners. [PDF pages 80-81]

Review status: **pass**. Factual consistency: pass; completeness: pass; citation support/refusal: pass.

Pages 80-81 identify Shorba and support the additional ingredients and everyday/wedding context. The answer names the dish directly.

Original physical PDF pages inspected: 80, 81.

Cited chunk metadata:

- `p080-081-4717074613d0`: PDF pages 80-81.

### q17: How can I reach Skardu from Islamabad by public bus, and when does Deosai close to vehicles?

Origin: New generation using saved top-five evaluation passages.

> To travel from Islamabad to Skardu by public bus, NATCO operates direct services departing daily around 2:00 pm. Estimated fares range from PKR 4,630 to 5,500 depending on the bus class, and the journey takes approximately 12 to 14 hours. [PDF pages 37-39; PDF pages 10-14]
> 
> Deosai National Park closes to vehicles due to snow roughly from November to May. [PDF pages 39-40]

Review status: **pass**. Factual consistency: pass; completeness: pass; citation support/refusal: pass.

Page 38 supports direct NATCO buses, daily departure around 2 pm, fare range, and 12-14 hours. Page 40 supports November-May vehicle closure. Both requested sections are answered; source IDs map to the actual page ranges.

Original physical PDF pages inspected: 11, 38, 40.

Cited chunk metadata:

- `p039-040-154eaa1a99b3`: PDF pages 39-40.
- `p037-039-63413879f3c2`: PDF pages 37-39.
- `p010-014-0aced0690245`: PDF pages 10-14.

### q21: What will the weather in Hunza be tomorrow?

Origin: Saved earlier chatbot output, same model and prompt; no new generation call.

> I couldn't find that information in the PDF.

Review status: **pass**. Factual consistency: not applicable; completeness: not applicable; citation support/refusal: pass.

Appropriate refusal of a live weather forecast. The PDF is a static guide, not a forecast source.

Citations: none, appropriate for unsupported information.

### q22: How many seats are available on the next NATCO bus from Islamabad to Skardu right now?

Origin: New generation using existing chatbot retrieval pipeline.

> I couldn't find that information in the PDF.

Review status: **pass**. Factual consistency: not applicable; completeness: not applicable; citation support/refusal: pass.

Appropriate refusal of live seat availability. The PDF gives routes, schedules, and fares, not current inventory.

Citations: none, appropriate for unsupported information.

### q23: What is the guest Wi-Fi password at Serena Shigar Fort?

Origin: New generation using existing chatbot retrieval pipeline.

> I couldn't find that information in the PDF.

Review status: **pass**. Factual consistency: not applicable; completeness: not applicable; citation support/refusal: pass.

Appropriate refusal of an undocumented Wi-Fi password. No password is fabricated.

Citations: none, appropriate for unsupported information.

### q24: What is the fare for a direct train from Islamabad to Skardu?

Origin: New generation using existing chatbot retrieval pipeline.

> I couldn't find that information in the PDF.

Review status: **pass**. Factual consistency: not applicable; completeness: not applicable; citation support/refusal: pass.

Appropriate refusal of an undocumented direct-train fare. The PDF describes air/road/bus access and supplies no such fare.

Citations: none, appropriate for unsupported information.

### q25: What are the exact GPS coordinates of Monday Lake?

Origin: New generation using existing chatbot retrieval pipeline.

> I couldn't find that information in the PDF.

Review status: **pass**. Factual consistency: not applicable; completeness: not applicable; citation support/refusal: pass.

Appropriate refusal of exact coordinates. The Monday Lake entry remains unresolved on PDF pages 48-49.

Original physical PDF pages inspected: 48, 49.

Citations: none, appropriate for unsupported information.

