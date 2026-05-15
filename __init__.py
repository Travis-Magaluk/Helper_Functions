"""
Helper_Functions — a Python utility library for state historic preservation office data projects.

Subpackages:
    audit               — NPS quarterly decision audit pipeline and helpers
    database            — SQL Server connectivity (DBConnector, TEST_DBConnector)
    data_cleaning       — NaN-safe text, date, monetary, and column-splitting utilities
    dataframe_comparison — column-level DataFrame reconciliation and difference analysis
    reporting           — bar charts, regression plots, trend analysis, NaN summaries
    saved_lists_dicts   — shared reference dictionaries (pivot configurations, etc.)

Quick start:
    from Helper_Functions.audit import decision_audit_pipeline
    from Helper_Functions.database import DBConnector
    from Helper_Functions.reporting import create_bar_chart_from_df
    from Helper_Functions.data_cleaning import full_address_clean

See README.md or the docs/ site for full usage examples.
"""
from Helper_Functions import audit
from Helper_Functions import database
from Helper_Functions import data_cleaning
from Helper_Functions import dataframe_comparison
from Helper_Functions import reporting
from Helper_Functions import saved_lists_dicts

__all__ = [
    "audit",
    "database",
    "data_cleaning",
    "dataframe_comparison",
    "reporting",
    "saved_lists_dicts",
]
