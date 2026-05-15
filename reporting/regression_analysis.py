import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from typing import List

from typing import List, Optional, Dict, Any, Union, Sequence

import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
from matplotlib import cm
from matplotlib.ticker import StrMethodFormatter


def regression_analysis_2(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    title: Optional[str] = None,
    figsize=(10, 6),
    legend_location: str = "best",
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    x_ticks: Optional[List[float]] = None,

    # legend control
    legend: bool = True,
    legend_font_size: Optional[int] = 14,

    # font controls
    font: Optional[str] = 'arial',
    title_font_size: int = 20,
    axis_font_size: int = 16,
    tick_font_size: Optional[int] = 14,
    x_tick_rotation: Optional[int] = 0,
    x_tick_ha: Optional[str] = 'center',

    # color control (colormap name or explicit list)
    palette: Optional[Union[str, Sequence]] = ["#2C5234", "#F2A900"],

    # scatter point size and opacity
    point_size: Optional[float] = 130,
    point_alpha: float = 1,

    # trendline weight
    line_width: Optional[float] = 3,

    # connecting lines between points
    connecting_lines: bool = False,
    connecting_line_width: Optional[float] = None,
    connecting_line_alpha: float = 0.7,

    # y-axis tick formatting
    y_tick_fmt: Optional[str] = '{x:,.0f}',

    # NEW: theming / color controls
    plot_bg_color: Optional[str] = None,
    figure_bg_color: Optional[str] = None,
    text_color: Optional[str] = None,
    grid_color: Optional[str] = None,
    frame_color: Optional[str] = None,

    # NEW: legend theming
    legend_facecolor: Optional[str] = None,
    legend_edgecolor: Optional[str] = None,
    legend_framealpha: Optional[float] = None,
):
    """Scatter-plot one or more y-columns against x, overlay OLS trendlines, and return regression statistics.

    Args:
        df (pd.DataFrame): DataFrame containing the data for regression.
        x_col (str): Name of the column to use as the independent variable (x-axis).
        y_cols (list of str): Column names to use as dependent variables; one series
            and trendline is drawn per column.
        x_label (str, optional): X-axis label.
        y_label (str, optional): Y-axis label.
        title (str, optional): Chart title.
        figsize (tuple): Figure dimensions as ``(width, height)`` in inches.
            Defaults to ``(10, 6)``.
        legend_location (str): Matplotlib legend location string. Defaults to
            ``"best"``.
        y_min (float, optional): Lower bound for the y-axis.
        y_max (float, optional): Upper bound for the y-axis.
        x_ticks (list of float, optional): Explicit tick positions for the x-axis.
        legend (bool): Whether to display the legend. Defaults to True.
        legend_font_size (int, optional): Font size for legend text. Defaults to 14.
        font (str, optional): Font family applied to all text elements. Defaults to
            ``"arial"``.
        title_font_size (int): Font size for the chart title. Defaults to 20.
        axis_font_size (int): Font size for axis labels. Defaults to 16.
        tick_font_size (int, optional): Font size for tick labels. Defaults to 14.
        x_tick_rotation (int, optional): Rotation angle for x-axis tick labels in
            degrees. Defaults to 0.
        x_tick_ha (str): Horizontal alignment of x-axis tick labels
            (``"left"``, ``"center"``, ``"right"``). Defaults to ``"center"``.
        palette (str or sequence, optional): Series colors. Pass a matplotlib
            colormap name (e.g. ``"tab10"``) or a list/tuple of hex/named colors.
            Defaults to green/gold.
        point_size (float, optional): Marker size for scatter points (matplotlib
            ``s`` parameter). Defaults to 130.
        point_alpha (float): Opacity of scatter points (0.0–1.0). Defaults to 1.
        line_width (float, optional): Width of the regression trendline. Defaults to 3.
        connecting_lines (bool): If True, draws lines connecting points sorted by
            x-value. Useful for time-series data. Defaults to False.
        connecting_line_width (float, optional): Width of connecting lines.
        connecting_line_alpha (float): Opacity of connecting lines (0.0–1.0).
            Defaults to 0.7.
        y_tick_fmt (str, optional): Format string for y-axis ticks using
            ``StrMethodFormatter`` syntax. Defaults to ``'{x:,.0f}'``.
        plot_bg_color (str, optional): Background color of the axes/chart area.
        figure_bg_color (str, optional): Background color of the outer figure canvas.
        text_color (str, optional): Color applied to all text elements.
        grid_color (str, optional): Color of the gridlines.
        frame_color (str, optional): Color of axis spines and tick marks.
        legend_facecolor (str, optional): Fill color of the legend box background.
        legend_edgecolor (str, optional): Border color of the legend box.
        legend_framealpha (float, optional): Opacity of the legend background
            (0.0–1.0).

    Returns:
        dict: Regression statistics keyed by column name. Each value is a dict
        with keys ``"slope"``, ``"intercept"``, ``"p_value"``, and ``"r_squared"``.

    Example:
        >>> import pandas as pd
        >>> import Helper_Functions.reporting.regression_analysis as ra
        >>> df = pd.DataFrame({
        ...     "Year": [2018, 2019, 2020, 2021, 2022, 2023],
        ...     "Part1_Apps": [80, 95, 102, 88, 115, 130],
        ...     "Part2_Apps": [60, 72, 78, 65, 90, 104],
        ... })
        >>> stats = ra.regression_analysis_2(
        ...     df,
        ...     x_col="Year",
        ...     y_cols=["Part1_Apps", "Part2_Apps"],
        ...     title="Tax Credit Applications Over Time",
        ...     x_label="Year",
        ...     y_label="Applications",
        ...     connecting_lines=True,
        ... )
        >>> print(stats["Part1_Apps"]["slope"])
    """
    stats: Dict[str, Dict[str, Any]] = {}

    # Resolve colors
    colors = None
    if palette is not None:
        if isinstance(palette, str):
            cmap = cm.get_cmap(palette)
            try:
                colors = list(cmap.colors)  # works for many qualitative maps (tab10, Set2, etc.)
            except AttributeError:
                # fallback for continuous colormaps
                n = max(1, len(y_cols))
                colors = [cmap(i / max(1, n - 1)) for i in range(n)]
        else:
            colors = list(palette)

    # Initialize plot (object-oriented style)
    fig, ax = plt.subplots(figsize=figsize)

    # Iterate through Y columns
    for i, y_col in enumerate(y_cols):
        # Extract paired non-null data for x_col and current y_col
        sub = df[[x_col, y_col]].dropna()
        if sub.empty:
            continue

        x = sub[x_col].astype(float)
        y = sub[y_col].astype(float)

        # Perform linear regression
        X = sm.add_constant(x)  # Add intercept to model
        model = sm.OLS(y, X).fit()

        # Extract regression statistics
        slope = float(model.params.iloc[1])
        intercept = float(model.params.iloc[0])
        p_value = float(model.pvalues.iloc[1])
        r_squared = float(model.rsquared)

        stats[y_col] = {
            "slope": slope,
            "intercept": intercept,
            "p_value": p_value,
            "r_squared": r_squared,
        }

        # Choose series color
        c = colors[i % len(colors)] if colors else f"C{i}"

        # Plot data and regression line
        scatter_kwargs = {"alpha": point_alpha, "color": c}
        if point_size is not None:
            scatter_kwargs["s"] = point_size
        ax.scatter(x, y, **scatter_kwargs)
        line_kwargs = {"linestyle": "--", "label": f"{y_col} (slope={slope:.2f})", "color": c}
        if line_width is not None:
            line_kwargs["linewidth"] = line_width
        ax.plot(x, slope * x + intercept, **line_kwargs)

        # Plot connecting lines between points (sorted by x-axis value)
        if connecting_lines:
            sorted_indices = x.argsort()
            x_sorted = x.iloc[sorted_indices].values
            y_sorted = y.iloc[sorted_indices].values
            connecting_kwargs = {"color": c, "alpha": connecting_line_alpha, "linestyle": "-"}
            if connecting_line_width is not None:
                connecting_kwargs["linewidth"] = connecting_line_width
            ax.plot(x_sorted, y_sorted, **connecting_kwargs)

    # Title and axis labels with font controls
    _font_kw = {"fontname": font} if font is not None else {}
    if title:
        ax.set_title(title, fontsize=title_font_size, **_font_kw)
    if x_label:
        ax.set_xlabel(x_label, fontsize=axis_font_size, **_font_kw)
    if y_label:
        ax.set_ylabel(y_label, fontsize=axis_font_size, **_font_kw)

    grid_kwargs = {"visible": True}
    if grid_color is not None:
        grid_kwargs["color"] = grid_color
    ax.grid(**grid_kwargs)

    # Tick font size and family
    if tick_font_size is not None:
        ax.tick_params(axis="both", labelsize=tick_font_size)
    if font is not None:
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname(font)

    # Legend on/off
    handles, _ = ax.get_legend_handles_labels()
    if legend and handles:
        legend_prop = {}
        if legend_font_size is not None:
            legend_prop["size"] = legend_font_size
        if font is not None:
            legend_prop["family"] = font
        ax.legend(loc=legend_location, prop=legend_prop if legend_prop else None)

    # Legend theming
    legend_obj = ax.get_legend()
    if legend_obj:
        if legend_facecolor is not None:
            legend_obj.get_frame().set_facecolor(legend_facecolor)
        if legend_edgecolor is not None:
            legend_obj.get_frame().set_edgecolor(legend_edgecolor)
        if legend_framealpha is not None:
            legend_obj.get_frame().set_alpha(legend_framealpha)

    # Y limits (robust to partial bounds)
    if y_min is not None or y_max is not None:
        ax.set_ylim(bottom=y_min, top=y_max)

    # Custom X ticks
    if x_ticks is not None:
        ax.set_xticks(x_ticks)

    # Y-axis tick formatting
    if y_tick_fmt is not None:
        ax.yaxis.set_major_formatter(StrMethodFormatter(y_tick_fmt))

    # Theming
    if plot_bg_color is not None:
        ax.set_facecolor(plot_bg_color)
    if figure_bg_color is not None:
        fig.set_facecolor(figure_bg_color)
    if frame_color is not None:
        for spine in ax.spines.values():
            spine.set_edgecolor(frame_color)
        ax.tick_params(color=frame_color)
    if text_color is not None:
        ax.title.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.tick_params(labelcolor=text_color)
        legend_obj = ax.get_legend()
        if legend_obj:
            for t in legend_obj.get_texts():
                t.set_color(text_color)

    fig.tight_layout()

    # Rotation must come after tight_layout so tick labels are populated
    if x_tick_rotation is not None:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(x_tick_rotation)
            lbl.set_ha(x_tick_ha)

    plt.show()

    return stats


