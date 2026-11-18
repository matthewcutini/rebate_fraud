# Unity Catalog Governance Evidence

## Deployment

- Governance job: `129437839852986`
- Successful governance run: `145914634774984`
- Governed consumption table: `vandelay.rebate_fraud.governed_case_features`
- Source table: `vandelay.rebate_fraud.gold_case_features`
- Dedicated non-admin service principal: `febar-rebate-governance-test`
- Application ID: `961bac9c-adf7-4dab-8197-748a848983ad`

The governance job completed successfully after creating the entitlement table, policy functions, governed consumption table, comments, tags, row filter, masks, least-privilege test grants, and harmless permission probe.

## Policy Definitions

```sql
CREATE OR REPLACE FUNCTION vandelay.rebate_fraud.f_region_access(region_value STRING)
RETURNS BOOLEAN
RETURN EXISTS (
  SELECT 1
  FROM vandelay.rebate_fraud.entitlements entitlement
  WHERE entitlement.principal = current_user()
    AND (entitlement.allowed_region = 'ALL' OR entitlement.allowed_region = region_value)
);

CREATE OR REPLACE FUNCTION vandelay.rebate_fraud.f_mask_sensitive(value STRING)
RETURNS STRING
RETURN CASE
  WHEN EXISTS (
    SELECT 1
    FROM vandelay.rebate_fraud.entitlements entitlement
    WHERE entitlement.principal = current_user()
      AND entitlement.can_see_sensitive
  ) THEN value
  ELSE 'RESTRICTED'
END;
```

`DESCRIBE TABLE EXTENDED vandelay.rebate_fraud.governed_case_features` confirmed:

```text
Row Filter: vandelay.rebate_fraud.f_region_access ON (region)
Column Mask: pharmacy_address -> vandelay.rebate_fraud.f_mask_sensitive
Column Mask: pharmacy_phone   -> vandelay.rebate_fraud.f_mask_sensitive
Column Mask: pharmacy_fax     -> vandelay.rebate_fraud.f_mask_sensitive
```

The policies are attached only to `governed_case_features`. The pipeline continues to read unfiltered bronze and silver tables and writes unfiltered `gold_case_features`.

## Persona Results

The same query was run after changing only the current user's row in `entitlements`:

```sql
SELECT
  count(*) AS visible_rows,
  count(DISTINCT region) AS visible_regions,
  concat_ws(',', sort_array(collect_set(region))) AS scopes,
  min(pharmacy_phone) AS phone_example
FROM vandelay.rebate_fraud.governed_case_features;
```

| Persona | Entitlement | Visible rows | Regions | Phone result |
|---|---|---:|---|---|
| SVP of Contracting and Rebates | `ALL`, sensitive `false` | 19,881 | `MIDWEST,NORTHEAST,SOUTH,WEST` | `RESTRICTED` |
| Director of Rebate Operations | `ALL`, sensitive `true` | 19,881 | `MIDWEST,NORTHEAST,SOUTH,WEST` | Synthetic value visible |
| Regional Rebate Analyst | `WEST`, sensitive `true` | 7,511 | `WEST` | Synthetic value visible |
| Legal Reviewer | Deferred until the Lakebase case table supplies legal-escalation status | Not tested | Escalated cases only | Sensitive access planned |

The current user's entitlement was restored to `SVP_CONTRACTING_REBATES`, `ALL`, sensitive `false` after the test.

## Comments and Tags

The deployed table and sensitive columns have business comments. `information_schema.table_tags` and `column_tags` returned:

| Level | Object | Tag | Value |
|---|---|---|---|
| Table | `governed_case_features` | `febar_domain` | `rebate_fraud` |
| Table | `governed_case_features` | `febar_classification` | `confidential` |
| Table | `governed_case_features` | `febar_synthetic_data` | `true` |
| Column | `pharmacy_address` | `febar_sensitivity` | `sensitive_contact` |
| Column | `pharmacy_phone` | `febar_sensitivity` | `sensitive_contact` |
| Column | `pharmacy_fax` | `febar_sensitivity` | `sensitive_contact` |
| Column | `estimated_overpayment` | `febar_sensitivity` | `commercially_sensitive` |

