from __future__ import annotations

import os
from dataclasses import asdict
from datetime import date
from pathlib import Path

import pandas as pd

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
from nhra_game_theory.v9 import Params, apply_intervention_partial, nep_cost_series, run_hybrid


def _save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


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


def equilibria_by_year(traj: pd.DataFrame, p: Params) -> pd.DataFrame:
    """Solve *all* Nash equilibria for each stage game at each year's mean state."""
    eq_rows: list[dict[str, object]] = []
    for _, row in traj.iterrows():
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
    out = Path("outputs/v19")
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    base = Params()

    # Defaults are conservative so the full build runs quickly.
    # Users can override for higher precision:
    #   N_MC_BASE=1000 N_MC_SCEN=800 PYTHONPATH=src python scripts/run_v19_all.py
    n_mc_base = int(os.environ.get("N_MC_BASE", "220"))
    n_mc_scen = int(os.environ.get("N_MC_SCEN", "160"))

    meta = {
        "version": "v19",
        "date": str(date.today()),
        "notes": (
            "v19 consolidates dynamic macro drift (NEP vs input costs) with stage-game equilibrium mapping, "
            "intervention packages, and interactive network exports."
        ),
        "n_mc_base": n_mc_base,
        "n_mc_scen": n_mc_scen,
    }
    (tables / "metadata.json").write_text(pd.Series(meta).to_json(indent=2), encoding="utf-8")
    (tables / "params_baseline.json").write_text(pd.Series(asdict(base)).to_json(indent=2), encoding="utf-8")

    # --- Baseline simulation ---
    traj, strat = run_hybrid(years=years, p=base, seed=123, n_mc=n_mc_base)
    _save_df(traj, tables / "trajectory_baseline.csv")
    _save_df(strat, tables / "strategy_freq_baseline.csv")
    _save_df(nep_cost_series(years, base), tables / "nep_cost_series.csv")

    # --- Equilibria mapping ---
    _save_df(equilibria_snapshot(base), tables / "equilibria_grid.csv")
    _save_df(equilibria_by_year(traj, base), tables / "equilibria_by_year.csv")

    # --- Intervention scenarios (single levers + packages) ---
    scenario_defs: dict[str, list[str]] = {
        "baseline": [],
        "pooled_funding": ["pooled_funding"],
        "ucc_integration": ["ucc_integration"],
        "aged_ndis_capacity": ["aged_ndis_capacity"],
        "cumulative_cap": ["cumulative_cap"],
        "nep_realism": ["nep_realism"],
        "nep_growth": ["nep_growth"],
        "wage_compact": ["wage_compact"],
        "integration_package": ["pooled_funding", "ucc_integration", "aged_ndis_capacity"],
        "macro_alignment_package": ["nep_realism", "nep_growth", "wage_compact"],
        "full_package": [
            "pooled_funding",
            "ucc_integration",
            "aged_ndis_capacity",
            "cumulative_cap",
            "nep_realism",
            "nep_growth",
            "wage_compact",
        ],
    }

    endpoints_rows: list[dict[str, object]] = []
    series_rows: list[pd.DataFrame] = []

    for name, levers in scenario_defs.items():
        pp = base
        for lever in levers:
            pp = apply_intervention_partial(pp, lever, strength=1.0)

        d, _ = run_hybrid(years=years, p=pp, seed=123, n_mc=n_mc_scen)
        end = d.iloc[-1]
        endpoints_rows.append(
            {
                "scenario": name,
                "rr_mean_2030": float(end["rr_mean"]),
                "pressure_mean_2030": float(end["pressure_mean"]),
                "offload_mean_2030": float(end["offload_mean"]),
                "within4_mean_2030": float(end["within4_mean"]),
                "effgap_mean_2030": float(end["effgap_mean"]),
                "occ_mean_2030": float(end["occupancy_mean"]),
                "nep_to_cost_2030": float(end["nep_mean"] / end["cost_mean"]),
            }
        )
        dd = d.copy()
        dd.insert(0, "scenario", name)
        series_rows.append(dd)

    endpoints = pd.DataFrame(endpoints_rows).sort_values("scenario").reset_index(drop=True)
    _save_df(endpoints, tables / "scenario_endpoints.csv")
    _save_df(pd.concat(series_rows, ignore_index=True), tables / "scenario_timeseries.csv")


if __name__ == "__main__":
    main()
