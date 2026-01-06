"""Validates that simulation mechanics align with expected strategic behavior."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from nhra_gt.domain.validation import MechanismValidator
from nhra_gt.sensitivity import GSA_PARAM_NAMES, run_morris_analysis


def model_wrapper(param_values: np.ndarray) -> float:
    """Wrap model for Morris analysis compatibility."""
    p_dict = dict(zip(GSA_PARAM_NAMES, param_values, strict=False))


def main() -> None:
    """Run mechanism validation suite."""
    results_path = Path("data/gsa/morris_results.csv")

    if results_path.exists():
        print(f"Loading existing GSA results from {results_path}...")
        df = pd.read_csv(results_path)
        # Handle Unnamed column if it exists (common with pandas to_csv default)
        if "Unnamed: 0" in df.columns:
            df = df.rename(columns={"Unnamed: 0": "parameter"})
        # Or if the first column looks like parameters but has no name
        elif df.columns[0] == "mu" and "parameter" not in df.columns:
            # This means the header is missing for the index
            # Reload with index_col=0 then reset_index
            df = pd.read_csv(results_path, index_col=0)
            df.index.name = "parameter"
            df = df.reset_index()
    else:
        print("GSA results not found. Running lightweight Morris analysis...")

        # Override bounds to ensure we cross tipping points
        bounds = {
            "cost_shifting_intensity": [0.05, 0.80],
            "discharge_delay_base": [0.8, 1.2],  # +/- 20% around 1.0
            "fragmentation_index": [0.8, 1.2],
            "rurality_weight": [0.2, 0.5],
            "admin_burden_weight": [0.1, 0.4],
            "political_salience": [0.1, 0.5],
        }

        problem = get_salib_problem(GSA_PARAM_NAMES, bounds_override=bounds)
        df = run_morris_analysis(problem, model_wrapper, n_trajectories=10, n_procs=1)

        # Ensure correct column names for validator
        # run_morris_analysis returns index as parameter name, we reset it
        if "parameter" not in df.columns:
            df = df.reset_index().rename(columns={"index": "parameter"})

        # Save for future use
        results_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(results_path, index=False)

    # Add rank if missing (for both loaded and new data)
    if "rank" not in df.columns:
        df["rank"] = df["mu_star"].rank(ascending=False)

    print("\n--- Mechanism Validation Report ---")
    validator = MechanismValidator(df)

    # Define Rules
    rules = [
        ("Discharge Delay is #1 Driver", lambda: validator.verify_rank("discharge_delay_base", 1)),
        ("Cost Shifting in Top 3", lambda: validator.verify_top_n("cost_shifting_intensity", 3)),
        ("Political Salience NOT #1", lambda: not validator.verify_rank("political_salience", 1)),
        (
            "Fragmentation > Rurality",
            lambda: validator.verify_inequality("fragmentation_index", "rurality_weight"),
        ),
    ]

    all_passed = True
    for name, check in rules:
        passed = check()
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            all_passed = False

    if not all_passed:
        print(
            "\nWARNING: Mechanism validation failed. Model may not align with historical narrative."
        )
        sys.exit(1)
    else:
        print("\nSUCCESS: All mechanism integrity checks passed.")


if __name__ == "__main__":
    main()
