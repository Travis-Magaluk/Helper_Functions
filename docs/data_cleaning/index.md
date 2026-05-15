# Data Cleaning

The `data_cleaning/` module provides standalone, NaN-safe utilities for normalizing text, addresses, dates, monetary values, and columns. Functions are designed to work with `df.apply()` and preserve `NaN` values throughout.

---

## Modules

| File | Purpose |
|---|---|
| `text_clean.py` | Address and text normalization (directions, abbreviations, phone numbers) |
| `safe_text_clean.py` | NaN-safe primitives (lower, strip, title case, remove quotes) |
| `date_clean.py` | Date string format conversion |
| `money_clean.py` | Monetary value parsing and cleaning |
| `column_splitting.py` | Split a single column into multiple structured columns |
| `text_clean_pipeliness.py` | Composed pipelines that chain multiple cleaning steps |

## Design pattern

All single-value functions handle `NaN` explicitly by checking `pd.isna()` at the top:

```python
def safe_lower(text):
    return text.lower() if not pd.isna(text) else text
```

Column-level pipeline functions accept a DataFrame and a list of column names:

```python
def full_address_clean(df, column_names):
    for column in column_names:
        df[column] = df[column].apply(safe_lower)
        df[column] = df[column].apply(safe_strip)
        # ...
    return df
```

## See also

- [Text Cleaning](text-cleaning.md) — address normalization, phone numbers
- [Money & Dates](money-and-dates.md) — monetary values, date format conversion
- [Column Splitting](column-splitting.md) — splitting complex columns without exploding rows
