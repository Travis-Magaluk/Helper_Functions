"""
Column-level DataFrame comparison and difference analysis.

Designed for reconciling two DataFrames from different sources (e.g., a spreadsheet
and a database). The comparison is driven by a comp_dict that describes how each
column pair should be compared (string, numerical, or zip code).

Note: legacy_comp_cols.py is an older pipeline kept for reference. Prefer the
functions in this module for all new work.

Public API — comparison functions (compare_columns.py):
    compare_string_columns          — compare two string columns row-by-row via df.apply()
    compare_numerical_columns       — compare two numeric columns with a percentage tolerance
    compare_zip_codes               — compare zip code columns with special NaN handling
    compare_decsision_date          — compare combined decision+date columns
    run_comparison_and_reorder      — run all comparisons defined in a comp_dict and reorder columns
    generate_comparison_dict        — build a comp_dict template from two DataFrames
    rename_columns_with_prefix      — prefix column names to distinguish source DataFrames
    get_column_order_from_dict      — derive column ordering from a comp_dict
    create_new_dataframe_with_new_columns_only — keep only the reconciled output columns

Public API — difference reporting (difference_reporting.py):
    report_number_DIFFERENT_values  — count rows marked DIFFERENT per column
    compare_columns_with_difference — filter a DataFrame to rows with any DIFFERENT value
    report_difference               — detailed difference report for a single column pair
    sum_top_x_differences           — aggregate and rank columns by number of differences
    compare_multiple_x_values       — compare differences across multiple top x groupings
    analyze_difference_reduction    — quantify how much a cleaning step reduced differences
"""
from Helper_Functions.dataframe_comparison.compare_columns import (
    compare_string_columns,
    compare_numerical_columns,
    compare_zip_codes,
    compare_decsision_date,
    run_comparison_and_reorder,
    generate_comparison_dict,
    rename_columns_with_prefix,
    get_column_order_from_dict,
    create_new_dataframe_with_new_columns_only,
)
from Helper_Functions.dataframe_comparison.difference_reporting import (
    report_number_DIFFERENT_values,
    compare_columns_with_difference,
    report_difference,
    sum_top_x_differences,
    compare_multiple_x_values,
    analyze_difference_reduction,
)

__all__ = [
    # comparison
    "compare_string_columns",
    "compare_numerical_columns",
    "compare_zip_codes",
    "compare_decsision_date",
    "run_comparison_and_reorder",
    "generate_comparison_dict",
    "rename_columns_with_prefix",
    "get_column_order_from_dict",
    "create_new_dataframe_with_new_columns_only",
    # difference reporting
    "report_number_DIFFERENT_values",
    "compare_columns_with_difference",
    "report_difference",
    "sum_top_x_differences",
    "compare_multiple_x_values",
    "analyze_difference_reduction",
]
