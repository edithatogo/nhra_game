"""Tests for Gambit API."""

import pygambit as gambit

_LEAF_COUNT = 4


def test_api():
    """Check API."""
    g = gambit.Game.new_tree(title="Test")
    p1 = g.add_player("P1")
    p2 = g.add_player("P2")

    # Root node is terminal. Add move for P1.
    print("Testing g.append_move(g.root, p1, ['A1', 'A2'])...")
    g.append_move(g.root, p1, ["A1", "A2"])

    # Now g.root has children.
    print(f"Number of children: {len(g.root.children)}")

    # For each child, add move for P2.
    print("Testing g.append_move(list(g.root.children), p2, ['B1', 'B2'])...")
    g.append_move(list(g.root.children), p2, ["B1", "B2"])

    row_payoff, column_payoff = 1, 2
    outcome = g.add_outcome("Terminal", [row_payoff, column_payoff])
    terminal_nodes = [node for node in g.nodes if node.is_terminal]
    assert len(terminal_nodes) == _LEAF_COUNT
    for node in terminal_nodes:
        g.set_outcome(node, outcome)
        assert node.outcome[p1] == row_payoff
        assert node.outcome[p2] == column_payoff

    print("Game structure built.")


if __name__ == "__main__":
    test_api()
