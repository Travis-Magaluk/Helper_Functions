# Money & Dates

**Modules:** `money_clean`, `date_clean`

---

## Monetary value cleaning — `money_clean`

```python
import Helper_Functions.data_cleaning.money_clean as mc
```

### `full_money_clean(df, column_names)`

Clean monetary values in one or more columns: removes `$` signs, commas, and strips whitespace.

```python
df = mc.full_money_clean(df, ["EstimatedRehabCost", "ApprovedAmount"])
```

| Parameter | Type | Description |
|---|---|---|
| `df` | `pd.DataFrame` | Input DataFrame |
| `column_names` | `list` | Columns to clean |

**Returns:** `pd.DataFrame` with cleaned monetary columns.

### `remove_money_punc_and_decimals(text)`

Remove `$` and `,` from a single value. NaN is preserved.

```python
# "$1,250,000" → "1250000"
clean = mc.remove_money_punc_and_decimals("$1,250,000")
```

### `extract_highest(value)`

Extract the maximum value from a semicolon-separated string of numbers. Returns `np.nan` if conversion fails.

```python
# "500000;750000;620000" → "750000"
highest = mc.extract_highest("500000;750000;620000")
```

---

## Date format conversion — `date_clean`

```python
import Helper_Functions.data_cleaning.date_clean as dc
```

### `convert_address_date(date_str)`

Convert a date string from `"9-Feb-12"` format (day-MonthAbbr-year) to `"2/9/12"` (MM/DD/YY). NaN values and unparseable strings are returned as-is.

```python
# "9-Feb-12" → "2/9/12"
converted = dc.convert_address_date("9-Feb-12")
```

```python
# Apply to a column
df["InspectionDate"] = df["InspectionDate"].apply(dc.convert_address_date)
```

| Input | Output |
|---|---|
| `"9-Feb-12"` | `"02/09/12"` |
| `"15-Mar-24"` | `"03/15/24"` |
| `NaN` | `NaN` |
| `"2024-01-15"` (unparseable format) | `"2024-01-15"` (unchanged) |
