"""Extensive form game construction and rendering using PyGambit."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

try:
    import pygambit as gambit
except ImportError:
    gambit = None

try:
    import graphviz
except ImportError:
    graphviz = None


def _require_pygambit() -> None:
    if gambit is None:
        raise ImportError("pygambit is required for game tree visualization.")


def _require_graphviz() -> None:
    if graphviz is None:
        raise ImportError("graphviz is required for game tree rendering.")


def create_extensive_game_from_matrix(
    u_row: Any,
    u_col: Any,
    row_player_label: str = "Commonwealth",
    col_player_label: str = "State",
    row_action_labels: Sequence[str] | None = None,
    col_action_labels: Sequence[str] | None = None,
    title: str = "Extensive Form Game",
) -> Any:
    """Constructs a 2-player extensive form game from payoff matrices.

    Sequence: Player 1 moves, then Player 2 moves (perfect information).
    """
    _require_pygambit()

    import numpy as np

    u_row = np.array(u_row)
    u_col = np.array(u_col)

    n_row_actions, n_col_actions = u_row.shape

    if row_action_labels is None:
        row_action_labels = [f"R{i + 1}" for i in range(n_row_actions)]
    if col_action_labels is None:
        col_action_labels = [f"C{j + 1}" for j in range(n_col_actions)]

    g = gambit.Game.new_tree(title=title)

    # Add players
    p1 = g.add_player(row_player_label)
    p2 = g.add_player(col_player_label)

    # Root node (P1 move)
    g.append_move(g.root, p1, list(row_action_labels))

    # For each branch of P1, add P2's moves
    for i in range(n_row_actions):
        p1_node = g.root.children[i]
        g.append_move(p1_node, p2, list(col_action_labels))

        # Set Outcomes/Payoffs for leaves of this node
        for j in range(n_col_actions):
            leaf = p1_node.children[j]
            payoffs = [float(u_row[i, j]), float(u_col[i, j])]
            outcome = g.add_outcome(payoffs)
            g.set_outcome(leaf, outcome)

    return g


def render_tree_static(game: Any, output_path: Path | str) -> None:
    """Renders the game tree to an SVG/PNG using Graphviz.

    Traverses the PyGambit tree and builds a Graphviz Digraph.
    """
    _require_graphviz()

    dot = graphviz.Digraph(comment=game.title)
    dot.attr(rankdir="LR")
    dot.attr(ranksep="1.5")
    dot.attr(nodesep="1.0")

    dot.attr(
        "node",
        fontname="Helvetica",
        fontsize="10",
        shape="circle",
        style="filled",
        fillcolor="white",
    )
    dot.attr("edge", fontname="Helvetica", fontsize="10")

    # Traverse BFS
    queue = [game.root]
    node_ids = {game.root: "n0"}
    counter = 1

    while queue:
        node = queue.pop(0)
        nid = node_ids[node]

        if node.is_terminal:
            if node.outcome:
                payoffs = [float(node.outcome[p]) for p in game.players]
                label = f"{payoffs[0]:.2f}\n{payoffs[1]:.2f}"
            else:
                label = "0.00\n0.00"
            dot.node(
                nid,
                label=label,
                shape="box",
                style="filled,rounded",
                fillcolor="#f8f9fa",
                fontsize="9",
            )
        else:
            player_name = node.player.label
            p_idx = node.player.number
            fcolor = "#008080" if p_idx == 0 else "#6c757d"
            dot.node(
                nid,
                label="",
                xlabel=player_name,
                width="0.15",
                height="0.15",
                fixedsize="true",
                fillcolor=fcolor,
            )

            for child in node.children:
                cid = f"n{counter}"
                counter += 1
                node_ids[child] = cid
                queue.append(child)

                edge_label = child.prior_action.label if child.prior_action else ""
                dot.edge(nid, cid, label=f" {edge_label} ")

    # Output
    out_base = Path(output_path)
    if out_base.suffix:
        out_base = out_base.with_suffix("")

    out_base.parent.mkdir(parents=True, exist_ok=True)

    # SVG
    dot.format = "svg"
    dot.render(outfile=out_base.with_suffix(".svg"), cleanup=True)

    # PNG
    dot.format = "png"
    dot.render(outfile=out_base.with_suffix(".png"), cleanup=True)


def export_gte_html(game: Any, output_path: Path | str) -> None:
    """Exports the game in .efg format for use in Game Theory Explorer."""
