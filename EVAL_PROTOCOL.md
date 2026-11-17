# Evaluation Protocol

**Protocol date:** 2026-11-17  
**Status:** Locked before results are produced

> `[REWRITE IN YOUR WORDS]` This protocol defines how the fraud-prioritization approach will be judged. Do not replace the original protocol after seeing results. Add any change as a dated amendment and retain the original results.

## Evaluation Question

Does explainable entity resolution and fraud scoring prioritize genuinely fraudulent rebate cases better than a simple exact-match rules baseline using only information available when the rebate decision would have been made?

## Simple Baseline

The baseline links pharmacy records only when a normalized exact identifier, phone number, or full address matches. It flags a case when claimed units exceed matched purchased units or when an exact entity has overlapping medical and pharmacy claims.

## Candidate Method

The candidate adds explainable fuzzy features for name, address, phone, and fax; combines them with cross-channel overlap and excess-quantity evidence; and ranks cases with a deterministic weighted score. `ai_query` explains the supplied evidence and drafts outreach, but it does not change the fraud score or ground-truth label.

## Held-Out Data

Use the final synthetic calendar month as the held-out set. All thresholds, weights, matching logic, prompts, and planted patterns are fixed using earlier months only. The held-out labels remain unavailable to scoring code until evaluation.

## Main Measure

The primary measure is **precision among the top 20 ranked cases**, matching the assumed monthly investigation capacity. Secondary measures are entity-link precision and recall, fraud-case recall, verified-fraud conversion rate, and unsupported-claim rate in AI explanations.

## Timing Rule

For each claim, both the baseline and candidate may use only sales, wholesaler, identity, claim, and case information whose event or receipt timestamp is at or before the simulated decision timestamp. Late files received afterward cannot influence that historical decision. Evaluation code must enforce the cutoff rather than relying on current table contents.

## AI Output Evaluation

Use a fixed synthetic gold set containing expected entity links, fraud reasons, and allowed evidence fields. Parse structured AI output and check:

1. Every cited claim, quantity, channel, pharmacy attribute, and dollar amount exists in the supplied case record.
2. The explanation identifies the expected fraud reason when one is present.
3. The draft uses neutral investigative language and does not assert that fraud is proven.
4. The output contains no real organization, customer, patient, or person information.

Report structured pass rates and manually review the same fixed examples for readability. Preserve model errors by using non-failing structured responses.

## Claim Threshold

Make no improvement claim unless candidate top-20 precision exceeds the baseline by at least 10 percentage points on the held-out month. Make no GenAI quality claim if more than 5% of evaluated explanations contain an unsupported factual assertion. Report a tie, regression, or threshold miss plainly and retain all original outputs.

## Reproducibility

- Fix random seeds, source file contents, evaluation case IDs, score weights, prompts, and model service name.
- Record input table versions or timestamps, run IDs, model service, prompt version, and generated SQL.
- Persist results in `vandelay.rebate_fraud.gold_ai_evaluations` and committed text/JSON evidence.
- Run the baseline and candidate over the identical held-out rows.

## Amendments

No amendments yet. Any future amendment must include its date, reason, effect on comparability, and both original and revised results.
