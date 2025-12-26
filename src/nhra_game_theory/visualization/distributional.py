from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .config import PlotConfig


def plot_strategy_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs,
) -> Figure:
    """
    Shows strategy shares over time for each game (one panel per game).
    """
    if config is None:
        config = PlotConfig()

    games = sorted(data["game"].unique())
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
            ax.plot(pivot.index, pivot[col], label=f"{col}", linewidth=config.linewidth, color=color)
            
        ax.set_ylim(0, 1)
        ax.set_ylabel(g, fontsize=config.fontsize_label)
        ax.grid(True, alpha=config.alpha_grid)
        ax.tick_params(axis="both", labelsize=config.fontsize_tick)
        
        if i == 1:
            ax.legend(ncol=4, fontsize=config.fontsize_legend, loc="upper right", frameon=False)
            
    ax.set_xlabel("Year", fontsize=config.fontsize_label)
    return fig


def plot_distributions(
    data: pd.DataFrame,
    value_col: str,
    group_col: str | None = None,
    config: PlotConfig | None = None,
) -> Figure:
    """
    Plots distributions (KDE/Histogram) of a variable, optionally grouped.
    """
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    if group_col:
        sns.kdeplot(data=data, x=value_col, hue=group_col, fill=True, palette=config.color_palette, ax=ax)
    else:
        sns.histplot(data=data, x=value_col, kde=True, color=config.primary_color, ax=ax)

    ax.set_xlabel(value_col, fontsize=config.fontsize_label)
    ax.set_title(f"Distribution: {value_col}", fontsize=config.fontsize_title)
    ax.grid(True, alpha=config.alpha_grid)
    
    return fig


def plot_pareto(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str | None = None,
    config: PlotConfig | None = None,
) -> Figure:
    """
    Plots a Pareto frontier (tradeoff scatter plot).
    """
    if config is None:
        config = PlotConfig()

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    ax.scatter(data[x_col], data[y_col], color=config.primary_color, alpha=0.7)

    if label_col:
        for _, row in data.iterrows():
            ax.annotate(row[label_col], (row[x_col], row[y_col]), fontsize=8, alpha=0.8)

    ax.set_xlabel(x_col, fontsize=config.fontsize_label)
    ax.set_ylabel(y_col, fontsize=config.fontsize_label)
    ax.set_title(f"Tradeoff: {x_col} vs {y_col}", fontsize=config.fontsize_title)
    ax.grid(True, alpha=config.alpha_grid)
    
    return fig