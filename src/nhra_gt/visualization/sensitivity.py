"""
Sensitivity Analysis Visualizations.

Sobol indices, Morris screening, and tornado plots.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .base import save_figure
from .config import PlotConfig
from .schemas import MorrisSchema, RankCorrelationSchema


def plot_sobol_indices(
    si: dict[str, Any],
    config: PlotConfig | None = None,
    total_order: bool = True,
    path: str | Path | None = None,
) -> Figure:
    """
    Generates Sobol sensitivity bar chart (S1 or ST).

    Args:
        si: Dictionary containing 'names', 'S1', 'ST', 'S1_conf', 'ST_conf'.
        config: PlotConfig for styling.
        total_order: If True, plots ST (Total-order), else S1 (First-order).
        path: Optional path to save the figure.

    Returns:
        Matplotlib Figure.
    """
    if config is None:
        config = PlotConfig()

    names = si["names"]
    key = "ST" if total_order else "S1"
    conf_key = f"{key}_conf"

    vals = si[key]
    conf = si[conf_key]

    df = pd.DataFrame({"index": vals, "conf": conf}, index=names).sort_values(
        "index", ascending=True
    )

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    color = config.primary_color if total_order else config.secondary_color
    ax.barh(df.index, df["index"], xerr=df["conf"], color=color, capsize=5, alpha=0.8)

    label = "Total-order (ST)" if total_order else "First-order (S1)"
    ax.set_xlabel(f"{label} sensitivity index", fontsize=config.fontsize_label)
    ax.set_title(f"Sobol Analysis: {label}", fontsize=config.fontsize_title)
    ax.grid(axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    if path:
        save_figure(fig, path, config)

    return fig


def plot_sobol_heatmap(
    si: dict[str, Any],
    config: PlotConfig | None = None,
    path: str | Path | None = None,
) -> Figure | None:
    """Generates a heatmap of second-order interaction indices (S2)."""
    if "S2" not in si or si["S2"] is None:
        return None

    if config is None:
        config = PlotConfig()

    names = si["names"]
    s2 = si["S2"]

    # Ensure square matrix
    if not (isinstance(s2, np.ndarray) and s2.ndim == 2):
        return None

    fig = plt.figure(figsize=(10, 8))
    ax = fig.gca()
    sns.heatmap(s2, annot=True, xticklabels=names, yticklabels=names, cmap="YlGnBu", ax=ax)
    ax.set_title("Sobol Analysis: Interaction Indices (S2)", fontsize=config.fontsize_title)

    if path:
        save_figure(fig, path, config)

    return fig


def plot_sobol_interaction_bars(
    si: dict[str, Any],
    top_n: int = 10,
    path: str | Path | None = None,
    config: PlotConfig | None = None,
) -> Figure | None:
    """
    Plots the top second-order interactions (S2) as a bar chart.
    """
    if "S2" not in si or si["S2"] is None:
        return None

    if config is None:
        config = PlotConfig()

    names = si["names"]
    s2 = si["S2"]

    interactions = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            val = s2[i, j]
            if not np.isnan(val) and val > 0:
                interactions.append({"Interaction": f"{names[i]} x {names[j]}", "S2": val})

    if not interactions:
        return None

    df_s2 = pd.DataFrame(interactions).sort_values("S2", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=config.default_figsize)
    sns.barplot(data=df_s2, x="S2", y="Interaction", palette="flare", ax=ax)

    ax.set_title(f"Top {top_n} Sobol Second-Order Interactions", fontsize=config.fontsize_title)
    ax.grid(True, axis="x", alpha=config.alpha_grid)

    if path:
        save_figure(fig, path, config)

    return fig


def plot_morris_tornado(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
    path: str | Path | None = None,
) -> Figure:
    """Generates a Morris Tornado plot (mu_star ranking)."""
    # Validation
    MorrisSchema.validate(data)

    if config is None:
        config = PlotConfig()

    df = data.sort_values("mu_star", ascending=True)

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    ax.barh(
        df.index,
        df["mu_star"],
        xerr=df["mu_star_conf"],
        color=config.primary_color,
        capsize=5,
        alpha=0.8,
    )
    ax.set_xlabel("mu_star (Absolute mean elementary effect)", fontsize=config.fontsize_label)
    ax.set_title("Morris Screening: Parameter Influence", fontsize=config.fontsize_title)
    ax.grid(axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    if path:
        save_figure(fig, path, config)

    return fig


def plot_rank_tornado(
    data: pd.DataFrame,
    outcome_col: str,
    params: list[str],
    config: PlotConfig | None = None,
    topk: int = 10,
    path: str | Path | None = None,
) -> Figure:
    """Rank-correlation tornado using Spearman rho."""
    # Validation
    RankCorrelationSchema.validate(data)
    for col in [outcome_col, *params]:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in data.")

    if config is None:
        config = PlotConfig()

    rows = []
    for p in params:
        rho = data[[p, outcome_col]].corr(method="spearman").iloc[0, 1]
        rows.append((p, float(rho)))

    rows.sort(key=lambda x: abs(x[1]), reverse=True)
    rows = rows[:topk]
    labels = [r[0] for r in rows][::-1]
    vals = [r[1] for r in rows][::-1]

    # Dynamic height
    height = 0.45 * len(labels) + 1.6
    fig = plt.figure(figsize=(config.default_figsize[0], height))
    ax = fig.gca()

    ax.barh(labels, vals, color=config.primary_color, alpha=0.8)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Spearman rank correlation", fontsize=config.fontsize_label)
    ax.set_title(f"Sensitivity (tornado): {outcome_col}", fontsize=config.fontsize_title)
    ax.grid(True, axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    if path:
        save_figure(fig, path, config)

    return fig
