"""Legacy comparison pipeline for commercial tax credit spreadsheet vs. CRIS audits.

.. deprecated::
    This module is superseded by :mod:`compare_columns` and
    :mod:`difference_reporting`. It remains for reference on older analysis
    notebooks. Prefer :func:`~compare_columns.run_comparison_and_reorder` for
    new work.
"""

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from typing import Dict, Tuple



def analyze_cris_xlsx(comp_dict: Dict[str, Tuple[str, str]], df: pd.DataFrame, x_lab: str, y_lab: str) -> pd.DataFrame:
    """
    Main funtion to analyze the commercial tax credit data compared to what is in CRIS

    Args:
        comp_dict (Dict[str, Tuple[str, str]]): _description_
        df (pd.DataFrame): _description_
        x_lab (str): Label for the X-Axis of the graph generated
        y_lab (str): Label for the Y-Axis of the graph generated

    Returns:
        df (pd.DataFrame): Dataframe containing original data for reference or further analysis
        pivot(pd.DataFrame): Dataframe in the format of a pivot table showing counts of various catageorical values
    """

    df = run_comparison(comp_dict, df)
    df = reorder_columns(comp_dict, df)
    pivot = prepare_for_graph(df, comp_dict)
    generate_graph(pivot, x_lab, y_lab)
    return df, pivot


def run_comparison(comp_dict: Dict[str, Tuple[str, str]], df: pd.DataFrame) -> pd.DataFrame:
    """Compares a set of columns defined by comp_dict and creates new column for each comparison

    Uses the compare columns function to compare each set of columns in comp_dict and returns a new column defined by the key of the
    dictionary.

    Args:
        comp_dict (Dict[str, Tuple[strm str]]): Key: str is new column name, string values in tuple are the two columns to be compared
        df (pd.DataFrame): dataframe to be modified. Must contain the columns in the dictionary tuples

    Returns:
        pd.DataFrame: Dataframe with the new columns created. 
    """
    for key in comp_dict.keys(): 
        compare_cols(key, comp_dict[key][0], comp_dict[key][1])
        df[key] = df.apply(compare_columns, args=(comp_dict[key][0], comp_dict[key][1]), axis=1)
    return df


def compare_cols(new_col: str, xlsx_col: str, cris_col: str):
    """
    Prints statements describing which columns are compared to each other. 

    Args:
        new_col (str): New Column in 
        xlsx_col (str): _description_
        cris_col (str): _description_
    """
    print(f'{new_col} is comparing CRIS Column: {cris_col} and xlsx Column: {xlsx_col}')


def compare_columns(row, xlsx_col: str, cris_col: str) -> str:
    """
    Compares two values and returns a string based on the values

    Designed to work with df.apply() method. Shows how the two columns compare. 

    Args:
        row (_type_): _description_
        xlsx_col (str): Column from the excel file (must be of float or int type)
        cris_col (str): Column from the CRIS database (must be of float or int type)


    Returns:
        str: returns one of the following values based on how the values related compare.
            Matching: values in each column are equal or equal when both values are rounded down to nearest integer
            Missing from XLSX: value is NaN in xlsx but non NaN value is present in CRIS
            Missing from CRIS: value is NaN in CRIS but non NaN value is present in xlsx
            Both Missing: values are NaN in both columns
            NOT Mathing: all other cases
    """

    if row[xlsx_col] == row[cris_col]:
        return 'Matching'
    elif not np.isnan(row[xlsx_col]) and not np.isnan(row[cris_col]):
        if row[xlsx_col] != math.floor(row[cris_col]):
            pass
        return 'NOT Matching'
    elif np.isnan(row[xlsx_col]) and row[cris_col]==row[cris_col]: 
        return 'Missing from XLSX'
    elif np.isnan(row[cris_col]) and row[xlsx_col]==row[xlsx_col]:
        return 'Missing from CRIS'
    elif np.isnan(row[cris_col]) and np.isnan(row[xlsx_col]):
        return 'Both Missing'
    else: 
        return "Matching"


def reorder_columns(comp_dict: Dict[str, Tuple[str, str]], df: pd.DataFrame) -> pd.DataFrame:
    """Reorder DataFrame columns so each comparison key precedes its source columns.

    Args:
        comp_dict (dict): Comparison dictionary whose keys are new column names
            and values are ``(xlsx_col, cris_col)`` tuples.
        df (pd.DataFrame): DataFrame that has been processed by :func:`run_comparison`.

    Returns:
        pd.DataFrame: DataFrame with columns ordered as key, xlsx_col, cris_col
        for each entry, followed by any remaining columns.
    """
    new_col_order = []
    cols = df.columns
    for key in comp_dict: 
        new_col_order.append(key)
        new_col_order.append(comp_dict[key][0])
        new_col_order.append(comp_dict[key][1])
    diff_list = list(set(cols) - set(new_col_order))
    diff_list.extend(new_col_order)
    df = df[diff_list]
    return df


def prepare_for_graph(df: pd.DataFrame, spec_dict: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    """
    Takes a dataframe of categorical values and outputs a pivot table of counts of the
    categorical values for each column broken down by each categorical value. 

    Args:
        df (pd.DataFrame): dataframe that has been modified by run_comparison()
        spec_dict (Dict[str, Tuple[str, str]]): dictionary used by run_comparision()

    Returns:
        pd.DataFrame: returns a pivot table 
    """
    df = df[list(spec_dict.keys())]
    melted = df.melt()
    counts = melted.reset_index().groupby(['variable', 'value']).count().reset_index()
    pivot = pd.pivot_table(
        counts,
        values='index',
        index='variable',
        columns='value'
        )
    
    custom_order = ["Matching", "Missing from CRIS", "Missing from XLSX", "Both Missing"]

    pivot = pivot.reindex(columns=custom_order)

    return pivot


def generate_graph(pivot: pd.DataFrame, x_lab: str, y_lab: str):
    """Generates a bar plot for counts of categorical values in the pivot table created with prepare_for_graph()

    Args:
        pivot (pd.DataFrame): Pivot table dataframe to create the plot from
        x_lab (str): Label for the X-Axis
        y_lab (str): Label for the Y-Axis
    """
    ax = pivot.plot(kind='bar')
    fig = ax.get_figure()
    fig.set_size_inches(12, 6)
    ax.set_xlabel(x_lab)
    ax.set_ylabel(y_lab)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    plt.show()

