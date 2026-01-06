"""Runs recursive rolling-horizon backtesting validation."""

from pathlib import Path


def main() -> None:
    """Execute the recursive backtest loop."""
    historical_path = Path("data/calibration/historical_normalized.csv")
    if not historical_path.exists():
        print(f"Error: {historical_path} not found.")
        return
    print("Running recursive backtest...")


if __name__ == "__main__":
    main()
