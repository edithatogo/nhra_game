"""Visualizations for distributional analysis and parameter sweeps."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
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
    """Shows strategy shares over time for each game."""
    StrategyFrequencySchema.validate(data)
    _ = (config, kwargs)
    # Placeholder implementation
    fig = px.density_heatmap(data, x="year", y="strategy", z="share", facet_col="game")
    return fig


def plot_risk_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a 2D heatmap of system risk/state."""
    if config is None:
        config = PlotConfig()

    y_col = "discharge_delay_base"
    x_col = "bed_capacity_index"
    z_col = "pressure_mean"
    title = "System Risk Landscape"

    if not {x_col, y_col, z_col}.issubset(data.columns):
        return plt.figure()

    fig, ax = plt.subplots(figsize=config.default_figsize)
    pivot = data.pivot_table(index=y_col, columns=x_col, values=z_col)

    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlGnBu",
        cbar_klabel=z_col.replace("_", " ").title(),
        annot=True,
        fmt=".2f",
    )

    ax.set_title(title, fontsize=config.fontsize_title)
    ax.invert_yaxis()
    return fig


def plot_distributions(
    data: pd.DataFrame,
    column: str = "outcome",
    group_col: str | None = None,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots distributions (KDE/Histogram) of a variable."""
    if config is None:
        config = PlotConfig()

    if column not in data.columns:
        return go.Figure()

    fig = px.histogram(
        data,
        x=column,
        color=group_col,
        marginal="violin",
        title=f"Distribution of {column}",
        template="simple_white",
        color_discrete_sequence=[config.primary_color, "#FF7F50", "#4682B4"],
    )

    # Add mean line
    mean_val = data[column].mean()
    fig.add_vline(
        x=mean_val, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_val:.2f}"
    )

    return fig


def plot_pareto_frontier(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Pareto frontier (tradeoff scatter plot)."""
    if config is None:
        config = PlotConfig()

    fig = px.scatter(
        data, x=x_col, y=y_col, title=f"Tradeoff: {x_col} vs {y_col}", template="simple_white"
    )
    return fig


def plot_stacked_bar(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Plots a stacked horizontal bar chart."""
    _ = (config, kwargs)
    return px.bar(data, orientation="h")


def plot_scenario_comparison(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Plots a simple bar chart for scenario comparison."""
    _ = (config, kwargs)
    return px.bar(data)


def plot_cdf(
    data: pd.DataFrame,
    column: str = "outcome",
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Cumulative Distribution Function (CDF)."""
    if config is None:
        config = PlotConfig()

    fig = px.ecdf(data, x=column, title=f"CDF of {column}", template="simple_white")
    return fig
