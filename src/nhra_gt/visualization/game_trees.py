"""Extensive form game construction and rendering using PyGambit."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np

try:
    from pygambit.gambit import Game
except ImportError:
    Game = None

try:
    import graphviz
except ImportError:
    graphviz = None


class _GameTreeLabels(NamedTuple):
    """Labels for players, actions and the game."""

    row_player_label: str = "Commonwealth"
    col_player_label: str = "State"
    row_action_labels: Sequence[str] | None = None
    col_action_labels: Sequence[str] | None = None
    title: str = "Extensive Form Game"


def create_extensive_game_from_matrix(
    u_row: Any, u_col: Any, *options: Any, **named_options: Any
) -> Any:
    """Constructs a 2-player extensive form game from payoff matrices.

    Sequence: Player 1 moves, then Player 2 moves (perfect information).
    """
    row_player_label, col_player_label, row_action_labels, col_action_labels, title = (
        _GameTreeLabels(*options, **named_options)
    )
    if Game is None:
        message = "pygambit is required for game tree visualization."
        raise ImportError(message)

    u_row = np.array(u_row)
    u_col = np.array(u_col)

    n_row_actions, n_col_actions = u_row.shape

    if row_action_labels is None:
        row_action_labels = [f"R{i + 1}" for i in range(n_row_actions)]
    if col_action_labels is None:
        col_action_labels = [f"C{j + 1}" for j in range(n_col_actions)]

    g = Game.new_tree(title=title)

    # Add players
    p1 = g.add_player(row_player_label)
    p2 = g.add_player(col_player_label)

    # Root node (P1 move)
    g.append_move(g.root, p1, list(row_action_labels))

    # For each branch of P1, add P2's moves
    for i, p1_node in enumerate(g.root.children):
        g.append_move(p1_node, p2, list(col_action_labels))

        # Set Outcomes/Payoffs for leaves of this node
        for j, leaf in enumerate(p1_node.children):
            payoffs = [float(u_row[i, j]), float(u_col[i, j])]
            outcome = g.add_outcome(
                label=f"{row_action_labels[i]} / {col_action_labels[j]}", payoffs=payoffs
            )
            g.set_outcome(leaf, outcome)

    return g


def game_tree_graph(game: Any) -> Any:
    """Build a Graphviz graph from the PyGambit tree without writing files."""
    if graphviz is None:
        message = "graphviz is required for game tree rendering."
        raise ImportError(message)

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

    return dot


def render_tree_static(game: Any, output_path: Path | str) -> None:
    """Render the game tree to SVG and PNG using Graphviz."""
    dot = game_tree_graph(game)
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
