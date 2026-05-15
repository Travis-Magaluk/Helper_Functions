"""
Helper utilities for auditing commercial tax credit data.

This module:
- Standardizes the NPS quarterly spreadsheets to the project's canonical column names/types.
- Converts wide decision columns (Part1/Part2/Part3 Decision/Date) into a database-friendly tall format.
- Ensures datatypes align between spreadsheet extracts and database extracts.
- Finds spreadsheet decisions that are missing from the database (with an optional date buffer).
- Provides convenience functions that call SQL queries in `Helper_Functions.audit.commercial_sql` via DBConnector.

Notes:
- All DB interactions are delegated to `DBConnector.fetch_data(...)`.
- Functions assume certain column names are present in inputs; see each function's docstring for details.
"""

from typing import Tuple, Dict, List, Any

import pandas as pd
from collections import defaultdict
from Helper_Functions.database.database_connections import DBConnector

import Helper_Functions.audit.commercial_sql as comm_sql



def standardize_nps_quarterly_reports(
        nps_report: pd.DataFrame, 
        nps_report_keep_columns: list[str], 
        nps_report_column_standardization: dict[str, str],
        decision_mapping_rename: dict[str, str], 
        date_cols: list[str]
) -> pd.DataFrame:
    """
    Normalize an NPS quarterly spreadsheet to a standard internal format.

    Parameters:
        nps_report (pd.DataFrame): Raw spreadsheet DataFrame.
        nps_report_keep_columns (list[str]): Columns to retain from the raw sheet.
        nps_report_column_standardization (dict): Mapping from raw column names -> standard names.
        decision_mapping_rename (dict): Mapping to normalize decision values (e.g., 'Approve ' -> 'Approve').
        date_cols (list[str]): List of column names that should be parsed as dates.

    Returns:
        pd.DataFrame: Standardized DataFrame with:
            - selected/renamed columns,
            - cleaned decision values,
            - 'ZIP' as pandas nullable Int64,
            - date columns parsed as datetimes,
            - filtered to rows where State == 'NY'.

    Assumptions & notes:
        - The incoming DataFrame contains a 'State' column. Rows not in NY are dropped.
        - ZIP coercion uses pandas nullable integer dtype 'Int64' to allow missing zips.
        - This function modifies and returns a new DataFrame (it does not do in-place edits on the caller's object).
    """
    # Keep only requested columns (defensive: this will raise if a required column is missing)
    nps_report = nps_report[nps_report_keep_columns]

    # Rename columns to canonical names used throughout the package
    nps_report = nps_report.rename(columns=nps_report_column_standardization)

    # Normalize decision strings based on user-provided mapping (e.g., remove trailing spaces)
    nps_report = nps_report.replace(to_replace=decision_mapping_rename)

    # Ensure ZIP column is stored as a nullable integer so missing zips are preserved as <NA>
    nps_report['ZIP'] = nps_report['ZIP'].astype('Int64')

    # Parse specified date columns into pandas datetime dtype
    for col in date_cols: 
        nps_report[col] = pd.to_datetime(nps_report[col])

    # Restrict to New York rows only (per audit requirements)
    nps_report = nps_report[nps_report['State'] == 'NY']

    return nps_report


