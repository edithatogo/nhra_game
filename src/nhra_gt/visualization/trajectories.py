from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .config import PlotConfig


def plot_trajectory(
    data: pd.DataFrame,
    y_col: str,
    ylabel: str,
    config: PlotConfig | None = None,
    q_low_col: str | None = None,
    q_high_col: str | None = None,
    **kwargs,
) -> Figure:
    """
    Plots a time-series trajectory with optional quantile ribbons.

    Args:
        data: DataFrame containing 'year' and the target columns.
        y_col: Column name for the primary metric.
        ylabel: Label for the y-axis.
        config: PlotConfig object for styling.
        q_low_col: Optional column name for the lower quantile ribbon.
        q_high_col: Optional column name for the upper quantile ribbon.
        **kwargs: Additional parameters passed to ax.plot.

    Returns:
        A matplotlib Figure object.
    """
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    # Data extraction
    x = data["year"].to_numpy(dtype=float)
    y = pd.to_numeric(data[y_col], errors="coerce").to_numpy(dtype=float)

    # Main plot
    ax.plot(x, y, linewidth=config.linewidth, color=config.primary_color, **kwargs)

    # Quantile ribbon
    if q_low_col and q_high_col and q_low_col in data.columns and q_high_col in data.columns:
        q_low = pd.to_numeric(data[q_low_col], errors="coerce").to_numpy(dtype=float)
        q_high = pd.to_numeric(data[q_high_col], errors="coerce").to_numpy(dtype=float)
        ax.fill_between(x, q_low, q_high, color=config.primary_color, alpha=config.alpha_ribbon)

    # Labels and grid
    ax.set_xlabel("Year", fontsize=config.fontsize_label)
    ax.set_ylabel(ylabel, fontsize=config.fontsize_label)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)
    ax.grid(True, alpha=config.alpha_grid)

    return fig
