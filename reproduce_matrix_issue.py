import os
import sys

# Validating the path setup to import the src module correctly
sys.path.append(os.path.abspath("src"))

from nhra_gt.game_theory.content import get_populated_registry
from nhra_gt.game_theory.visualization import generate_payoff_matrix_figure


def reproduce():
    registry = get_populated_registry()
    game = registry.get("definition_game")  # Test with Definition Game

    print(f"Testing Game: {game.title}")

    try:
        fig = generate_payoff_matrix_figure(game)
        print("Figure generated successfully.")

        # Check trace data
        print(f"Number of traces: {len(fig.data)}")
        if len(fig.data) > 0:
            trace = fig.data[0]
            print(f"Trace type: {trace.type}")
            print(f"Z values: {trace.z}")
            print(f"X values: {trace.x}")
            print(f"Y values: {trace.y}")

        # Check annotations
        print(f"Number of annotations: {len(fig.layout.annotations)}")
        for i, ann in enumerate(fig.layout.annotations):
            print(f"Annotation {i}: x={ann.x}, y={ann.y}, text={ann.text}")

    except Exception as e:
        print(f"Error generating figure: {e}")


if __name__ == "__main__":
    reproduce()
