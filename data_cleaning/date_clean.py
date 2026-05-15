import pandas as pd
from datetime import datetime

def convert_address_date(date_str):
    """
    Converts a date string from '9-Feb-12' format to '2/9/12' (MM/DD/YY).
    Used for cleaning historic spreadsheets. No longer accessed. 

    Args:
        date_str (str or NaN): The date string to convert.

    Returns:
        str: Converted date string, or original value if conversion fails.
    """
    # Return NaN as-is
    if pd.isna(date_str):
        return date_str

    try:
        # Parse the date string using the known format
        parsed_date = datetime.strptime(date_str, "%d-%b-%y")
        # Convert the parsed date to MM/DD/YY format
        return parsed_date.strftime("%m/%d/%y")
    except (ValueError, TypeError):
        # Return original value if conversion fails
        return date_str