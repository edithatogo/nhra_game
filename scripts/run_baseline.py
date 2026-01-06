"""Runs the baseline simulation and generates standard tables."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pandas as pd

try:
    import polars as pl  # type: ignore
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]

from nhra_gt.engine import Params, nep_series, nep_vs_cost_series, run_hybrid
from nhra_gt.subgames.games import (
    GameParams,
    bargaining_game,
    compliance_game,
    cost_shifting_game,
    definition_game,
    discharge_coordination_game,
    governance_integration_game,
)
from nhra_gt.subgames.nash import all_nash


def equilibria_snapshot(p: Params) -> pd.DataFrame:
    """Count equilibria for each stage game over a small grid (pressure × effgap)."""
    rows: list[dict[str, object]] = []
    pressures = [0.8, 1.0, 1.2, 1.4]
    effgaps = [0.0, 0.2, 0.4, 0.6]
    for pr in pressures:
        for eg in effgaps:
            gp = GameParams(
                pressure=pr,
                efficiency_gap=eg,
                discharge_delay=1.0,
                political_salience=p.political_salience,
                audit_pressure=p.audit_pressure,
                cost_shifting_intensity=p.cost_shifting_intensity,
                political_capital=1.0,
            )
            games = {
                "DEF": definition_game(gp),
                "BARG": bargaining_game(gp),
                "SHIFT": cost_shifting_game(gp),
                "DISC": discharge_coordination_game(gp),
                "GOV": governance_integration_game(gp),
                "COMP": compliance_game(gp),
            }
            for name, g in games.items():
                eqs = all_nash(g)
                rows.append(
                    {
                        "game": name,
                        "pressure": pr,
                        "effgap": eg,
                        "n_equilibria": len(eqs),
                        "has_mixed": any(e.kind == "mixed" for e in eqs),
                    }
                )
    return pd.DataFrame(rows)


def equilibria_by_year(df: pd.DataFrame, p: Params) -> pd.DataFrame:
    """Solve *all* Nash equilibria for each stage game at each year's mean state."""
    eq_rows: list[dict[str, object]] = []
    # df is expected to have aggregated results (means)
    for row in df.to_dict(orient="records"):
        gp = GameParams(
            pressure=float(row["pressure_mean"]),
            efficiency_gap=float(row["effgap_mean"]),
            discharge_delay=float(row.get("discharge_mean", 1.0)),
            political_salience=p.political_salience,
            audit_pressure=p.audit_pressure,
            cost_shifting_intensity=p.cost_shifting_intensity,
            political_capital=1.0,
        )
        games = {
            "DEF": definition_game(gp),
            "BARG": bargaining_game(gp),
            "SHIFT": cost_shifting_game(gp),
            "DISC": discharge_coordination_game(gp),
            "GOV": governance_integration_game(gp),
            "COMP": compliance_game(gp),
        }
        for gname, g in games.items():
            eqs = all_nash(g)
            for k, eq0 in enumerate(eqs, start=1):
                er = float(eq0.row @ g.u_row @ eq0.col)
                ec = float(eq0.row @ g.u_col @ eq0.col)
                eq_rows.append(
                    {
                        "year": int(row["year"]),
                        "game": gname,
                        "eq_index": k,
                        "kind": eq0.kind,
                        "row_action": g.row_actions[int(eq0.row.argmax())],
                        "col_action": g.col_actions[int(eq0.col.argmax())],
                        "row_payoff": er,
                        "col_payoff": ec,
                        "n_equilibria_in_game": len(eqs),
                    }
                )
    return pd.DataFrame(eq_rows)


def scenario_endpoints(
    years: list[int], scenarios: dict[str, Params], seed: int = 123
) -> pd.DataFrame:
    """Run a set of scenarios and return end-year summary metrics."""
    rows: list[dict[str, object]] = []
    for name, pp in scenarios.items():
        d_pd, _ = run_hybrid(years=years, p=pp, seed=seed, n_mc=200)
        end = d_pd.tail(1).to_dict(orient="records")[0]
        rows.append(
            {
                "scenario": name,
                "rr_mean_2030": float(end["rr_mean"]),
                "pressure_mean_2030": float(end["pressure_mean"]),
                "offload_mean_2030": float(end["offload_mean"]),
                "within4_mean_2030": float(end["within4_mean"]),
                "effgap_mean_2030": float(end["effgap_mean"]),
                "occ_mean_2030": float(end["occupancy_mean"]),
            }
        )
    return pd.DataFrame(rows).sort_values("scenario", kind="stable").reset_index(drop=True)


