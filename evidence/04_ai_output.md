Generated 2026-11-19T20:31:37Z by tools/generate_evidence.py from the live workspace

# AI Output Samples

This file proves the exact facts supplied to the model and the verbatim persisted model responses for live top-ranked cases, without adding or rewriting model claims.

## Sample 1

- Case ID: `31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64`
- Review period: `2026-10`
- Explainable score: `80`
- Generator: `databricks-claude-haiku-4-5`
- Prompt: `prompt-v2`

### Supplied Facts

```json
{
  "case_id": "31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64",
  "claimed_units": 540.0,
  "entity_status": "ACTIVE",
  "estimated_overpayment": 152777.771722,
  "excess_units": 495.0,
  "matched_cross_channel_pairs": 1,
  "medical_claim_count": 1,
  "pharmacy_claim_count": 1,
  "review_period": "2026-10",
  "score_drivers": [
    "Unsupported quantity: 495.00 excess units",
    "Matched medical/pharmacy activity: 1 pair(s)"
  ],
  "source_identity_count": 1,
  "supported_units": 45.0
}
```

### Verbatim Model Output

```json
{
  "explanation": "For review period 2026-10, the entity claimed 540.00 units but only 45.00 units are supported by documentation, resulting in 495.00 excess units. This variance corresponds to an estimated overpayment of $152,777.77. The case shows 1 medical claim and 1 pharmacy claim that form a matched cross-channel pair, with 1 source identity involved.",
  "likely_explanation": "The claimed quantity of 540.00 units exceeds the supported quantity of 45.00 units by 495.00 units. This 92% variance between claimed and supported amounts is the primary driver of the estimated overpayment.",
  "next_action": "Request that the entity provide documentation or explanation for the 495.00 excess units claimed in review period 2026-10, specifically reconciling how the claimed quantity of 540.00 units relates to the supported quantity of 45.00 units and the single matched medical/pharmacy claim pair on record."
}
```

## Sample 2

- Case ID: `c5c145d8ffc6a7a5fdb7e319f8311c610cb8d3d8cd76d9a96a6f077f12fe1b69`
- Review period: `2026-10`
- Explainable score: `80`
- Generator: `databricks-claude-haiku-4-5`
- Prompt: `prompt-v2`

### Supplied Facts

```json
{
  "case_id": "c5c145d8ffc6a7a5fdb7e319f8311c610cb8d3d8cd76d9a96a6f077f12fe1b69",
  "claimed_units": 520.0,
  "entity_status": "ACTIVE",
  "estimated_overpayment": 152243.583577,
  "excess_units": 475.0,
  "matched_cross_channel_pairs": 1,
  "medical_claim_count": 1,
  "pharmacy_claim_count": 1,
  "review_period": "2026-10",
  "score_drivers": [
    "Unsupported quantity: 475.00 excess units",
    "Matched medical/pharmacy activity: 1 pair(s)"
  ],
  "source_identity_count": 1,
  "supported_units": 45.0
}
```

### Verbatim Model Output

```json
{
  "explanation": "For review period 2026-10, the entity claimed 520.00 units but only 45.00 units are supported by documentation, resulting in 475.00 excess units. This variance corresponds to an estimated overpayment of $152,243.58. The case shows 1 medical claim and 1 pharmacy claim that form 1 matched cross-channel pair from 1 source identity.",
  "likely_explanation": "The claimed quantity of 520.00 units exceeds supported quantity of 45.00 units by 475.00 units.",
  "next_action": "Request that the entity provide documentation or explanation reconciling the 475.00-unit variance between claimed units (520.00) and supported units (45.00) for review period 2026-10."
}
```

## Sample 3

- Case ID: `47e83c350ab24822f99bb2d91d33423c334b6ba4915983013d7696991f20263c`
- Review period: `2026-10`
- Explainable score: `80`
- Generator: `databricks-claude-haiku-4-5`
- Prompt: `prompt-v2`

### Supplied Facts

```json
{
  "case_id": "47e83c350ab24822f99bb2d91d33423c334b6ba4915983013d7696991f20263c",
  "claimed_units": 38.0,
  "entity_status": "ACTIVE",
  "estimated_overpayment": 50000.0,
  "excess_units": 19.0,
  "matched_cross_channel_pairs": 1,
  "medical_claim_count": 1,
  "pharmacy_claim_count": 1,
  "review_period": "2026-10",
  "score_drivers": [
    "Unsupported quantity: 19.00 excess units",
    "Matched medical/pharmacy activity: 1 pair(s)"
  ],
  "source_identity_count": 1,
  "supported_units": 19.0
}
```

### Verbatim Model Output

```json
{
  "explanation": "For review period 2026-10, the entity claimed 38.00 units but only 19.00 units are supported by documentation, resulting in 19.00 excess units. This variance is associated with an estimated overpayment of $50,000.00. The case identifies 1 medical claim and 1 pharmacy claim that form a matched cross-channel pair from a single source identity.",
  "likely_explanation": "The claimed quantity of 38.00 units exceeds the supported quantity of 19.00 units by exactly 50 percent. One possibility, not established by these facts, is that units were claimed twice across channels or that documentation supporting the full claimed amount was not provided during review.",
  "next_action": "Request that the entity provide a detailed reconciliation explaining the variance between the 38.00 claimed units and 19.00 supported units, including clarification of how the matched medical and pharmacy claim pair relates to the stated quantities and supporting documentation for the excess 19.00 units."
}
```
