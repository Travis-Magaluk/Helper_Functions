# Text Cleaning

**Modules:** `text_clean`, `safe_text_clean`, `text_clean_pipeliness`

---

## NaN-safe primitives — `safe_text_clean`

Low-level functions that operate on individual values and preserve `NaN` through the operation. Use these with `df.apply()` or as building blocks for pipelines.

```python
import Helper_Functions.data_cleaning.safe_text_clean as stc

df["Address"] = df["Address"].apply(stc.safe_lower)
df["Address"] = df["Address"].apply(stc.safe_strip)
df["Name"] = df["Name"].apply(stc.safe_title)
```

| Function | Description |
|---|---|
| `safe_lower(text)` | Lowercase; preserves NaN |
| `safe_strip(text)` | Strip whitespace; preserves NaN |
| `safe_title(text)` | Title case; preserves NaN |
| `safe_remove_quotes(text)` | Remove `"` characters; preserves NaN |

---

## Address normalization — `text_clean`

Functions for normalizing street addresses to a consistent format.

```python
import Helper_Functions.data_cleaning.text_clean as tc

# Expand street abbreviations
# "123 main st" → "123 main street"
df["Address"] = df["Address"].apply(tc.replace_abbrivations)

# Expand cardinal directions
# "123 n main street" → "123 north main street"
df["Address"] = df["Address"].apply(tc.replace_directionality)

# Standardize "HD" to "Historic District"
df = tc.replace_standardize_historic_district(df, ["ResourceName"])

# Format phone numbers
# "(518) 474-0479" → "518-474-0479"
df["Phone"] = df["Phone"].apply(tc.standardize_phone_number)
```

| Function | Description |
|---|---|
| `replace_abbrivations(text)` | Expands street abbreviations (`st→street`, `ave→avenue`, etc.) |
| `replace_directionality(text)` | Expands cardinal directions (`n→north`, `s→south`, etc.) |
| `remove_some_punctuation(text)` | Removes double-quote characters |
| `replace_hashtag(text)` | Replaces `#` with a space |
| `clean_hyphens_decisions(value)` | Replaces hyphens with spaces |
| `remove_periods_from_abbreviations(text)` | Removes trailing periods from spelled-out words |
| `replace_standardize_historic_district(df, cols)` | Standardizes `HD` → `Historic District` in column(s) |
| `standardize_phone_number(phone)` | Formats 10-digit phone as `XXX-XXX-XXXX` |

---

## Composed pipelines — `text_clean_pipeliness`

Pre-built chains of the primitives above for common use cases.

### `full_address_clean(df, column_names)`

Full address normalization pipeline: lowercase → strip → remove punctuation → expand abbreviations → expand directions.

```python
import Helper_Functions.data_cleaning.text_clean_pipeliness as tcp

df = tcp.full_address_clean(df, ["Address", "MailingAddress"])
```

### `standardize_text(df, column_names)`

Title case + strip whitespace. Use for name fields or other free-text columns.

```python
df = tcp.standardize_text(df, ["BuildingName", "City"])
```

### `remove_periods_from_abbreviations_full(df, column_names)`

Removes trailing periods from common directional and street-type words. Pipeline: lowercase → strip → remove periods → title case.

```python
df = tcp.remove_periods_from_abbreviations_full(df, ["Address"])
```
