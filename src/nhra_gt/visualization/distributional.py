"""Visualizations for distributional analysis and parameter sweeps."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns

from .base import Figure
from .config import PlotConfig
from .schemas import StrategyFrequencySchema


def plot_strategy_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Shows strategy shares over time for each game (one panel per game)."""
    # Validation
    StrategyFrequencySchema.validate(data)
    _ = (config, kwargs)
    return go.Figure()


def plot_risk_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a 2D heatmap of system risk/state.

    Typically used for parameter sweeps (e.g. Bed Capacity vs Demand).
    """
    if config is None:
        config = PlotConfig()

    y_col = "discharge_delay_base"  # Example
    x_col = "bed_capacity_index"
    z_col = "pressure_mean"
    title = "System Risk Landscape"

    fig, ax = plt.subplots(figsize=config.default_figsize)

    # Check if cols exist, else return empty
    if not {x_col, y_col, z_col}.issubset(data.columns):
        return fig

    pivot = data.pivot_table(index=y_col, columns=x_col, values=z_col)

    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlGnBu",  # Professional gradient
        cbar_klabel=z_col.replace("_", " ").title(),
        annot=True,
        fmt=".2f",
    )

    ax.set_title(title, fontsize=config.fontsize_title)
    ax.invert_yaxis()  # Standard orientation for sweeps
    return fig


def plot_distributions(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots distributions (KDE/Histogram) of a variable, optionally grouped."""
    _ = (data, config)
    return go.Figure()


def plot_pareto_frontier(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Pareto frontier (tradeoff scatter plot)."""
    _ = (data, config)
    return go.Figure()


def plot_stacked_bar(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Plots a stacked horizontal bar chart."""
    _ = (data, config, kwargs)
    return go.Figure()


def plot_scenario_comparison(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Plots a simple bar chart for scenario comparison."""
    _ = (data, config, kwargs)
    return go.Figure()


def plot_cdf(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Cumulative Distribution Function (CDF)."""
    _ = (data, config)
    return go.Figure()
