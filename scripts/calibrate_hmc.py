"""Performs Bayesian calibration using Hamiltonian Monte Carlo."""

import argparse
from pathlib import Path

import numpyro
import numpyro.distributions as dist


def model(historical_years, observed_within4, observed_occupancy):
    """Define the probabilistic model for NumPyro."""
    # 1. Priors
    demand_base = numpyro.sample("demand_base", dist.Normal(1.0, 0.1))
    return demand_base


def main() -> None:
    """Run the HMC calibration process."""
    parser = argparse.ArgumentParser(description="NumPyro HMC Calibration")
    parser.add_argument("--samples", type=int, default=500)
    parser.add_argument("--warmup", type=int, default=200)
    args = parser.parse_args()

    hist_path = Path("data/calibration/historical_normalized.csv")
    if not hist_path.exists():
        print("Historical data not found. Run preprocessing first.")
        return

    # Load data logic...
    print(f"Starting HMC Calibration (Samples={args.samples}, Warmup={args.warmup})...")


if __name__ == "__main__":
    main()
