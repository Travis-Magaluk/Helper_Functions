# Audit

The `audit/` module supports the quarterly NPS commercial tax credit decision audit workflow. It compares decisions recorded in NPS quarterly spreadsheets against decisions in the CRIS database and flags discrepancies.

---

## Workflow overview

```
NPS quarterly Excel/CSV
        │
        ▼
standardize_nps_quarterly_reports()   ← normalizes columns, decision values, dates
        │
        ▼
convert_wide_tall_decisions()         ← Part1/2/3 columns → tall format
        │
        ▼
database decisions (from CRIS)
        │
        ▼
ensure_correct_datatypes()            ← align dtypes for comparison
        │
        ▼
find_missing_decisions_with_date_buffer()  ← core diff (with date tolerance)
        │
        ▼
join_CRIS_PR_numbers()                ← attach internal project numbers
        │
        ▼
CSV / Excel output
```

The `decision_audit_pipeline()` function in `commercial_audit_pipeline.py` executes all of these steps in sequence.

---

## Modules

| File | Contents |
|---|---|
| `commercial_audit_pipeline.py` | High-level orchestration functions |
| `commercial_audit.py` | Individual helper functions for each audit step |
| `commercial_lists_dicts.py` | Column name mappings and decision normalization constants |
| `commercial_sql.py` | SQL query strings (decisions, NPS mapping, health checks) |

---

## See also

- [Pipeline Functions](pipeline.md) — `decision_audit_pipeline()`, `database_health_pipeline()`
- [Core Helpers](helpers.md) — individual step functions
- [Configuration Constants](configuration.md) — `commercial_lists_dicts` reference