## Non-Admin Test

The service principal was created without admin membership. It received only the SQL workspace entitlement, `CAN_USE` on the selected warehouse, read access to the bundle's deployed SQL files, and the temporary Unity Catalog privileges required for this test.

### Approved Read and Masks

Command:

```text
databricks bundle run governance_access_allowed -t dev --profile vandelay
```

Result:

```text
run_id=323306132311672
state=SUCCESS
current_user=961bac9c-adf7-4dab-8197-748a848983ad
visible_rows=19881
visible_regions=4
phone_example=RESTRICTED
address_example=RESTRICTED
masked_column_join_rows=197617140
```

The join was intentionally run on the masked phone column. Because every unauthorized value becomes `RESTRICTED`, it produces 197,617,140 matches. This proves the mask is enforced and demonstrates that a masked sensitive column must not be used as a business join key.

### Protected Read

Command:

```text
databricks bundle run governance_access_protected -t dev --profile vandelay
```

Only response metadata was retained:

```text
run_id=102902864349364
state=TERMINATED
code=RUN_EXECUTION_ERROR
response_characters=2604
permission_related=true
not_found=false
```

No protected table contents were recorded.

### Permission-Hiding Comparison

The harmless table `governance_permission_probe` followed this sequence:

| Step | Command/action | Run ID | Result |
|---|---|---:|---|
| No table grant | Run `governance_access_probe` | `401550699167886` | Failed; permission-related; response 1,021 characters; not-found `false` |
| Temporary `SELECT` granted | Run `governance_access_probe` | `631843563660950` | `SUCCESS` |
| `SELECT` revoked | Run `governance_access_probe` | `89305346965435` | Failed; permission-related; response 1,020 characters; not-found `false` |

The protected table and harmless table therefore fail for permission reasons rather than object absence.

### Cleanup

The following Unity Catalog privileges were removed from the service principal:

```text
SELECT on governed_case_features
SELECT, MODIFY on governance_access_test_results
SELECT on governance_permission_probe
USE SCHEMA on vandelay.rebate_fraud
USE CATALOG on vandelay
```

Post-cleanup checks:

```text
governance_access_allowed run_id=237974633431307
state=RUN_EXECUTION_ERROR
permission_related=true
response_characters=1024

information_schema.table_privileges rows for the principal=0
```

The SQL entitlement, warehouse `CAN_USE`, and read-only access to the deployed test scripts remain so the identity can execute a future approved access test, but it has no remaining Unity Catalog data privileges.

## Lineage

Query:

```sql
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events
FROM system.access.table_lineage
WHERE event_date >= current_date() - 7
  AND target_table_full_name IN (
    'vandelay.rebate_fraud.gold_case_features',
    'vandelay.rebate_fraud.governed_case_features'
  )
GROUP BY source_table_full_name, target_table_full_name;
```

Results available at evidence capture time:

| Source | Target | Events |
|---|---|---:|
| `vandelay.rebate_fraud.silver_claims` | `vandelay.rebate_fraud.gold_case_features` | 5 |
| `vandelay.rebate_fraud.silver_pharmacy_entities` | `vandelay.rebate_fraud.gold_case_features` | 5 |
| `vandelay.rebate_fraud.silver_product_movement` | `vandelay.rebate_fraud.gold_case_features` | 5 |

The system lineage table had not yet emitted the newer CTAS edge from `gold_case_features` to `governed_case_features` when evidence was captured. The deployed SQL and successful governance run provide the immediate text proof of that edge; system-table lineage is eventually populated.

## Failed Attempts Preserved

- Bundle deployment initially returned `403 PERMISSION_DENIED` because the creator lacked `servicePrincipal.user` on the new principal. The role was granted, and all three run-as jobs then deployed.
- The first governance run rejected the workspace-governed tag key `domain`; project-specific `febar_*` tags were used instead.
- The first non-admin run lacked the `databricks-sql-access` entitlement, then could not read the owner-only bundle files directory. The minimum SQL entitlement, warehouse `CAN_USE`, and bundle-directory `CAN_READ` resolved those execution-layer failures without granting additional data access.
