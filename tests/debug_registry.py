import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

from nhra_gt.game_theory.content import get_populated_registry


def check_registry():
    registry = get_populated_registry()
    games = registry.list_all()

    print(f"Found {len(games)} games.")

    for game in games:
        print(f"Checking {game.id}...")
        if "matrix" in game.payoffs:
            print("  [OK] 'matrix' key found.")
            # Print first row to verify content
            print(f"  Matrix sample: {game.payoffs['matrix'][0]}")
        else:
            print("  [FAIL] 'matrix' key MISSING in payoffs!")
            print(f"  Keys found: {list(game.payoffs.keys())}")


if __name__ == "__main__":
    check_registry()
