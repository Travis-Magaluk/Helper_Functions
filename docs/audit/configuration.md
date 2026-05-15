# Configuration Constants

**Module:** `Helper_Functions.audit.commercial_lists_dicts`

This module holds the configuration dictionaries and lists that drive the NPS quarterly report standardization pipeline. Edit these constants to adapt the pipeline when NPS changes its column names or decision vocabulary.

---

## `nps_report_keep_columns`

List of raw NPS spreadsheet column names to retain when loading a quarterly export.

```python
nps_report_keep_columns = [
    'WASO NUMBER', 'BUILDING NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP Code',
    'ESTIMATED COST', 'PT1 App', 'PT1 DEC',
    'PT2 App', 'PT2 DEC', 'PT3 App', 'PT3 DEC'
]
```

---

## `nps_report_column_standardization`

Maps raw NPS column headers to canonical internal column names.

| Raw name | Canonical name |
|---|---|
| `WASO NUMBER` | `NPSProjectNumber` |
| `BUILDING NAME` | `BuildingName` |
| `ADDRESS` | `Address` |
| `CITY` | `City` |
| `STATE` | `State` |
| `ZIP Code` | `ZIP` |
| `ESTIMATED COST` | `EstimatedRehabCost` |
| `PT1 App` | `Part1Decision` |
| `PT1 DEC` | `Part1DateDecision` |
| `PT2 App` | `Part2Decision` |
| `PT2 DEC` | `Part2DateDecision` |
| `PT3 App` | `Part3Decision` |
| `PT3 DEC` | `Part3DateDecision` |

---

## `decision_mapping_rename`

Normalizes raw decision text values from NPS spreadsheets to a controlled vocabulary.

| Raw value | Canonical value |
|---|---|
| `APPROVE` | `Approve` |
| `CONDITIONAL APPROVAL` | `CA` |
| `DENY` | `Deny` |
| `APPROVED, UPON LISTING ON THE NATIONAL REGISTER...` | `CA` |
| `WITHDRAWN` | `Status: Withdrawn` |
| `INFO RECV` | `Status: Info Recv` |
| `MORE INFO` | `Status: More Info Needed` |
| `APP INCOMPLETE` | `Status: Application Incomplete` |
| `NO ACTION NEEDED` | `Status: No Action Needed` |

!!! warning
    This mapping is case-sensitive. Raw values must match exactly as they appear in the NPS export. If NPS changes a value's formatting, add the new variant here.

NOTE: Status columns are not stored within CRIS, but helpful to note. Future work is to add functionality to tracking project statuses over time. 

---

## `date_cols`

Canonical names of the date columns parsed as `datetime` during standardization.

```python
date_cols = ['Part1DateDecision', 'Part2DateDecision', 'Part3DateDecision']
```
