import numpy as np  
import pandas as pd
from typing import List, Dict, Optional, Set

def compare_string_columns(row, column_1: str, column_2: str, default_first: bool, strict_nan: bool) -> str:
    """Reconcile two string columns row-by-row.

    Designed to be used with ``df.apply(..., axis=1)``. Walks through a series
    of cases and returns a single reconciled value (or ``"DIFFERENT"`` when the
    two sides disagree and no fallback applies).

    Resolution order:
        1. If both values are equal, return that value.
        2. If both are NaN, return ``np.nan``.
        3. If ``strict_nan`` is True and exactly one side is NaN, return
           ``"DIFFERENT"`` (treat NaN/non-NaN pairs as a disagreement).
        4. If only one side is NaN, return the non-NaN value.
        5. Otherwise the two values differ — return ``column_1`` if
           ``default_first`` is True, else ``"DIFFERENT"``.

    Args:
        row (pd.Series): A single DataFrame row.
        column_1 (str): Name of the first string column (typically the
            spreadsheet source).
        column_2 (str): Name of the second string column (typically the
            CRIS database source).
        default_first (bool): When the two values disagree and neither is NaN,
            return ``column_1``'s value instead of ``"DIFFERENT"``.
        strict_nan (bool): When True, a NaN paired with a non-NaN is treated
            as a disagreement rather than being filled from the non-NaN side.

    Returns:
        str: Reconciled value, ``np.nan``, or ``"DIFFERENT"`` per the rules
        above.
    """
    val1, val2 = row[column_1], row[column_2]

    if val1 == val2:
        return val1
    
    if pd.isna(val1) and pd.isna(val2):
        return np.nan
    
    if strict_nan and (pd.isna(val1) != pd.isna(val2)):
        return "DIFFERENT"
    
    if pd.isna(val2):
        return val1
    
    if pd.isna(val1): 
        return val2
    
    return val1 if default_first else "DIFFERENT"

    
def compare_numerical_columns(row, column_1: str, column_2: str, margin: int, default_first: bool, strict_nan: bool) -> str:
    """Reconcile two numerical columns row-by-row with a percent-based tolerance.

    Designed to be used with ``df.apply(..., axis=1)``.

    Resolution order:
        1. If both values are NaN, return ``np.nan``.
        2. If ``strict_nan`` is True and exactly one side is NaN, return
           ``"DIFFERENT"``.
        3. If only one side is NaN, return the non-NaN value.
        4. If either value cannot be cast to ``float``, return
           ``"Invalid Value"``.
        5. If the two values are exactly equal, return that value.
        6. Otherwise compute the relative difference as
           ``abs(val1 - val2) / average``. If it is within ``margin / 100``,
           return ``max(val1, val2)`` (treats the two as a match and keeps the
           larger figure).
        7. If the relative difference exceeds the margin, return ``column_1``'s
           value if ``default_first`` is True, else ``"DIFFERENT"``.

    Args:
        row (pd.Series): A single DataFrame row.
        column_1 (str): Name of the first numerical column.
        column_2 (str): Name of the second numerical column.
        margin (int): Tolerance expressed as a percent of the average of the
            two values (e.g., ``10`` means within 10%). ``0`` requires an
            exact match.
        default_first (bool): When the two values disagree beyond ``margin``
            and neither is NaN, return ``column_1``'s value instead of
            ``"DIFFERENT"``.
        strict_nan (bool): When True, a NaN paired with a non-NaN is treated
            as a disagreement rather than being filled from the non-NaN side.

    Returns:
        float or str: A numeric value, ``np.nan``, ``"DIFFERENT"``, or
        ``"Invalid Value"`` per the rules above.
    """
    val1, val2 = row[column_1], row[column_2]

    # If both values are NaN, return NaN
    if pd.isna(val1) and pd.isna(val2):
        return np.nan

    if strict_nan and (pd.isna(val1) != pd.isna(val2)):
        return "DIFFERENT"
    
    # If only val2 is NaN, return val1
    if pd.isna(val2):
        return val1

    # If only val1 is NaN, return val2
    if pd.isna(val1):
        return val2

    # Attempt to convert values to float; handle invalid inputs gracefully
    try:
        val1, val2 = float(val1), float(val2)
    except (ValueError, TypeError):
        return "Invalid Value"

    # If values are exactly equal, return either
    if val1 == val2:
        return val1

    # Calculate the average of the two values
    average = (val1 + val2) / 2

    # Calculate the relative difference between the values
    diff = abs(val1 - val2) / average if average != 0 else 0

    # If the difference is within the margin, return the larger value
    if diff <= margin / 100:
        return max(val1, val2)

    # If values differ beyond the margin, return based on the default_first flag
    return val1 if default_first else "DIFFERENT"



