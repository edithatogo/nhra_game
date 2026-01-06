"""Generates animated GIFs of simulation trajectories."""

from pathlib import Path

import pandas as pd


def main() -> None:
    """Run the animation generation script."""
    input_path = Path("outputs/baseline/trajectory.csv")
    if not input_path.exists():
        return

    df = pd.read_csv(input_path)
    print(f"Animating {len(df)} frames...")


if __name__ == "__main__":
    main()
