# Core Audit Helpers

**Module:** `Helper_Functions.audit.commercial_audit`

These are the individual step functions composed by the pipeline. You can call them directly if you need finer control over the audit workflow.

---

## `standardize_nps_quarterly_reports()`

Normalize a raw NPS quarterly spreadsheet to canonical column names and types.

```python
import Helper_Functions.audit.commercial_audit as ca
import Helper_Functions.audit.commercial_lists_dicts as cld

standardized = ca.standardize_nps_quarterly_reports(
    nps_report=raw_df,
    nps_report_keep_columns=cld.nps_report_keep_columns,
    nps_report_column_standardization=cld.nps_report_column_standardization,
    decision_mapping_rename=cld.decision_mapping_rename,
    date_cols=cld.date_cols,
)
```

**What it does:**
- Selects the columns listed in `nps_report_keep_columns`
- Renames them using `nps_report_column_standardization`
- Normalizes decision text using `decision_mapping_rename`
- Coerces ZIP to nullable `Int64`
- Parses date columns to `datetime`
- Filters to rows where `State == "NY"`

---

## `convert_wide_tall_decisions()`

Convert wide Part1/Part2/Part3 decision columns into a tall, database-friendly format.

```python
tall_decisions = ca.convert_wide_tall_decisions(standardized)
```

**Input columns required:** `NPSProjectNumber`, `Part1Decision`, `Part1DateDecision`, `Part2Decision`, `Part2DateDecision`, `Part3Decision`, `Part3DateDecision`

**Output columns:** `NPSProjectNumber`, `TaxCreditPart` (int 1–3), `Decision`, `DateDecision`

---

## `ensure_correct_datatypes()`

Coerce datatypes so spreadsheet and database DataFrames can be compared meaningfully.

```python
spreadsheet_df, database_df = ca.ensure_correct_datatypes(
    df_spreadsheet=tall_decisions,
    df_database=database_decisions,
)
```

Casts `NPSProjectNumber` and `TaxCreditPart` to nullable `Int64`, strips whitespace from `Decision` strings, and converts `DateDecision` to `datetime.date`.

---

## `find_missing_decisions_with_date_buffer()`

Core diff function — finds spreadsheet rows whose (project, part, decision, date) combination is not present in the database.

```python
missing = ca.find_missing_decisions_with_date_buffer(
    df_spreadsheet=spreadsheet_df,
    df_database=database_df,
    date_buffer_days=7,
    restrict_to_existing_projects=False,
    match_on_month_year=True,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `df_spreadsheet` | `pd.DataFrame` | required | Tall decisions from the NPS sheet |
| `df_database` | `pd.DataFrame` | required | Tall decisions from CRIS |
| `date_buffer_days` | `int` | `0` | Day tolerance when `match_on_month_year=False` |
| `restrict_to_existing_projects` | `bool` | `False` | Only check projects already in CRIS |
| `match_on_month_year` | `bool` | `False` | Match by month/year only (ignores day) (default and recommended behavior) |

**Returns:** `pd.DataFrame` — filtered spreadsheet rows with no match in the database.

---

## `join_CRIS_PR_numbers()`

Enrich a DataFrame containing `NPSProjectNumber` with `ProjectNum` from CRIS.

```python
enriched = ca.join_CRIS_PR_numbers(missing_decisions)
```

`ProjectNum` is placed as the first column to make triage easier. Uses a left merge so rows without a match remain present with `ProjectNum = NaN`.

---

## Database health check functions

These functions query the database and print a summary count to stdout.

### `find_missing_financials_housing(pr_exclude_list=[])`

Finds Part 2/3 commercial projects with incomplete financial or housing fields.

```python
df = ca.find_missing_financials_housing(pr_exclude_list=["25PR0001"])
```

### `find_duplicate_nps_numbers()`

Finds `NPSProjectNumber` values appearing more than once in CRIS.

```python
df = ca.find_duplicate_nps_numbers()
```

### `check_nonspatial_usn()`

Finds commercial tax credit projects linked to USN records with no spatial geometry.

```python
df = ca.check_nonspatial_usn()
```