def compare_zip_codes(row, column_1: str, column_2: str) -> str:
    """Reconcile two zip code columns, tolerating 5- vs. 9-digit format differences.

    Designed to be used with ``df.apply(..., axis=1)``. Treats two zip codes
    as matching when their first five digits agree, and prefers the more
    specific 9-digit form (``XXXXX-XXXX``) when one is available. Hyphens and
    surrounding whitespace are stripped before length comparison so formatting
    variations don't cause false mismatches.

    Resolution order:
        1. If exactly one side is NaN, return the stripped value from the
           other side.
        2. Both 5-digit and equal → return that zip code.
        3. One 5-digit, one 9-digit, with matching 5-digit prefixes → return
           the 9-digit value (more specific).
        4. Both 9-digit and equal → return that zip code.
        5. Anything else (lengths unexpected, or prefixes don't match) →
           return ``"DIFFERENT"``.

    Note:
        When both sides are NaN this function falls through to the final
        ``else`` and returns ``"DIFFERENT"``. Callers expecting NaN for empty
        rows should filter beforehand.

    Args:
        row (pd.Series): A single DataFrame row.
        column_1 (str): Name of the first zip code column.
        column_2 (str): Name of the second zip code column.

    Returns:
        str: The reconciled zip code (5- or 9-digit, with hyphen preserved
        for 9-digit) or ``"DIFFERENT"`` when no rule applies.
    """
    zip1 = row[column_1]  # Get the value from column_1
    zip2 = row[column_2]  # Get the value from column_2

    # Check for NaN values and return the valid zip code if one column is NaN
    if pd.isna(zip1) and not pd.isna(zip2):
        return zip2.strip()  # Return the zip code from column_2 if column_1 is NaN
    elif pd.isna(zip2) and not pd.isna(zip1):
        return zip1.strip()  # Return the zip code from column_1 if column_2 is NaN

    # Remove hyphens and spaces from 9-digit zip codes for comparison
    zip1 = str(zip1).strip()  # Ensure it's treated as a string
    zip2 = str(zip2).strip()  # Ensure it's treated as a string

    zip1_no_hyphen = zip1.replace(' ', '').replace('-', '')
    zip2_no_hyphen = zip2.replace(' ', '').replace('-', '')

    # Case 1: Both zip codes are 5-digit
    if len(zip1_no_hyphen) == 5 and len(zip2_no_hyphen) == 5:
        if zip1_no_hyphen == zip2_no_hyphen:
            return zip1

    # Case 2: One zip code is 9-digit and the other is 5-digit
    elif len(zip1_no_hyphen) == 5 and len(zip2_no_hyphen) == 9:
        if zip1_no_hyphen == zip2_no_hyphen[:5]:  # Compare the 5-digit part of the 9-digit zip
            return zip2.strip()  # Return the 9-digit zip code with hyphen intact

    elif len(zip1_no_hyphen) == 9 and len(zip2_no_hyphen) == 5:
        if zip1_no_hyphen[:5] == zip2_no_hyphen:  # Compare the 5-digit part of the 9-digit zip
            return zip1.strip()  # Return the 9-digit zip code with hyphen intact

    # Case 3: Both zip codes are in 9-digit format
    elif len(zip1_no_hyphen) == 9 and len(zip2_no_hyphen) == 9:
        if zip1_no_hyphen == zip2_no_hyphen:
            return zip1.strip()  # Return the 9-digit zip code with hyphen intact

    # Return 'DIFFERENT' if the zip codes don't match the expected patterns
    else:
        return 'DIFFERENT'



