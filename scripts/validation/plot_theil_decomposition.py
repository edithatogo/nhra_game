from __future__ import annotations

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from nhra_gt.domain.validation import calculate_theil_decomposition

def main():
    results_path = Path("data/calibration_v21/recursive_results.json")
    if not results_path.exists():
        print("Error: Backtest results not found.")
        return

    with open(results_path) as f:
        results = json.load(f)

    metrics = ["within4", "occupancy"]
    data = []

    for m in metrics:
        actuals = np.array([r["actual"][m] for r in results])
        preds = np.array([r["predicted"][m] for r in results])
        
        decomp = calculate_theil_decomposition(actuals, preds)
        data.append({
            "Metric": m,
            "Bias (UM)": decomp["um"],
            "Variance (US)": decomp["us"],
            "Covariance (UC)": decomp["uc"]
        })

    df = pd.DataFrame(data).set_index("Metric")
    
    # Plot
    from nhra_gt.visualization.distributional import plot_stacked_bar
    from nhra_gt.visualization.base import save_figure, PlotConfig

    config = PlotConfig()
    fig = plot_stacked_bar(df, "Theil Inequality Decomposition (Error Source)", "Proportion", config=config)
    
    # Save
    out_dir = Path("outputs/validation")
    plot_path = out_dir / "theil_decomposition.png"
    save_figure(fig, plot_path, config)
    print(f"Saved Theil decomposition plot to {plot_path}")

if __name__ == "__main__":
    main()
