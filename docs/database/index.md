# Database Connections

**Module:** `Helper_Functions.database.database_connections`

Two connector classes provide SQL Server access via SQLAlchemy + pyodbc using Windows Trusted Authentication. No username or password is required — the machine must be domain-joined with appropriate SQL Server permissions.

---

## `DBConnector` — Production

Connects to the **production** CRIS database at `YOUR_SERVER\YOUR_INSTANCE`.

```python
from Helper_Functions.database.database_connections import DBConnector

db = DBConnector()
```

### Methods

#### `fetch_data(sql_query)`

Execute a T-SQL query string and return results as a DataFrame.

```python
df = db.fetch_data("SELECT NPSProjectNumber, ProjectNum FROM tblTaxCreditCommercial")
```

| Parameter | Type | Description |
|---|---|---|
| `sql_query` | `str` | Valid T-SQL query |

**Returns:** `pd.DataFrame`, or `None` on error (error is printed to stdout).

#### `fetch_data_from_file(file_path)`

Read a `.sql` file and execute it.

```python
df = db.fetch_data_from_file("audit/SQL/decisions.sql")
```

| Parameter | Type | Description |
|---|---|---|
| `file_path` | `str` | Path to a `.sql` file (absolute or relative to working directory) |

**Returns:** `pd.DataFrame`, or `None` on error.

---

## `TEST_DBConnector` — Test Environment

Connects to the **non-production** CRIS database at `YOUR_TEST_SERVER\YOUR_TEST_INSTANCE`. Use this when validating new queries or pipeline changes before running them against production data.

```python
from Helper_Functions.database.database_connections import TEST_DBConnector

db = TEST_DBConnector()
df = db.fetch_data("SELECT TOP 5 * FROM tblTaxCreditCommercial")
```

### Methods

Same interface as `DBConnector`. The `fetch_data_from_file()` method looks for files relative to a `SQL/` subdirectory:

```python
df = db.fetch_data_from_file("decisions.sql")
# reads from: SQL/decisions.sql
```

---

## When to use each connector

| Situation | Connector |
|---|---|
| Running quarterly audit pipelines | `DBConnector` |
| Writing a new SQL query | `TEST_DBConnector` first, then `DBConnector` |
| Exploratory analysis or one-off queries | `DBConnector` |
| Any pipeline that writes data back to the DB | `TEST_DBConnector` to validate, then `DBConnector` |

!!! warning
    All audit functions (`commercial_audit.py`, `commercial_audit_pipeline.py`) instantiate `DBConnector` directly. To use the test environment, you must pass data in manually or temporarily swap the import.
