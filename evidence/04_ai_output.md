# AI Output Evidence

**Run date:** 2026-11-18  
**Held-out period:** `2026-10`  
**Generator:** `databricks-claude-haiku-4-5`  
**Final prompt:** `prompt-v2`  
**Successful partial job run:** `936164329821574`

The deterministic score ran over every governed case. `ai_query` ran only for the top 20 held-out cases. The deployed table contained 20 explanations, zero model errors, scores from 20 to 80, and 13 rows flagged by the exact excess-or-cross-channel rule.

## Verbatim Sample 1

Supplied facts:

```json
{"case_id":"31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64","review_period":"2026-10","entity_status":"ACTIVE","claimed_units":540.00,"supported_units":45.00,"excess_units":495.00,"estimated_overpayment":152777.771722,"medical_claim_count":1,"pharmacy_claim_count":1,"matched_cross_channel_pairs":1,"source_identity_count":1,"score_drivers":["Unsupported quantity: 495.00 excess units","Matched medical/pharmacy activity: 1 pair(s)"]}
```

Model output:

```json
{"explanation":"For review period 2026-10, the entity claimed 540.00 units but only 45.00 units are supported by documentation, resulting in 495.00 excess units. This variance corresponds to an estimated overpayment of $152,777.77. The case shows 1 medical claim and 1 pharmacy claim that form a matched cross-channel pair, with 1 source identity involved.","likely_explanation":"The claimed quantity of 540.00 units exceeds the supported quantity of 45.00 units by 495.00 units. This 92% variance between claimed and supported amounts is the primary driver of the estimated overpayment.","next_action":"Request that the entity provide documentation or explanation for the 495.00 excess units claimed in review period 2026-10, specifically reconciling how the claimed quantity of 540.00 units relates to the supported quantity of 45.00 units and the single matched medical/pharmacy claim pair on record."}
```

## Verbatim Sample 2

Supplied facts:

```json
{"case_id":"c5c145d8ffc6a7a5fdb7e319f8311c610cb8d3d8cd76d9a96a6f077f12fe1b69","review_period":"2026-10","entity_status":"ACTIVE","claimed_units":520.00,"supported_units":45.00,"excess_units":475.00,"estimated_overpayment":152243.583577,"medical_claim_count":1,"pharmacy_claim_count":1,"matched_cross_channel_pairs":1,"source_identity_count":1,"score_drivers":["Unsupported quantity: 475.00 excess units","Matched medical/pharmacy activity: 1 pair(s)"]}
```

Model output:

```json
{"explanation":"For review period 2026-10, the entity claimed 520.00 units but only 45.00 units are supported by documentation, resulting in 475.00 excess units. This variance corresponds to an estimated overpayment of $152,243.58. The case shows 1 medical claim and 1 pharmacy claim that form 1 matched cross-channel pair from 1 source identity.","likely_explanation":"The claimed quantity of 520.00 units exceeds supported quantity of 45.00 units by 475.00 units.","next_action":"Request that the entity provide documentation or explanation reconciling the 475.00-unit variance between claimed units (520.00) and supported units (45.00) for review period 2026-10."}
```

These outputs are preserved verbatim. The unsupported phrase “supported by documentation” remained after the prompt iteration and is not treated as a successful quality result.
