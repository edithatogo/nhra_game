"""System Stability and Hysteresis Metrics.

Utilities for calculating phase space area and recovery times.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from nhra_gt.subgames.games import GameParams, cost_shifting_game
from nhra_gt.subgames.nash import all_nash, select_equilibrium


def analyze_cost_shifting_stability(
    intensities: np.ndarray[Any, Any], pressures: np.ndarray[Any, Any], efficiency_gap: float = 0.20
) -> pd.DataFrame:
    """Performs a grid search to map stability regions of the Cost Shifting game."""
    results = []

    for csi in intensities:
        for pr in pressures:
            gp = GameParams(
                pressure=float(pr),
                efficiency_gap=efficiency_gap,
                discharge_delay=1.0,
                political_salience=0.3,
                audit_pressure=0.5,
                cost_shifting_intensity=float(csi),
                political_capital=1.0,
            )

            game = cost_shifting_game(gp)
            eqs = all_nash(game)
            sel = select_equilibrium(
                eqs, rule="payoff_dominant", u_row=game.u_row, u_col=game.u_col
            )

            # Determine effective strategy
            row_idx = int(np.argmax(sel.row))
            col_idx = int(np.argmax(sel.col))
            row_strat = game.row_actions[row_idx]
            col_strat = game.col_actions[col_idx]

            effective_strat = "S" if (row_strat == "S" or col_strat == "S") else "I"

            results.append(
                {
                    "cost_shifting_intensity": csi,
                    "pressure": pr,
                    "outcome": 1 if effective_strat == "S" else 0,
                }
            )

    return pd.DataFrame(results)


def calculate_hysteresis_area(x: np.ndarray, y: np.ndarray) -> float:
    """Calculates the area of the hysteresis loop in phase-space using the Shoelace formula.

    A larger area indicates greater system lag or inertia in responding to demand shocks.
    """
    if len(x) < 3:
        return 0.0
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def calculate_recovery_metrics(modes: list[str]) -> dict[str, Any]:
    """Calculates system resilience metrics based on mode transitions."""
    if not modes:
        return {"recovery_time": 0, "crisis_count": 0, "resilience_index": 1.0}

    recovery_time = sum(1 for m in modes if m != "normal")
    crisis_count = sum(
        1 for i in range(1, len(modes)) if modes[i] == "crisis" and modes[i - 1] != "crisis"
    )
    if modes[0] == "crisis":
        crisis_count += 1

    resilience_index = 1.0 - (recovery_time / len(modes))

    return {
        "recovery_time": recovery_time,
        "crisis_count": crisis_count,
        "resilience_index": resilience_index,
    }
