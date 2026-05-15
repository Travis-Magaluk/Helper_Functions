import pandas as pd
from typing import Dict


def report_number_DIFFERENT_values(comp_dict: Dict[str, int], compared_data: pd.DataFrame) -> pd.DataFrame:
    """Count the rows tagged ``"DIFFERENT"`` in each reconciled column.

    Provides a quick per-column tally of how often the two source columns
    disagreed (i.e. how often the comparison function fell through to its
    final ``"DIFFERENT"`` sentinel). Useful as a first pass to identify which
    fields are the noisiest and warrant deeper investigation.

    Every key in ``comp_dict`` is iterated, including entries whose value is
    ``None`` — their ``"DIFFERENT"`` count will be zero, which keeps the
    output aligned with the dictionary's structure.

    Args:
        comp_dict (dict): Comparison dictionary whose keys are the names of
            reconciled columns in ``compared_data`` (see
            ``comparison_dict_example.py`` for shape).
        compared_data (pd.DataFrame): DataFrame already processed by
            :func:`~dataframe_comparison.compare_columns.run_comparison_and_reorder`.

    Returns:
        pd.DataFrame: Two-column DataFrame ``[Column, Values]`` where
        ``Column`` is the reconciled column name and ``Values`` is the count
        of rows equal to ``"DIFFERENT"``.
    """
    difference_dict = {'Column': [], 'Values': []}

    for key in list(comp_dict.keys()):
        num_diff = compared_data[compared_data[key] == 'DIFFERENT'].shape[0]
        difference_dict['Column'].append(key)
        difference_dict['Values'].append(num_diff)
    

    df = pd.DataFrame(difference_dict)

    return df


def compare_columns_with_difference(df, comparison_dict):
    """Append a ``_difference`` column for each numerical comparison and reorder.

    For every numerical entry in ``comparison_dict``, this adds a new column
    named ``f"{key}_difference"`` holding the absolute gap between the two
    source values — but only for rows the reconciliation tagged
    ``"DIFFERENT"``. Rows that matched (or were filled from a single side)
    are left as ``None`` in the difference column, since their gap isn't
    meaningful.

    The output column order is built from the dictionary: for each numerical
    key the layout is ``[col1, col2, key, key_difference]``; for each
    ``None`` entry just the key is emitted. Any columns in ``df`` that the
    dictionary doesn't reference are appended at the end in their original
    order, so identifier columns and other passthroughs are preserved.

    Operates on a copy of ``df`` — the input is not mutated.

    Args:
        df (pd.DataFrame): DataFrame already processed by
            :func:`~dataframe_comparison.compare_columns.run_comparison_and_reorder`
            so the reconciled key columns exist.
        comparison_dict (dict): Comparison dictionary used to produce the
            reconciled columns.

    Returns:
        pd.DataFrame: DataFrame with ``_difference`` columns added for
        numerical comparisons and columns reordered for side-by-side review.
    """
    df = df.copy()
    new_columns = []  # To store the final column order
    
    for key, params in comparison_dict.items():
        if params is None:
            new_columns.append(key)  # Always include the key
        
        else:
            col1, col2 = params['columns']
            diff_col = f"{key}_difference"

            new_columns.extend([col1, col2, key])  # Add the compared columns

            if params['type'] == 'numerical':
                df[diff_col] = None
                df.loc[df[key] == "DIFFERENT", diff_col] = abs(df[col1] - df[col2])
                df[diff_col] = df[diff_col].astype(float)
                new_columns.append(diff_col)  # Add the difference column

    # Add remaining columns that were not in the comparison dictionary
    remaining_cols = [c for c in df.columns if c not in new_columns]
    df = df[new_columns + remaining_cols]

    return df



def report_difference(df, comparison_dict):
    """Summarize total disagreement per numerical column.

    For each numerical entry that has a ``_difference`` column on ``df``,
    reports the summed absolute difference, a "total" value to scale it
    against, and the resulting percent difference. This gives a sense of how
    materially the two sources diverge — a column with many small
    disagreements may matter less than a column with a few large ones.

    The "Total" used as the denominator is ``max(sum(col1), sum(col2))``.
    Taking the max (rather than either side, or the average) is intentional:
    it picks whichever source claims a larger total, which gives a
    conservative (smaller) percent-difference figure when the two totals
    disagree.

    Depends on :func:`compare_columns_with_difference` having been run first
    to populate the ``_difference`` columns. Numerical entries without a
    corresponding ``_difference`` column on ``df`` are silently skipped;
    string entries and ``None`` entries are skipped by design.

    Args:
        df (pd.DataFrame): DataFrame already processed by
            :func:`compare_columns_with_difference`.
        comparison_dict (dict): Comparison dictionary used to produce the
            reconciled columns.

    Returns:
        pd.DataFrame: Summary table with columns
        ``[Numerical Column, Difference, Total, Percent Difference]``.
    """
    results = []
    
    for key, params in comparison_dict.items():
        if params and params['type'] == 'numerical' and f"{key}_difference" in df.columns:
            difference_summed = df[f"{key}_difference"].sum()
            total = max(df[params['columns'][0]].sum(), df[params['columns'][1]].sum())
            percent_error = (difference_summed / total * 100) if total else 0

            results.append({
                'Numerical Column': key,
                'Difference': difference_summed,
                'Total': total,
                'Percent Difference': percent_error
            })

    return pd.DataFrame(results)


