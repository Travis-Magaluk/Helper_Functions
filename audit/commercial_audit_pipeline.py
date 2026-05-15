"""
Pipeline helpers that compose functions from `commercial_audit`, `commercial_sql`, and
`commercial_lists_dicts` into higher-level audit workflows.

This module exposes:
- `get_list_missing_nps_project_numbers`: quick lookup of NPS project numbers not present in CRIS.
- `decision_audit_pipeline`: end-to-end pipeline to detect missing decisions between an NPS
  quarterly report and the database.
- `database_health_pipeline`: collection of database health checks (missing financials/housing,
  duplicate NPS numbers, non-spatial USNs).

Type hints are used throughout and functions return pandas DataFrames or lists for easy programmatic use.
"""
from typing import List, Tuple, Optional
from pathlib import Path

import Helper_Functions.audit.commercial_audit as ca
import Helper_Functions.audit.commercial_sql as cs
import Helper_Functions.audit.commercial_lists_dicts as cld

from Helper_Functions.database.database_connections import DBConnector
import pandas as pd


def get_list_missing_nps_project_numbers(nps_report: pd.DataFrame) -> List[int]:
    """Return NPS project numbers that appear in the provided NPS report but are not in CRIS.

    Parameters:
        nps_report: pandas DataFrame that must include an 'NPSProjectNumber' column.

    Returns:
        A list of NPSProjectNumber values (integers) that are in `nps_report` but not present
        in `tblTaxCreditCommercial` (CRIS).
    """
    db = DBConnector()

    # Read the canonical NPSProjectNumber values from the database
    nps_numbers = db.fetch_data('SELECT NPSProjectNumber from tblTaxCreditCommercial')

    # Build a set of known NPS numbers for fast membership testing
    known_projects = set(nps_numbers['NPSProjectNumber'].unique())
    
    # Find values in the provided report that are not in known_projects
    missing_nps_numbers = list(nps_report[~nps_report['NPSProjectNumber'].isin(known_projects)]['NPSProjectNumber'])

    # Print for interactive / script usage; returned value is the programmatic result
    print(f'Missing NPS Project Nubmers in CRIS: {missing_nps_numbers}')

    return missing_nps_numbers


def decision_audit_pipeline(
    NPS_quarterly_report: pd.DataFrame,
    date_buffer: int,
    match_on_month_year: Optional[bool] = True,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    output_root: str = "data/output"
) -> Tuple[pd.DataFrame, List[int]]:
    """Full decision audit pipeline.

    Steps performed:
      1. Standardize the incoming NPS quarterly report to canonical column names/types.
      2. Convert wide decision columns (Part1/2/3) to tall format.
      3. Load existing decisions from the database.
      4. Ensure comparable datatypes between spreadsheet and DB.
      5. Identify NPS project numbers that are missing from the database.
      6. Find decisions in the spreadsheet that are not present in the database (with date buffer).
      7. Join ProjectNum values for missing decisions for easier triage.
      8. (Optional) If `year` and `quarter` are provided, export missing decisions to:
         data/output/{Year}_{Quarter}/{Year}_Q{Quarter}_Missing_Decisions.csv

    Parameters:
        NPS_quarterly_report: Raw NPS quarterly report DataFrame.
        date_buffer: int number of days tolerance when comparing decision dates.
        match_on_month_year: optional bool (default: True) Defines a match as being in the same month and year. 
        year: optional int (e.g., 2025) or str for the report year. When provided with quarter, triggers CSV export.
        quarter: optional int (1-4) or str like 'Q1'. When provided with year, triggers CSV export.
        output_root: root output directory (default 'data/output').

    Returns:
        Tuple:
          - missing_decisions: pandas DataFrame with decisions that appear missing from CRIS.
          - missing_nps_numbers_from_CRIS: list of NPSProjectNumber values not found in CRIS.
    """
    # 1. Standardize columns and types for the incoming sheet
    standardized_nps_report = ca.standardize_nps_quarterly_reports(
        NPS_quarterly_report,
        cld.nps_report_keep_columns,
        cld.nps_report_column_standardization,
        cld.decision_mapping_rename,
        cld.date_cols
    )

    # 2. Convert the wide-form parts -> tall decisions table
    quarterly_report_decisions = ca.convert_wide_tall_decisions(standardized_nps_report)

    db = DBConnector()

    # 3. Fetch decisions currently in the database
    database_decisions = db.fetch_data(cs.decisions_sql)

    # 4. Harmonize datatypes between the two sources
    quarterly_report_decisions, database_decisions = ca.ensure_correct_datatypes(
        quarterly_report_decisions, database_decisions
    )

    # 5. Find NPS numbers present in the sheet but not in CRIS
    missing_nps_numbers_from_CRIS = get_list_missing_nps_project_numbers(quarterly_report_decisions)

    # 6. Compute missing decisions (respecting provided date buffer)
    missing_decisions = ca.find_missing_decisions_with_date_buffer(
        quarterly_report_decisions,
        database_decisions,
        date_buffer_days=date_buffer,
        restrict_to_existing_projects=False,
        match_on_month_year=match_on_month_year
    )

    # 7. Attach internal ProjectNum values to help triage the missing decisions
    missing_decisions = ca.join_CRIS_PR_numbers(missing_decisions)

    # 8. Optionally write CSV to data/output/{Year}_{Quarter}/Year_Q{Quarter}_Missing_Decisions.csv
    if (year is not None) and (quarter is not None):
        # Normalize year/quarter strings
        y_str = str(year)

        # Accept quarter as int 1-4 or strings like 'Q1' or '1'
        if isinstance(quarter, int):
            if quarter not in (1, 2, 3, 4):
                raise ValueError("quarter must be 1..4 when provided as int")
            q_str = f"Q{quarter}"
        else:
            q_raw = str(quarter).upper()
            q_str = q_raw if q_raw.startswith("Q") else f"Q{q_raw}"

        out_dir = Path(output_root) / f"{y_str}_{q_str}"
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{y_str}_{q_str}_Missing_Decisions.csv"
        out_path = out_dir / filename

        # Write CSV (overwrites existing file). Keep index=False for a clean CSV.
        missing_decisions.to_csv(out_path, index=False)

        print(f"Missing decisions exported to: {out_path}")

    return missing_decisions, missing_nps_numbers_from_CRIS


