CREATE OR REPLACE TABLE vandelay.rebate_fraud.gold_fraud_case_scores
COMMENT 'Deterministic, explainable fraud-prioritization scores; one row per resolved pharmacy, product and review month.'
AS
WITH components AS (
  SELECT
    *,
    CASE
      WHEN claimed_units > 0 AND excess_units / claimed_units >= 0.50 THEN 50
      WHEN excess_units > 0 THEN 30
      ELSE 0
    END AS excess_quantity_points,
    CASE WHEN has_cross_channel_activity THEN 30 ELSE 0 END AS cross_channel_points,
    CASE WHEN has_multiple_source_identities THEN 10 ELSE 0 END AS multiple_identity_points,
    CASE WHEN entity_status IN ('CLOSED', 'PENDING') THEN 10 ELSE 0 END AS entity_status_points
  FROM vandelay.rebate_fraud.governed_case_features
), scored AS (
  SELECT
    *,
    excess_quantity_points + cross_channel_points + multiple_identity_points + entity_status_points AS fraud_score,
    array_compact(array(
      CASE WHEN excess_quantity_points > 0 THEN concat('Unsupported quantity: ', cast(excess_units AS STRING), ' excess units') END,
      CASE WHEN cross_channel_points > 0 THEN concat('Matched medical/pharmacy activity: ', cast(matched_cross_channel_pairs AS STRING), ' pair(s)') END,
      CASE WHEN multiple_identity_points > 0 THEN concat('Multiple source identities: ', cast(source_identity_count AS STRING)) END,
      CASE WHEN entity_status_points > 0 THEN concat('Entity status: ', entity_status) END
    )) AS score_drivers
  FROM components
)
SELECT
  *,
  row_number() OVER (
    PARTITION BY review_period
    ORDER BY fraud_score DESC, estimated_overpayment DESC, case_id
  ) AS period_rank,
  current_timestamp() AS scored_at,
  'score-v1' AS score_version
FROM scored;

SELECT review_period, count(*) AS cases, max(fraud_score) AS max_score
FROM vandelay.rebate_fraud.gold_fraud_case_scores
GROUP BY review_period
ORDER BY review_period;
