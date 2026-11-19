Generated 2026-11-19T20:33:30Z by tools/generate_evidence.py from the live workspace

# Databricks App Route Checks

This file proves the live app deployment, user-authorized route availability, persona-specific presentation, and deployed SQL warehouse, Genie, and Postgres resources.

## Deployed App

| App | Status | Compute | Deployment |
| --- | --- | --- | --- |
| `rebate-ops-matt-cutini` | `RUNNING` | `ACTIVE` | `SUCCEEDED` |

## Route Checks

| route | http_status |
| --- | --- |
| / | 200 |
| /cases | 200 |
| /cases/[CASE_ID] | 200 |
| /genie | 200 |
| /api/health | 200 |
| /api/whoami | 200 |

## Persona Checks

| persona | http_status | headline | emphasis |
| --- | --- | --- | --- |
| director | 200 | Investigation flow and complete paper trail | case status, ownership, due dates, history |
| svp | 200 | Financial exposure and control outcome | estimated exposure, priority cases, executive questions |

## Deployed Resources

| resource | kind | target |
| --- | --- | --- |
| sql-warehouse | sql_warehouse | 5d942ad88a289cf7 |
| genie-space | genie_space | 01f1e3b93f4b11e79b2fbfcd74547821 |
| postgres | postgres | projects/rebate-fraud-ops/branches/production/databases/databricks-postgres |

The route checks use the current Databricks OAuth token only in the request header. No token, response identity, email, or customer/entity name is written to evidence.
