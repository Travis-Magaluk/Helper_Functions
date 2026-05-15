
import pandas as pd
import os
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

class DBConnector:
    """SQLAlchemy-backed connector for the production CRIS database.

    Connects to ``YOUR_SERVER\\YOUR_INSTANCE / CRIS`` using Windows Trusted
    Authentication (no username or password required). The machine must be
    domain-joined and have appropriate SQL Server access.

    Example:
        >>> from Helper_Functions.database.database_connections import DBConnector
        >>> db = DBConnector()
        >>> df = db.fetch_data("SELECT TOP 10 * FROM tblTaxCreditCommercial")
    """

    def __init__(self):
        self.connection_string = "DRIVER={SQL Server};SERVER=YOUR_SERVER\YOUR_INSTANCE;DATABASE=CRIS;TRUSTED_CONNECTION=yes"
        self.connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": self.connection_string})
        self.engine = create_engine(self.connection_url)

    def fetch_data(self, sql_query: str) -> pd.DataFrame:
        """Execute a SQL query string and return the results as a DataFrame.

        Args:
            sql_query (str): A valid T-SQL query string.

        Returns:
            pd.DataFrame: Query results, or ``None`` if an error occurred
            (the error is printed to stdout).

        Example:
            >>> db = DBConnector()
            >>> df = db.fetch_data("SELECT NPSProjectNumber FROM tblTaxCreditCommercial")
        """
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql(sql_query, connection)
            return df
        except Exception as e:
            print(f'An unexpected error occured: {e}')
            return None

    def fetch_data_from_file(self, file_path: str) -> pd.DataFrame:
        """Read a SQL query from a file and execute it.

        Args:
            file_path (str): Absolute or relative path to a ``.sql`` file.

        Returns:
            pd.DataFrame: Query results, or ``None`` if an error occurred.

        Example:
            >>> db = DBConnector()
            >>> df = db.fetch_data_from_file("audit/SQL/decisions.sql")
        """
        with open(file_path, 'r') as file:
            query = file.read()

        return self.fetch_data(query)
    

class TEST_DBConnector:
    """SQLAlchemy-backed connector for the test/non-production CRIS database.

    Connects to ``YOUR_TEST_SERVER\\YOUR_TEST_INSTANCE / CRIS`` using Windows Trusted
    Authentication. Use this connector when validating queries or pipeline
    changes against the test environment before running against production.

    Example:
        >>> from Helper_Functions.database.database_connections import TEST_DBConnector
        >>> db = TEST_DBConnector()
        >>> df = db.fetch_data("SELECT TOP 5 * FROM tblTaxCreditCommercial")
    """

    def __init__(self):
        self.connection_string = "DRIVER={SQL Server};SERVER=YOUR_TEST_SERVER\YOUR_TEST_INSTANCE;DATABASE=CRIS;TRUSTED_CONNECTION=yes"
        self.connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": self.connection_string})
        self.engine = create_engine(self.connection_url)

    def fetch_data(self, sql_query: str) -> pd.DataFrame:
        """Execute a SQL query string and return the results as a DataFrame.

        Args:
            sql_query (str): A valid T-SQL query string.

        Returns:
            pd.DataFrame: Query results, or ``None`` if an error occurred
            (the error is printed to stdout).
        """
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql(sql_query, connection)
            return df
        except Exception as e:
            print(f'An unexpected error occured: {e}')
            return None

    def fetch_data_from_file(self, file_name: str) -> pd.DataFrame:
        """Read a SQL query from a file in the ``SQL/`` subdirectory and execute it.

        Args:
            file_name (str): Filename (not full path) of a ``.sql`` file located
                in the ``SQL/`` subdirectory relative to the working directory.

        Returns:
            pd.DataFrame: Query results, or ``None`` if an error occurred.

        Example:
            >>> db = TEST_DBConnector()
            >>> df = db.fetch_data_from_file("decisions.sql")
        """
        file_path = os.path.join('SQL', file_name)

        with open(file_path, 'r') as file:
            query = file.read()

        return self.fetch_data(query)