from __future__ import annotations

from pathlib import Path

import numpy as np
import optuna
import pandas as pd
from nhra_game_theory.engine import Params, run_hybrid


def load_targets(path: Path) -> dict[str, float]:
    df = pd.read_csv(path)
    targets = {}
    for _, row in df.iterrows():
        targets[row["metric"]] = float(row["value"])
    return targets

def stochastic_objective(means: np.ndarray, targets: np.ndarray, variances: np.ndarray, lam: float = 0.5) -> float:
    """Composite objective: MSE of means plus lambda * average variance."""
    mse = np.mean((means - targets)**2)
    penalty = lam * np.mean(variances)
    return float(mse + penalty)

def objective(trial: optuna.Trial, targets: dict[str, float], n_mc: int, seed: int) -> float:
    # Granular parameter set based on v2 re-integration
    p = Params(
        cost_shifting_intensity=trial.suggest_float("cost_shifting_intensity", 0.05, 0.8),
        fragmentation_index=trial.suggest_float("fragmentation_index", 0.6, 1.5),
        discharge_delay_base=trial.suggest_float("discharge_delay_base", 0.6, 1.4),
        political_salience=trial.suggest_float("political_salience", 0.05, 0.9),
        audit_pressure=trial.suggest_float("audit_pressure", 0.1, 1.0),
    )
    
    years = list(range(2025, 2031))
    traj, _ = run_hybrid(years=years, p=p, seed=seed, n_mc=n_mc)
    
    # End state (2030)
    last = traj.iloc[-1]
    
    # Define model outcomes vs targets
    model_outcomes = np.array([
        last["within4_mean"],
        last["occupancy_mean"]
    ])
    
    target_values = np.array([
        targets.get("ED_WITHIN_4H_2024_25", 0.53),
        targets.get("AGED_CARE_OCCUPANCY", 0.88)
    ])
    
    # Compute variances (using p90-p10 spread as a proxy for variance)
    # var = ((p90 - p10) / 2.56)^2 approx for normal dist
    variances = np.array([
        ((last["within4_p90"] - last["within4_p10"]) / 2.56)**2,
        ((last["pressure_p90"] - last["pressure_p10"]) / 2.56)**2
    ])
    
    score = stochastic_objective(model_outcomes, target_values, variances, lam=0.5)
    return score

def main() -> None:
    out_dir = Path("data/calibration_v21")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    targets_path = Path("data/raw/calibration_targets.csv")
    if not targets_path.exists():
        print(f"Warning: {targets_path} not found.")
        return

    targets = load_targets(targets_path)
    
    # Use TPESampler for better search in constrained space
    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
    
    print("Starting Stochastic Calibration...")
    study.optimize(lambda t: objective(t, targets, n_mc=100, seed=42), n_trials=50)
    
    # Save all trials (Posterior)
    trials_df = study.trials_dataframe()
    trials_df.to_csv(out_dir / "calibration_trials_posterior.csv", index=False)
    
    # Save best
    best_df = pd.DataFrame([study.best_params])
    best_df["best_value"] = study.best_value
    best_df.to_csv(out_dir / "calibration_optuna_best.csv", index=False)
    print(f"Best params: {study.best_params}")
    print(f"Best value: {study.best_value}")
    print(f"Saved posterior data to: {out_dir / 'calibration_trials_posterior.csv'}")

if __name__ == "__main__":
    main()
