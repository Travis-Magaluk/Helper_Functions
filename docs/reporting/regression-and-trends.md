# Regression & Trends

**Module:** `Helper_Functions.reporting.regression_analysis`

Three functions cover scatter/OLS regression plots and automated trend ranking.

---

## `regression_analysis_2()`

Scatter-plots one or more y-columns against a single x-column, overlays an OLS trendline for each, and returns regression statistics.

### Basic usage

```python
import pandas as pd
import Helper_Functions.reporting.regression_analysis as ra

df = pd.DataFrame({
    "Year": [2018, 2019, 2020, 2021, 2022, 2023],
    "Part1_Apps": [80, 95, 102, 88, 115, 130],
    "Part2_Apps": [60, 72, 78, 65, 90, 104],
})

stats = ra.regression_analysis_2(
    df,
    x_col="Year",
    y_cols=["Part1_Apps", "Part2_Apps"],
    title="Tax Credit Applications Over Time",
    x_label="Year",
    y_label="Applications",
)

# Access regression statistics
print(stats["Part1_Apps"])
# {'slope': 9.94, 'intercept': -19924.8, 'p_value': 0.003, 'r_squared': 0.87}
```

![Multi-series scatter plot with trendlines](img/regression_basic.png`)

### With connecting lines (time series)

```python
stats = ra.regression_analysis_2(
    df,
    x_col="Year",
    y_cols=["Part1_Apps", "Part2_Apps"],
    title="Applications Over Time",
    connecting_lines=True,
    connecting_line_alpha=0.5,
    point_size=100,
)
```

![Multi-series scatter plot with trendlines and connecting lines](img/connecting_lines.png`)

### Custom colors and theming

```python
stats = ra.regression_analysis_2(
    df,
    x_col="Year",
    y_cols=["Part1_Apps", "Part2_Apps"],
    title="Custom Themed Chart",
    palette=["#2C5234", "#F2A900"],
    plot_bg_color="#F8F8F8",
    figure_bg_color="#FFFFFF",
    text_color="#333333",
    grid_color="#DDDDDD",
)
```
![Multi-series scatter plot with trendlines and custom theming](img/reg_custom_colors.png`)

### Return value

Returns a `dict` keyed by column name. Each value is a dict with:

| Key | Description |
|---|---|
| `slope` | Regression slope (change per x-unit) |
| `intercept` | Y-intercept |
| `p_value` | P-value for the slope coefficient |
| `r_squared` | R² (coefficient of determination, 0–1) |

---

## `analyze_trends()`

Calculates OLS regression for every column in a DataFrame and returns the top `N` most strongly increasing or decreasing columns.

Useful for identifying which programs or categories are growing or shrinking fastest over a multi-year period.

### Usage

```python
# df has years as the index, one program/agency per column
trends = ra.analyze_trends(df, top_x=5, trend="increasing")

for name, stats in trends.items():
    print(f"{name}: slope={stats['slope']:.2f}, p={stats['p_value']:.3f}")
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `df` | `pd.DataFrame` | required | Numeric index (years), one series per column |
| `top_x` | `int` | required | Number of top trends to return |
| `trend` | `str` | `"increasing"` | `"increasing"` (largest slope) or `"decreasing"` (most negative slope) |

**Returns:** `dict` — keyed by column name; values contain `slope`, `intercept`, `p_value`.

!!! note
    Columns with fewer than 3 non-null data points are skipped.

---

## `plot_top_trends()`

Combines `analyze_trends()` and `regression_analysis_2()` into a single call — finds the top trending columns and plots them immediately.

### Usage

  ```python
  import pandas as pd
  import Helper_Functions.reporting.regression_analysis as ra

  df = pd.DataFrame(
      {
          "Tax_Credits_Commercial": [120, 145, 170, 195, 210, 240, 275],
          "Tax_Credits_Residential": [85, 100, 118, 135, 155, 178, 200],
          "Section_106_Reviews":     [450, 510, 580, 645, 720, 790, 860],
          "NR_Nominations":          [28, 30, 32, 35, 33, 38, 40],
          "Survey_Reports":          [75, 72, 78, 70, 68, 72, 65],
          "Easements":               [22, 20, 18, 19, 15, 14, 12],
      },
      index=[2018, 2019, 2020, 2021, 2022, 2023, 2024],
  )
  df.index.name = "Year"

  stats = ra.plot_top_trends(
      df,
      top_x=3,
      trend="increasing",
      title="Top 3 Growing Programs (2018–2024)",
      y_label="Annual Count",
      connecting_lines=True,
      figsize=(14, 7),
      palette='Set1'
  )
  ```

Any keyword argument accepted by `regression_analysis_2()` can be passed via `**kwargs`.

![Top 3 Program Trends](img/top3_trends.png`)

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `df` | `pd.DataFrame` | required | Numeric index, one series per column |
| `top_x` | `int` | required | Number of top trends to identify and plot |
| `trend` | `str` | `"increasing"` | `"increasing"` or `"decreasing"` |
| `x_col_name` | `str` | `"Year"` | Name for the x-axis column |
| `title` | `str` | `"Top Trends"` | Chart title |
| `**kwargs` | | | Forwarded to `regression_analysis_2()` |

**Returns:** `dict` — same regression statistics format as `regression_analysis_2()`.

---

## `count_nan_per_column()` — `general_reporting`

A quick utility to audit data completeness before a pipeline run.

```python
import Helper_Functions.reporting.general_reporting as gr

nan_summary = gr.count_nan_per_column(df, exclude_columns=["ProjectNum", "NPSProjectNumber"])
print(nan_summary)
```

**Returns:** `pd.DataFrame` with columns `"Column Name"` and `"NaN Count"`.
