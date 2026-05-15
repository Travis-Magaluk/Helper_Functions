"""
Commercial historic tax credit audit pipeline and helpers.

Typical workflow:
    1. Load the raw NPS quarterly Excel export into a DataFrame.
    2. Call decision_audit_pipeline() to find decisions missing from CRIS.
    3. Manually enter decisions and NPS numbers into CRIS. 
    4. Call database_health_pipeline() for financials, duplicate NPS numbers, and spatial checks.

Public API — pipeline functions (high-level, call these directly):
    decision_audit_pipeline              — end-to-end missing-decision audit; exports CSV
    database_health_pipeline             — three database health checks; exports CSV or Excel
    get_list_missing_nps_project_numbers — quick lookup of NPS numbers absent from CRIS

Public API — helper functions (lower-level; used by the pipelines but also useful standalone):
    standardize_nps_quarterly_reports    — normalize raw NPS sheet column names and values
    convert_wide_tall_decisions          — pivot wide Part1/2/3 columns to tall format
    ensure_correct_datatypes             — align dtypes between spreadsheet and DB DataFrames
    find_missing_decisions_with_date_buffer — core diff logic with configurable day tolerance
"""
from Helper_Functions.audit.commercial_audit_pipeline import (
    decision_audit_pipeline,
    database_health_pipeline,
    get_list_missing_nps_project_numbers,
)
from Helper_Functions.audit.commercial_audit import (
    standardize_nps_quarterly_reports,
    convert_wide_tall_decisions,
    ensure_correct_datatypes,
    find_missing_decisions_with_date_buffer,
)

__all__ = [
    "decision_audit_pipeline",
    "database_health_pipeline",
    "get_list_missing_nps_project_numbers",
    "standardize_nps_quarterly_reports",
    "convert_wide_tall_decisions",
    "ensure_correct_datatypes",
    "find_missing_decisions_with_date_buffer",
]