def convert_wide_tall_decisions(nps_quarterly_report_standardized: pd.DataFrame) -> pd.DataFrame:
    """
    Convert wide-format part decisions in the standardized NPS sheet into a tall (database-friendly) table.

    Input expectations:
        The standardized DataFrame should contain these columns:
          - 'NPSProjectNumber'
          - 'Part1Decision', 'Part1DateDecision'
          - 'Part2Decision', 'Part2DateDecision'
          - 'Part3Decision', 'Part3DateDecision'

    Output:
        pd.DataFrame with columns:
          - 'NPSProjectNumber' (nullable integer in earlier steps)
          - 'TaxCreditPart' (int: 1, 2, or 3)
          - 'Decision' (string)  -- this comes from the 'Decision' column created by the pivot
          - 'DateDecision' (datetime/date)  -- comes from the 'DateDecision' pivot column

    Behavior:
        - Uses pandas.melt to create long-form rows for each (NPSProjectNumber, Part, Field).
        - Extracts part number and field type ('Decision' or 'DateDecision') via regex.
        - Pivots back so each row has one Decision and one DateDecision column per part.
        - Converts 'TaxCreditPart' to integer.

    Notes:
        - If any Part columns are entirely missing from the input, the result may not include that part.
        - The function preserves the first non-null value on pivot via aggfunc='first'.
    """
    cols_to_keep = [
        'NPSProjectNumber', 
        'Part1Decision','Part1DateDecision',
        'Part2Decision', 'Part2DateDecision',
        'Part3Decision','Part3DateDecision'
    ]

    # Narrow to required columns (will raise KeyError if missing)
    nps_quarterly_decisions = nps_quarterly_report_standardized[cols_to_keep]

    # Melt into long form so each (project, part, field) is a row
    nps_quarterly_decisions_long = pd.melt(
        nps_quarterly_decisions,
        id_vars=['NPSProjectNumber'],
        value_vars=[
                'Part1Decision','Part1DateDecision',
                'Part2Decision', 'Part2DateDecision',
                'Part3Decision','Part3DateDecision'
                ],
        var_name='TaxCreditPart_Field',
        value_name='Value'
    )
    
    # Split the 'PartXDecision' / 'PartXDateDecision' into ['PartX', 'Decision'|'DateDecision']
    nps_quarterly_decisions_long[
        ['TaxCreditPart', 'Field']
    ] = nps_quarterly_decisions_long[
            'TaxCreditPart_Field'].str.extract(r'(Part\d)(Decision|DateDecision)')

    # Pivot so we have one row per (NPSProjectNumber, TaxCreditPart), with columns 'Decision' and 'DateDecision'
    nps_quarterly_decisions_database_friendly = nps_quarterly_decisions_long.pivot_table(
        index=['NPSProjectNumber', 'TaxCreditPart'],
        columns='Field',
        values='Value',
        aggfunc='first'
    ).reset_index()

    # Convert TaxCreditPart from 'Part1' string -> integer 1
    nps_quarterly_decisions_database_friendly[
        'TaxCreditPart'] = nps_quarterly_decisions_database_friendly[
            'TaxCreditPart'].str.extract(r'Part(\d)').astype(int)

    return nps_quarterly_decisions_database_friendly


