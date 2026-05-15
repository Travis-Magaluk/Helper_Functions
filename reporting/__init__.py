"""
Publication-quality chart and reporting helpers built on Matplotlib.

Public API:
    create_bar_chart_from_df  — grouped or stacked bar charts with full styling control
    regression_analysis_2     — scatter plot with OLS regression line for a single series
    analyze_trends            — rank all columns by slope and return a summary DataFrame
    plot_top_trends           — scatter/line plot of the top-N increasing or decreasing trends
    count_nan_per_column      — NaN count summary DataFrame for data-quality reporting
"""
from Helper_Functions.reporting.graph_creation_2 import create_bar_chart_from_df
from Helper_Functions.reporting.regression_analysis import (
    regression_analysis_2,
    analyze_trends,
    plot_top_trends,
)
from Helper_Functions.reporting.general_reporting import count_nan_per_column

__all__ = [
    "create_bar_chart_from_df",
    "regression_analysis_2",
    "analyze_trends",
    "plot_top_trends",
    "count_nan_per_column",
]
