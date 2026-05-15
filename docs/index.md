# Helper Functions

A Python utility library for various reporting, data cleaning, and other data efforts across a state historic preservation office. This was developed to keep repeatable functions in one location and prevent updates to functions coppied across multiple projects. The package connects to a Microsoft SQL Server database (CRIS) and provides tools for data cleaning, DataFrame comparison, audit pipeline orchestration, and publication-quality reporting charts.

## What's in this library?

| Module | Purpose |
|---|---|
| [`audit/`](audit/index.md) | End-to-end NPS quarterly decision audit pipeline |
| [`database/`](database/index.md) | SQL Server connectivity (production and test) |
| [`reporting/`](reporting/index.md) | Bar charts, regression plots, trend analysis |
| [`data_cleaning/`](data_cleaning/index.md) | Text, date, and monetary value normalization |
| [`dataframe_comparison/`](dataframe_comparison/index.md) | Column-level DataFrame diffing and difference analysis |

## Quick links

- [Getting Started](getting-started.md) — setup, imports, database access
- [Audit Pipeline](audit/pipeline.md) — run your first quarterly audit
- [Bar Charts](reporting/bar-charts.md) — create publication-ready charts
- [Regression & Trends](reporting/regression-and-trends.md) — analyze trends over time
