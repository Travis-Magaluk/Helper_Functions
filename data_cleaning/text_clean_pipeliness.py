import Helper_Functions.data_cleaning.safe_text_clean as stc
import Helper_Functions.data_cleaning.text_clean as tc


def full_address_clean(df, column_names):
    """
    Applies a series of cleaning functions to standardize addresses in specified columns.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_names (list): List of column names to clean.

    Returns:
        pd.DataFrame: DataFrame with cleaned address columns.
    """
    # Iterate through the specified columns
    for column in column_names:
        df[column] = df[column].apply(stc.safe_lower)              # Convert to lowercase
        df[column] = df[column].apply(stc.safe_strip)              # Remove leading/trailing whitespace
        df[column] = df[column].apply(tc.remove_some_punctuation) # Remove punctuation
        df[column] = df[column].apply(tc.replace_abbrivations)    # Replace abbreviations
        df[column] = df[column].apply(tc.replace_directionality)  # Replace cardinal directions

    return df


def standardize_text(df, column_names):
    """
    Standardizes text by applying title casing and stripping whitespace.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_names (list): List of column names to standardize.

    Returns:
        pd.DataFrame: DataFrame with standardized text columns.
    """
    for column in column_names:
        df[column] = df[column].apply(stc.safe_title)  # Convert to title case
        df[column] = df[column].apply(stc.safe_strip) # Remove leading/trailing whitespace

    return df


def remove_periods_from_abbreviations_full(df, column_names):
    """Remove trailing periods from spelled-out directional and street-type words.

    Pipeline: lowercase → strip → remove periods → title case.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_names (list): Column names to process.

    Returns:
        pd.DataFrame: DataFrame with periods removed from common abbreviations
        in the specified columns.
    """
    for column in column_names:
        df[column] = df[column].apply(stc.safe_lower)
        df[column] = df[column].apply(stc.safe_strip)
        df[column] = df[column].apply(tc.remove_periods_from_abbreviations)
        df[column] = df[column].apply(stc.safe_title)

    return df

