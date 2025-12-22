from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from nhra_game_theory.v9 import Params, State, baseline_state, step
from nhra_game_theory.subgames.nash import all_nash, select_equilibrium
from nhra_game_theory.subgames.games import (
    GameParams,
    definition_game,
    bargaining_game,
    cost_shifting_game,
    discharge_coordination_game,
    governance_integration_game,
    compliance_game,
)

class DetermRNG:
    """Deterministic RNG stand-in for fixed-point runs (always returns zero noise)."""
    def normal(self, loc: float = 0.0, scale: float = 1.0, size=None):
        if size is None:
            return 0.0
        import numpy as np
        return np.zeros(size)

    def random(self, size=None):
        if size is None:
            return 0.5
        import numpy as np
        return 0.5 * np.ones(size)



def deterministic_strategies(s: State, p: Params) -> dict[str, str]:
    """Deterministic strategy selection using all Nash equilibria + a selection rule.

    This avoids Monte Carlo sampling so we can compute a fixed-point / steady-state trajectory.
    """
    gp = GameParams(
        pressure=float(s.pressure),
        efficiency_gap=float(s.efficiency_gap),
        discharge_delay=float(s.discharge_delay),
        political_salience=float(p.political_salience),
        audit_pressure=float(p.audit_pressure),
    )

    def _pick(game):
        eqs = all_nash(game)
        sel = select_equilibrium(eqs, rule=p.equilibrium_selection_rule, u_row=game.u_row, u_col=game.u_col)
        a = game.row_actions[int(sel.row.argmax())]
        return a

    return {
        # SIGNAL isn't used in transitions in v9; keep a stable value for bookkeeping.
        "SIGNAL": "L",
        "DEF": _pick(definition_game(gp)),
        "BARG": _pick(bargaining_game(gp)),
        "SHIFT": _pick(cost_shifting_game(gp)),
        "DISC": _pick(discharge_coordination_game(gp)),
        "GOV": _pick(governance_integration_game(gp)),
        "COMP": _pick(compliance_game(gp)),
    }


def fixed_point_trajectory(p: Params, start_year: int = 2025, years: int = 20, tol: float = 1e-6) -> pd.DataFrame:
    """Iterate the deterministic system and detect convergence."""
    # Remove stochasticity
    p = replace(p, noise_sd=0.0, use_stage_game_equilibria=True)

    s = baseline_state(start_year=start_year, p=p)
    rows = []
    for t in range(years):
        strat = deterministic_strategies(s, p)
        s_next = step(s, p, strat, rng=DetermRNG())  # rng unused inside step
        delta = abs(s_next.pressure - s.pressure) + abs(s_next.occupancy - s.occupancy) + abs(s_next.discharge_delay - s.discharge_delay)
        rows.append(
            {
                "iter": t,
                "year": int(s.year),
                "pressure": float(s.pressure),
                "occupancy": float(s.occupancy),
                "offload_min": float(s.offload_min),
                "within4": float(s.within4),
                "efficiency_gap": float(s.efficiency_gap),
                "cth_share_nominal": float(s.effective_cth_share),
                "cth_share_effective": float(s.effective_cth_share / (1.0 + s.efficiency_gap)),
                "discharge_delay": float(s.discharge_delay),
                "delta": float(delta),
                **{f"strat_{k}": v for k, v in strat.items()},
            }
        )
        s = s_next
        if delta < tol:
            break
    return pd.DataFrame(rows)


def main() -> None:
    out = Path("outputs/v19")
    tables = out / "tables"
    plots = out / "plots"
    tables.mkdir(parents=True, exist_ok=True)
    plots.mkdir(parents=True, exist_ok=True)

    p = Params()
    df = fixed_point_trajectory(p, start_year=2025, years=40)
    df.to_csv(tables / "fixed_point_trajectory.csv", index=False)

    plt.figure()
    plt.plot(df["iter"], df["delta"])
    plt.yscale("log")
    plt.title("Deterministic fixed-point convergence (log scale)")
    plt.xlabel("Iteration")
    plt.ylabel("Δ(state)")
    plt.tight_layout()
    plt.savefig(plots / "fixed_point_convergence.png", dpi=220)
    plt.close()

    # Plot steady-state levels (last few iterations)
    tail = df.tail(10)
    plt.figure()
    plt.plot(tail["iter"], tail["pressure"], marker="o")
    plt.title("Pressure near steady-state")
    plt.xlabel("Iteration")
    plt.ylabel("Pressure")
    plt.tight_layout()
    plt.savefig(plots / "fixed_point_pressure_tail.png", dpi=220)
    plt.close()


if __name__ == "__main__":
    main()