def analyze_trends(df, top_x, trend='increasing'):
    """Calculate OLS linear regression for each column and return the top trending series.

    Columns with fewer than 3 non-null data points are skipped.

    Args:
        df (pd.DataFrame): DataFrame with a numeric index (e.g. years) and one
            agency/category per column.
        top_x (int): Number of top trends to return.
        trend (str): ``"increasing"`` to rank by largest (most positive) slope;
            ``"decreasing"`` to rank by smallest (most negative) slope.
            Defaults to ``"increasing"``.

    Returns:
        dict: Keyed by column name; each value is a dict with keys
        ``"slope"``, ``"intercept"``, and ``"p_value"``.

    Example:
        >>> trends = analyze_trends(df, top_x=5, trend="increasing")
        >>> for name, stats in trends.items():
        ...     print(name, stats["slope"])
    """
    trends = {}

    for column in df.columns:
        y = df[column].dropna()
        x = y.index.astype(float)  # Ensure the index is numeric for regression

        if len(y) < 3:
            # Skip columns with insufficient data for regression
            continue

        X = sm.add_constant(x)  # Add intercept to model
        model = sm.OLS(y.values, X).fit()

        trends[column] = {
            'slope': model.params[1],
            'intercept': model.params[0],
            'p_value': model.pvalues[1],
        }

    # Sort by slope and select top_x trends
    sorted_trends = sorted(
        trends.items(),
        key=lambda item: item[1]['slope'],
        reverse=(trend == 'increasing')
    )

    # Return top_x trends as a dictionary
    return dict(sorted_trends[:top_x])


