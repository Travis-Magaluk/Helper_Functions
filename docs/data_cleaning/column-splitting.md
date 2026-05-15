# Column Splitting

**Module:** `Helper_Functions.data_cleaning.column_splitting`

Utilities for decomposing complex columns into structured parts without changing the row count.

---

## `split_check_date_column()`

Split a column containing mixed check numbers, dates, and other text into three separate columns.

```python
import Helper_Functions.data_cleaning.column_splitting as cs

df = cs.split_check_date_column(
    df,
    to_split_column_name="PaymentInfo",
    new_check_col="CheckNumber",
    new_date_col="PaymentDate",
    new_others_col="OtherInfo",
)
```

Patterns used:
- **Check numbers:** `#\d+` (e.g. `#12345`)
- **Dates:** `MM/DD/YY`, `MM/DD/YYYY`, or `YYYY-MM-DD`
- **Others:** anything that doesn't match either pattern

---

## `split_owner_name()`

Split the `OwnerName` column into `O_FirstName_D` and `O_LastName_D` on the first space. The original `OwnerName` column is dropped.

```python
df = cs.split_owner_name(df)
```

**Raises:** `ValueError` if `OwnerName` does not exist in the DataFrame.

---

## `split_shpo_column()`

Split a column into project number type categories based on pattern matching.

```python
df = cs.split_shpo_column(
    df,
    to_split_column_name="ProjectReference",
    pr_col_name="PRNumber",
    itc_col_name="ITCNumber",
    other_col_name="OtherReference",
)
```

Patterns:
- **PR:** values matching `^\d{2}PR` (e.g. `25PR0123`)
- **ITC:** values matching `^\d{2}ITC` (e.g. `24ITC0045`)
- **Other:** anything not matching the above

The original column is dropped. Unmatched rows in each category receive `NaN`.

---

## `split_decision_date(value)`

Split a string containing a decision label and an embedded date into two values. Designed for use with `df.apply(..., result_type="expand")`.

```python
df[["Decision", "DecisionDate"]] = df["RawDecision"].apply(cs.split_decision_date)
```

| Input | Decision output | Date output |
|---|---|---|
| `"Approve 3/15/24"` | `"Approve"` | `"3/15/24"` |
| `"CA"` | `"CA"` | `NaN` |
| `"Approve 3/15/24 4/1/24"` | `"more than one decision"` | `"more than one date"` |
| `NaN` | `NaN` | `NaN` |
