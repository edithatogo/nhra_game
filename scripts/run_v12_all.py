"""Run v12 analyses (adds derived 'network' and 'cost stack' views).

Usage:
  PYTHONPATH=src python scripts/run_v12_all.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from nhra_game_theory.plotting import plot_trajectory
from nhra_game_theory.legacy_engine import (
    Params,
    nep_series,
    one_way_sensitivity,
    probabilistic_sensitivity,
    run_hybrid,
    scenario_summary,
)


def main() -> None:
    out = Path("outputs/v12")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "plots").mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    p = Params()

    traj, freq = run_hybrid(years, p, seed=123, n_mc=220)
    traj.to_csv(out / "tables" / "trajectory.csv", index=False)
    freq.to_csv(out / "tables" / "strategy_frequency.csv", index=False)

    nep = nep_series(years, p)
    nep.to_csv(out / "tables" / "nep_series.csv", index=False)

    # Derived 'cost stack' (index units)
    merged = traj.merge(nep, on="year", how="left")
    merged["cth_payment_index"] = merged["cth_nominal_mean"] * merged["efficient_payment"]
    merged["actual_cost_index"] = merged["efficient_payment"] * (1.0 + merged["effgap_mean"])
    merged["state_payment_index"] = merged["actual_cost_index"] - merged["cth_payment_index"]
    merged["network_externality"] = merged["pressure_mean"] * (1.0 - merged["within4_mean"])
    merged.to_csv(out / "tables" / "trajectory_derived.csv", index=False)

    # Plots
    plot_trajectory(merged, "network_externality", "Network externality proxy", out / "plots" / "network_externality.png")
    plot_trajectory(merged, "actual_cost_index", "Actual cost (index)", out / "plots" / "actual_cost_index.png")
    plot_trajectory(merged, "cth_payment_index", "Cth payment (index)", out / "plots" / "cth_payment_index.png")
    plot_trajectory(merged, "state_payment_index", "State payment (index)", out / "plots" / "state_payment_index.png")

    # Scenarios (smaller set, shown as bars)
    scenarios = {
        "baseline": [],
        "pooled": ["pooled"],
        "discharge": ["discharge"],
        "indexation": ["indexation"],
        "bundle": ["pooled", "discharge", "indexation", "integration", "workforce", "cap", "audit_relief"],
    }
    scen = scenario_summary(years, p, scenarios, seed=123, n_mc=170)
    scen.to_csv(out / "tables" / "scenario_summary.csv", index=False)

    def _bar(data: dict[str, float], title: str, path: Path) -> None:
        labels = list(data.keys())
        values = [float(data[k]) for k in labels]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(labels, values)
        ax.set_title(title)
        ax.tick_params(axis="x", labelrotation=30)
        fig.tight_layout()
        fig.savefig(path, dpi=300)
        plt.close(fig)

    _bar(scen.set_index("scenario")["rr_mean"].to_dict(), "RR (end-year)", out / "plots" / "scenario_rr_bars.png")
    _bar(scen.set_index("scenario")["pressure_mean"].to_dict(), "Pressure (end-year)", out / "plots" / "scenario_pressure_bars.png")

    # One-way sensitivity
    grid = {"cost_shifting_intensity": [0.2, 0.35, 0.5], "discharge_delay_base": [0.7, 1.0, 1.3]}
    sens = one_way_sensitivity(years, p, grid, seed=123, n_mc=90)
    sens.to_csv(out / "tables" / "one_way_sensitivity.csv", index=False)

    # PSA (flagship bundle)
    psa = probabilistic_sensitivity(years, p, ["pooled", "discharge", "indexation"], seed=123, n_param=80, n_mc=50)
    psa.to_csv(out / "tables" / "psa_bundle.csv", index=False)


if __name__ == "__main__":
    main()
