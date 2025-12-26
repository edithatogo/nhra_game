from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pandas as pd

from nhra_game_theory.engine import Params, nep_series, nep_vs_cost_series, run_hybrid
from nhra_game_theory.subgames.games import (
    GameParams,
    bargaining_game,
    compliance_game,
    cost_shifting_game,
    definition_game,
    discharge_coordination_game,
    governance_integration_game,
)
from nhra_game_theory.subgames.nash import all_nash


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
    for _, row in df.iterrows():
        gp = GameParams(
            pressure=float(row["pressure_mean"]),
            efficiency_gap=float(row["effgap_mean"]),
            discharge_delay=float(row["discharge_mean"]),
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
        d, _ = run_hybrid(years=years, p=pp, seed=seed, n_mc=200)
        end = d.iloc[-1]
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
    df = pd.DataFrame(rows).sort_values("scenario").reset_index(drop=True)
    return df


def main() -> None:
    out = Path("data/baseline")
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    base = Params()

    # Baseline
    traj, strat = run_hybrid(years=years, p=base, seed=123, n_mc=250)
    traj.to_csv(tables / "trajectory.csv", index=False)
    strat.to_csv(tables / "strategy_frequency.csv", index=False)

    nep_cost = nep_vs_cost_series(years, base)
    nep_cost.to_csv(tables / "nep_cost_series.csv", index=False)

    # NEP series (index discipline; NEP is annual $/NWAU index)
    nep = nep_series(years=years, p=base)
    nep.to_csv(tables / "nep_series.csv", index=False)

    # Equilibria exports
    eq_grid = equilibria_snapshot(base)
    eq_grid.to_csv(tables / "equilibria_grid.csv", index=False)
    eq_year = equilibria_by_year(traj, base)
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

    # Policy intervention scenarios (stylised levers; intended for directionality, not point prediction)
    interventions = {
        # Governance integration / pooled budgets reduce fragmentation and cost-shifting incentives
        "pooled_funding_pilot": replace(
            base, fragmentation_index=0.92, cost_shifting_intensity=0.90
        ),
        "ucc_integrated_governance": replace(
            base, fragmentation_index=0.95, admin_burden_weight=0.95
        ),
        # Aged care / NDIS throughput improves discharge delay
        "aged_care_places_increase": replace(
            base, discharge_delay_base=0.90, bed_capacity_index=1.02
        ),
        # NEP indexation realism (raises NEP-to-cost ratio, reducing the efficiency gap for rurality/remote)
        "nep_indexation_uplift": replace(
            base,
            nep_to_cost_ratio_metro=min(1.0, base.nep_to_cost_ratio_metro + 0.03),
            nep_to_cost_ratio_regional=min(1.0, base.nep_to_cost_ratio_regional + 0.05),
            nep_to_cost_ratio_remote=min(1.0, base.nep_to_cost_ratio_remote + 0.07),
        ),
        # Compliance/audit push (may reduce gaming but adds admin burden)
        "audit_blitz": replace(base, audit_pressure=1.25, admin_burden_weight=1.10),
    }
    interv = scenario_endpoints(years, interventions, seed=123)
    interv.to_csv(tables / "intervention_scenarios.csv", index=False)

    # Intervention deltas vs baseline
    baseline_row = (
        interv.assign(_k=1)
        .merge(
            core[core["scenario"] == "baseline_equilibria"].assign(_k=1),
            on="_k",
            suffixes=("", "_baseline"),
        )
        .drop(columns=["_k"])
    )
    deltas = []
    for _, r in baseline_row.iterrows():
        deltas.append(
            {
                "scenario": str(r["scenario"]),
                "delta_rr_2030": float(r["rr_mean_2030"] - r["rr_mean_2030_baseline"]),
                "delta_offload_2030": float(
                    r["offload_mean_2030"] - r["offload_mean_2030_baseline"]
                ),
                "delta_within4_2030": float(
                    r["within4_mean_2030"] - r["within4_mean_2030_baseline"]
                ),
                "delta_pressure_2030": float(
                    r["pressure_mean_2030"] - r["pressure_mean_2030_baseline"]
                ),
                "delta_effgap_2030": float(r["effgap_mean_2030"] - r["effgap_mean_2030_baseline"]),
            }
        )
    pd.DataFrame(deltas).to_csv(tables / "intervention_deltas.csv", index=False)


if __name__ == "__main__":
    main()
