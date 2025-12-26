"""Run v11 analyses and write outputs (tables, plots, interactive).

Usage:
  PYTHONPATH=src python scripts/run_v11_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))


from pathlib import Path

import pandas as pd
from nhra_game_theory.plotting import plot_strategy_heatmap, plot_trajectory
from nhra_game_theory.legacy_engine import (
    Params,
    apply_intervention_partial,
    nep_series,
    one_way_sensitivity,
    probabilistic_sensitivity,
    run_hybrid,
    scenario_summary,
)


def main() -> None:
    out = Path("outputs/v11")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "plots").mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    p = Params()

    # Baseline trajectory
    traj, freq = run_hybrid(years, p, seed=123, n_mc=200)
    traj.to_csv(out / "tables" / "trajectory.csv", index=False)
    freq.to_csv(out / "tables" / "strategy_frequency.csv", index=False)

    # NEP series (illustrative)
    nep = nep_series(years, p)
    nep.to_csv(out / "tables" / "nep_series.csv", index=False)

    # Core trajectory plots (with quantile bands where present)
    plot_trajectory(traj, "pressure_mean", "Pressure index", out / "plots" / "pressure.png", "pressure_p10", "pressure_p90")
    plot_trajectory(traj, "offload_mean", "Ambulance offload (min)", out / "plots" / "offload.png", "offload_p10", "offload_p90")
    plot_trajectory(traj, "within4_mean", "ED within 4 hours (share)", out / "plots" / "within4.png", "within4_p10", "within4_p90")
    plot_trajectory(traj, "rr_mean", "Relative risk proxy", out / "plots" / "rr_proxy.png", "rr_p10", "rr_p90")

    # NEP plot (index)
    plot_trajectory(nep.rename(columns={"nep_per_nwau": "nep_idx"}), "nep_idx", "NEP ($/NWAU) index", out / "plots" / "nep_index.png")

    # Strategy heatmap (publication-friendly: short labels)
    plot_strategy_heatmap(freq, out / "plots" / "strategy_heatmap.png")

    # Scenarios
    scenarios = {
        "baseline": [],
        "pooled": ["pooled"],
        "discharge": ["discharge"],
        "indexation": ["indexation"],
        "pooled+discharge": ["pooled", "discharge"],
        "bundle": ["pooled", "discharge", "indexation", "integration", "workforce", "cap", "audit_relief"],
    }
    scen = scenario_summary(years, p, scenarios, seed=123, n_mc=80)

    # Add partial pooled (50% strength)
    pp = apply_intervention_partial(p, "pooled", strength=0.5)
    tr_pp, _ = run_hybrid(years, pp, seed=123, n_mc=80)
    end_pp = tr_pp.iloc[-1].to_dict()
    scen = pd.concat(
        [
            scen,
            pd.DataFrame(
                [
                    {
                        "scenario": "partial_pooled",
                        "interventions": "pooled_partial(0.5)",
                        "end_year": years[-1],
                        "pressure_mean": float(end_pp["pressure_mean"]),
                        "offload_mean": float(end_pp["offload_mean"]),
                        "within4_mean": float(end_pp["within4_mean"]),
                        "rr_mean": float(end_pp["rr_mean"]),
                        "cth_nominal_mean": float(end_pp["cth_nominal_mean"]),
                        "cth_effective_mean": float(end_pp["cth_effective_mean"]),
                        "effgap_mean": float(end_pp["effgap_mean"]),
                        "discharge_mean": float(end_pp["discharge_mean"]),
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    scen.to_csv(out / "tables" / "scenario_summary.csv", index=False)

    # One-way sensitivity
    grid = {
        "noise_sd": [0.01, 0.03, 0.06],
        "cost_shifting_intensity": [0.20, 0.30, 0.40, 0.50],
        "discharge_delay_base": [0.7, 1.0, 1.3],
        "political_salience": [0.10, 0.30, 0.50],
    }
    sens = one_way_sensitivity(years, p, grid, seed=123, n_mc=80)
    sens.to_csv(out / "tables" / "one_way_sensitivity.csv", index=False)

    # PSA for flagship bundle
    psa = probabilistic_sensitivity(years, p, ["pooled", "discharge", "indexation"], seed=123, n_param=80, n_mc=50)
    psa.to_csv(out / "tables" / "psa_pooled_discharge_indexation.csv", index=False)


if __name__ == "__main__":
    main()
