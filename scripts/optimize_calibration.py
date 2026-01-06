"""Optimizes model parameters using Optuna Bayesian search."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import optuna
import pandas as pd

from nhra_gt.engine import Params, run_hybrid


def load_targets(path: Path) -> dict[str, float]:
    """Load calibration targets from CSV."""
    df = pd.read_csv(path)
    targets = {}
    for _, row in df.iterrows():
        targets[row["metric"]] = float(row["value"])
    return targets


def stochastic_objective(
    means: np.ndarray, targets: np.ndarray, variances: np.ndarray, lam: float = 0.5
) -> float:
    """Composite objective: MSE of means plus lambda * average variance."""
    # Normalize by target value to ensure all metrics have similar weight
    weights = 1.0 / (np.abs(targets) + 1e-9)
    mse = np.mean(((means - targets) * weights) ** 2)
    penalty = lam * np.mean(variances * (weights**2))
    return float(mse + penalty)


def objective(trial: optuna.Trial, targets: dict[str, float], n_mc: int, seed: int) -> float:
    """Optuna objective function for parameter optimization."""
    # Granular parameter set
    p = Params(
        cost_shifting_intensity=trial.suggest_float("cost_shifting_intensity", 0.05, 0.8),
        discharge_delay_base=trial.suggest_float("discharge_delay_base", 0.6, 1.4),
        political_salience=trial.suggest_float("political_salience", 0.05, 0.9),
        audit_pressure=trial.suggest_float("audit_pressure", 0.1, 1.0),
        capacity_lag=trial.suggest_float("capacity_lag", 0.05, 0.5),
    )

    years = [2025, 2030]  # Start and end
    traj, _ = run_hybrid(years=years, p=p, seed=seed, n_mc=n_mc)

    # End state (2030)
    last = traj.iloc[-1]

    # Define model outcomes vs targets
    model_outcomes = np.array(
        [
            last["within4_mean"],
            last["occupancy_mean"],
            last["effgap_mean"],
            last["cth_effective_mean"],
        ]
    )

    target_values = np.array(
        [
            targets.get("ED_WITHIN_4H_2030", 0.53),
            targets.get("HOSPITAL_OCCUPANCY_2030", 0.88),
            targets.get("EFFICIENCY_GAP_2030", 0.20),
            targets.get("CTH_EFFECTIVE_SHARE_2030", 0.38),
        ]
    )

    # Compute variances (using p90-p10 spread as a proxy)
    variances = np.array(
        [
            ((last["within4_p90"] - last["within4_p10"]) / 2.56) ** 2,
            ((last["occupancy_p90"] - last["occupancy_p10"]) / 2.56) ** 2,
            ((last["effgap_mean"] * 0.1) / 2.56) ** 2,  # Stylised variance for gap
            ((last["cth_effective_mean"] * 0.05) / 2.56) ** 2,
        ]
    )

    score = stochastic_objective(model_outcomes, target_values, variances, lam=0.5)
    return score


def main() -> None:
    """Run the multi-target calibration optimization."""
    import os

    out_dir = Path("data/calibration")
    out_dir.mkdir(parents=True, exist_ok=True)

    targets_path = Path("data/raw/calibration_targets.csv")
    targets = load_targets(targets_path) if targets_path.exists() else {}

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))

    n_trials = int(os.environ.get("NHRA_CALIBRATION_TRIALS", 30))
    print(f"Starting Multi-Target Stochastic Calibration with {n_trials} trials...")
    study.optimize(lambda t: objective(t, targets, n_mc=50, seed=42), n_trials=n_trials)

    # Save best
    best_df = pd.DataFrame([study.best_params])
    best_df["best_value"] = study.best_value
    best_df.to_csv(out_dir / "calibration_optuna_best.csv", index=False)

    # Save all trials (Posterior)
    trials_df = study.trials_dataframe()
    trials_df.to_csv(out_dir / "calibration_trials_posterior.csv", index=False)

    print(f"Best params: {study.best_params}")


if __name__ == "__main__":
    main()
