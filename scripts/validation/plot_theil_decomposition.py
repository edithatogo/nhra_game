"""Create the chart of bias, variance and covariance in holdout errors."""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nhra_gt.domain.validation import calculate_theil_decomposition
from nhra_gt.visualization.base import save_figure


def main() -> int:
    """Plot the Theil proportions from the completed backtest."""
    results_path = Path("data/calibration/recursive_results.json")
    if not results_path.is_file():
        print("Run the recursive backtest before plotting its errors.", file=sys.stderr)
        return 2
    results = json.loads(results_path.read_text(encoding="utf-8"))
    if not results:
        print("The backtest contains no holdout results.", file=sys.stderr)
        return 2

    proportions = {}
    for metric in ("within4", "occupancy"):
        actual = np.array([row["actual"][metric] for row in results])
        predicted = np.array([row["predicted"][metric] for row in results])
        parts = calculate_theil_decomposition(actual, predicted)
        proportions[metric] = {
            "Bias": parts["um"],
            "Variance": parts["us"],
            "Covariance": parts["uc"],
        }

    frame = pd.DataFrame.from_dict(proportions, orient="index")
    figure, axes = plt.subplots()
    frame.plot.barh(stacked=True, ax=axes, title="Theil decomposition of holdout errors")
    axes.set_xlabel("Proportion of squared error")
    destination = Path("outputs/validation/theil_decomposition.png")
    destination.parent.mkdir(parents=True, exist_ok=True)
    save_figure(figure, destination, formats=["png"])
    plt.close(figure)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
