from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
import plotly.graph_objects as go

from .legacy_engine import GAME_NODES


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

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line={"width": 2}, hoverinfo="none", mode="lines")

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
        marker={"size": sizes, "line": {"width": 2}},
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="NHRA strategic interaction network (games as nodes)",
        showlegend=False,
        hovermode="closest",
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
    )
    outpath_html.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(outpath_html), include_plotlyjs="cdn")
    return G, outpath_html
