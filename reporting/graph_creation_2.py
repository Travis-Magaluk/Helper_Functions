import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import StrMethodFormatter


def create_bar_chart_from_df(
    df,
    columns=None,
    x=None,
    stacked=False,
    title=None,
    xlabel=None,
    ylabel=None,
    figsize=(10, 6),
    palette=("#2C5234","#F2A900"),
    legend=True,
    y_min=None,
    y_max=None,

    # font controls
    font='Arial',
    title_font_size=20,
    axis_font_size=16,
    tick_font_size=14,

    x_tick_rotation=0,
    x_tick_ha="center",
    show_y_ticks=True,

    # trendline controls
    show_trendlines=False,
    trendline_style="--",
    trendline_linewidth=2,
    trendline_alpha=0.9,
    trendline_palette=None,

    # bar label controls
    annotate_bars=False,
    annotation_font_size=14,
    annotation_rotation=0,
    annotation_fmt="{:,.0f}",
    stack_label_style="total",  # total, segment

    # y-axis tick formatting
    y_tick_fmt='{x:,.0f}',

    # theming / color controls
    plot_bg_color=None,
    figure_bg_color=None,
    text_color=None,
    frame_color=None,

    # legend theming
    legend_facecolor=None,
    legend_edgecolor=None,
    legend_framealpha=None,
):
    """Create a bar chart from a DataFrame with extensive styling and annotation options.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        columns (str or list of str, optional): Column(s) to use as y-values.
            If None, all columns are plotted.
        x (str, optional): Column to use as the x-axis. If None, the DataFrame
            index is used.
        stacked (bool): If True, bars are stacked when multiple columns are plotted.
            Defaults to False.
        title (str, optional): Chart title.
        xlabel (str, optional): X-axis label.
        ylabel (str, optional): Y-axis label.
        figsize (tuple): Figure dimensions as ``(width, height)`` in inches.
            Defaults to ``(10, 6)``.
        palette (str or list of str, optional): Bar colors. Pass a matplotlib
            colormap name (e.g. ``"tab10"``) or a list of hex/named colors.
            Defaults to green/gold ``("#2C5234", "#F2A900")``.
        legend (bool): Whether to display a legend. Defaults to True.
        y_min (float, optional): Lower bound for the y-axis.
        y_max (float, optional): Upper bound for the y-axis.
        font (str, optional): Font family applied to all text elements.
            Defaults to ``"Arial"``.
        title_font_size (int): Font size for the chart title. Defaults to 20.
        axis_font_size (int): Font size for axis labels. Defaults to 16.
        tick_font_size (int): Font size for tick labels. Defaults to 14.
        x_tick_rotation (int): Rotation angle for x-axis tick labels in degrees.
            Defaults to 0.
        x_tick_ha (str): Horizontal alignment of x-axis tick labels
            (``"left"``, ``"center"``, ``"right"``). Defaults to ``"center"``.
        show_y_ticks (bool): If False, hides y-axis tick labels and marks.
            Defaults to True.
        show_trendlines (bool): If True, overlays a linear trendline per plotted
            column. Defaults to False.
        trendline_style (str): Line style for trendlines (e.g. ``"--"``).
            Defaults to ``"--"``.
        trendline_linewidth (float): Line width for trendlines. Defaults to 2.
        trendline_alpha (float): Opacity of trendlines (0.0–1.0). Defaults to 0.9.
        trendline_palette (str, list, or None): Colors for trendlines. ``None``
            matches bar colors; a str is a colormap name; a list provides explicit
            colors. Defaults to green/gold.
        annotate_bars (bool): If True, adds value labels to bars. Defaults to False.
        annotation_font_size (int): Font size for bar annotations. Defaults to 14.
        annotation_rotation (int): Rotation angle for bar annotations in degrees.
            Defaults to 0.
        annotation_fmt (str): Python format string for annotation values.
            Defaults to ``"{:,.0f}"``.
        stack_label_style (str): How to annotate stacked bars. ``"total"`` labels
            the total at the top of each stack; ``"segment"`` labels each individual
            segment at its center. Defaults to ``"total"``.
        y_tick_fmt (str, optional): Format string for y-axis tick labels using
            ``StrMethodFormatter`` syntax. Defaults to ``'{x:,.0f}'``.
        plot_bg_color (str, optional): Background color of the axes/chart area.
        figure_bg_color (str, optional): Background color of the outer figure canvas.
        text_color (str, optional): Color applied to all text elements (title,
            axis labels, tick labels, legend).
        frame_color (str, optional): Color of axis spines and tick marks.
        legend_facecolor (str, optional): Fill color of the legend box background.
        legend_edgecolor (str, optional): Border color of the legend box.
        legend_framealpha (float, optional): Opacity of the legend background
            (0.0–1.0).

    Returns:
        None: Displays the chart via ``plt.show()``.

    Example:
        >>> import pandas as pd
        >>> import Helper_Functions.reporting.graph_creation_2 as gc
        >>> df = pd.DataFrame({
        ...     "Year": [2020, 2021, 2022, 2023],
        ...     "Applications": [120, 145, 98, 160],
        ... })
        >>> gc.create_bar_chart_from_df(
        ...     df,
        ...     columns="Applications",
        ...     x="Year",
        ...     title="Historic Tax Credit Applications by Year",
        ...     ylabel="Number of Applications",
        ...     annotate_bars=True,
        ...     show_trendlines=True,
        ... )
    """
    # Use index as x-axis if no x column is provided
    data = df if x is None else df.set_index(x)

    # Select specified columns if provided
    if columns:
        if isinstance(columns, str):
            columns = [columns]
        data = data[columns]

    # Determine bar colors
    if palette:
        if isinstance(palette, str):
            cmap = cm.get_cmap(palette)
            try:
                color_palette = cmap.colors[:len(data.columns)]
            except AttributeError:
                color_palette = [
                    cmap(i / max(len(data.columns) - 1, 1))
                    for i in range(len(data.columns))
                ]
        else:
            color_palette = palette
    else:
        color_palette = None

    # Plot the bar chart
    ax = data.plot.bar(
        stacked=stacked,
        figsize=figsize,
        color=color_palette,
        legend=legend
    )

    _font_kw = {"fontname": font} if font is not None else {}

    # Title styling
    if title:
        ax.set_title(title, fontsize=title_font_size, **_font_kw)

    # Axis labels styling
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_font_size, **_font_kw)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_font_size, **_font_kw)

    # Y limits
    if y_min is not None or y_max is not None:
        ax.set_ylim(bottom=y_min, top=y_max)

    # Tick styling
    ax.tick_params(axis="x", labelsize=tick_font_size)
    ax.tick_params(axis="y", labelsize=tick_font_size)

    for lbl in ax.get_xticklabels():
        if font is not None:
            lbl.set_fontname(font)
        lbl.set_rotation(x_tick_rotation)
        lbl.set_ha(x_tick_ha)

    for lbl in ax.get_yticklabels():
        if font is not None:
            lbl.set_fontname(font)

    if not show_y_ticks:
        ax.yaxis.set_ticks([])

    # ---------------------------
    # Trendlines
    # ---------------------------
    if show_trendlines:
        x_positions = np.arange(len(data.index))

        # Grab bar colors so trendlines can match by default
        container_colors = []
        for container in ax.containers[:len(data.columns)]:
            if len(container) > 0:
                container_colors.append(container[0].get_facecolor())
            else:
                container_colors.append(None)

        # Determine trendline colors
        if trendline_palette is None:
            trend_colors = container_colors
        elif isinstance(trendline_palette, str):
            trend_cmap = cm.get_cmap(trendline_palette)
            try:
                trend_colors = trend_cmap.colors[:len(data.columns)]
            except AttributeError:
                trend_colors = [
                    trend_cmap(i / max(len(data.columns) - 1, 1))
                    for i in range(len(data.columns))
                ]
        else:
            trend_colors = trendline_palette

        for i, col in enumerate(data.columns):
            y_values = data[col].astype(float).values

            # Handle missing values safely
            valid_mask = ~np.isnan(y_values)
            x_valid = x_positions[valid_mask]
            y_valid = y_values[valid_mask]

            if len(x_valid) < 2:
                continue

            slope, intercept = np.polyfit(x_valid, y_valid, 1)
            y_fit = slope * x_positions + intercept

            line_color = trend_colors[i] if i < len(trend_colors) else None

            ax.plot(
                x_positions,
                y_fit,
                linestyle=trendline_style,
                linewidth=trendline_linewidth,
                alpha=trendline_alpha,
                color=line_color,
                label=f"{col} trend (slope={slope:.2f})"
            )

        if legend:
            ax.legend()

    # ---------------------------
    # Bar labels
    # ---------------------------
    if annotate_bars:
        if stacked and len(data.columns) > 1:
            if stack_label_style == "segment":
                # Label each stacked segment in the center
                for container in ax.containers[:len(data.columns)]:
                    labels = []
                    for bar in container:
                        height = bar.get_height()
                        if pd.isna(height) or height == 0:
                            labels.append("")
                        else:
                            labels.append(annotation_fmt.format(height))

                    texts = ax.bar_label(
                        container,
                        labels=labels,
                        label_type="center",
                        fontsize=annotation_font_size,
                        rotation=annotation_rotation
                    )
                    for t in texts:
                        if font is not None:
                            t.set_fontname(font)
            else:
                # Default: label totals at the top of each stacked bar
                totals = data.sum(axis=1)
                y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.01

                for i, total in enumerate(totals):
                    if pd.notna(total):
                        ax.text(
                            i,
                            total + y_offset,
                            annotation_fmt.format(total),
                            ha="center",
                            va="bottom",
                            fontsize=annotation_font_size,
                            rotation=annotation_rotation,
                            **_font_kw
                        )
        else:
            # Label each visible bar for non-stacked charts
            for container in ax.containers[:len(data.columns)]:
                labels = []
                for bar in container:
                    height = bar.get_height()
                    if pd.isna(height) or height == 0:
                        labels.append("")
                    else:
                        labels.append(annotation_fmt.format(height))

                texts = ax.bar_label(
                    container,
                    labels=labels,
                    padding=3,
                    fontsize=annotation_font_size,
                    rotation=annotation_rotation
                )
                for t in texts:
                    if font is not None:
                        t.set_fontname(font)

    # Y-axis tick formatting
    if y_tick_fmt is not None:
        ax.yaxis.set_major_formatter(StrMethodFormatter(y_tick_fmt))

    # Legend theming
    legend_obj = ax.get_legend()
    if legend_obj:
        if legend_facecolor is not None:
            legend_obj.get_frame().set_facecolor(legend_facecolor)
        if legend_edgecolor is not None:
            legend_obj.get_frame().set_edgecolor(legend_edgecolor)
        if legend_framealpha is not None:
            legend_obj.get_frame().set_alpha(legend_framealpha)

    # Theming
    fig = ax.get_figure()
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

    plt.tight_layout()
    plt.show()