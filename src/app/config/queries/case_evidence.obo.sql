-- @param caseId STRING = 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64
SELECT case_id, pharmacy_name, entity_status, region, state_code, product_code, review_period,
       claimed_units, manufacturer_units, wholesaler_units, supported_units, excess_units,
       medical_claim_count, pharmacy_claim_count, matched_cross_channel_pairs,
       source_identity_count, round(estimated_overpayment, 2) AS estimated_exposure,
       fraud_score, score_drivers, ai_explanation, ai_next_action, ai_model, explained_at
FROM vandelay.rebate_fraud.gold_fraud_cases
WHERE case_id = :caseId
