from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .config import PlotConfig


def plot_strategy_heatmap(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    **kwargs,
) -> Figure:
    """
    Shows strategy shares over time for each game (one panel per game).

    Args:
        data: DataFrame containing 'year', 'game', 'strategy', and 'share'.
        config: PlotConfig object for styling.
        **kwargs: Additional parameters.

    Returns:
        A matplotlib Figure object.
    """
    if config is None:
        config = PlotConfig()

    games = sorted(data["game"].unique())
    # Adjust figure size based on number of subplots
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
