from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .config import PlotConfig
from .schemas import TrajectorySchema


def plot_trajectory(
    data: pd.DataFrame,
    y_col: str,
    ylabel: str,
    config: PlotConfig | None = None,
    q_low_col: str | None = None,
    q_high_col: str | None = None,
    **kwargs: Any,
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
    # Validation
    TrajectorySchema.validate(data)
    if y_col not in data.columns:
        raise ValueError(f"y_col '{y_col}' not found in data.")

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


def plot_comparison_trajectory(
    data: pd.DataFrame,
    y_col: str,
    ylabel: str,
    group_col: str = "Scenario",
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """
    Plots multiple trajectories for comparison across scenarios.

    Args:
        data: DataFrame containing 'year', y_col, and group_col.
        y_col: Column name for the metric.
        ylabel: Label for the y-axis.
        group_col: Column name to group by (e.g. 'Scenario').
        config: PlotConfig object.
        **kwargs: Passed to ax.plot.
    """
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    groups = data[group_col].unique()
    for i, grp in enumerate(groups):
        sub = data[data[group_col] == grp]
        color = config.color_palette[i % len(config.color_palette)]
        ax.plot(
            sub["year"],
            sub[y_col],
            label=str(grp),
            color=color,
            linewidth=config.linewidth,
            **kwargs,
        )

    ax.set_xlabel("Year", fontsize=config.fontsize_label)
    ax.set_ylabel(ylabel, fontsize=config.fontsize_label)
    ax.grid(True, alpha=config.alpha_grid)

    return fig


def plot_swarm(
    data: pd.DataFrame,
    y_col: str,
    ylabel: str,
    run_col: str = "run",
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """
    Plots a 'swarm' of Monte Carlo trajectories.

    Args:
        data: DataFrame with 'year', y_col, and run_col.
        y_col: Column name for the metric.
        ylabel: Label for the y-axis.
        run_col: Column name for the MC run ID.
        config: PlotConfig object.
        **kwargs: Passed to ax.plot for individual lines.
    """
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    runs = data[run_col].unique()
    for r in runs:
        sub = data[data[run_col] == r]
        ax.plot(
            sub["year"],
            sub[y_col],
            color=config.primary_color,
            alpha=0.1,
            linewidth=0.5,
            **kwargs,
        )

    # Mean line
    mean_df = data.groupby("year")[y_col].mean().reset_index()
    ax.plot(
        mean_df["year"],
        mean_df[y_col],
        color=config.error_color,
        linewidth=config.linewidth,
        label="Mean",
    )

    ax.set_xlabel("Year", fontsize=config.fontsize_label)
    ax.set_ylabel(ylabel, fontsize=config.fontsize_label)
    ax.legend(fontsize=config.fontsize_legend, frameon=False)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)
    ax.grid(True, alpha=config.alpha_grid)

    return fig
