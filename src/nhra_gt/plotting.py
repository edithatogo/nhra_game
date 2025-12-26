from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from .visualization.base import PlotConfig, save_figure
from .visualization.distributional import plot_strategy_heatmap as new_plot_strategy_heatmap
from .visualization.sensitivity import plot_rank_tornado as new_plot_rank_tornado
from .visualization.trajectories import plot_trajectory as new_plot_trajectory


def plot_trajectory(
    agg: pd.DataFrame,
    y: str,
    ylab: str,
    outpath: Path,
    qlo: str | None = None,
    qhi: str | None = None,
) -> None:
    warnings.warn(
        "plot_trajectory is deprecated, use nhra_game_theory.visualization.trajectories instead",
        DeprecationWarning,
        stacklevel=2,
    )
    config = PlotConfig()
    fig = new_plot_trajectory(agg, y, ylab, config=config, q_low_col=qlo, q_high_col=qhi)
    save_figure(fig, outpath, config)


def plot_strategy_heatmap(freq: pd.DataFrame, outpath: Path) -> None:
    warnings.warn(
        "plot_strategy_heatmap is deprecated, use nhra_game_theory.visualization.distributional instead",
        DeprecationWarning,
        stacklevel=2,
    )
    config = PlotConfig()
    fig = new_plot_strategy_heatmap(freq, config=config)
    save_figure(fig, outpath, config)


def tornado_from_rankcorr(
    df: pd.DataFrame, outcome_col: str, params: list[str], outpath: Path, topk: int = 10
) -> None:
    warnings.warn(
        "tornado_from_rankcorr is deprecated, use nhra_game_theory.visualization.sensitivity instead",
        DeprecationWarning,
        stacklevel=2,
    )
    config = PlotConfig()
    fig = new_plot_rank_tornado(df, outcome_col, params, config=config, topk=topk)
    save_figure(fig, outpath, config)


# Keep build_games_graph and render_games_graph_interactive for now as they are specialized
# and not fully migrated to the new generic API yet (Plotly network graphs)
from .plotting_legacy import build_games_graph, render_games_graph_interactive  # noqa
