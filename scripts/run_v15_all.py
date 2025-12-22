from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_game_theory.v8 import Params, run_hybrid
from nhra_game_theory.subgames.nash import all_nash
from nhra_game_theory.subgames.games import (
    GameParams,
    definition_game,
    bargaining_game,
    cost_shifting_game,
    discharge_coordination_game,
    governance_integration_game,
    compliance_game,
)


def equilibria_snapshot(p: Params) -> pd.DataFrame:
    """Compute equilibria for each stage game over a grid of (pressure, effgap)."""
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


def main() -> None:
    out = Path("outputs/v15")
    (out / "tables").mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    base = Params()

    # Baseline (moderate MC for CI runtime)
    df, strat = run_hybrid(years=years, p=base, seed=123, n_mc=250)
    df.to_csv(out / "tables" / "trajectory.csv", index=False)
    strat.to_csv(out / "tables" / "strategy_frequency.csv", index=False)

    # Equilibria summaries
    eq_grid = equilibria_snapshot(base)
    eq_grid.to_csv(out / "tables" / "equilibria_grid.csv", index=False)

    eq_year = equilibria_by_year(df, base)
    eq_year.to_csv(out / "tables" / "equilibria_by_year.csv", index=False)

    # Scenario set emphasising equilibrium behaviour and policy levers
    scenarios = {
        "baseline_equilibria": Params(),
        "no_stage_equilibria": Params(use_stage_game_equilibria=False),
        # Cooperative stylisation: lower cost shifting and fragmentation; stronger bed/discharge capacity
        "cooperative": Params(cost_shifting_intensity=0.8, fragmentation_index=0.9, bed_capacity_index=1.05, discharge_delay_base=0.95),
        # Adversarial stylisation: higher cost shifting and fragmentation; tighter capacity; higher political salience
        "adversarial": Params(cost_shifting_intensity=1.2, fragmentation_index=1.1, bed_capacity_index=0.97, discharge_delay_base=1.05, political_salience=0.7),
        # Alternative equilibrium selection rule
        "equilibrium_row_favourable": Params(equilibrium_selection_rule="row_favourable"),
    }
    end_rows = []
    for name, pp in scenarios.items():
        d, _ = run_hybrid(years=years, p=pp, seed=123, n_mc=200)
        end = d.iloc[-1]
        end_rows.append(
            {
                "scenario": name,
                "rr_mean": float(end["rr_mean"]),
                "pressure_mean": float(end["pressure_mean"]),
                "offload_mean": float(end["offload_mean"]),
                "within4_mean": float(end["within4_mean"]),
                "effgap_mean": float(end["effgap_mean"]),
            }
        )
    pd.DataFrame(end_rows).to_csv(out / "tables" / "scenario_summary.csv", index=False)


if __name__ == "__main__":
    main()