def database_health_pipeline(
    PR_nums_exclude: List[str],
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    output_root: str = "data/output",
    output_format: str = "csv"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run a set of database health checks and optionally export results.

    Checks executed:
      - find_missing_financials_housing: projects missing required Part 2/3 financial or housing fields,
        excluding any ProjectNum values passed in `PR_nums_exclude`.
      - find_duplicate_nps_numbers: identifies NPSProjectNumber values used more than once.
      - check_nonspatial_usn: finds commercial projects linked to USN records that have no spatial geometry.

    Export behavior:
      - If both `year` and `quarter` are provided, results will be written to
        `data/output/{Year}_{Quarter}/` (or `output_root/{Year}_{Quarter}/`).
      - `output_format` controls whether three CSVs are created ("csv") or a single Excel workbook ("excel").
      - Files are overwritten if they already exist. Empty DataFrames produce files with headers only.

    Parameters:
        PR_nums_exclude: list of ProjectNum strings to exclude from the missing-financials/housing check.
        year: optional int (e.g., 2025). Must be provided together with `quarter` to trigger export.
        quarter: optional int (1-4) or str like 'Q1'. Must be provided together with `year` to trigger export.
        output_root: root output directory (default 'data/output').
        output_format: 'csv' or 'excel' determining the export format when year/quarter are supplied.

    Returns:
        Tuple of three pandas DataFrames (in order):
          (missing_financials_housing, duplicate_nps_numbers, nonspatial_tax_credit_usn)
    """
    # Missing required financial/housing fields (optionally filter by PR number)
    missing_financials_housing = ca.find_missing_financials_housing(pr_exclude_list=PR_nums_exclude)
    
    # Duplicate NPS project number checks
    duplicate_nps_numbers = ca.find_duplicate_nps_numbers()

    # Non-spatial USN checks for tax credit-related USNs
    nonspatial_tax_credit_usn = ca.check_nonspatial_usn()

    # If year and quarter provided, write outputs
    if (year is not None) and (quarter is not None):
        # Normalize year and quarter
        y_str = str(year)

        # Normalize quarter to 'Q1'..'Q4'
        if isinstance(quarter, int):
            if quarter not in (1, 2, 3, 4):
                raise ValueError("quarter must be 1..4 when provided as int")
            q_label = f"Q{quarter}"
        else:
            q_raw = str(quarter).upper()
            q_label = q_raw if q_raw.startswith("Q") else f"Q{q_raw}"

        folder = Path(output_root) / f"{y_str}_{q_label}"
        folder.mkdir(parents=True, exist_ok=True)

        if output_format.lower() == "csv":
            # Compose filenames
            f1 = folder / f"{y_str}_{q_label}_Missing_Financials_Housing.csv"
            f2 = folder / f"{y_str}_{q_label}_Duplicate_NPS_Numbers.csv"
            f3 = folder / f"{y_str}_{q_label}_Nonspatial_USN.csv"

            missing_financials_housing.to_csv(f1, index=False)
            duplicate_nps_numbers.to_csv(f2, index=False)
            nonspatial_tax_credit_usn.to_csv(f3, index=False)

            print(f"Database health CSVs exported to: {folder}")

        elif output_format.lower() in ("excel", "xlsx"):
            # Single workbook with multiple sheets
            out_file = folder / f"{y_str}_{q_label}_Database_Health.xlsx"
            with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
                missing_financials_housing.to_excel(writer, sheet_name="MissingFinancialsHousing", index=False)
                duplicate_nps_numbers.to_excel(writer, sheet_name="DuplicateNPSNumbers", index=False)
                nonspatial_tax_credit_usn.to_excel(writer, sheet_name="NonspatialUSN", index=False)

            print(f"Database health Excel workbook exported to: {out_file}")

        else:
            raise ValueError("output_format must be 'csv' or 'excel'")

    return missing_financials_housing, duplicate_nps_numbers, nonspatial_tax_credit_usn