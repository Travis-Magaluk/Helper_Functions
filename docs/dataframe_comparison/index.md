# DataFrame Comparison

The `dataframe_comparison/` module provides a framework for comparing two DataFrames column by column and analyzing the resulting differences. It is particularly useful for reconciling data between a spreadsheet source and a database source or multiple spreadsheet sources.

---

## Modules

| File | Purpose |
|---|---|
| `compare_columns.py` | Core comparison functions and comparison-dict runner |
| `difference_reporting.py` | Difference analysis and summary reporting |
| `legacy_comp_cols.py` | Legacy pipeline (superseded; kept for reference) |

!!! warning
    `legacy_comp_cols.py` is an older pipeline kept for reference on prior analysis notebooks. Prefer `compare_columns.py` and `difference_reporting.py` for new work.

---

## The comparison dictionary

All comparison functions are driven by a `comp_dict` that describes how each column pair should be compared. Each top-level key is the name of a new reconciled column that the comparison will produce. The value is either a per-column spec or `None`.

```python
comp_dict = {
    "RehabCost": {
        "columns": ["XLSX_RehabCost", "CRIS_RehabCost"],
        "type": "numerical",
        "margin": 5,          # allow up to 5% relative difference
        "default_first": False,
    },
    "Decision": {
        "columns": ["XLSX_Decision", "CRIS_Decision"],
        "type": "string",
        "default_first": True,  # use XLSX value on mismatch
    },
    "ProjectNum": None,  # stand-alone identifier — pass through, no comparison
}
```

### Spec fields

| Field | Required | Description |
|---|---|---|
| `columns` | yes | `[left_col, right_col]`. Order matters because `default_first` refers to the first entry. |
| `type` | yes | `"string"` or `"numerical"` — selects which comparison function runs. |
| `margin` | numerical only | Percent tolerance (e.g. `5` = within 5% of the two values' average). `0` requires an exact match. |
| `default_first` | yes | If the two sources disagree, return the left value instead of the `"DIFFERENT"` sentinel. |

### Stand-alone entries (`None`)

Entries whose value is `None` (like `ProjectNum` above) are "stand-alone" — typically identifier columns. They participate in column ordering but no comparison is run, so the column passes through unchanged.

A full worked example lives in `dataframe_comparison/comparison_dict_example.py` — see that file for a real audit's mix of margins and types.

---

## See also

- [Comparing Columns](comparing-columns.md) — running comparisons, generating comparison dicts
- [Difference Reporting](difference-reporting.md) — summarizing and analyzing discrepancies
