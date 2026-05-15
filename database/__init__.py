"""
Database connectivity for the CRIS SQL Server database.

Public API:
    DBConnector      — production CRIS database (YOUR_SERVER\\YOUR_INSTANCE)
    TEST_DBConnector — non-production CRIS database (YOUR_TEST_SERVER\\YOUR_TEST_INSTANCE)

Both use Windows Trusted Authentication; no username or password required.
The machine must be domain-joined with appropriate SQL Server permissions.
"""
from Helper_Functions.database.database_connections import DBConnector, TEST_DBConnector

__all__ = [
    "DBConnector",
    "TEST_DBConnector",
]
