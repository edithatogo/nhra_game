from __future__ import annotations

import numpy as np

from nhra_game_theory.v9 import Params, baseline_state, step


def test_v9_macro_drift_widens_when_costs_outpace_nep() -> None:
    p = Params(
        nep_annual_growth=0.02, input_cost_annual_growth=0.05, macro_drift_weight=1.0, noise_sd=0.0
    )
    s0 = baseline_state(start_year=2025, p=p)

    # Force a neutral strategy profile (no major reforms); only macro drift should matter
    strategies = {"BARG": "A", "SHIFT": "S", "DISC": "F", "GOV": "S", "COMP": "H", "DEF": "E"}

    rng = np.random.default_rng(1)
    s1 = step(s0, p, strategies, rng)
    s2 = step(s1, p, strategies, rng)

    macro0 = max(0.0, s0.efficiency_gap - s0.efficiency_gap_micro)
    macro2 = max(0.0, s2.efficiency_gap - s2.efficiency_gap_micro)

    assert s2.nep_per_nwau > s0.nep_per_nwau
    assert s2.input_cost_index > s0.input_cost_index
    assert macro2 > macro0


def test_v9_macro_drift_can_be_disabled() -> None:
    p = Params(
        nep_annual_growth=0.02, input_cost_annual_growth=0.08, macro_drift_weight=0.0, noise_sd=0.0
    )
    s0 = baseline_state(start_year=2025, p=p)
    strategies = {"BARG": "A", "SHIFT": "S", "DISC": "F", "GOV": "S", "COMP": "H", "DEF": "E"}
    rng = np.random.default_rng(2)
    s2 = step(step(s0, p, strategies, rng), p, strategies, rng)

    macro2 = max(0.0, s2.efficiency_gap - s2.efficiency_gap_micro)
    assert macro2 == 0.0
