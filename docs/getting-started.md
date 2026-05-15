# Getting Started

## Requirements

- Python 3.10 or higher
- A domain-joined Windows machine with SQL Server access to the CRIS database
- The following Python packages:

```
pandas
numpy
matplotlib
statsmodels
sqlalchemy
pyodbc
openpyxl
```

Install with pip:

```bash
pip install pandas numpy matplotlib statsmodels sqlalchemy pyodbc openpyxl
```

For the MkDocs documentation site itself:

```bash
pip install mkdocs mkdocs-material
```

## Python Path Configuration

The package uses absolute imports with the `Helper_Functions.` prefix. The parent directory of the `Helper_Functions/` folder must be on your Python path.

**In a Jupyter notebook:**

```python
import sys
sys.path.append(r"C:\path\to\parent_of_Helper_Functions")
```

**Permanently (via `.pth` file or IDE project settings):** Add the parent directory to your environment's `sys.path` so every notebook or script picks it up automatically.

## Verifying the setup

```python
from Helper_Functions.database.database_connections import DBConnector

db = DBConnector()
df = db.fetch_data("SELECT TOP 1 NPSProjectNumber FROM tblTaxCreditCommercial")
print(df)
```

If you see a one-row DataFrame, your path and database access are both working.

## Database connections

Two connectors are available:

| Class | Server | When to use |
|---|---|---|
| `DBConnector` | `YOUR_SERVER\YOUR_INSTANCE` | Production work |
| `TEST_DBConnector` | `YOUR_TEST_SERVER\YOUR_TEST_INSTANCE` | Validating changes before production |

Both use Windows Trusted Authentication — no username or password required, but the machine must be domain-joined with appropriate SQL Server permissions.

```python
from Helper_Functions.database.database_connections import DBConnector, TEST_DBConnector

# Production
db = DBConnector()

# Test environment
test_db = TEST_DBConnector()
```

## Importing modules

All modules follow the same import pattern:

```python
import Helper_Functions.audit.commercial_audit_pipeline as cap
import Helper_Functions.reporting.graph_creation_2 as gc
import Helper_Functions.reporting.regression_analysis as ra
import Helper_Functions.data_cleaning.text_clean as tc
import Helper_Functions.dataframe_comparison.compare_columns as cc
```
