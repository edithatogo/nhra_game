from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pygambit as gambit
from beartype import beartype

try:
    from jaxtyping import Array, Float
except ImportError:
    # Fallback for environments without JAX/jaxtyping (e.g. Streamlit Cloud)
    class _DummySubscriptable:
        def __class_getitem__(cls, item):
            return Any

    Array = _DummySubscriptable
    Float = _DummySubscriptable


@beartype
def create_extensive_game_from_matrix(
    u_row: Float[Array, "m n"],
    u_col: Float[Array, "m n"],
    title: str = "NHRA Subgame",
    row_player_label: str = "Commonwealth",
    col_player_label: str = "State",
    row_action_labels: Sequence[str] | None = None,
    col_action_labels: Sequence[str] | None = None,
) -> gambit.Game:
    """
    Constructs a 2-player extensive form game from payoff matrices.
    Sequence: Player 1 moves, then Player 2 moves (perfect information).
    """
    m, n = u_row.shape
    g = gambit.Game.new_tree(title=title)

    p1 = g.add_player(row_player_label)
    p2 = g.add_player(col_player_label)

    # 1. Add P1 move at root
    row_actions = list(row_action_labels) if row_action_labels else [f"R{i}" for i in range(m)]
    g.append_move(g.root, p1, row_actions)

    # 2. Add P2 moves at each of P1's children
    col_actions = list(col_action_labels) if col_action_labels else [f"C{j}" for j in range(n)]
    for i, child in enumerate(g.root.children):
        g.append_move(child, p2, col_actions)

        # 3. Create outcomes and set payoffs at the new leaves
        for j, leaf in enumerate(child.children):
            outcome = g.add_outcome([float(u_row[i, j]), float(u_col[i, j])])
            g.set_outcome(leaf, outcome)

    return g


@beartype
def create_hybrid_game_tree(
    u_cth: Float[Array, "m n"],
    u_state_macro: Float[Array, "m n"],
    micro_matrices: Sequence[tuple[Array, Array]],
    title: str = "Hybrid NHRA Game",
) -> gambit.Game:
    """
    Constructs a 3-player hierarchical/hybrid game tree.
    Sequence: Cth -> State -> LHN.
    """
    m, n = u_cth.shape
    g = gambit.Game.new_tree(title=title)

    p_cth = g.add_player("Commonwealth")
    p_state = g.add_player("State")
    p_lhn = g.add_player("LHN")

    # Cth moves
    g.append_move(g.root, p_cth, [f"Cth{i}" for i in range(m)])

    for i, node_i in enumerate(g.root.children):
        # State moves
        g.append_move(node_i, p_state, [f"State{j}" for j in range(n)])

        for j, node_j in enumerate(node_i.children):
            # LHN moves
            u_sm, u_l = micro_matrices[i * n + j]
            mi, _ = u_sm.shape
            g.append_move(node_j, p_lhn, [f"LHN{k}" for k in range(mi)])

            for k, leaf in enumerate(node_j.children):
                payoffs = [
                    float(u_cth[i, j]),
                    float(u_state_macro[i, j] + u_sm[k, 0]),
                    float(u_l[k, 0]),
                ]
                outcome = g.add_outcome(payoffs)
                g.set_outcome(leaf, outcome)

    return g


def render_tree_static(game: gambit.Game, output_path: Path | str) -> None:
    """Renders the game tree to an SVG/PNG using Graphviz."""
    import graphviz

    dot = graphviz.Digraph(comment=game.title)
    dot.attr(rankdir="LR")  # Left to right for trees

    def walk(node, parent_id=None, edge_label=""):
        node_id = str(id(node))

        if node.is_terminal:
            # terminal nodes have outcomes
            if node.outcome:
                payoffs = ", ".join([f"{p.label}:{node.outcome[p]:.2f}" for p in game.players])
                dot.node(node_id, payoffs, shape="box")
            else:
                dot.node(node_id, "Leaf", shape="box")
        else:
            label = f"{node.player.label}"
            dot.node(node_id, label, shape="circle")

        if parent_id:
            dot.edge(parent_id, node_id, label=edge_label)

        for branch in node.children:
            walk(branch, node_id, edge_label=branch.label)

    walk(game.root)
    dot.render(output_path, format="svg", cleanup=True)


def export_gte_html(game: gambit.Game, output_path: Path | str) -> None:
    """Exports the game in .efg format."""
    path = Path(output_path).with_suffix(".efg")
    path.write_text(game.serialize(), encoding="utf-8")


def get_game_evidence(game_name: str) -> dict[str, str]:
    """Returns bibliographic mapping for subgame nodes."""
    mappings = {
        "Definition": {
            "source": "NHRA Section 127",
            "context": "Defines 'efficient' price and scope of services.",
        },
        "Bargaining": {
            "source": "Federal Financial Relations Agreement",
            "context": "Rules for CAP convergence and funding share negotiations.",
        },
        "Cost Shifting": {
            "source": "Productivity Commission (2023)",
            "context": "Evidence of incentive misalignment between levels of government.",
        },
        "Discharge": {
            "source": "Medicare UCC Evaluation (2024)",
            "context": "Strategic interface between acute and primary care.",
        },
        "Governance": {
            "source": "Performance and Accountability Framework",
            "context": "Governance structures for integrated care pilots.",
        },
        "Compliance": {
            "source": "Independent Hospital Pricing Authority Audit Suite",
            "context": "Rules for activity coding and financial reconciliation.",
        },
    }
    return mappings.get(
        game_name, {"source": "Internal Logic", "context": "Derived from mechanism dynamics."}
    )
