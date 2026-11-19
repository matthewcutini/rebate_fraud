Generated 2026-11-19T20:32:13Z by tools/generate_evidence.py from the live workspace

# Unity Catalog Governance

This file proves the live entitlement configuration, current governed result, dedicated non-admin test results, and governance metadata without exposing principal identities or contact values.

## Deployed Governance Run

| Job ID | Run ID | Result |
| --- | --- | --- |
| `129437839852986` | `875275322019240` | `SUCCESS` |

## Configured Personas

Statement `01f1e458-4e99-1d4e-bc81-1fc7c8148461`:

| persona | allowed_region | can_see_sensitive | principals |
| --- | --- | --- | --- |
| SVP_CONTRACTING_REBATES | ALL | false | 2 |

## Current Persona Result

Statement `01f1e458-4f69-166a-9e14-45add59b9b6b`:

| visible_rows | visible_regions | visible_scopes | phone_example |
| --- | --- | --- | --- |
| 21845 | 4 | MIDWEST,NORTHEAST,SOUTH,WEST | RESTRICTED |

## Dedicated Non-Admin Access Results

Statement `01f1e458-5109-149a-bad1-7a66f2d4e277`:

| visible_rows | visible_regions | phone_policy | address_policy | masked_column_join_rows | tested_at |
| --- | --- | --- | --- | --- | --- |
| 19881 | 4 | MASKED | MASKED | 197617140 | 2026-11-18T23:10:11.813Z |

## Governed Table Tags

Statement `01f1e458-51f4-116c-98ad-90756a15c68c`:

| tag_name | tag_value |
| --- | --- |
| febar_classification | confidential |
| febar_domain | rebate_fraud |
| febar_synthetic_data | true |

Unity Catalog enforces row visibility and contact-field masking on the governed Delta table. Lakebase workflow-row authorization is enforced by the app, not inherited from Unity Catalog.
