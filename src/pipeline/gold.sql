-- Business-ready features connect identity resolution, channel overlap and units purchased.

CREATE OR REFRESH MATERIALIZED VIEW gold_case_features
COMMENT 'One row per resolved pharmacy, product and review month with fraud investigation features.'
AS
WITH resolved_claim_rows AS (
  SELECT
    coalesce(entity_by_address.pharmacy_id, entity_by_phone.pharmacy_id, entity_by_fax.pharmacy_id, concat('UNRESOLVED-', claims.source_entity_id)) AS pharmacy_id,
    claims.claim_id,
    claims.claim_channel,
    claims.product_code,
    claims.service_date,
    claims.submitted_at,
    claims.rebate_units,
    claims.rebate_amount,
    claims.pharmacy_name
  FROM silver_claims claims
  LEFT JOIN silver_pharmacy_entities entity_by_address
    ON claims.pharmacy_address = entity_by_address.pharmacy_address
  LEFT JOIN silver_pharmacy_entities entity_by_phone
    ON claims.phone <> '' AND claims.phone = entity_by_phone.phone
  LEFT JOIN silver_pharmacy_entities entity_by_fax
    ON claims.fax <> '' AND claims.fax = entity_by_fax.fax
), claims_resolved AS (
  SELECT
    pharmacy_id,
    product_code,
    date_format(service_date, 'yyyy-MM') AS review_period,
    count(*) AS claim_count,
    sum(rebate_units) AS claimed_units,
    sum(rebate_amount) AS claimed_rebate_amount,
    count_if(claim_channel = 'MEDICAL') AS medical_claim_count,
    count_if(claim_channel = 'PHARMACY') AS pharmacy_claim_count,
    count(DISTINCT claim_channel) AS channel_count,
    count(DISTINCT pharmacy_name) AS source_identity_count,
    max(pharmacy_name) AS observed_pharmacy_name
  FROM resolved_claim_rows
  WHERE submitted_at <= CAST(date_add(last_day(service_date), 1) AS TIMESTAMP)
  GROUP BY 1, 2, 3
), cross_channel_matches AS (
  SELECT
    medical.pharmacy_id,
    medical.product_code,
    date_format(medical.service_date, 'yyyy-MM') AS review_period,
    count(*) AS matched_cross_channel_pairs
  FROM resolved_claim_rows medical
  INNER JOIN resolved_claim_rows pharmacy
    ON medical.pharmacy_id = pharmacy.pharmacy_id
   AND medical.product_code = pharmacy.product_code
   AND medical.service_date = pharmacy.service_date
   AND medical.rebate_units = pharmacy.rebate_units
   AND medical.rebate_amount >= 10000
   AND pharmacy.rebate_amount >= 10000
   AND medical.claim_channel = 'MEDICAL'
   AND pharmacy.claim_channel = 'PHARMACY'
  GROUP BY 1, 2, 3
), movements_resolved AS (
  SELECT
    coalesce(entity_by_address.pharmacy_id, entity_by_phone.pharmacy_id, entity_by_fax.pharmacy_id, concat('UNRESOLVED-', movements.source_entity_id)) AS pharmacy_id,
    movements.product_code,
    date_format(movements.movement_date, 'yyyy-MM') AS review_period,
    sum(movements.signed_units) AS supported_units,
    sum(CASE WHEN movements.movement_source = 'MANUFACTURER' THEN movements.signed_units ELSE 0 END) AS manufacturer_units,
    sum(CASE WHEN movements.movement_source = 'WHOLESALER' THEN movements.signed_units ELSE 0 END) AS wholesaler_units
  FROM silver_product_movement movements
  LEFT JOIN silver_pharmacy_entities entity_by_address
    ON movements.pharmacy_address = entity_by_address.pharmacy_address
  LEFT JOIN silver_pharmacy_entities entity_by_phone
    ON movements.phone <> '' AND movements.phone = entity_by_phone.phone
  LEFT JOIN silver_pharmacy_entities entity_by_fax
    ON movements.fax <> '' AND movements.fax = entity_by_fax.fax
  GROUP BY 1, 2, 3
)
SELECT
  sha2(concat_ws('|', claims.pharmacy_id, claims.product_code, claims.review_period), 256) AS case_id,
  claims.pharmacy_id,
  entities.legal_name AS pharmacy_name,
  entities.entity_status,
  CASE
    WHEN regexp_extract(entities.pharmacy_address, ', ([A-Z]{2}) [0-9]{5}$', 1) IN ('CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA') THEN 'NORTHEAST'
    WHEN regexp_extract(entities.pharmacy_address, ', ([A-Z]{2}) [0-9]{5}$', 1) IN ('IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI') THEN 'MIDWEST'
    WHEN regexp_extract(entities.pharmacy_address, ', ([A-Z]{2}) [0-9]{5}$', 1) IN ('AL', 'AR', 'DE', 'FL', 'GA', 'KY', 'LA', 'MD', 'MS', 'NC', 'OK', 'SC', 'TN', 'TX', 'VA', 'WV') THEN 'SOUTH'
    ELSE 'WEST'
  END AS region,
  regexp_extract(entities.pharmacy_address, ', ([A-Z]{2}) [0-9]{5}$', 1) AS state_code,
  entities.pharmacy_address,
  entities.phone AS pharmacy_phone,
  entities.fax AS pharmacy_fax,
  claims.product_code,
  claims.review_period,
  claims.claim_count,
  claims.medical_claim_count,
  claims.pharmacy_claim_count,
  claims.channel_count,
  claims.source_identity_count,
  claims.claimed_units,
  coalesce(movements.supported_units, 0) AS supported_units,
  greatest(claims.claimed_units - coalesce(movements.supported_units, 0), 0) AS excess_units,
  claims.claimed_rebate_amount,
  CASE
    WHEN claims.claimed_units > 0
    THEN greatest(claims.claimed_units - coalesce(movements.supported_units, 0), 0) / claims.claimed_units * claims.claimed_rebate_amount
    ELSE 0
  END AS estimated_overpayment,
  coalesce(cross_channel_matches.matched_cross_channel_pairs, 0) > 0 AS has_cross_channel_activity,
  coalesce(cross_channel_matches.matched_cross_channel_pairs, 0) AS matched_cross_channel_pairs,
  claims.source_identity_count > 1 AS has_multiple_source_identities,
  coalesce(movements.manufacturer_units, 0) AS manufacturer_units,
  coalesce(movements.wholesaler_units, 0) AS wholesaler_units
FROM claims_resolved claims
LEFT JOIN movements_resolved movements
  ON claims.pharmacy_id = movements.pharmacy_id
 AND claims.product_code = movements.product_code
 AND claims.review_period = movements.review_period
LEFT JOIN cross_channel_matches
  ON claims.pharmacy_id = cross_channel_matches.pharmacy_id
 AND claims.product_code = cross_channel_matches.product_code
 AND claims.review_period = cross_channel_matches.review_period
LEFT JOIN silver_pharmacy_entities entities
  ON claims.pharmacy_id = entities.pharmacy_id;
