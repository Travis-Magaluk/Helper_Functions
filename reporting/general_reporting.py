import pandas as pd

def count_nan_per_column(df: pd.DataFrame, exclude_columns: list) -> pd.DataFrame:
    """Return a summary of NaN counts per column, excluding specified columns.

    Args:
        df (pd.DataFrame): Input DataFrame to inspect.
        exclude_columns (list): Column names to skip. Columns that do not
            exist in ``df`` are silently ignored.

    Returns:
        pd.DataFrame: Two-column DataFrame with ``"Column Name"`` and
        ``"NaN Count"``, one row per included column.

    Example:
        >>> import pandas as pd
        >>> import Helper_Functions.reporting.general_reporting as gr
        >>> df = pd.DataFrame({"A": [1, None, 3], "B": [None, None, 6], "ID": [1, 2, 3]})
        >>> gr.count_nan_per_column(df, exclude_columns=["ID"])
          Column Name  NaN Count
        0           A          1
        1           B          2
    """
    # Drop excluded columns
    filtered_df = df.drop(columns=exclude_columns, errors='ignore')

    # Count NaN values per column
    nan_counts = filtered_df.isna().sum()

    # Create result dataframe
    result_df = pd.DataFrame({'Column Name': nan_counts.index, 'NaN Count': nan_counts.values})

    return result_df

