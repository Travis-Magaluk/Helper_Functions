# Difference Reporting

**Module:** `Helper_Functions.dataframe_comparison.difference_reporting`

After running a comparison, these functions summarize and analyze the discrepancies.

!!! note "Dependency chain"
    Most functions on this page (`report_difference`, `sum_top_x_differences`, `compare_multiple_x_values`, `analyze_difference_reduction`) expect `_difference` columns to already exist on the DataFrame. Run `compare_columns_with_difference()` first to populate them.

---

## `compare_columns_with_difference()`

Add a `_difference` column for each numerical comparison and reorder the DataFrame so source columns, comparison column, and difference column appear together.

```python
import Helper_Functions.dataframe_comparison.difference_reporting as dr

expanded_df = dr.compare_columns_with_difference(compared_df, comp_dict)
```

For each numerical entry in `comp_dict`, a new column `f"{key}_difference"` holds the absolute difference between the two source values — but **only for rows the reconciliation tagged `"DIFFERENT"`**. Rows that matched or were filled from a single side are left as `None` in the difference column, since their gap isn't meaningful.

Column order becomes: `XLSX_col`, `CRIS_col`, `ComparisonKey`, `ComparisonKey_difference` for each numerical column. Columns not referenced by `comp_dict` are appended at the end in their original order. The input DataFrame is not mutated — a copy is returned.

---

## `report_number_DIFFERENT_values()`

Quick count of how many `"DIFFERENT"` values appear in each comparison column. Useful as a first pass to identify the noisiest fields before drilling into magnitudes.

```python
diff_counts = dr.report_number_DIFFERENT_values(comp_dict, compared_df)
print(diff_counts)
#         Column  Values
# 0   RehabCost      14
# 1    Decision       3
```

Every key in `comp_dict` is iterated (including stand-alone `None` entries, whose count will be zero), so the output stays aligned with the dictionary.

---

## `report_difference()`

Summarize the total dollar (or numeric) difference for each numerical column.

```python
summary = dr.report_difference(expanded_df, comp_dict)
print(summary)
#   Numerical Column  Difference     Total  Percent Difference
# 0       RehabCost   125000.0  8500000.0               1.471
```

!!! info "Why `max(sum(col1), sum(col2))` for `Total`"
    The percent denominator is the larger of the two source columns' sums, not the average. Picking the max gives a conservative (smaller) percent figure when the two source totals disagree — i.e. it won't overstate how divergent the data is.

---

## `sum_top_x_differences()`

Find the sum of the top `x` largest individual discrepancies for each numerical column, alongside the sum of everything outside that top group.

```python
top5 = dr.sum_top_x_differences(expanded_df, comp_dict, x=5)
print(top5)
#   Numerical Column  Top 5 Sum  Remaining Sum (5)
# 0       RehabCost   98000.0            27000.0
```

Useful for answering "if I manually reconciled the worst N rows, how much disagreement would remain?" The column headers embed `x` so multiple calls can be merged without name collisions.

---

## `compare_multiple_x_values()`

Run `sum_top_x_differences()` for several `x` values and outer-merge the results on `"Numerical Column"`, so each row shows how a single column's disagreement breaks down at different thresholds.

```python
multi = dr.compare_multiple_x_values(expanded_df, comp_dict, x_values=[5, 10, 20])
```

The outer join means a column that appears in some calls but not others (for instance, one with fewer than `x` differences) is still represented.

---

## `analyze_difference_reduction()`

Comprehensive report showing what happens to the total discrepancy as you resolve the top 5, 10, 20, etc. differences.

```python
reduction = dr.analyze_difference_reduction(expanded_df, comp_dict, x_values=[5, 10, 20])
print(reduction)
```

| Column | Original Difference | Total Sum | Original % Diff | Reduction (Top 5) | New % Diff (After 5) | ... |
|---|---|---|---|---|---|---|
| RehabCost | 125000 | 8500000 | 1.471 | 98000 | 0.318 | ... |

For each `x`, the top `x` absolute differences are summed (`nlargest`) and treated as "resolved" — subtracted from the original total to compute the new total and new percent. `Total Sum` uses the same `max(sum(col1), sum(col2))` convention as `report_difference()` to keep the percent conservative. All numeric outputs are rounded (two decimals for sums, three for percents).

Use this to prioritize which discrepancies to investigate first — a small number of records often account for the majority of the difference.
