"""
Domain-specific text normalization for address and historic district data.

All functions are NaN-safe: if the input is NaN (as detected by pd.isna), the value
is returned unchanged. This makes every function safe to use with df.apply() on columns
that may contain missing values.

For primitive NaN-safe wrappers (lower, strip, title case), see safe_text_clean.py.
For composed multi-step cleaning pipelines, see text_clean_pipeliness.py.
"""
import re
import pandas as pd


def remove_some_punctuation(text):
    """
    Removes specific punctuation (commas, periods, double quotes) from a text string.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Text with specified punctuation removed, or NaN if input is NaN.
    """
    # Return NaN as-is
    if pd.isna(text):
        return text

    # Define specific punctuation to remove
    specific_punctuation = ['"']

    # Remove specified punctuation from the text
    for punctuation in specific_punctuation:
        text = text.replace(punctuation, '')

    return text


def replace_directionality(text):
    """
    Replaces abbreviated cardinal directions (e.g., 'n', 's.') with full words (e.g., 'north', 'south').

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Text with cardinal directions replaced, or NaN if input is NaN.
    """
    # Return NaN as-is
    if pd.isna(text):
        return text

    # Dictionary mapping abbreviations to full direction words
    direction_dict = {
        r'\bn\b': 'north',
        r'\bs\b': 'south',
        r'\be\b': 'east',
        r'\bw\b': 'west',
        r'\bn.\b': 'north',
        r'\bs.\b': 'south',
        r'\be.\b': 'east',
        r'\bw.\b': 'west'
    }

    # Replace abbreviations using regex
    for pattern, replacement in direction_dict.items():
        text = re.sub(pattern, replacement, text)

    return text


def replace_abbrivations(text):
    """
    Replaces common street abbreviations (e.g., 'st', 'ave') with full words.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Text with abbreviations replaced, or NaN if input is NaN.
    """
    # Return NaN as-is
    if pd.isna(text):
        return text

    # Dictionary mapping abbreviations to full words
    abv_dict = {
        r'\bpl\b': 'place',
        r'\bave\b': 'avenue',
        r'\bst\b': 'street',
        r'\bct\b': 'court',
        r'\brd\b': 'road',
        r'\bblvd\b': 'boulevard',
        r'\bdr\b': 'drive',
        r'\bsq\b': 'square'
    }

    # Replace abbreviations using regex
    for pattern, replacement in abv_dict.items():
        text = re.sub(pattern, replacement, text)

    return text

def replace_hashtag(text):
    """
    Replaces # with a blank string.

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Text with abbreviations replaced, or NaN if input is NaN.
    """
    if pd.isna(text):
        return text

    # Replace hyphens with spaces and trim the text
    return re.sub("#", " ", text).strip()



def clean_hyphens_decisions(value):
    """
    Replaces hyphens in the input text with spaces and trims whitespace.

    Args:
        value (str or NaN): Input text.

    Returns:
        str: Cleaned text with hyphens replaced, or NaN if input is NaN.
    """
    # Return NaN as-is
    if pd.isna(value):
        return value

    # Replace hyphens with spaces and trim the text
    return re.sub("-", " ", value).strip()


def replace_standardize_historic_district(df, column_names):
    """
    Standardizes 'HD' abbreviations in specified columns to 'Historic District'.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_names (list): List of column names to process.

    Returns:
        pd.DataFrame: DataFrame with standardized 'Historic District' text in the specified columns.
    """
    def sub_hd(text):
        # Return NaN as-is
        if pd.isna(text):
            return text

        # Convert to lowercase, replace 'HD', and return title case
        text = text.lower()
        text = re.sub(r'\bhd', 'Historic District', text)
        return text.title()

    # Apply the `sub_hd` function to each column
    for column in column_names:
        df[column] = df[column].apply(sub_hd)

    return df


def remove_periods_from_abbreviations(text):
    """
    Replaces abbreviated cardinal directions (e.g., 'n', 's.') with full words (e.g., 'north', 'south').

    Args:
        text (str or NaN): Input text.

    Returns:
        str: Text with cardinal directions replaced, or NaN if input is NaN.
    """
    # Return NaN as-is
    if pd.isna(text):
        return text

    # Dictionary mapping abbreviations to full direction words
    direction_dict = {
        r'\bnorth.\b': 'north ',
        r'\bsouth.\b': 'south ',
        r'\beast.\b': 'east ',
        r'\bwwest.\b': 'west ',
        r'\bplace.\b': 'place ',
        r'\bavenue.\b': 'avenue ',
        r'\bstreet.\b': 'street ',
        r'\bcourt.\b': 'court ',
        r'\broad.\b': 'road ',
        r'\bboulevard.\b': 'boulevard ',
        r'\bdrive.\b': 'drive ',
        r'\bsquare.\b': 'square '
    }

    # Replace abbreviations using regex
    for pattern, replacement in direction_dict.items():
        text = re.sub(pattern, replacement, text)

    return text



def standardize_phone_number(phone):
    """Format a 10-digit phone number as XXX-XXX-XXXX.

    Args:
        phone (str, int, or NaN): Raw phone value. Non-digit characters are
            stripped before formatting.

    Returns:
        str: Formatted phone string ``"XXX-XXX-XXXX"``, the original value if
        the digit count is not 10, or NaN if input is NaN.

    Example:
        >>> standardize_phone_number("(518) 474-0479")
        '518-474-0479'
    """
    if pd.isna(phone):
        return phone

    # remove all non-digit characters
    digits = re.sub(r'\D', '', str(phone))

    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
    else:
        return phone
    
