# Audit Pipeline Functions

**Module:** `Helper_Functions.audit.commercial_audit_pipeline`

---

## `decision_audit_pipeline()`

End-to-end audit pipeline: standardizes the NPS quarterly report, compares it to CRIS decisions, and optionally exports results to CSV.

### Usage

```python
import pandas as pd
import Helper_Functions.audit.commercial_audit_pipeline as cap

nps_report = pd.read_excel("data/input/2025_Q1_NPS_Report.xlsx")

missing_decisions, missing_nps_numbers = cap.decision_audit_pipeline(
    NPS_quarterly_report=nps_report,
    date_buffer=7,
    year=2025,
    quarter=1,
)
```

When `year` and `quarter` are provided, the function exports:

```
data/output/2025_Q1/2025_Q1_Missing_Decisions.csv
```

### Steps performed

1. Standardize column names and decision values using `commercial_lists_dicts` constants.
2. Convert wide Part1/2/3 decision columns to tall format.
3. Load existing decisions from CRIS.
4. Align datatypes between spreadsheet and database DataFrames.
5. Find NPS project numbers in the spreadsheet that are missing from CRIS.
6. Find spreadsheet decisions not present in CRIS (with `date_buffer` day tolerance).
7. Join internal `ProjectNum` values to the missing decisions for triage.
8. *(Optional)* Export to `data/output/{Year}_{Quarter}/`.

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `NPS_quarterly_report` | `pd.DataFrame` | required | Raw NPS quarterly report |
| `date_buffer` | `int` | required | Day tolerance for date matching |
| `match_on_month_year` | `bool` | True | Considers a decision date match to be the correct decision in the same month and year |
| `year` | `int` or `str` | `None` | Report year (triggers CSV export) |
| `quarter` | `int` or `str` | `None` | Report quarter (triggers CSV export) |
| `output_root` | `str` | `"data/output"` | Root output directory |

**Returns:** `Tuple[pd.DataFrame, List[int]]` — `(missing_decisions, missing_nps_numbers)`.

!!! tip
    Use `match_on_month_year=True` as a starting point. This is the recommended default behavior from management.  

---

## `database_health_pipeline()`

Run three database health checks and optionally export results to CSV or a single Excel workbook.

### Usage

```python
exclude = ["25PR0001", "24PR0099"]  # projects to skip in the financials check

missing_fin, dup_nps, nonspatial = cap.database_health_pipeline(
    PR_nums_exclude=exclude,
    year=2025,
    quarter=1,
    output_format="excel",  # or "csv"
)
```

### Checks performed

| Check | Description |
|---|---|
| Missing financials/housing | Part 2/3 projects with incomplete financial or housing fields |
| Duplicate NPS numbers | `NPSProjectNumber` values that appear more than once in CRIS |
| Non-spatial USNs | USN records with no spatial geometry linked to tax credit projects |

### Export output

**CSV mode** (`output_format="csv"`) creates three files:
```
data/output/2025_Q1/
├── 2025_Q1_Missing_Financials_Housing.csv
├── 2025_Q1_Duplicate_NPS_Numbers.csv
└── 2025_Q1_Nonspatial_USN.csv
```

**Excel mode** (`output_format="excel"`) creates one workbook with three sheets:
```
data/output/2025_Q1/2025_Q1_Database_Health.xlsx
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `PR_nums_exclude` | `list[str]` | required | ProjectNum values to skip in the financials check |
| `year` | `int` or `str` | `None` | Report year (triggers export) |
| `quarter` | `int` or `str` | `None` | Report quarter (triggers export) |
| `output_root` | `str` | `"data/output"` | Root output directory |
| `output_format` | `str` | `"csv"` | `"csv"` or `"excel"` |

**Returns:** `Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]` — `(missing_financials_housing, duplicate_nps_numbers, nonspatial_usn)`.

---

## `get_list_missing_nps_project_numbers()`

Quick utility to find NPS project numbers in a report that are not yet in CRIS.

```python
missing = cap.get_list_missing_nps_project_numbers(standardized_nps_report)
# also prints: Missing NPS Project Numbers in CRIS: [12345, 67890]
```

**Returns:** `List[int]` — NPS project numbers not found in `tblTaxCreditCommercial`.
