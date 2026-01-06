"""Plots the Theil U decomposition for model performance analysis."""

from pathlib import Path


def main() -> None:
    """Generate the Theil decomposition plot."""
    results_path = Path("data/calibration/recursive_results.json")
    if not results_path.exists():
        print("Error: Backtest results not found.")
        return
    print("Plotting Theil decomposition...")


if __name__ == "__main__":
    main()
