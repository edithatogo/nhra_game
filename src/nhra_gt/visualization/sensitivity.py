from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .config import PlotConfig


def plot_sobol_indices(
    si: dict[str, Any],
    config: PlotConfig | None = None,
    total_order: bool = True,
) -> Figure:
    """
    Generates Sobol sensitivity bar chart (S1 or ST).

    Args:
        si: Dictionary containing 'names', 'S1', 'ST', 'S1_conf', 'ST_conf'.
        config: PlotConfig for styling.
        total_order: If True, plots ST (Total-order), else S1 (First-order).

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

    color = "salmon" if total_order else "lightgreen"
    ax.barh(df.index, df["index"], xerr=df["conf"], color=color, capsize=5)

    label = "Total-order (ST)" if total_order else "First-order (S1)"
    ax.set_xlabel(f"{label} sensitivity index", fontsize=config.fontsize_label)
    ax.set_title(f"Sobol Analysis: {label}", fontsize=config.fontsize_title)
    ax.grid(axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    return fig


def plot_sobol_heatmap(
    si: dict[str, Any],
    config: PlotConfig | None = None,
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

    return fig


def plot_morris_tornado(
    data: pd.DataFrame,
    config: PlotConfig | None = None,
) -> Figure:
    """Generates a Morris Tornado plot (mu_star ranking)."""
    if config is None:
        config = PlotConfig()

    df = data.sort_values("mu_star", ascending=True)

    fig = plt.figure(figsize=config.default_figsize)
    ax = fig.gca()

    ax.barh(df.index, df["mu_star"], xerr=df["mu_star_conf"], color="skyblue", capsize=5)
    ax.set_xlabel("mu_star (Absolute mean elementary effect)", fontsize=config.fontsize_label)
    ax.set_title("Morris Screening: Parameter Influence", fontsize=config.fontsize_title)
    ax.grid(axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    return fig


def plot_rank_tornado(
    data: pd.DataFrame,
    outcome_col: str,
    params: list[str],
    config: PlotConfig | None = None,
    topk: int = 10,
) -> Figure:
    """Rank-correlation tornado using Spearman rho."""
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

    ax.barh(labels, vals, color=config.primary_color)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Spearman rank correlation", fontsize=config.fontsize_label)
    ax.set_title(f"Sensitivity (tornado): {outcome_col}", fontsize=config.fontsize_title)
    ax.grid(True, axis="x", alpha=config.alpha_grid)
    ax.tick_params(axis="both", labelsize=config.fontsize_tick)

    return fig