def get_column_order_from_dict(comparison_dictionary: Dict[str, Dict[str, List]], input_df: pd.DataFrame, new_cols_only: bool = False) -> List[str]:
    """Derive a column order from a comparison dictionary.

    Two modes:
        * Default (``new_cols_only=False``): for each key in the dictionary,
          emit its mapped source columns followed by the key itself, so each
          reconciled column appears directly after the two columns it was
          derived from. Dictionary entries whose value is ``None`` contribute
          just the key (no source columns). Only columns actually present in
          ``input_df`` are included.
        * Reduced (``new_cols_only=True``): emit only the dictionary keys
          present in ``input_df`` — used to slice the DataFrame down to the
          reconciled output columns after manual review.

    Columns in ``input_df`` that are not mentioned by the dictionary are not
    returned by this function; callers that want to retain them should append
    them separately.

    Args:
        comparison_dictionary (Dict): Comparison dictionary (see
            ``comparison_dict_example.py`` for the expected shape).
        input_df (pd.DataFrame): DataFrame whose columns are being reordered.
        new_cols_only (bool): If True, return only the reconciled key columns.

    Returns:
        List[str]: Ordered list of column names suitable for slicing
        ``input_df``.
    """
    # Initialize the new column order
    new_col_order = []

    if new_cols_only: 
        for key in comparison_dictionary:
            if key in input_df.columns:
                new_col_order.append(key)

    else: 
        # Iterate over the dictionary to extract column order
        for key in comparison_dictionary:
            # If no specific columns are mapped, add the key directly if it exists in the DataFrame
            if comparison_dictionary[key] is None:
                if key in input_df.columns:
                    new_col_order.append(key)
            else:
                # Add all mapped columns that exist in the DataFrame
                for col in comparison_dictionary[key]['columns']:
                    if col in input_df.columns:
                        new_col_order.append(col)
                # Add the key itself if it exists in the DataFrame
                if key in input_df.columns:
                    new_col_order.append(key)

    return new_col_order


def run_comparison_and_reorder(comp_dict: Dict[str, Dict[str, List]], df: pd.DataFrame, strict_nan_compare: bool = False) -> pd.DataFrame:
    """Run all comparisons defined by ``comp_dict`` and reorder the DataFrame.

    For each entry in ``comp_dict``, applies either
    :func:`compare_string_columns` or :func:`compare_numerical_columns` to
    produce a new column named for the dictionary key. Entries whose value is
    ``None`` are skipped (no comparison performed), which lets callers list
    columns they want to keep in the output order without running a
    comparison on them. After all comparisons run, columns are reordered via
    :func:`get_column_order_from_dict` so each reconciled column sits next to
    the two source columns it was derived from.

    Each non-``None`` entry in ``comp_dict`` is a dict shaped like:

        {
            'columns': [col1_name, col2_name],
            'type': 'string' | 'numerical',
            'margin': int,           # numerical only; percent tolerance
            'default_first': bool    # whether to prefer col1 on disagreement
        }

    See ``comparison_dict_example.py`` for a full example.

    Args:
        comp_dict (Dict[str, Dict]): Mapping from new column name to its
            comparison spec (or ``None`` to skip).
        df (pd.DataFrame): DataFrame containing every column listed in
            ``comp_dict[*]['columns']``.
        strict_nan_compare (bool): Forwarded as ``strict_nan`` to the
            underlying string/numerical comparison functions. When True, a
            NaN paired with a non-NaN is treated as ``"DIFFERENT"`` rather
            than being filled from the non-NaN side.

    Returns:
        pd.DataFrame: ``df`` with new reconciled columns appended and the
        column order rearranged.
    """
    # Iterate through the comparison dictionary
    for key in comp_dict.keys():

        if comp_dict[key] is None:
            # Skip if no comparison is required for this key
            continue

        compare_type = comp_dict[key]['type']
        col1, col2 = comp_dict[key]['columns']
        default_first = comp_dict[key].get('default_first', False)

        if compare_type == 'string':
            df[key] = df.apply(
                compare_string_columns,
                args=(col1, col2, default_first, strict_nan_compare),
                axis=1
            )

        elif compare_type == 'numerical':
            margin = comp_dict[key].get('margin', 0)
            df[key] = df.apply(
                compare_numerical_columns,
                args=(col1, col2, margin, default_first, strict_nan_compare),
                axis=1
            )

    col_order = get_column_order_from_dict(comp_dict, df)

    df = df[col_order]

    return df
        

