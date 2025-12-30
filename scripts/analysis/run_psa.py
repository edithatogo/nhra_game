from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

# Add src
sys.path.append("src")

from nhra_gt.engine import Params, run_hybrid, summarise_outcome
from nhra_gt.sensitivity import run_psa

# Define PSA Parameters
PSA_PARAMS = [
    "cost_shifting_intensity",
    "discharge_delay_base",
    "fragmentation_index",
    "political_salience",
]
PSA_YEARS = list(range(2025, 2031))


def model_wrapper(param_values: np.ndarray) -> float:
    """Wrapper for PSA execution."""
    p_dict = dict(zip(PSA_PARAMS, param_values, strict=False))
    p = replace(Params(), **p_dict)
    # Use fewer MC runs for speed in PSA loop (we rely on many parameter samples)
    traj, _ = run_hybrid(PSA_YEARS, p, seed=None, n_mc=20)
    return float(summarise_outcome(traj)["pressure_2030"])


def main():
    print("Starting Probabilistic Sensitivity Analysis (PSA)...")

    # Define Distributions
    dists = {
        "cost_shifting_intensity": lambda n: np.random.uniform(0.05, 0.80, n),
        "discharge_delay_base": lambda n: np.clip(np.random.normal(1.0, 0.15, n), 0.5, 2.0),
        "fragmentation_index": lambda n: np.clip(np.random.normal(1.0, 0.12, n), 0.6, 1.5),
        "political_salience": lambda n: np.random.uniform(0.1, 0.5, n),
    }

    # Run PSA
    df = run_psa(dists, model_wrapper, n_samples=500, n_procs=4)

    # Save Results
    out_dir = Path("data/gsa")
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "psa_results.csv", index=False)
    print(f"PSA results saved to {out_dir / 'psa_results.csv'}")

    # Plotting
    from nhra_gt.visualization.base import PlotConfig, save_figure
    from nhra_gt.visualization.distributional import plot_distributions

    config = PlotConfig()
    fig = plot_distributions(df, "outcome", config=config)

    # Custom additions to the plot (mean and CI)
    ax = fig.gca()
    mean_val = df["outcome"].mean()
    ax.axvline(x=mean_val, color="r", linestyle="--", label=f"Mean: {mean_val:.2f}")

    # Calculate 95% CI
    ci_lower = np.percentile(df["outcome"], 2.5)
    ci_upper = np.percentile(df["outcome"], 97.5)
    ax.axvline(x=ci_lower, color="k", linestyle=":", label="95% CI")
    ax.axvline(x=ci_upper, color="k", linestyle=":")

    ax.legend()
    plot_path = out_dir / "psa_distribution.png"
    save_figure(fig, plot_path, config)
    print(f"Plot saved to {plot_path}")

    # Summary stats
    print("\nSummary Statistics:")
    print(df["outcome"].describe())
    print(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")


if __name__ == "__main__":
    main()
