from __future__ import annotations

from pathlib import Path

import jax.numpy as jnp

from nhra_gt.visualization.game_trees import create_extensive_game_from_matrix, render_tree_static


def test_render_static_tree_smoke(tmp_path):
    # Setup simple game
    u_row = jnp.array([[2, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[2, 0], [0, 1]], dtype=float)

    g = create_extensive_game_from_matrix(u_row, u_col, title="Test Game")

    out_path = tmp_path / "test_tree"
    render_tree_static(g, out_path)

    # Check if SVG was created
    assert Path(str(out_path) + ".svg").exists()
