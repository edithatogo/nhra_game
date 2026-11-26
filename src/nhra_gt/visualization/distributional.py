"""Visualizations for distributional analysis and parameter sweeps."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from matplotlib.figure import Figure

from .config import PlotConfig
from .schemas import StrategyFrequencySchema


def plot_strategy_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> Figure:
    """Shows strategy shares over time for each game (one panel per game)."""
    del kwargs
    # Validation
    StrategyFrequencySchema.validate(data)

    if config is None:
        config = PlotConfig()

    games = sorted(data["game"].unique())
    if not games:
        return plt.figure(figsize=config.default_figsize)
    figsize = (config.default_figsize[0], 2.1 * len(games))
    fig = plt.figure(figsize=figsize)

    for i, g in enumerate(games, start=1):
        ax = fig.add_subplot(len(games), 1, i)
        sub = data[data["game"] == g].copy()

        pivot = sub.pivot_table(
            index="year", columns="strategy", values="share", aggfunc="mean"
        ).fillna(0)

        for idx, col in enumerate(pivot.columns):
            color = config.color_palette[idx % len(config.color_palette)]
            ax.plot(
                pivot.index, pivot[col], label=f"{col}", linewidth=config.linewidth, color=color
            )

        ax.set_ylim(0, 1)
        ax.set_ylabel(g, fontsize=config.fontsize_label)
        ax.grid(True, alpha=config.alpha_grid)
        ax.tick_params(axis="both", labelsize=config.fontsize_tick)

        if i == 1:
            ax.legend(ncol=4, fontsize=config.fontsize_legend, loc="upper right", frameon=False)

    ax.set_xlabel("Year", fontsize=config.fontsize_label)
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
        cbar_kws={"label": z_col.replace("_", " ").title()},
        annot=True,
        fmt=".2f",
    )

    ax.set_title(title, fontsize=config.fontsize_title)
    ax.invert_yaxis()
    return fig


def plot_distributions(
    data: pd.DataFrame,
    value_col: str = "outcome",
    group_col: str | None = None,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots distributions (KDE/Histogram) of a variable, optionally grouped."""
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    if value_col not in data.columns:
        return fig
    ax = fig.gca()

    if group_col:
        sns.kdeplot(
            data=data, x=value_col, hue=group_col, fill=True, palette=config.color_palette, ax=ax
        )
    else:
        sns.histplot(data=data, x=value_col, kde=True, color=config.primary_color, ax=ax)

    ax.set_xlabel(value_col, fontsize=config.fontsize_label)
    ax.set_title(f"Distribution: {value_col}", fontsize=config.fontsize_title)
    ax.grid(True, alpha=config.alpha_grid)

    return fig


def plot_pareto_frontier(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    config: PlotConfig | None = None,
) -> go.Figure:
    """Plots a Pareto frontier (tradeoff scatter plot)."""
    if config is None:
        config = PlotConfig()

    return px.scatter(
        data, x=x_col, y=y_col, title=f"Tradeoff: {x_col} vs {y_col}", template="simple_white"
    )


def plot_stacked_bar(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> go.Figure:
    """Plots a stacked horizontal bar chart."""
    _ = (config, kwargs)
    return px.bar(data, orientation="h")


def plot_scenario_comparison(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs: Any,
) -> go.Figure:
    """Plots a simple bar chart for scenario comparison."""
    _ = (config, kwargs)
    return px.bar(data)


def plot_cdf(
    data: pd.Series | pd.DataFrame,
    value_col: str | None = None,
    title: str = "Cumulative Distribution Function",
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Cumulative Distribution Function (CDF)."""
    if config is None:
        config = PlotConfig()

    if isinstance(data, pd.DataFrame):
        if value_col is None:
            message = "value_col must be provided for DataFrame input"
            raise ValueError(message)
        s = data[value_col].dropna().sort_values().reset_index(drop=True)
    else:
        s = data.dropna().sort_values().reset_index(drop=True)

    y = (s.index + 1) / len(s)

    fig, ax = plt.subplots(figsize=config.default_figsize)
    ax.plot(s, y, color=config.primary_color, linewidth=config.linewidth)

    ax.set_title(title, fontsize=config.fontsize_title)
    ax.set_xlabel(value_col or "Value", fontsize=config.fontsize_label)
    ax.set_ylabel("CDF", fontsize=config.fontsize_label)
    ax.grid(True, alpha=config.alpha_grid)

    return fig


def plot_pareto(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str | None = None,
    config: PlotConfig | None = None,
) -> Figure:
    """Plots a Pareto frontier (tradeoff scatter plot)."""
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    ax.scatter(data[x_col], data[y_col], color=config.primary_color, alpha=0.7)

    if label_col:
        for _, row in data.iterrows():
            ax.annotate(str(row[label_col]), (row[x_col], row[y_col]), fontsize=8, alpha=0.8)

    ax.set_xlabel(x_col, fontsize=config.fontsize_label)
    ax.set_ylabel(y_col, fontsize=config.fontsize_label)
    ax.set_title(f"Tradeoff: {x_col} vs {y_col}", fontsize=config.fontsize_title)
    ax.grid(True, alpha=config.alpha_grid)

    return fig


def plot_comparison_bar(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    ylabel: str,
    *styles: PlotConfig | None,
    **kwargs: Any,
) -> Figure:
    """Plots a simple bar chart for scenario comparison."""
    if len(styles) > 1 or (styles and "config" in kwargs):
        message = "Supply one plot configuration"
        raise TypeError(message)
    config = styles[0] if styles else kwargs.pop("config", None)
    if config is None:
        config = PlotConfig()

    fig, ax = plt.subplots(figsize=config.default_figsize)
    sns.barplot(
        data=data,
        x=x_col,
        y=y_col,
        ax=ax,
        palette=config.color_palette,
        hue=x_col,
        legend=False,
        **kwargs,
    )

    ax.set_title(title, fontsize=config.fontsize_title)
    ax.set_ylabel(ylabel, fontsize=config.fontsize_label)
    ax.set_xlabel(x_col.replace("_", " ").title(), fontsize=config.fontsize_label)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig
