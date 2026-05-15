import matplotlib.pyplot as plt
from matplotlib import cm

def create_bar_chart_from_df(
    df,
    columns=None,
    x=None,
    stacked=False,
    title=None,
    xlabel=None,
    ylabel=None,
    figsize=(10, 6),
    palette=None,
    legend=True,
    y_min=None,
    y_max=None,

    # NEW: title styling
    title_font_size=14,
    title_font="DejaVu Sans",

    # NEW: axis label styling (xlabel/ylabel)
    axis_font_size=12,
    axis_font="DejaVu Sans",

    # Optional but commonly desired: tick label styling
    tick_font_size=10,
    tick_font="DejaVu Sans",

    # Existing behavior controls, made explicit
    x_tick_rotation=45,
    x_tick_ha="right",
):
    """
    Creates a bar chart using Pandas' DataFrame.plot.bar() method.

    Parameters:
        df: DataFrame containing the data.
        columns: str or list of str for y-values.
        x: str column to use as x-axis (index if None).
        stacked: stack bars if multiple columns.
        title/xlabel/ylabel: strings.
        figsize: (w, h).
        palette: matplotlib colormap name or list of colors.
        legend: show legend.
        y_min/y_max: y-axis bounds (set either or both).

        title_font_size/title_font: title styling.
        axis_font_size/axis_font: xlabel/ylabel styling.
        tick_font_size/tick_font: tick label styling.
        x_tick_rotation/x_tick_ha: x tick label orientation.
    """
    # Use index as x-axis if no x column is provided
    data = df if x is None else df.set_index(x)

    # Select specified columns if provided
    if columns:
        if isinstance(columns, str):
            columns = [columns]
        data = data[columns]

    # Determine colors
    if palette:
        if isinstance(palette, str):
            cmap = cm.get_cmap(palette)
            # Some colormaps return callable; handle both gracefully
            try:
                color_palette = cmap.colors[:len(data.columns)]
            except AttributeError:
                color_palette = [cmap(i) for i in range(len(data.columns))]
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

    # Title styling
    if title:
        ax.set_title(title, fontsize=title_font_size, fontname=title_font)

    # Axis labels styling
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=axis_font_size, fontname=axis_font)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=axis_font_size, fontname=axis_font)

    # Y limits: allow partial specification
    if y_min is not None or y_max is not None:
        ax.set_ylim(bottom=y_min, top=y_max)

    # Tick styling (x + y)
    ax.tick_params(axis="x", labelsize=tick_font_size)
    ax.tick_params(axis="y", labelsize=tick_font_size)
    for lbl in ax.get_xticklabels():
        lbl.set_fontname(tick_font)
        lbl.set_rotation(x_tick_rotation)
        lbl.set_ha(x_tick_ha)
    for lbl in ax.get_yticklabels():
        lbl.set_fontname(tick_font)

    plt.tight_layout()
    plt.show()
