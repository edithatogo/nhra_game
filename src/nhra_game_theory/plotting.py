from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from matplotlib.figure import Figure

from .legacy_engine import GAME_NODES


def savefig(fig: Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_trajectory(
    agg: pd.DataFrame,
    y: str,
    ylab: str,
    outpath: Path,
    qlo: str | None = None,
    qhi: str | None = None,
) -> None:
    fig = plt.figure()
    ax = fig.gca()
    x = agg["year"].to_numpy(dtype=float)
    yv = pd.to_numeric(agg[y], errors="coerce").to_numpy(dtype=float)
    ax.plot(x, yv, linewidth=2)
    if qlo and qhi and qlo in agg.columns and qhi in agg.columns:
        qlo_v = pd.to_numeric(agg[qlo], errors="coerce").to_numpy(dtype=float)
        qhi_v = pd.to_numeric(agg[qhi], errors="coerce").to_numpy(dtype=float)
        ax.fill_between(x, qlo_v, qhi_v, alpha=0.25)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylab)
    ax.grid(True, alpha=0.25)
    savefig(fig, outpath)


def plot_strategy_heatmap(freq: pd.DataFrame, outpath: Path) -> None:
    """
    Shows strategy shares over time for each game (one panel per game, minimal styling).
    """
    games = sorted(freq["game"].unique())
    fig = plt.figure(figsize=(12, 2.1 * len(games)))
    for i, g in enumerate(games, start=1):
        ax = fig.add_subplot(len(games), 1, i)
        sub = freq[freq["game"] == g].copy()
        pivot = sub.pivot_table(
            index="year", columns="strategy", values="share", aggfunc="mean"
        ).fillna(0)
        for col in pivot.columns:
            ax.plot(pivot.index, pivot[col], label=f"{g}:{col}", linewidth=2)
        ax.set_ylim(0, 1)
        ax.set_ylabel(g)
        ax.grid(True, alpha=0.25)
        if i == 1:
            ax.legend(ncol=4, fontsize=9, loc="upper right", frameon=False)
    ax.set_xlabel("Year")
    savefig(fig, outpath)


def tornado_from_rankcorr(
    df: pd.DataFrame, outcome_col: str, params: list[str], outpath: Path, topk: int = 10
) -> None:
    """
    Rank-correlation tornado using Spearman rho.
    """
    # scipy not required; use pandas spearman correlation
    rows = []
    for p in params:
        # Cast to float explicitly to avoid mypy generic union confusion
        val = df[[p, outcome_col]].corr(method="spearman").iloc[0, 1]
        rho = float(val)  # type: ignore
        rows.append((p, rho))
    rows.sort(key=lambda x: abs(x[1]), reverse=True)
    rows = rows[:topk]
    labels = [r[0] for r in rows][::-1]
    vals = [r[1] for r in rows][::-1]

    fig = plt.figure(figsize=(8, 0.45 * len(labels) + 1.6))
    ax = fig.gca()
    ax.barh(labels, vals)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("Spearman rank correlation")
    ax.set_title(f"Sensitivity (tornado): {outcome_col}")
    ax.grid(True, axis="x", alpha=0.25)
    savefig(fig, outpath)


def build_games_graph() -> nx.DiGraph[Any]:
    """
    Network used for the interactive visual. Edges reflect influence pathways (conceptual).
    """
    G: nx.DiGraph[Any] = nx.DiGraph()
    for k, v in GAME_NODES.items():
        G.add_node(k, label=v)

    edges = [
        ("SHIFT", "DISC"),
        ("SHIFT", "BARG"),
        ("DEF", "BARG"),
        ("BARG", "COMP"),
        ("BARG", "GOV"),
        ("DISC", "SIGNAL"),
        ("SHIFT", "SIGNAL"),
        ("SIGNAL", "BARG"),
        ("COMP", "SIGNAL"),
        ("GOV", "SHIFT"),
        ("GOV", "SIGNAL"),
    ]
    for u, v in edges:
        G.add_edge(u, v)
    return G


def render_games_graph_interactive(outpath_html: Path) -> tuple[nx.DiGraph[Any], Path]:
    G = build_games_graph()
    pos = nx.spring_layout(G, seed=7, k=1.1)

    # Edge traces
    edge_x = []
    edge_y = []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=2), hoverinfo="none", mode="lines")

    # Node traces
    node_x = []
    node_y = []
    node_text = []
    node_label = []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        node_text.append(n)
        node_label.append(G.nodes[n]["label"])

    # centrality for size
    cent = nx.betweenness_centrality(G)
    sizes = [18 + 40 * cent[n] for n in G.nodes()]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_label,
        hoverinfo="text",
        marker=dict(size=sizes, line=dict(width=2)),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="NHRA strategic interaction network (games as nodes)",
        showlegend=False,
        hovermode="closest",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    outpath_html.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(outpath_html), include_plotlyjs="cdn")
    return G, outpath_html
