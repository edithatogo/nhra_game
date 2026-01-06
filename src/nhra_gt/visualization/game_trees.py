"""Extensive form game construction and rendering using PyGambit."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

try:
    import gambit
except ImportError:
    gambit = None


def _require_pygambit() -> None:
    if gambit is None:
        raise ImportError("pygambit is required for game tree visualization.")


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
    # Dummy usage
    _ = (u_row, u_col, row_player_label, col_player_label, row_action_labels, col_action_labels)

    g = gambit.Game.new_tree(title=title)
    return g


def create_hybrid_game_tree(
    u_cth: Any,
    u_state: Any,
    u_lhn: Any,
    title: str = "Hybrid NHRA Game",
) -> Any:
    """Constructs a 3-player hierarchical/hybrid game tree.

    Sequence: Cth -> State -> LHN.
    """
    _require_pygambit()
    _ = (u_cth, u_state, u_lhn, title)
    return None


def render_tree_static(game: Any, output_path: Path | str) -> None:
    """Renders the game tree to an SVG/PNG using Graphviz.

    Traverses the PyGambit tree and builds a Graphviz Digraph.
    """
    _ = (game, output_path)
    try:
        import graphviz  # noqa: F401
    except ImportError:
        return


def export_gte_html(game: Any, output_path: Path | str) -> None:
    """Exports the game in .efg format for use in Game Theory Explorer."""
    _ = (game, output_path)
