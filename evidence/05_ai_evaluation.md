# AI Evaluation Evidence

**Run date:** 2026-11-18  
**Protocol:** `EVAL_PROTOCOL.md`, unchanged  
**Held-out period:** `2026-10`  
**Generator:** `databricks-claude-haiku-4-5`  
**Different-family judge:** `databricks-gpt-5-6-luna`  
**Rows evaluated per prompt:** 20

## Ranking Result

| Method | Top-20 precision | Required improvement | Claim allowed |
|---|---:|---:|---|
| Exact-match baseline | 65% | — | — |
| Explainable candidate score | 65% | +10 percentage points | No |

The candidate tied the baseline. Per the locked protocol, this build makes no ranking-improvement claim.

## GenAI Judge Results

| Judge | Prompt v1 | Prompt v2 | Change |
|---|---:|---:|---:|
| Grounded in supplied facts | 35% | 35% | 0 points |
| Actionable next step | 95% | 100% | +5 points |
| No invented data | 45% | 25% | -20 points |
| Neutral investigative language | 100% | 100% | 0 points |

- Prompt v1 MLflow run: `fe80568d98a94035a139282f13562968`
- Prompt v2 MLflow run: `c683dcf24bf549cdb372d84a54c0d831`
- Per-row assessments and rationales: `vandelay.rebate_fraud.gold_ai_evaluations`

## Failure Review and Iteration

The v1 judge repeatedly identified “supported by documentation,” named documents, patient references, and “coordinated activity” as facts not present in the supplied record. Prompt v2 explicitly prohibited those additions and limited the next step to quantity reconciliation and asking the entity to explain the variance.

The model still produced “supported by documentation” and requests for documentation. Groundedness did not improve, and the no-invented-data score regressed. Judges were not weakened or changed. Because unsupported assertions exceeded 5%, the build makes no GenAI-quality claim and flags all generated drafts for investigator review.
