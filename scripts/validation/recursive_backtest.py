"""Run the rolling-horizon backtest against observed historical data."""

import sys
from pathlib import Path

import pandas as pd

from nhra_gt.domain.validation import RecursiveBacktest, aggregate_metrics


def main() -> int:
    """Run the backtest and retain its results for the validation report."""
    historical_path = Path("data/calibration/historical_normalized.csv")
    if not historical_path.is_file():
        print(f"Run historical preprocessing to produce {historical_path}.", file=sys.stderr)
        return 2

    historical = pd.read_csv(historical_path)
    missing = {"year", "within4", "occupancy"} - set(historical.columns)
    if missing:
        print(f"Historical observations require {', '.join(sorted(missing))}.", file=sys.stderr)
        return 2

    engine = RecursiveBacktest(historical_data=historical)
    results = engine.run_all()
    if not results:
        print("The historical series has no complete training and holdout window.", file=sys.stderr)
        return 2

    destination = Path("data/calibration/recursive_results.json")
    engine.save_results(results, destination)
    print(f"Saved {len(results)} holdout results to {destination}")
    for metric, scores in aggregate_metrics(results).items():
        print(f"{metric} mean error metrics {scores}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