def main() -> None:
    """Execute the standard baseline simulation and save results."""
    out = Path("data/baseline")
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    base = Params()

    # Baseline
    traj_pd, strat_pd = run_hybrid(years=years, p=base, seed=123, n_mc=250)

    # Ensure types are correct for stable downstream CSVs.
    if not strat_pd.empty:
        strat_pd["year"] = strat_pd["year"].astype(int)
        strat_pd["game"] = strat_pd["game"].astype(str)
        strat_pd["strategy"] = strat_pd["strategy"].astype(str)
        strat_pd["n"] = strat_pd["n"].astype(int)
        strat_pd["share"] = strat_pd["share"].astype(float)

    traj_pd.to_csv(tables / "trajectory.csv", index=False)
    strat_pd.to_csv(tables / "strategy_frequency.csv", index=False)

    nep_vs_cost_series(years, base).to_csv(tables / "nep_cost_series.csv", index=False)

    # NEP series (index discipline; NEP is annual $/NWAU index)
    nep_series(years=years, p=base).to_csv(tables / "nep_series.csv", index=False)

    # Equilibria exports
    eq_grid = equilibria_snapshot(base)
    eq_grid.to_csv(tables / "equilibria_grid.csv", index=False)
    eq_year = equilibria_by_year(traj_pd, base)
    eq_year.to_csv(tables / "equilibria_by_year.csv", index=False)

    # Core scenario set
    scenarios_core = {
        "baseline_equilibria": Params(),
        "no_stage_equilibria": Params(use_stage_game_equilibria=False),
        "cooperative": Params(
            cost_shifting_intensity=0.8,
            fragmentation_index=0.9,
            bed_capacity_index=1.05,
            discharge_delay_base=0.95,
        ),
        "adversarial": Params(
            cost_shifting_intensity=1.2,
            fragmentation_index=1.1,
            bed_capacity_index=0.97,
            discharge_delay_base=1.05,
            political_salience=0.7,
        ),
        "equilibrium_row_favourable": Params(equilibrium_selection_rule="row_favourable"),
        "equilibrium_random": Params(equilibrium_selection_rule="random"),
    }
    core = scenario_endpoints(years, scenarios_core, seed=123)
    core.to_csv(tables / "scenario_summary.csv", index=False)

    # Policy intervention scenarios
    interventions = {
        "pooled_funding_pilot": replace(
            base, cost_shifting_intensity=0.90, fragmentation_index=0.92
        ),
        "ucc_integrated_governance": replace(
            base, admin_burden_weight=0.95, fragmentation_index=0.95
        ),
        "aged_care_places_increase": replace(
            base, bed_capacity_index=1.02, discharge_delay_base=0.90
        ),
        "nep_indexation_uplift": replace(
            base,
            nep_to_cost_ratio_metro=min(1.0, base.nep_to_cost_ratio_metro + 0.03),
            nep_to_cost_ratio_regional=min(1.0, base.nep_to_cost_ratio_regional + 0.05),
            nep_to_cost_ratio_remote=min(1.0, base.nep_to_cost_ratio_remote + 0.07),
        ),
        "audit_blitz": replace(base, admin_burden_weight=1.10, audit_pressure=1.25),
    }
    interv = scenario_endpoints(years, interventions, seed=123)
    interv.to_csv(tables / "intervention_scenarios.csv", index=False)

    # Intervention deltas vs baseline
    baseline_metrics = core[core["scenario"] == "baseline_equilibria"].drop(columns=["scenario"])
    baseline_metrics_row = baseline_metrics.iloc[0]

    deltas = []
    for row in interv.to_dict(orient="records"):
        deltas.append(
            {
                "scenario": row["scenario"],
                "delta_rr_2030": row["rr_mean_2030"] - baseline_metrics_row["rr_mean_2030"],
                "delta_offload_2030": row["offload_mean_2030"]
                - baseline_metrics_row["offload_mean_2030"],
                "delta_within4_2030": row["within4_mean_2030"]
                - baseline_metrics_row["within4_mean_2030"],
                "delta_pressure_2030": row["pressure_mean_2030"]
                - baseline_metrics_row["pressure_mean_2030"],
                "delta_effgap_2030": row["effgap_mean_2030"]
                - baseline_metrics_row["effgap_mean_2030"],
            }
        )
    pd.DataFrame(deltas).to_csv(tables / "intervention_deltas.csv", index=False)


if __name__ == "__main__":
    main()
