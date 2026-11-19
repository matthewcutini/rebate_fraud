# Databricks App Evidence

- **App:** `rebate-ops-matt-cutini`
- **URL:** https://rebate-ops-matt-cutini-8259554820748444.gcp.databricksapps.com
- **Execution identity:** Analytics and Genie use the signed-in user's forwarded token; Lakebase uses the app service principal with app-level row authorization.

## Route Checks

| Route | HTTP status |
| --- | ---: |
| `/` | 200 |
| `/cases` | 200 |
| `/cases/31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64` | 200 |
| `/genie` | 200 |
| `/api/health` | 200 |
| `/api/whoami` | 200 |

## Persona Comparison

- **Director lens:** Investigation flow and complete paper trail; shows case status, ownership, due dates, history.
- **SVP lens:** Financial exposure and control outcome; shows estimated exposure, priority cases, executive questions.
- Persona lenses change presentation only and never expand the signed-in user's governed data access.

## Lakebase Edit and History

- **Case:** `31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64`
- **Before status:** `IN_REVIEW`
- **After status:** `IN_REVIEW`
- **Saved note:** App acceptance check 2026-11-19T02:16:17.278899+00:00
- **Latest history event:** `UPDATE` from `APP` by `matt.cutini@databricks.com` at `2026-11-19T02:16:17.671Z`.
- **Changed columns:** notes, updated_at.

## Screen Sources

- Overview and priority queue: user-authorized SQL warehouse queries over governed gold tables.
- Case workspace: governed gold evidence plus mutable Lakebase workflow and history.
- Ask Genie: governed Genie space with answer, table, and generated SQL shown in the AppKit chat surface.
