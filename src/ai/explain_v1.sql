CREATE OR REPLACE TABLE vandelay.rebate_fraud.gold_fraud_cases
COMMENT 'Ranked fraud cases with grounded AI investigation assistance for the top twenty held-out cases.'
AS
WITH eligible AS (
  SELECT *
  FROM vandelay.rebate_fraud.gold_fraud_case_scores
  WHERE review_period = '2026-10' AND period_rank <= 20
), prompted AS (
  SELECT
    *,
    to_json(named_struct(
      'case_id', case_id,
      'review_period', review_period,
      'entity_status', entity_status,
      'claimed_units', claimed_units,
      'supported_units', supported_units,
      'excess_units', excess_units,
      'estimated_overpayment', estimated_overpayment,
      'medical_claim_count', medical_claim_count,
      'pharmacy_claim_count', pharmacy_claim_count,
      'matched_cross_channel_pairs', matched_cross_channel_pairs,
      'source_identity_count', source_identity_count,
      'score_drivers', score_drivers
    )) AS supplied_facts
  FROM eligible
), generated AS (
  SELECT
    *,
    ai_query(
      :generator_model,
      concat(
        'You assist a rebate investigator. Use only the JSON facts supplied. ',
        'Draft a concise explanation and one next action. Do not invent people, amounts, dates, documents, or contacts. ',
        'Do not state that fraud is proven. Facts: ', supplied_facts
      ),
      responseFormat => '{"type":"json_schema","json_schema":{"name":"rebate_case_explanation","schema":{"type":"object","properties":{"explanation":{"type":"string"},"next_action":{"type":"string"},"likely_explanation":{"type":"string"}},"required":["explanation","next_action","likely_explanation"],"additionalProperties":false},"strict":true}}',
      modelParameters => named_struct('temperature', 0.0),
      failOnError => false
    ) AS ai_result
  FROM prompted
)
SELECT
  *,
  from_json(ai_result.result, 'explanation STRING, next_action STRING, likely_explanation STRING').explanation AS ai_explanation,
  from_json(ai_result.result, 'explanation STRING, next_action STRING, likely_explanation STRING').next_action AS ai_next_action,
  from_json(ai_result.result, 'explanation STRING, next_action STRING, likely_explanation STRING').likely_explanation AS ai_likely_explanation,
  ai_result.result AS ai_raw_response,
  ai_result.errorMessage AS ai_error_message,
  :generator_model AS ai_model,
  'prompt-v1' AS prompt_version,
  current_timestamp() AS explained_at
FROM generated;

SELECT case_id, supplied_facts, ai_raw_response, ai_error_message
FROM vandelay.rebate_fraud.gold_fraud_cases
ORDER BY period_rank
LIMIT 5;
