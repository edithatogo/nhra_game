from __future__ import annotations

from pathlib import Path

import optuna
import pandas as pd
from nhra_game_theory.engine import Params, run_hybrid


def load_targets(path: Path) -> dict[str, float]:
    df = pd.read_csv(path)
    targets = {}
    for _, row in df.iterrows():
        targets[row["metric"]] = float(row["value"])
    return targets

def objective(trial: optuna.Trial, targets: dict[str, float], n_mc: int, seed: int) -> float:
    # Minimal parameter set for baseline optimization
    p = Params(
        cost_shifting_intensity=trial.suggest_float("cost_shifting_intensity", 0.1, 0.8),
        fragmentation_index=trial.suggest_float("fragmentation_index", 0.5, 1.5),
        discharge_delay_base=trial.suggest_float("discharge_delay_base", 0.5, 1.5),
    )
    
    # Run model for 2025-2030
    years = list(range(2025, 2031))
    traj, _ = run_hybrid(years=years, p=p, seed=seed, n_mc=n_mc)
    
    # Compare against a few key targets (simple MSE for now)
    # Using ED_WITHIN_4H_2024_25 as a proxy target for end-state
    w4_model = traj.iloc[-1]["within4_mean"]
    w4_target = targets.get("ED_WITHIN_4H_2024_25", 0.53)
    
    error = (w4_model - w4_target) ** 2
    return error

def main() -> None:
    out_dir = Path("data/baseline_v21")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    targets_path = Path("data/raw/calibration_targets.csv")
    if not targets_path.exists():
        print(f"Warning: {targets_path} not found.")
        return

    targets = load_targets(targets_path)
    
    study = optuna.create_study(direction="minimize")
    # Low n_mc and n_trials for baseline establishment
    study.optimize(lambda t: objective(t, targets, n_mc=50, seed=42), n_trials=20)
    
    # Save best
    best_df = pd.DataFrame([study.best_params])
    best_df["best_value"] = study.best_value
    best_df.to_csv(out_dir / "baseline_optuna_best.csv", index=False)
    print(f"Best params: {study.best_params}")
    print(f"Best value: {study.best_value}")

if __name__ == "__main__":
    main()
