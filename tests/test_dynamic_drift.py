from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from nhra_game_theory.engine import Params, baseline_state, step


def test_dynamic_drift_calculation():
    """Verify that step() uses economic_spine when available."""
    # Create a spine with divergence
    # Year 2025 -> 2026: NEP stays same, WPI grows 10% (drift_factor should be 1.1)
    spine = pd.DataFrame(
        {"year": [2025, 2026], "nep_per_nwau": [5000.0, 5000.0], "wpi_health_index": [100.0, 110.0]}
    )

    p = Params(economic_spine=spine)
    s = baseline_state(start_year=2025, p=p)

    # Efficiency gap at baseline is derived from metro/regional ratios
    # approx 0.11 by default
    initial_gap = s.efficiency_gap

    # Mock strategies (Default to Realism 'R' which applies 0.93 multiplier after drift)
    strategies = {
        "SIGNAL": "H",
        "DEF": "R",
        "BARG": "A",
        "SHIFT": "I",
        "DISC": "C",
        "GOV": "I",
        "COMP": "T",
    }

    rng = np.random.default_rng(42)
    next_s = step(s, p, strategies, rng)

    # Expected gap: ((1 + initial_gap) * drift_factor - 1) * 0.93
    # drift_factor = (1+0.1)/(1+0.0) = 1.1
    expected_gap = ((1.0 + initial_gap) * 1.1 - 1.0) * 0.93

    assert next_s.efficiency_gap == pytest.approx(expected_gap)


def test_drift_fallback():
    """Verify fallback to constant growth when spine is missing."""
    p = Params(economic_spine=None, input_cost_annual_growth=0.10, nep_annual_growth=0.05)
    s = baseline_state(start_year=2025, p=p)
    initial_gap = s.efficiency_gap

    strategies = {
        "SIGNAL": "H",
        "DEF": "R",
        "BARG": "A",
        "SHIFT": "I",
        "DISC": "C",
        "GOV": "I",
        "COMP": "T",
    }
    rng = np.random.default_rng(42)
    next_s = step(s, p, strategies, rng)

    # drift_factor = 1.10 / 1.05
    drift_factor = 1.10 / 1.05
    expected_gap = ((1.0 + initial_gap) * drift_factor - 1.0) * 0.93

    assert next_s.efficiency_gap == pytest.approx(expected_gap)