def sum_top_x_differences(df, comparison_dict, x):
    """Split each numerical column's total disagreement into "top x" vs. "rest".

    For each numerical column with a ``_difference`` column on ``df``, picks
    the ``x`` largest absolute differences (via ``nlargest``) and sums them,
    then reports the sum of everything outside that top group. Useful for
    answering "if I manually reconciled the worst N rows, how much
    disagreement would remain?" — a long-tail vs. concentrated-error
    diagnostic.

    Depends on :func:`compare_columns_with_difference` having been run first.

    Args:
        df (pd.DataFrame): DataFrame already processed by
            :func:`compare_columns_with_difference`.
        comparison_dict (dict): Comparison dictionary used to produce the
            reconciled columns.
        x (int): Number of largest differences to bucket as "top".

    Returns:
        pd.DataFrame: Summary table with columns
        ``[Numerical Column, "Top {x} Sum", "Remaining Sum ({x})"]``. The
        column headers include the ``x`` value so multiple calls can be
        joined without name collisions.
    """
    results = []
    
    for key, params in comparison_dict.items():
        if params and params['type'] == 'numerical' and f"{key}_difference" in df.columns:
            sorted_differences = df[f"{key}_difference"].nlargest(x)
            top_x_sum = sorted_differences.sum()
            remaining_sum = df[f"{key}_difference"].sum() - top_x_sum

            results.append({
                'Numerical Column': key,
                f'Top {x} Sum': top_x_sum,
                f'Remaining Sum ({x})': round(remaining_sum, 2)
            })
    
    return pd.DataFrame(results)


def compare_multiple_x_values(df, comparison_dict, x_values):
    """Run :func:`sum_top_x_differences` for several ``x`` values and join them.

    Calls :func:`sum_top_x_differences` once per entry in ``x_values`` and
    outer-merges the results on ``"Numerical Column"``, so each row shows how
    a single column's disagreement breaks down at different thresholds. The
    outer join means a column that appears in some calls but not others (for
    example if it has fewer than ``x`` differences) is still represented.

    Args:
        df (pd.DataFrame): DataFrame already processed by
            :func:`compare_columns_with_difference`.
        comparison_dict (dict): Comparison dictionary used to produce the
            reconciled columns.
        x_values (list): Threshold values to evaluate (each fed to
            :func:`sum_top_x_differences`).

    Returns:
        pd.DataFrame: One row per numerical column. Columns are
        ``"Numerical Column"`` plus the ``"Top {x} Sum"`` /
        ``"Remaining Sum ({x})"`` pair for each ``x`` in ``x_values``.
    """
    master_df = None
    
    for x in x_values:
        temp_df = sum_top_x_differences(df, comparison_dict, x)
        
        if master_df is None:
            master_df = temp_df
        else:
            master_df = master_df.merge(temp_df, on="Numerical Column", how='outer')
    
    return master_df


def analyze_difference_reduction(df, comparison_dict, x_values):
    """Quantify how much resolving the top X disagreements would shrink the total.

    For each numerical column with a ``_difference`` column on ``df``, this
    starts from the original total disagreement and simulates manually
    reconciling the largest ``x`` differences for every ``x`` in
    ``x_values``. The output shows both the absolute remaining difference
    and the resulting percent difference at each threshold, which makes it
    easy to justify how many rows are worth a human's attention.

    Mechanics:
        * "Total Sum" is ``max(sum(col1), sum(col2))`` — same convention as
          :func:`report_difference` — used as the denominator for percent
          difference. Picking the max keeps the percent conservative.
        * For each ``x``, the top ``x`` absolute differences are summed
          (``nlargest``). That sum is treated as "resolved" and subtracted
          from the original total to compute the new total and new percent.

    All numeric outputs are rounded to two decimals (or three for percent
    values).

    Args:
        df (pd.DataFrame): DataFrame already processed by
            :func:`compare_columns_with_difference`.
        comparison_dict (dict): Comparison dictionary used to produce the
            reconciled columns.
        x_values (list): Threshold values to evaluate.

    Returns:
        pd.DataFrame: One row per numerical column with base columns
        ``[Numerical Column, Original Difference, Total Sum,
        Original Percent Difference]`` plus, for each ``x`` in ``x_values``,
        ``[Reduction (Top x), New Total Difference (After x),
        New Percent Difference (After x)]``.
    """
    results = []

    # Compute original differences
    for key, params in comparison_dict.items():
        if params and params['type'] == 'numerical' and f"{key}_difference" in df.columns:
            total_difference = df[f"{key}_difference"].sum()
            total_sum = max(df[params['columns'][0]].sum(), df[params['columns'][1]].sum())
            original_percent_diff = (total_difference / total_sum * 100) if total_sum else 0
            
            # Initialize a dictionary for this key
            report_entry = {
                'Numerical Column': key,
                'Original Difference': round(total_difference, 2),
                'Total Sum': round(total_sum, 2),
                'Original Percent Difference': round(original_percent_diff, 3)
            }

            # Compute difference reduction for each X value
            for x in x_values:
                # Get top X largest differences
                sorted_differences = df[f"{key}_difference"].nlargest(x)
                top_x_sum = sorted_differences.sum()

                # Compute new total difference after resolving X discrepancies
                new_total_diff = total_difference - top_x_sum
                new_percent_diff = (new_total_diff / total_sum * 100) if total_sum else 0

                # Store in dictionary dynamically
                report_entry[f'Reduction (Top {x})'] = round(top_x_sum, 2)
                report_entry[f'New Total Difference (After {x})'] = round(new_total_diff, 2)
                report_entry[f'New Percent Difference (After {x})'] = round(new_percent_diff, 3)

            # Append to results list
            results.append(report_entry)

    # Convert results to DataFrame
    return pd.DataFrame(results)
