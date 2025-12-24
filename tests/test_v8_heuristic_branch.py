from __future__ import annotations

import numpy as np
from nhra_game_theory.v8 import Params, baseline_state, decide_strategies


def test_decide_strategies_heuristic_branch_runs() -> None:
    p = Params(use_stage_game_equilibria=False)
    s = baseline_state(2025, p)
    rng = np.random.default_rng(7)
    strat = decide_strategies(s, p, rng)
    # v8 returns a dictionary of stage-game strategies
    assert {"DEF", "BARG", "SHIFT", "DISC", "GOV", "COMP", "SIGNAL"} <= set(strat.keys())
