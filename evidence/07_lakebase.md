Generated 2026-11-19T20:32:34Z by tools/generate_evidence.py from the live workspace

# Lakebase Operational Serving

This file proves live operational counts, uniqueness, preserved human-owned workflow fields, immutable change history, and the final OAuth-authenticated sync result.

## Operational Summary

| case_count | estimated_exposure | duplicate_business_keys |
| --- | --- | --- |
| 20 | 893017.75 | 0 |

## Counts by Status

| status | case_count |
| --- | --- |
| IN_REVIEW | 1 |
| NEW | 19 |

## Human Edit Read-Back

| status | owner_preserved | notes_preserved | due_date | last_updated |
| --- | --- | --- | --- | --- |
| IN_REVIEW | True | True | 2026-11-25 | 2026-11-19 19:44:38.721667+00:00 |

## Recent Immutable History

| event_type | change_source | changed_columns | changed_at |
| --- | --- | --- | --- |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | ai_next_action, source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |
| UPDATE | SYNC | source_explained_at, source_refreshed_at, source_scored_at, updated_at | 2026-11-19 19:44:38.721667+00:00 |

## Final Sync Exit Value

Task run `561038139248061` from job run `806236758003209`:

```json
{
  "notebook_result": {
    "case_rows": 20,
    "endpoint": "projects/rebate-fraud-ops/branches/production/endpoints/primary",
    "history_rows": 82,
    "inserted_rows": 0,
    "source_rows": 20
  }
}
```

The connection used a newly generated OAuth database credential with `sslmode=require`; no static password was read or written.
