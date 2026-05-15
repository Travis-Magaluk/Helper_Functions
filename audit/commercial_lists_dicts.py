"""
Lists and dictionaries used to standardize and parse NPS quarterly commercial reports.

Contents:
- nps_report_keep_columns: column names to keep from raw NPS sheet (raw header names).
- nps_report_column_standardization: maps raw header names -> canonical internal column names.
- decision_mapping_rename: maps many raw decision text variants to a small set of canonical values.
- date_cols: list of canonical date column names that should be parsed as dates.

These constants are consumed by the audit pipeline (standardization, conversion, and comparison).
DO NOT change keys/values here unless you also update any downstream code or management mappings.
"""

# Raw NPS spreadsheet column names to keep when loading a sheet.
# These are the column headers as they appear in the exported NPS quarterly Excel/CSV.
nps_report_keep_columns = [
    'WASO NUMBER', 'BUILDING NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP Code',
       'ESTIMATED COST', 'PT1 App', 'PT1 DEC',
       'PT2 App', 'PT2 DEC', 'PT3 App', 'PT3 DEC'
]

# Mapping from the raw NPS spreadsheet column names -> canonical column names used across this project.
# After loading the raw sheet, call .rename(columns=nps_report_column_standardization) so downstream
# functions always reference the same column names.
nps_report_column_standardization = {
    'WASO NUMBER': 'NPSProjectNumber', 
    'BUILDING NAME': 'BuildingName', 
    'ADDRESS': 'Address', 
    'CITY': 'City', 
    'STATE': 'State', 
    'ZIP Code': 'ZIP',
    'ESTIMATED COST': 'EstimatedRehabCost', 
    'PT1 App': 'Part1Decision', 
    'PT1 DEC': 'Part1DateDecision',
    'PT2 App': 'Part2Decision', 
    'PT2 DEC': 'Part2DateDecision', 
    'PT3 App': 'Part3Decision', 
    'PT3 DEC': 'Part3DateDecision'
}

# Normalize decision text values found on the raw NPS sheet into a controlled vocabulary.
# Left side: raw values seen in spreadsheets (case-sensitive as they appear). Right side: canonical label.
# The canonical values are used by comparison logic and by the DB import logic.
decision_mapping_rename = {
    # Clear, simple mappings for common statuses
    'APPROVE': 'Approve',
    'CONDITIONAL APPROVAL': 'CA',
    'DENY': 'Deny',

    # Long-form variations that map to the same canonical statuses
    'APPROVED, UPON LISTING ON THE NATIONAL REGISTER OF HISTORIC PLACES': 'CA',

    # Less-common statuses mapped to a prefixed 'Status:' label so they are distinct from actionable decisions
    'WITHDRAWN': 'Status: Withdrawn',
    'INFO RECV': 'Status: Info Recv',
    'MORE INFO': 'Status: More Info Needed',
    'APP INCOMPLETE': 'Status: Application Incomplete',
    'NO ACTION NEEDED': 'Status: No Action Needed'
}

# Canonical names of the date columns we expect after renaming.
# These are parsed by the standardization function and converted to datetime.
date_cols = ['Part1DateDecision', 'Part2DateDecision', 'Part3DateDecision']