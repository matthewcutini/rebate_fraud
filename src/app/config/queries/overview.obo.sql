SELECT
  count(DISTINCT case_id) AS suspected_cases,
  round(sum(estimated_overpayment), 2) AS estimated_exposure,
  round(sum(excess_units), 2) AS excess_units,
  count_if(has_cross_channel_activity) AS cross_channel_cases,
  max(scored_at) AS data_freshness
FROM vandelay.rebate_fraud.gold_fraud_cases
