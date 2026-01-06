"""Runs Probabilistic Sensitivity Analysis (PSA) on the NHRA model."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd

from nhra_gt.domain.params import Params
from nhra_gt.helpers import run_hybrid
from nhra_gt.visualization.base import PlotConfig, save_figure
from nhra_gt.visualization.distributional import plot_distributions


def model_wrapper(params: Params) -> float:
    """Wraps simulation to return a single outcome for PSA."""
    years = [2025, 2030]
    agg, _ = run_hybrid(years, params, n_mc=10)
    return float(agg.iloc[-1]["rr_mean"])


def run_psa(
    dists: dict[str, Callable[[int], np.ndarray]],
    model_func: Callable[[Params], float],
    n_samples: int = 100,
    n_procs: int = 1,
) -> pd.DataFrame:
    """Runs PSA by sampling from provided distributions."""
    samples = {}
    for name, dist in dists.items():
        samples[name] = dist(n_samples)

    results = []
    base_p = Params()
    for i in range(n_samples):
        # Update params
        update_dict = {name: samples[name][i] for name in samples}
        p = base_p.replace(**update_dict)
        outcome = model_func(p)
        results.append({**update_dict, "outcome": outcome})

    return pd.DataFrame(results)


def main() -> None:
    """Execute the PSA workflow and save results."""
    print("Starting Probabilistic Sensitivity Analysis (PSA)...")

    # Define Distributions
    dists = {
        "cost_shifting_intensity": lambda n: np.random.uniform(0.05, 0.80, n),
        "discharge_delay_base": lambda n: np.clip(np.random.normal(1.0, 0.15, n), 0.5, 2.0),
        "fragmentation_index": lambda n: np.clip(np.random.normal(1.0, 0.12, n), 0.6, 1.5),
        "political_salience": lambda n: np.random.uniform(0.1, 0.5, n),
    }

    # Run PSA
    df = run_psa(dists, model_wrapper, n_samples=100, n_procs=1)

    # Save Results
    out_dir = Path("data/gsa")
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "psa_results.csv", index=False)
    print(f"PSA results saved to {out_dir / 'psa_results.csv'}")

    # Plotting
    config = PlotConfig()
    # Note: plot_distributions currently returns an empty Figure, we should implement it
    fig = plot_distributions(df, config=config)

    plot_path = out_dir / "psa_distribution.png"
    save_figure(fig, plot_path, config)
    print(f"Plot saved to {plot_path}")


if __name__ == "__main__":
    main()
