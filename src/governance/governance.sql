CREATE TABLE IF NOT EXISTS vandelay.rebate_fraud.entitlements (
  principal STRING NOT NULL COMMENT 'User email or service-principal application ID returned by current_user().',
  principal_type STRING NOT NULL COMMENT 'USER or SERVICE_PRINCIPAL.',
  persona STRING NOT NULL COMMENT 'Approved rebate-governance persona.',
  allowed_region STRING NOT NULL COMMENT 'ALL or one US business region.',
  can_see_sensitive BOOLEAN NOT NULL COMMENT 'Whether contact and address fields are returned without masking.',
  updated_at TIMESTAMP NOT NULL COMMENT 'Timestamp of the latest entitlement decision.'
)
USING DELTA
COMMENT 'Data-driven regional and sensitive-field entitlements for rebate fraud consumers.';

MERGE INTO vandelay.rebate_fraud.entitlements AS target
USING (
  SELECT
    'matt.cutini@databricks.com' AS principal,
    'USER' AS principal_type,
    'SVP_CONTRACTING_REBATES' AS persona,
    'ALL' AS allowed_region,
    false AS can_see_sensitive,
    current_timestamp() AS updated_at
  UNION ALL
  SELECT
    '961bac9c-adf7-4dab-8197-748a848983ad',
    'SERVICE_PRINCIPAL',
    'SVP_CONTRACTING_REBATES',
    'ALL',
    false,
    current_timestamp()
) AS source
ON target.principal = source.principal
WHEN MATCHED THEN UPDATE SET
  target.principal_type = source.principal_type,
  target.persona = source.persona,
  target.allowed_region = source.allowed_region,
  target.can_see_sensitive = source.can_see_sensitive,
  target.updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT *;

CREATE OR REPLACE FUNCTION vandelay.rebate_fraud.f_region_access(region_value STRING)
RETURNS BOOLEAN
COMMENT 'Allows a consumer to see all regions or the region recorded in the entitlement table.'
RETURN EXISTS (
  SELECT 1
  FROM vandelay.rebate_fraud.entitlements entitlement
  WHERE entitlement.principal = current_user()
    AND (entitlement.allowed_region = 'ALL' OR entitlement.allowed_region = region_value)
);

CREATE OR REPLACE FUNCTION vandelay.rebate_fraud.f_mask_sensitive(value STRING)
RETURNS STRING
COMMENT 'Returns sensitive contact data only when the current principal is explicitly cleared.'
RETURN CASE
  WHEN EXISTS (
    SELECT 1
    FROM vandelay.rebate_fraud.entitlements entitlement
    WHERE entitlement.principal = current_user()
      AND entitlement.can_see_sensitive
  ) THEN value
  ELSE 'RESTRICTED'
END;

CREATE OR REPLACE TABLE vandelay.rebate_fraud.governed_case_features
COMMENT 'Governed fraud investigation features for people, applications and Genie; one row per pharmacy, product and review month.'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'data_domain' = 'rebate_fraud',
  'data_classification' = 'confidential'
)
AS
SELECT *
FROM vandelay.rebate_fraud.gold_case_features;

ALTER TABLE vandelay.rebate_fraud.governed_case_features
  SET ROW FILTER vandelay.rebate_fraud.f_region_access ON (region);

ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_address SET MASK vandelay.rebate_fraud.f_mask_sensitive;
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_phone SET MASK vandelay.rebate_fraud.f_mask_sensitive;
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_fax SET MASK vandelay.rebate_fraud.f_mask_sensitive;

COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.case_id IS 'Stable identifier for one suspected rebate fraud case.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.pharmacy_id IS 'Synthetic canonical pharmacy identifier.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.pharmacy_name IS 'Synthetic pharmacy name shown to investigators.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.region IS 'US business region used by the row-access policy.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.state_code IS 'Synthetic US state code derived from the pharmacy reference address.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.pharmacy_address IS 'Synthetic contact address masked unless the consumer is cleared.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.pharmacy_phone IS 'Synthetic phone number masked unless the consumer is cleared.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.pharmacy_fax IS 'Synthetic fax number masked unless the consumer is cleared.';
COMMENT ON COLUMN vandelay.rebate_fraud.governed_case_features.estimated_overpayment IS 'Illustrative suspected overpayment calculated from claimed and supported units.';

ALTER TABLE vandelay.rebate_fraud.governed_case_features SET TAGS (
  'febar_domain' = 'rebate_fraud',
  'febar_classification' = 'confidential',
  'febar_synthetic_data' = 'true'
);
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_address SET TAGS ('febar_sensitivity' = 'sensitive_contact');
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_phone SET TAGS ('febar_sensitivity' = 'sensitive_contact');
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN pharmacy_fax SET TAGS ('febar_sensitivity' = 'sensitive_contact');
ALTER TABLE vandelay.rebate_fraud.governed_case_features
  ALTER COLUMN estimated_overpayment SET TAGS ('febar_sensitivity' = 'commercially_sensitive');

CREATE TABLE IF NOT EXISTS vandelay.rebate_fraud.governance_permission_probe (
  probe_id INT,
  probe_label STRING
)
USING DELTA
COMMENT 'Harmless table used only to distinguish permission hiding from object absence.';

MERGE INTO vandelay.rebate_fraud.governance_permission_probe AS target
USING (SELECT 1 AS probe_id, 'permission-check' AS probe_label) AS source
ON target.probe_id = source.probe_id
WHEN NOT MATCHED THEN INSERT *;

CREATE TABLE IF NOT EXISTS vandelay.rebate_fraud.governance_access_test_results (
  test_principal STRING,
  visible_rows BIGINT,
  visible_regions BIGINT,
  phone_example STRING,
  address_example STRING,
  masked_column_join_rows BIGINT,
  tested_at TIMESTAMP
)
USING DELTA
COMMENT 'Aggregate-only read-back from the dedicated non-admin governance test.';

GRANT USE CATALOG ON CATALOG vandelay TO `961bac9c-adf7-4dab-8197-748a848983ad`;
GRANT USE SCHEMA ON SCHEMA vandelay.rebate_fraud TO `961bac9c-adf7-4dab-8197-748a848983ad`;
GRANT SELECT ON TABLE vandelay.rebate_fraud.governed_case_features TO `961bac9c-adf7-4dab-8197-748a848983ad`;
GRANT SELECT, MODIFY ON TABLE vandelay.rebate_fraud.governance_access_test_results TO `961bac9c-adf7-4dab-8197-748a848983ad`;

SELECT
  current_user() AS governance_job_principal,
  (SELECT count(*) FROM vandelay.rebate_fraud.entitlements) AS entitlement_rows,
  (SELECT count(*) FROM vandelay.rebate_fraud.governed_case_features) AS governed_rows;