def plot_top_trends(df, top_x, trend='increasing', x_col_name='Year', title='Top Trends', **kwargs):
    """Identify and plot the top trending columns in a DataFrame.

    Combines :func:`analyze_trends` with :func:`regression_analysis_2` to find
    the ``top_x`` most strongly increasing or decreasing columns and render a
    scatter-plus-trendline chart in a single call.

    Args:
        df (pd.DataFrame): DataFrame with a numeric index (e.g. years) and one
            agency/category per column.
        top_x (int): Number of top trends to identify and display.
        trend (str): ``"increasing"`` or ``"decreasing"``. Defaults to
            ``"increasing"``.
        x_col_name (str): Name for the x-axis column added internally before
            passing to :func:`regression_analysis_2`. Defaults to ``"Year"``.
        title (str): Chart title. Defaults to ``"Top Trends"``.
        **kwargs: Any additional keyword arguments forwarded to
            :func:`regression_analysis_2` (e.g. ``figsize``, ``palette``,
            ``connecting_lines``, ``y_label``).

    Returns:
        dict: Regression statistics from :func:`regression_analysis_2`, keyed by
        column name. Each value contains ``"slope"``, ``"intercept"``,
        ``"p_value"``, and ``"r_squared"``.

    Example:
        >>> import Helper_Functions.reporting.regression_analysis as ra
        >>> stats = ra.plot_top_trends(
        ...     df,
        ...     top_x=5,
        ...     trend="increasing",
        ...     title="Top 5 Growing Programs",
        ...     y_label="Applications",
        ...     connecting_lines=True,
        ... )
    """
    trend_data = analyze_trends(df, top_x, trend)
    y_cols = list(trend_data.keys())

    # Add index as a column for regression_analysis_2
    df_for_plot = df.copy()
    df_for_plot[x_col_name] = df.index.astype(float)

    return regression_analysis_2(
        df_for_plot,
        x_col=x_col_name,
        y_cols=y_cols,
        title=title,
        **kwargs
    )
