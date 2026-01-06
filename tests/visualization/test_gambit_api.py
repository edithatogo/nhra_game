import pygambit as gambit


def test_api():
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

    # Set payoffs
    for node in g.nodes:
        if node.is_leaf:
            node.payoffs[p1] = 1.0
            node.payoffs[p2] = 2.0

    print("Game structure built.")


if __name__ == "__main__":
    test_api()