def create_new_dataframe_with_new_columns_only(comp_dict: Dict[str, Dict[str, List]], df: pd.DataFrame) -> pd.DataFrame:
    """Slice ``df`` down to only the reconciled output columns.

    Returns a DataFrame containing just the keys of ``comp_dict`` that exist
    in ``df``. This includes both reconciled comparison columns (keys whose
    value is a comparison spec) and "stand-alone" columns (keys whose value
    is ``None`` — typically identifier columns that the caller wants carried
    through alongside the comparison results).

    Intended to be called after :func:`run_comparison_and_reorder` and any
    manual review, when the full source columns are no longer needed.

    Args:
        comp_dict (Dict[str, Dict[str, List]]): Comparison dictionary used to
            generate the reconciled columns.
        df (pd.DataFrame): DataFrame already processed by
            :func:`run_comparison_and_reorder`.

    Returns:
        pd.DataFrame: DataFrame containing only the keys of ``comp_dict``
        that are present in ``df``, in dictionary order.
    """

    col_order = get_column_order_from_dict(comp_dict, df, True)

    df = df[col_order]

    return df

def compare_decsision_date(row, decision_1_col, decision_date_1_col, decision_2_col, decision_date_2_col, day_margin):
    """Reconcile a (decision, date) pair from two sources.

    Designed to be used with ``df.apply(..., axis=1)``. Returns a two-element
    Series intended to be unpacked into two new DataFrame columns (decision
    and reconciled date string).

    Decision resolution:
        * Both NaN → ``np.nan``.
        * One NaN, one not → the non-NaN value.
        * Both present and equal → that value.
        * Both present and unequal → ``"Different"``.

    Date resolution (dates are parsed with ``pd.to_datetime(errors='coerce')``,
    so unparseable strings become NaT and behave like NaN):
        * Both NaN → ``np.nan``.
        * One NaN, one not → the non-NaN date, formatted ``'%Y-%m-%d'``.
        * Both present and within ``day_margin`` days → ``date_1`` formatted
          ``'%Y-%m-%d'``.
        * Both present but beyond ``day_margin`` → ``"Date Mismatch"``.

    Args:
        row (pd.Series): A single DataFrame row.
        decision_1_col (str): Column name for the first decision value.
        decision_date_1_col (str): Column name for the first decision date.
        decision_2_col (str): Column name for the second decision value.
        decision_date_2_col (str): Column name for the second decision date.
        day_margin (int): Maximum allowed difference, in days, for two dates
            to be considered a match.

    Returns:
        pd.Series: Two-element Series ``[decision, date_result]`` where
        ``date_result`` is either an ``'%Y-%m-%d'`` string, ``np.nan``, or
        ``"Date Mismatch"``.
    """
    # Extract values and convert dates
    decision_1 = row[decision_1_col]
    decision_2 = row[decision_2_col]
    date_1 = pd.to_datetime(row[decision_date_1_col], errors='coerce')
    date_2 = pd.to_datetime(row[decision_date_2_col], errors='coerce')

    # Handle decisions
    if pd.isna(decision_1) and pd.isna(decision_2):
        decision = np.nan
    elif pd.isna(decision_1) and pd.notna(decision_2):
        decision = decision_2
    elif pd.notna(decision_1) and pd.isna(decision_2):
        decision = decision_1
    elif decision_1 == decision_2:
        decision = decision_1
    else:
        decision = "Different"

    # Handle dates
    if pd.isna(date_1) and pd.isna(date_2):
        date_result = np.nan
    elif pd.isna(date_1) and pd.notna(date_2):
        date_result = date_2.strftime('%Y-%m-%d')
    elif pd.notna(date_1) and pd.isna(date_2):
        date_result = date_1.strftime('%Y-%m-%d')
    elif pd.notna(date_1) and pd.notna(date_2):
        if date_1 == date_2 or abs((date_1 - date_2).days) <= day_margin:
            date_result = date_1.strftime('%Y-%m-%d')
        else:
            date_result = "Date Mismatch"
    else:
        date_result = "Invalid Date"

    return pd.Series([decision, date_result])



