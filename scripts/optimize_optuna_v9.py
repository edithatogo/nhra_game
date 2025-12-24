from __future__ import annotations

"""
Optional: policy search via Optuna.

This is **not** an economic evaluation. It is a computational way to explore "policy levers"
(e.g., pooled funding intensity, governance integration, indexation realism) that minimise
a composite objective built from the v8 stylised outcomes.

Run:
  pip install -e ".[opt]"
  PYTHONPATH=src python scripts/optimize_optuna_v9.py --trials 200
"""

import argparse
from dataclasses import replace
from pathlib import Path

import numpy as np
from nhra_game_theory.legacy_engine import Params, StrategyMix, run_hybrid


def objective_from_summary(summary: dict[str, float]) -> float:
    """
    Composite objective: lower is better.
    - penalise higher relative risk (rr_2030)
    - penalise longer offload (offload_2030)
    - reward higher ED within 4h (within4_2030)
    """
    rr = float(summary["rr_2030"])
    off = float(summary["offload_2030"])
    w4 = float(summary["within4_2030"])
    # weights tuned for interpretability (not calibration)
    return (1.0 * rr) + (0.003 * off) + (1.0 * (1.0 - w4))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=120)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--n-mc", type=int, default=120)
    ap.add_argument("--out", type=Path, default=Path("outputs/v9/tables/optuna_best.csv"))
    args = ap.parse_args()

    try:
        import optuna  # type: ignore
    except Exception as e:
        raise SystemExit("Optuna not installed. Run: pip install -e '.[opt]'") from e

    rng = np.random.default_rng(args.seed)

    # Fix a baseline strategy mix (can be extended to make strategy a decision variable)
    mix = StrategyMix(
        cth="Glide45",
        state="Reject",
        provider="Escalate",
        regulator="Tighten",
        media="Amplify",
        consumer="Demand",
    )

    base = Params()

    def trial_objective(trial: optuna.Trial) -> float:
        p = replace(
            base,
            # levers
            pooled_funding=trial.suggest_float("pooled_funding", 0.0, 1.0),
            governance_integration=trial.suggest_float("governance_integration", 0.0, 1.0),
            indexation_realism=trial.suggest_float("indexation_realism", 0.6, 1.4),
            discharge_integration=trial.suggest_float("discharge_integration", 0.0, 1.0),
            data_interop=trial.suggest_float("data_interop", 0.0, 1.0),
        )
        df = run_hybrid(p, mix=mix, n_mc=args.n_mc, seed=int(rng.integers(0, 2**31 - 1)))
        # take last year mean outcome
        last = df[df["year"] == df["year"].max()].iloc[0].to_dict()
        return objective_from_summary({
            "rr_2030": float(last["rr_mean"]),
            "offload_2030": float(last["offload_mean"]),
            "within4_2030": float(last["within4_mean"]),
        })

    sampler = optuna.samplers.TPESampler(seed=args.seed)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(trial_objective, n_trials=args.trials)

    best = study.best_params | {"best_value": float(study.best_value)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("parameter,value\n" + "\n".join(f"{k},{v}" for k, v in best.items()), encoding="utf-8")
    print(f"Wrote: {args.out}")

if __name__ == "__main__":
    main()
