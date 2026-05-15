import pandas as pd
import re
import numpy as np


# Function: Process column without exploding rows
def split_check_date_column(df: pd.DataFrame, to_split_column_name: str, new_check_col: str, new_date_col: str, new_others_col: str):
    """
    Splits a column into separate check, date, and other information without changing the row count.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        to_split_column_name (str): The name of the column to split.
        new_check_col (str): The name of the column to store check numbers.
        new_date_col (str): The name of the column to store dates.
        new_others_col (str): The name of the column to store remaining unmatched data.

    Returns:
        pd.DataFrame: The updated DataFrame with new columns added.
    """

    # Helper function to extract the first match of a regex pattern
    def extract_pattern(value, pattern):
        """
        Extracts the first match of a given regex pattern from a string.

        Parameters:
            value (str): The string to search.
            pattern (str): The regex pattern to use.

        Returns:
            str or None: The first matching substring, or None if no match is found.
        """

        # Ensure the value is a string
        if not isinstance(value, str):
            value = str(value)
        matches = re.findall(pattern, value)
        return matches[0] if matches else None

    # Replace NaN with empty string and ensure all values are strings
    df[to_split_column_name] = df[to_split_column_name].fillna("").astype(str)


    # Extract check numbers using a regex pattern
    df[new_check_col] = df[to_split_column_name].apply(lambda x: extract_pattern(x, r'(#?\d+)'))

    # Extract dates using a regex pattern for multiple date formats
    df[new_date_col] = df[to_split_column_name].apply(lambda x: extract_pattern(x, r'(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})'))

    # Identify rows where neither check nor date patterns were found
    df[new_others_col] = df.apply(
        lambda row: row[to_split_column_name] if pd.isna(row[new_check_col]) and pd.isna(row[new_date_col]) else None, axis=1
    )

    return df



def split_owner_name(df):
    """
    Splits the 'OwnerName' column into first and last name columns in the dataset. 
    Used to process an old spreadsheet maintained by and executive. 
    No longer used. 

    Parameters:
        df (pd.DataFrame): The input DataFrame containing the 'OwnerName' column.
    
    Returns:
        pd.DataFrame: DataFrame with 'OwnerName' split into 'O_FirstName_D' and 'O_LastName_D'.
    
    Raises:
        ValueError: If the 'OwnerName' column does not exist.
    """
    # Check if "OwnerName" exists in the DataFrame
    if "OwnerName" not in df.columns:
        raise ValueError("The column 'OwnerName' does not exist in the dataset.")
    
    # Split 'OwnerName' into two parts: first name and last name
    df[['O_FirstName_D', 'O_LastName_D']] = (
        df['OwnerName']
        .astype(str)  # Ensure values are strings for split to work
        .where(df['OwnerName'].notna())  # Retain NaN values
        .str.split(n=1, expand=True)  # Split on the first space
    )
    
    df[['O_FirstName_D', 'O_LastName_D']] = df[['O_FirstName_D', 'O_LastName_D']].replace({None: np.nan})

    # Drop the original 'OwnerName' column
    df.drop(columns='OwnerName', inplace=True)
    
    return df



def split_shpo_column(df, to_split_column_name, pr_col_name, itc_col_name, other_col_name):
    """
    Splits a column into specific parts based on patterns and creates new columns for each part.
    Used for cleaning historic spreadsheets. No longer accessed. 

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        to_split_column_name (str): The name of the column to split.
        pr_col_name (str): The name of the column to store 'PR' pattern matches.
        itc_col_name (str): The name of the column to store 'ITC' pattern matches.
        other_col_name (str): The name of the column to store unmatched data.

    Returns:
        pd.DataFrame: The updated DataFrame with new columns and the original column dropped.
    """
    # Finding Cases that follow XXPR where X's are digits
    df[pr_col_name] = df[to_split_column_name].where(df[to_split_column_name].str.match(r'^\d{2}PR', na=False))

    # Finding cases that follow XXITC where X's are digits
    df[itc_col_name] = df[to_split_column_name].where(df[to_split_column_name].str.match(r'^\d{2}ITC', na=False))

    # Finding cases that do not match the above cases. 
    df[other_col_name] = df[to_split_column_name].where(~df[to_split_column_name].str.match(r'^\d{2}PR|^\d{2}ITC', na=False))

    # Dropping the original column
    df.drop(columns=to_split_column_name, inplace=True)
    return df


def split_decision_date(value):
    """
    Splits a value into decision and date parts.
    Used for cleaning historic spreadsheets. No longer accessed. 
    
    Parameters:
        value (str): The input string containing decision and date information.
        
    Returns:
        pd.Series: A Series containing the decision and date in separate columns.
    """
    # Handle missing values
    if pd.isna(value):  
        return pd.Series([np.nan, np.nan])  # Return NaN for missing values
    
    # Extract all dates from the string using a regex
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-[a-zA-Z]{3}-\d{2,4}", value)
    
    # Handle multiple dates
    if len(dates) > 1:  
        return pd.Series(["more than one decision", "more than one date"])
    
    # Handle a single date
    elif len(dates) == 1:  
        # Extract the date
        date = dates[0].strip()
        
        # Remove the date from the original string to isolate the decision
        decision = re.sub(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-[a-zA-Z]{3}-\d{2,4}", "", value).strip()
        
        # Return the decision and date
        return pd.Series([decision if decision else np.nan, date])
    
    # Handle cases with no dates
    else:  
        return pd.Series([value.strip(), np.nan])  # Keep the original value in the decision column