def generate_comparison_dict(
    columns: List[str],
    left_prefix: str,
    right_prefix: str,
    string_columns: Optional[Set[str]] = None,
    none_columns: Optional[Set[str]] = None
) -> Dict[str, Optional[Dict]]:
    """Build a comparison dictionary template from a list of base column names.

    For each base name ``col`` in ``columns``, this produces an entry keyed
    by ``col`` whose ``columns`` pair points at the prefixed versions
    ``f"{left_prefix}{col}"`` and ``f"{right_prefix}{col}"``. Useful when the
    two source DataFrames have been renamed to disambiguate identical column
    names (see :func:`rename_columns_with_prefix`).

    Defaults applied to each entry:
        * ``type``: ``"string"`` if ``col`` is in ``string_columns``, else
          ``"numerical"``.
        * ``margin``: ``0`` for numerical entries, ``None`` for string
          entries.
        * ``default_first``: ``False``.

    Columns listed in ``none_columns`` are emitted as ``key: None`` — they
    pass through :func:`run_comparison_and_reorder` without a comparison but
    still participate in column ordering.

    Args:
        columns (List[str]): Base (un-prefixed) column names to compare.
        left_prefix (str): Prefix applied to the left DataFrame's columns.
        right_prefix (str): Prefix applied to the right DataFrame's columns.
        string_columns (Set[str], optional): Subset of ``columns`` to compare
            as strings. Anything not listed here is treated as numerical.
        none_columns (Set[str], optional): Subset of ``columns`` to emit as
            ``None`` (carried through with no comparison).

    Returns:
        Dict[str, Optional[Dict]]: A dictionary suitable for passing to
        :func:`run_comparison_and_reorder`. Margins and ``default_first`` can
        be tuned per-entry after generation.
    """
    if string_columns is None:
        string_columns = set()
    if none_columns is None:
        none_columns = set()

    comparison_dict = {}

    for col in columns:
        if col in none_columns:
            comparison_dict[col] = None  # No comparison needed
        else:
            comparison_dict[col] = {
                "columns": [f"{left_prefix}{col}", f"{right_prefix}{col}"],
                "type": "string" if col in string_columns else "numerical",
                "margin": 0 if col not in string_columns else None,
                "default_first": False
            }

    return comparison_dict



def rename_columns_with_prefix(df, prefix1, exclude_columns=None):
    """Prefix every column name in ``df``, optionally skipping a few.

    Used to disambiguate columns from two source DataFrames before they are
    merged or compared side-by-side (typically called once per source with a
    different prefix). Columns whose names appear in ``exclude_columns`` are
    left untouched — useful for join keys that need to remain identical
    across both DataFrames.

    Args:
        df (pd.DataFrame): DataFrame whose columns will be renamed.
        prefix1 (str): Prefix to prepend to each column name.
        exclude_columns (set, optional): Column names to leave unprefixed.
            Defaults to an empty set.

    Returns:
        pd.DataFrame: A new DataFrame (via ``df.rename``) with prefixed
        column names.
    """
    if exclude_columns is None:
        exclude_columns = set()
    
    df_renamed = df.rename(columns=lambda col: col if col in exclude_columns else f"{prefix1}{col}")
    
    return df_renamed