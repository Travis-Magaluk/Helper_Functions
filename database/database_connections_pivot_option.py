
import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import os

class DBConnector:
    """
    Older version of this class and functions. Not used often. Keeping for legacy connections in notebooks.
    """
    def __init__(self):

        self.connection_string = "DRIVER={SQL Server};SERVER=YOUR_SERVER\YOUR_INSTANCE;DATABASE=CRIS;TRUSTED_CONNECTION=yes"
        self.connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": self.connection_string})
        self.engine = create_engine(self.connection_url)

    def fetch_data(self, sql_query):
        """_summary_

        Args:
            sql_query (str): sql query string

        Returns:
            pd.DataFrame: Dataframe containing data returned from sql query
        """
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql(sql_query, connection)
            return df
        except Exception as e:
            print(f'An unexpected error occured: {e}')
            return None
        

    def fetch_data_from_file(self,file_path:str, file_name: str) -> pd.DataFrame:
        
        file_path = os.path.join(file_path, file_name)
        
        with open(file_path, 'r') as file:
            query = file.read()

        return self.fetch_data(query)
    
    def fetch_and_pivot(self, file_path: str, file_name: str, pivot_dict: dict, **kwargs) -> pd.DataFrame:
        """
        Fetches and pivots data from a SQL file based on the pivot dictionary.

        Args:
            file_name (str): SQL file name.
            pivot_dict (dict): Pivot configuration dictionary.

        Returns:
            pd.DataFrame: A pivoted DataFrame, optionally normalized.
        """
        # Extract the normalize flag; default to False if not provided
        normalize = kwargs.get('normalize', False)

        # Extract pivot parameters from the dictionary
        pivot_params = pivot_dict.get(file_name, {})
        index = pivot_params.get("index")
        columns = pivot_params.get("columns")
        values = pivot_params.get("values")
        can_normalize = pivot_params.get("can_normalize", False)
        normalized_values = pivot_params.get("normalized_values")

        # Fetch the data
        df = self.fetch_data_from_file(file_path, file_name)

        # Determine which column to use for pivoting
        pivot_values = normalized_values if normalize and can_normalize and normalized_values in df.columns else values
        # pivot_values = values
        try: 
            pivoted_df = df.pivot(index=index, 
                                  columns=columns, 
                                  values=pivot_values)
            
            return pivoted_df

        except KeyError as e: 
            raise KeyError(f"Pivot error for {file_name}: Missing column '{e}' in the dataframe")
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error during pivot for {file_name}: {e}")

    def fetch_pivot_and_combine(self, file_path:str, file_list: list, pivot_dict: dict, consultations_only: bool = False, normalize: bool = False) -> pd.DataFrame:
        """
        Fetches, pivots, and combines data from multiple SQL files.

        Args:
            file_list (list): List of SQL file names to process.
            pivot_dict (dict): Pivot configuration dictionary.
            consultations_only (bool): If True, processes files where consultations_only is True.
            normalize (bool): If True, only include columns that can be normalized.

        Returns:
            pd.DataFrame: A combined DataFrame with normalized columns where applicable.
        """
        combined_df = pd.DataFrame()

        for file_name in file_list:
            # Extract pivot parameters
            pivot_params = pivot_dict.get(file_name, {})
            can_normalize = pivot_params.get("can_normalize", False)
            consultations_only_flag = pivot_params.get("consultations_only", False)

            # Skip files not matching consultations_only condition
            if consultations_only and not consultations_only_flag:
                print(f"Skipping file: {file_name} (consultations_only=False)")
                continue

            # Skip files that cannot be normalized when normalization is requested
            if normalize and not can_normalize:
                print(f"Skipping file: {file_name} (can_normalize=False)")
                continue

            # Fetch and pivot the data
            pivoted_df = self.fetch_and_pivot(file_path, file_name, pivot_dict, normalize=normalize)

            # Combine results
            if combined_df.empty:
                combined_df = pivoted_df
            else:
                combined_df = pd.merge(combined_df, pivoted_df, left_index=True, right_index=True, how="outer")

        return combined_df
