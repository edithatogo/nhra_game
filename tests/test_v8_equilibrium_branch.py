from __future__ import annotations

import numpy as np

from nhra_game_theory.legacy_engine import Params, baseline_state, decide_strategies


def test_decide_strategies_equilibrium_branch_runs() -> None:
    p = Params(use_equilibrium_bargaining=True)
    s = baseline_state(2025, p)
    rng = np.random.default_rng(123)
    strat = decide_strategies(s, p, rng)
    assert "BARG" in strat
    assert strat["BARG"] in {"E", "A"}
