from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from datetime import date

import pandas as pd

from nhra_game_theory.v9 import Params, run_hybrid, nep_cost_series, apply_intervention_partial
from nhra_game_theory.subgames.nash import all_nash
from nhra_game_theory.subgames.games import (
    GameParams,
    definition_game,
    bargaining_game,
    cost_shifting_game,
    discharge_coordination_game,
    governance_integration_game,
    compliance_audit_game,
)


def _save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    out = Path("outputs/v18")
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    # --- 0) Metadata ---
    meta = {
        "version": "v18",
        "date": str(date.today()),
        "notes": "v18 adds explicit NEP ($/NWAU) and input-cost indices over time (macro drift), plus expanded sensitivity and intervention scenarios.",
    }
    (tables / "metadata.json").write_text(pd.Series(meta).to_json(indent=2), encoding="utf-8")

    # --- 1) Solve equilibria for each stage game (representative baseline state) ---
    gp = GameParams(pressure=1.0, efficiency_gap=0.20, discharge_delay=1.0, fragmentation=1.0, audit_pressure=1.0)

    games = {
        "definition": definition_game(gp),
        "bargaining": bargaining_game(gp),
        "cost_shifting": cost_shifting_game(gp),
        "discharge_coordination": discharge_coordination_game(gp),
        "governance_integration": governance_integration_game(gp),
        "compliance_audit": compliance_audit_game(gp),
    }

    eq_rows = []
    for name, g in games.items():
        eqs = all_nash(g)
        for i, e in enumerate(eqs):
            eq_rows.append(
                {
                    "game": name,
                    "equilibrium_id": i,
                    "profile": str(e.profile),
                    "payoffs": str(e.payoffs),
                }
            )
    _save_df(pd.DataFrame(eq_rows), tables / "equilibria_all_games.csv")

    # --- 2) Baseline simulation ---
    years = list(range(2025, 2031))
    base = Params()
    traj, strat = run_hybrid(years=years, p=base, seed=123, n_mc=400)

    _save_df(traj, tables / "trajectory_baseline.csv")
    _save_df(strat, tables / "strategy_freq_baseline.csv")
    _save_df(nep_cost_series(years, base), tables / "nep_cost_series.csv")

    # --- 3) One-way sensitivity (expanded, includes macro drift terms) ---
    keys = [
        ("cost_shifting_intensity", 0.15),
        ("fragmentation_index", 0.15),
        ("discharge_delay_base", 0.15),
        ("audit_pressure", 0.15),
        ("nep_annual_growth", 0.20),
        ("input_cost_annual_growth", 0.20),
        ("macro_drift_weight", 0.25),
        ("nep_to_cost_ratio_regional", 0.10),
        ("nep_to_cost_ratio_remote", 0.10),
    ]

    sens = []
    for key, frac in keys:
        base_val = getattr(base, key)
        for label, mult in [("low", 1.0 - frac), ("high", 1.0 + frac)]:
            if isinstance(base_val, bool):
                continue
            p2 = replace(base, **{key: base_val * mult})
            df2, _ = run_hybrid(years=years, p=p2, seed=123, n_mc=250)
            endrow = df2[df2["year"] == max(years)].iloc[0].to_dict()
            sens.append(
                {
                    "parameter": key,
                    "level": label,
                    "multiplier": mult,
                    "pressure_mean_2030": float(endrow["pressure_mean"]),
                    "offload_mean_2030": float(endrow["offload_mean"]),
                    "within4_mean_2030": float(endrow["within4_mean"]),
                    "rr_mean_2030": float(endrow["rr_mean"]),
                    "effgap_mean_2030": float(endrow["effgap_mean"]),
                    "effgap_micro_mean_2030": float(endrow.get("effgap_micro_mean", float("nan"))),
                    "effgap_macro_mean_2030": float(endrow.get("effgap_macro_mean", float("nan"))),
                    "nep_mean_2030": float(endrow.get("nep_mean", float("nan"))),
                    "cost_mean_2030": float(endrow.get("cost_mean", float("nan"))),
                }
            )
    sens_df = pd.DataFrame(sens)
    _save_df(sens_df, tables / "sensitivity_oneway.csv")

    # Influence edges (one-way effect size on end-year offload and RR)
    piv = sens_df.pivot_table(index="parameter", columns="level", values="offload_mean_2030")
    edges = []
    for param in piv.index:
        if "high" in piv.columns and "low" in piv.columns:
            diff = float(piv.loc[param, "high"] - piv.loc[param, "low"])
            edges.append({"source": param, "target": "offload_mean_2030", "weight": diff})
    piv2 = sens_df.pivot_table(index="parameter", columns="level", values="rr_mean_2030")
    for param in piv2.index:
        if "high" in piv2.columns and "low" in piv2.columns:
            diff = float(piv2.loc[param, "high"] - piv2.loc[param, "low"])
            edges.append({"source": param, "target": "rr_mean_2030", "weight": diff})
    _save_df(pd.DataFrame(edges), tables / "influence_edges.csv")

    # --- 4) Intervention scenarios (policy levers) ---
    scenarios = {
        "baseline": [],
        "pooled_funding": ["pooled_funding"],
        "ucc_integration": ["ucc_integration"],
        "nep_realism": ["nep_realism"],
        "aged_ndis_capacity": ["aged_ndis_capacity"],
        "cumulative_cap": ["cumulative_cap"],
        # New macro levers (v9)
        "nep_uplift": ["nep_uplift"],
        "input_cost_containment": ["input_cost_containment"],
        # Packages
        "integration_package": ["pooled_funding", "ucc_integration", "aged_ndis_capacity"],
        "macro_alignment_package": ["nep_realism", "nep_uplift", "input_cost_containment"],
        "full_package": ["pooled_funding", "ucc_integration", "aged_ndis_capacity", "nep_realism", "nep_uplift", "input_cost_containment", "cumulative_cap"],
    }

    rows = []
    base_end = traj[traj["year"] == max(years)].iloc[0].to_dict()
    for sname, ints in scenarios.items():
        p_s = base
        for it in ints:
            p_s = apply_intervention_partial(p_s, it, strength=1.0)
        tr_s, _ = run_hybrid(years=years, p=p_s, seed=123, n_mc=400)
        end = tr_s[tr_s["year"] == max(years)].iloc[0].to_dict()
        rows.append(
            {
                "scenario": sname,
                "rr_mean_2030": float(end["rr_mean"]),
                "offload_mean_2030": float(end["offload_mean"]),
                "within4_mean_2030": float(end["within4_mean"]),
                "pressure_mean_2030": float(end["pressure_mean"]),
                "effgap_mean_2030": float(end["effgap_mean"]),
                "delta_rr_2030": float(end["rr_mean"] - base_end["rr_mean"]),
                "delta_offload_2030": float(end["offload_mean"] - base_end["offload_mean"]),
                "delta_within4_2030": float(end["within4_mean"] - base_end["within4_mean"]),
                "delta_pressure_2030": float(end["pressure_mean"] - base_end["pressure_mean"]),
                "delta_effgap_2030": float(end["effgap_mean"] - base_end["effgap_mean"]),
            }
        )

    _save_df(pd.DataFrame(rows).sort_values("scenario"), tables / "intervention_scenarios.csv")


if __name__ == "__main__":
    main()
