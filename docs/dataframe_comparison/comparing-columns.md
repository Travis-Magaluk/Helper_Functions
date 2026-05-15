# Comparing Columns

**Module:** `Helper_Functions.dataframe_comparison.compare_columns`

---

## `run_comparison_and_reorder()`

The main entry point: applies all comparisons defined in `comp_dict`, creates new reconciled columns, and reorders the DataFrame so each reconciled column sits directly after the two source columns it was derived from.

```python
import Helper_Functions.dataframe_comparison.compare_columns as cc

compared_df = cc.run_comparison_and_reorder(comp_dict, df)
```

Each key in `comp_dict` becomes a new column. The value in each row depends on how the two source values relate:

- The matching value if the two source columns agree (or are within the margin)
- The larger of the two values if a numerical pair is within `margin` but not exactly equal — the function favors the bigger figure
- The non-NaN value if exactly one side is NaN (default behavior)
- `"DIFFERENT"` if they disagree beyond the margin and `default_first=False`
- The left column's value if they disagree and `default_first=True`
- `np.nan` if both source values are NaN
- `"Invalid Value"` (numerical only) if a value cannot be cast to `float`

Entries in `comp_dict` whose value is `None` are skipped — no column is created but the key still participates in the final column ordering.

### Strict NaN mode

By default, a NaN in one column and a value in the other is resolved by returning the non-NaN value. Pass `strict_nan_compare=True` to treat this case as `"DIFFERENT"` instead:

```python
compared_df = cc.run_comparison_and_reorder(comp_dict, df, strict_nan_compare=True)
```

Use this when a missing value on one side should be treated as a real disagreement rather than silently filled from the other side.

---

## `generate_comparison_dict()`

Auto-generate a `comp_dict` template from a list of base column names. Each base name is paired with its prefixed left/right versions, so this works hand-in-hand with `rename_columns_with_prefix()` below.

```python
columns = ["RehabCost", "Decision", "ZipCode", "ProjectNum"]
comp_dict = cc.generate_comparison_dict(
    columns=columns,
    left_prefix="XLSX_",
    right_prefix="CRIS_",
    string_columns={"Decision"},
    none_columns={"ProjectNum"},   # pass through without comparing
)
```

This produces:

```python
{
    "RehabCost": {"columns": ["XLSX_RehabCost", "CRIS_RehabCost"], "type": "numerical", "margin": 0, "default_first": False},
    "Decision":  {"columns": ["XLSX_Decision",  "CRIS_Decision"],  "type": "string",    "margin": None, "default_first": False},
    "ZipCode":   {"columns": ["XLSX_ZipCode",   "CRIS_ZipCode"],   "type": "numerical", "margin": 0, "default_first": False},
    "ProjectNum": None,
}
```

### Defaults

| Field | Default |
|---|---|
| `type` | `"numerical"` unless the column is in `string_columns` |
| `margin` | `0` (exact match) for numerical entries; `None` for string entries |
| `default_first` | `False` |

`margin` and `default_first` can be tuned per-entry after generation — the function returns a regular dict you can edit.

---

## `rename_columns_with_prefix()`

Add a prefix to all column names except those in `exclude_columns`. Use this before merging two DataFrames so their columns can be compared side by side.

```python
xlsx_df = cc.rename_columns_with_prefix(xlsx_df, prefix1="XLSX_", exclude_columns={"ProjectNum"})
cris_df = cc.rename_columns_with_prefix(cris_df, prefix1="CRIS_", exclude_columns={"ProjectNum"})

merged = xlsx_df.merge(cris_df, on="ProjectNum", how="outer")
```

---

## Low-level comparison functions

These are used internally by `run_comparison_and_reorder()` but can be called directly with `df.apply()`.

### `compare_string_columns(row, column_1, column_2, default_first, strict_nan)`

Reconciles a pair of string columns row-by-row using the following resolution order:

1. Values are equal → return that value.
2. Both NaN → `np.nan`.
3. `strict_nan=True` and exactly one side is NaN → `"DIFFERENT"`.
4. One side is NaN → return the non-NaN value.
5. Otherwise the values disagree → return the left value if `default_first=True`, else `"DIFFERENT"`.

```python
df["DecisionComp"] = df.apply(
    cc.compare_string_columns,
    args=("XLSX_Decision", "CRIS_Decision", True, False),
    axis=1,
)
```

### `compare_numerical_columns(row, column_1, column_2, margin, default_first, strict_nan)`

Reconciles a pair of numerical columns with a percent-based tolerance. Resolution order:

1. Both NaN → `np.nan`.
2. `strict_nan=True` and exactly one side is NaN → `"DIFFERENT"`.
3. One side is NaN → return the non-NaN value.
4. Either value cannot be cast to `float` → `"Invalid Value"`.
5. Values are exactly equal → return that value.
6. Relative difference (`abs(v1 - v2) / average`) is within `margin / 100` → return `max(v1, v2)`. The function favors the larger figure when both sources are "close enough."
7. Otherwise → return the left value if `default_first=True`, else `"DIFFERENT"`.

```python
df["CostComp"] = df.apply(
    cc.compare_numerical_columns,
    args=("XLSX_Cost", "CRIS_Cost", 5, False, False),  # 5% margin
    axis=1,
)
```

### `compare_zip_codes(row, column_1, column_2)`

Handles 5-digit and 9-digit (`XXXXX-XXXX`) ZIP codes. Hyphens and surrounding whitespace are stripped before length comparison, so two zip codes match when their first five digits agree. When one side is 9-digit and the other is 5-digit (and prefixes match), the 9-digit form is returned — the function prefers the more specific representation.

Returns `"DIFFERENT"` when prefixes don't match or the lengths are unexpected. If a single side is NaN, the other side is returned; if both sides are NaN, the function falls through to `"DIFFERENT"`, so filter empty rows beforehand if you need `np.nan` there.

```python
df["ZipComp"] = df.apply(
    cc.compare_zip_codes,
    args=("XLSX_Zip", "CRIS_Zip"),
    axis=1,
)
```

### `compare_decsision_date(row, decision_1_col, decision_date_1_col, decision_2_col, decision_date_2_col, day_margin)`

Reconciles a paired *(decision, date)* tuple from two sources. Returns a two-element `pd.Series` intended to be unpacked into two new DataFrame columns.

**Decision resolution:** both NaN → `np.nan`; one NaN → the non-NaN value; both equal → that value; both present and unequal → `"Different"`.

**Date resolution** (dates parsed with `pd.to_datetime(errors='coerce')`, so unparseable strings behave like NaN): both NaN → `np.nan`; one NaN → the other formatted `'%Y-%m-%d'`; within `day_margin` days → `date_1` formatted `'%Y-%m-%d'`; beyond `day_margin` → `"Date Mismatch"`.

```python
df[["DecisionFinal", "DecisionDateFinal"]] = df.apply(
    cc.compare_decsision_date,
    args=("XLSX_Decision", "XLSX_Date", "CRIS_Decision", "CRIS_Date", 7),  # 7-day tolerance
    axis=1,
)
```

---

## `create_new_dataframe_with_new_columns_only()`

Reduce the compared DataFrame to only the reconciled columns (keys of `comp_dict`). Includes both reconciled comparison columns and any "stand-alone" identifier keys (entries whose value is `None`).

```python
summary_df = cc.create_new_dataframe_with_new_columns_only(comp_dict, compared_df)
```

Typically called after `run_comparison_and_reorder()` and any manual review, when the full source columns are no longer needed.
