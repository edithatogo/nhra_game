"""Test script to verify Game Tree rendering."""

from pathlib import Path

import numpy as np

from nhra_gt.visualization.game_trees import create_extensive_game_from_matrix, render_tree_static


def test_render():
    u_row = np.array([[10, 0], [0, 5]])
    u_col = np.array([[10, 0], [0, 5]])

    print("Creating Game...")
    g = create_extensive_game_from_matrix(
        u_row,
        u_col,
        row_action_labels=["Cooperate", "Defect"],
        col_action_labels=["Cooperate", "Defect"],
        title="Prisoners Dilemma Test",
    )

    out_path = Path("test_tree_render")
    print(f"Rendering to {out_path}...")
    render_tree_static(g, out_path)

    if Path("test_tree_render.svg").exists():
        print("SUCCESS: SVG generated.")
    else:
        print("FAILURE: SVG not found.")


if __name__ == "__main__":
    test_render()
