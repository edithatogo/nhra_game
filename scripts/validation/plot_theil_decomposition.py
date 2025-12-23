from __future__ import annotations

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from nhra_game_theory.domain.validation import calculate_theil_decomposition

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
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(kind="barh", stacked=True, ax=ax, color=["#008080", "#20B2AA", "#afeeee"])
    
    ax.set_title("Theil Inequality Decomposition (Error Source)")
    ax.set_xlabel("Proportion")
    ax.set_xlim(0, 1)
    
    # Save
    out_dir = Path("outputs/validation")
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_path = out_dir / "theil_decomposition.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"Saved Theil decomposition plot to {plot_path}")

if __name__ == "__main__":
    main()