def ensure_correct_datatypes(df_spreadsheet: pd.DataFrame, df_database: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Coerce datatypes to canonical types so spreadsheet vs database diffs are meaningful.

    Parameters:
        df_spreadsheet (pd.DataFrame): DataFrame created from the spreadsheet (tall decisions).
        df_database (pd.DataFrame): DataFrame loaded from the database (tall decisions).

    Returns:
        tuple(pd.DataFrame, pd.DataFrame): The two DataFrames with adjusted dtypes:
            - 'NPSProjectNumber' and 'TaxCreditPart' -> pandas nullable Int64
            - 'Decision' -> stripped string
            - 'DateDecision' -> python date (datetime.date)

    Notes:
        - This function mutates the DataFrames provided by casting columns; it returns them for convenience.
        - Converts DateDecision using pd.to_datetime(...).dt.date (loses timezone info).
    """
    # Ensure project number is comparable (nullable integer)
    df_spreadsheet['NPSProjectNumber'] = df_spreadsheet['NPSProjectNumber'].astype('Int64')
    df_database['NPSProjectNumber'] = df_database['NPSProjectNumber'].astype('Int64')

    # Ensure TaxCreditPart is an integer type (nullable)
    df_spreadsheet['TaxCreditPart'] = df_spreadsheet['TaxCreditPart'].astype('Int64')
    df_database['TaxCreditPart'] = df_database['TaxCreditPart'].astype('Int64')

    # Trim whitespace from decision strings to avoid false mismatches
    df_spreadsheet['Decision'] = df_spreadsheet['Decision'].astype('str').str.strip()
    df_database['Decision'] = df_database['Decision'].astype('str').str.strip()

    # Normalize DateDecision to date objects for reliable day-level comparisons
    df_spreadsheet['DateDecision'] = pd.to_datetime(df_spreadsheet['DateDecision']).dt.date
    df_database['DateDecision'] = pd.to_datetime(df_database['DateDecision']).dt.date

    return df_spreadsheet, df_database



def find_missing_decisions_with_date_buffer(
    df_spreadsheet: pd.DataFrame,
    df_database: pd.DataFrame,
    date_buffer_days: int = 0,
    restrict_to_existing_projects: bool = False,
    match_on_month_year: bool = True,
) -> pd.DataFrame:
    """
    Compare spreadsheet decisions to database decisions and return those missing from the database.

    Matching logic:
        - If match_on_month_year is False:
            Use a date buffer: dates match if their absolute difference in days
            is <= date_buffer_days.
        - If match_on_month_year is True (default):
            Dates match if they are in the same calendar month and year, regardless of day.

    Parameters:
        df_spreadsheet (pd.DataFrame):
            The new decisions to check (must have matching columns).
        df_database (pd.DataFrame):
            The existing decisions already in the database.
        date_buffer_days (int):
            Number of days to allow as a tolerance between dates when match_on_month_year=False.
        restrict_to_existing_projects (bool):
            If True, only check projects that exist in df_database.
        match_on_month_year (bool):
            If True, consider two decisions a match when their decision dates are in the
            same month and year. If False, use the date_buffer_days tolerance instead.

    Returns:
        pd.DataFrame:
            A filtered version of df_spreadsheet with decisions not found in df_database.
    """

    # Optionally restrict the spreadsheet to only projects that already exist in the database
    if restrict_to_existing_projects:
        # Set of all known project numbers in the database
        known_projects: set[Any] = set(df_database["NPSProjectNumber"].unique())

        # Keep only spreadsheet rows whose project number is in the known set
        df_spreadsheet = df_spreadsheet[
            df_spreadsheet["NPSProjectNumber"].isin(known_projects)
        ].copy()

    # Build a lookup dictionary:
    #   key   = (project number, tax credit part, decision)
    #   value = list of decision dates from the database
    db_lookup: Dict[Tuple[Any, Any, Any], List[pd.Timestamp]] = defaultdict(list)

    for _, row in df_database.iterrows():
        key: Tuple[Any, Any, Any] = (
            row["NPSProjectNumber"],
            row["TaxCreditPart"],
            row["Decision"],
        )
        db_lookup[key].append(row["DateDecision"])

    # List to collect spreadsheet rows that do NOT find a matching decision in the database
    unmatched_rows: List[pd.Series] = []

    # Iterate over each decision in the spreadsheet
    for _, row in df_spreadsheet.iterrows():
        # Build the same key used for the database lookup
        key = (row["NPSProjectNumber"], row["TaxCreditPart"], row["Decision"])

        # Spreadsheet decision date
        sheet_date: Any = row["DateDecision"]

        # Flag to indicate if this spreadsheet row has a match in the database
        matched: bool = False

        # Loop through all database decision dates that share the same project/part/decision key
        for db_date in db_lookup.get(key, []):
            # Skip comparison if either date is missing/NaT
            if pd.isna(sheet_date) or pd.isna(db_date):
                continue

            if match_on_month_year:
                # Match dates by calendar month and year only (ignore the day)
                if sheet_date.year == db_date.year and sheet_date.month == db_date.month:
                    matched = True
                    break
            else:
                # Match dates based on a +/- day buffer
                # Convert the timedelta to number of days and compare to the buffer
                if abs((sheet_date - db_date).days) <= date_buffer_days:
                    matched = True
                    break

        # If no matching database decision was found, collect this spreadsheet row as unmatched
        if not matched:
            unmatched_rows.append(row)

    # Return a DataFrame of all unmatched spreadsheet decisions
    return pd.DataFrame(unmatched_rows)


def join_CRIS_PR_numbers(records_with_nps_number: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich a DataFrame containing NPSProjectNumber with ProjectNum values from CRIS (database).

    Parameters:
        records_with_nps_number (pd.DataFrame): DataFrame that must contain 'NPSProjectNumber' column.

    Returns:
        pd.DataFrame: Input DataFrame merged with a 'ProjectNum' column (left merge).
                      ProjectNum is placed as the first column in the returned DataFrame.

    Behavior:
        - Fetches the mapping using comm_sql.nps_number_pr_mapping through DBConnector.
        - Casts NPSProjectNumber in the mapping to nullable Int64 to match the records input.
        - Performs a left merge so rows without a mapping remain present (ProjectNum NaN).
    """
    db = DBConnector()

    # Keep the original column order so we can reinsert ProjectNum at the front
    og_col_order = list(records_with_nps_number.columns)
    new_col_order = ['ProjectNum'] + og_col_order

    # Fetch mapping from the database and ensure comparable dtype
    NPS_to_PR_mapping = db.fetch_data(comm_sql.nps_number_pr_mapping)
    NPS_to_PR_mapping['NPSProjectNumber'] = NPS_to_PR_mapping['NPSProjectNumber'].astype('Int64')

    # Merge mapping into the provided DataFrame
    records_with_nps_number = records_with_nps_number.merge(
        NPS_to_PR_mapping, how='left', on='NPSProjectNumber'
    )

    # Reorder so ProjectNum is first
    records_with_nps_number = records_with_nps_number[new_col_order]

    return records_with_nps_number


def find_missing_financials_housing(pr_exclude_list: list[str] = []) -> pd.DataFrame:
    """
    Query the database for commercial tax credit projects missing required Part 2/3 financial or housing fields.

    Parameters:
        pr_exclude_list (list[str]): List of ProjectNum values to exclude from results.

    Returns:
        pd.DataFrame: DataFrame of projects matching the 'missing' criteria from the SQL defined in comm_sql.projects_missing_financials_or_housing.

    Notes:
        - Uses DBConnector.fetch_data and the SQL stored in comm_sql.projects_missing_financials_or_housing.
        - pr_exclude_list elements are compared to the 'ProjectNum' column returned by the SQL.
    """
    db = DBConnector()

    df = db.fetch_data(comm_sql.projects_missing_financials_or_housing)

    df = df[~df['ProjectNum'].isin(pr_exclude_list)]

    print(f'There are at most {df.shape[0]} Commercial Tax Credit projects that are missing housing or financial information.')

    return df


def find_duplicate_nps_numbers() -> pd.DataFrame:
    """
    Find cases where an NPSProjectNumber appears more than once across projects.

    Returns:
        pd.DataFrame: Rows from the duplicate-NPS query; caller can inspect ProjectNum and NPSProjectNumber.
    """
    db = DBConnector()
    
    df = db.fetch_data(comm_sql.duplicate_NPS_project_numbers)

    # Because BasePull returns one row per project, and the query filters NPSNumber_Count > 1,
    # the number of distinct duplicate groups is df.shape[0] / 2 (approx) depending on data; the print is a soft hint.
    print(f'There are at least {df.shape[0]/2} cases where a NPS project number has been used in CRIS more than once.')

    return df


def check_nonspatial_usn() -> pd.DataFrame:
    """
    Find non-spatial USN entries that are referenced by commercial tax credit projects.

    Returns:
        pd.DataFrame: Rows linking commercial projects to USN records that have no geometry (as defined by gu.OBJECTID IS NULL in the SQL).
    """
    db = DBConnector()

    df = db.fetch_data(comm_sql.nonspatial_usn)

    print(f"There are at least {df.shape[0]} non-spatial USNs attached to commercial tax credit projects.")

    return df
