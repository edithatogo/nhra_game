from __future__ import annotations

import numpy as np
from nhra_game_theory.legacy_engine import Params, baseline_state, step


def test_step_covers_else_branches() -> None:
    p = Params()
    s = baseline_state(2025, p)
    # Force strategies into the "else" paths for several multipliers
    strategies = {"DEF": "E", "BARG": "D", "DISC": "F", "GOV": "S", "SHIFT": "S", "COMP": "T"}
    rng = np.random.default_rng(42)
    s2 = step(s, p, strategies, rng)
    # sanity checks
    assert 0.05 <= s2.efficiency_gap <= 0.60
    assert 0.30 <= s2.effective_cth_share <= 0.50
    assert 0.75 <= s2.discharge_delay <= 1.50
