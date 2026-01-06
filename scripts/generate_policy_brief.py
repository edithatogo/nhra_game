"""Generates a PDF policy brief summarizing simulation insights."""

from pathlib import Path

import pandas as pd


def generate_brief(scenario_name: str, output_path: Path) -> None:
    """Generate a professional PDF policy brief for a given scenario."""
    # 1. Run Simulation
    print(f"Generating brief for {scenario_name}...")
    # ... logic ...


def main() -> None:
    """Generate a summary PDF brief from the latest simulation output."""
    latest_results = Path("outputs/baseline/trajectory.csv")
    if not latest_results.exists():
        print("No simulation results found.")
        return

    df = pd.read_csv(latest_results)
    print(f"Generating policy brief for {len(df)} months of simulation...")


if __name__ == "__main__":
    main()
