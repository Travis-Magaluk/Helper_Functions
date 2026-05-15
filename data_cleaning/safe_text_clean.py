"""
NaN-safe wrappers for Python's built-in string methods.

Each function checks pd.isna(text) before applying the operation and returns the
original value (NaN) unchanged if the input is missing. Use these as building blocks
inside df.apply() pipelines.

For domain-specific normalization (address abbreviations, directionality, punctuation),
see text_clean.py. For composed pipelines, see text_clean_pipeliness.py.
"""
import re
import pandas as pd


def safe_lower(text):
    """
    Converts text to lowercase safely, handling NaN values.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Lowercase text, or NaN if input is NaN.
    """
    return text.lower() if not pd.isna(text) else text


def safe_strip(text):
    """
    Removes leading and trailing whitespace safely, handling NaN values.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Stripped text, or NaN if input is NaN.
    """
    return text.strip() if not pd.isna(text) else text


def safe_remove_quotes(text):
    """
    Removes quote marks safely, handling NaN values.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: text with " removed, or NaN if input is NaN.
    """
    return re.sub("\"", "", text) if not pd.isna(text) else text


def safe_title(text):
    """
    Converts text to title case safely, handling NaN values.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Title-cased text, or NaN if input is NaN.
    """
    return text.title() if not pd.isna(text) else text

