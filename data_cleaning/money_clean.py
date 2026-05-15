import pandas as pd
from Helper_Functions.data_cleaning.safe_text_clean import safe_strip
import numpy as np

def full_money_clean(df, column_names):
    """
    Cleans monetary values in specified columns of a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_names (list): List of column names to clean.

    Returns:
        pd.DataFrame: DataFrame with cleaned monetary values in the specified columns.
    """
    # Iterate through each column in the list of column names
    for column in column_names:
        # Remove money-related punctuation and decimals from values in the column
        df[column] = df[column].apply(remove_money_punc_and_decimals)
        # Extract the highest value from multi-valued entries in the column

        df[column] = df[column].apply(safe_strip)

    return df


def remove_money_punc_and_decimals(text):
    """
    Removes specific money-related punctuation from a string.

    Args:
        text (str or NaN): Input text to clean.

    Returns:
        str: Cleaned text with money-related punctuation and decimals removed.
    """
    # If the value is NaN, return it as-is
    if pd.isna(text):
        return text

    # Define the specific punctuation characters to be removed
    specific_punctuation = ['$', ',']

    # Iterate over each punctuation character and remove it from the text
    for punctuation in specific_punctuation:
        text = str(text).replace(punctuation, '')

    return text


def extract_highest(value):
    """
    Extracts the highest value from a string containing multiple semicolon-separated values.

    Args:
        value (str): A string that contains multiple values separated by semicolons.

    Returns:
        str or float: The highest value in the string, or np.nan if conversion fails.
    """
    if pd.isnull(value) or value == "":
        return np.nan
    elif isinstance(value, str):
        try:
            # Split by ';', clean values, and convert to float
            all_vals = [int(v) for v in value.split(";")]
            return str(max(all_vals)) if all_vals else np.nan
        except ValueError:
            # Return NaN if conversion fails
            return np.nan
