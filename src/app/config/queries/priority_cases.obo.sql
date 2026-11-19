SELECT case_id, pharmacy_name, region, state_code, product_code, review_period,
       fraud_score, score_drivers,
       round(estimated_overpayment, 2) AS estimated_exposure,
       round(excess_units, 2) AS excess_units,
       has_cross_channel_activity, has_multiple_source_identities
FROM vandelay.rebate_fraud.gold_fraud_cases
ORDER BY fraud_score DESC, estimated_overpayment DESC, case_id
LIMIT 20
