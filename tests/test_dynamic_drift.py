from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from nhra_gt.engine import Params, baseline_state, step


def test_dynamic_drift_calculation():
    """Verify that step() uses economic_spine when available."""
    # Create a spine with divergence
    # Year 2025 -> 2026: NEP stays same, WPI grows 10%
    spine = pd.DataFrame(
        {"year": [2025, 2026], "nep_per_nwau": [5000.0, 5000.0], "wpi_health_index": [100.0, 110.0]}
    )

    p = Params(economic_spine=spine)
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

    # Expected gap (Monthly logic)
    # drift_factor = (1 + (1.1 - 1)/12) / (1 + (1.0 - 1)/12) = 1 + 0.1/12
    drift_factor = (1.0 + 0.1 / 12.0) / (1.0 + 0.0 / 12.0)
    mgf = 1.0 / 12.0
    expected_gap = ((1.0 + initial_gap) * drift_factor - 1.0) * (0.93**mgf)

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

    # Expected gap (Monthly logic)
    drift_factor = (1.0 + 0.10 / 12.0) / (1.0 + 0.05 / 12.0)
    mgf = 1.0 / 12.0
    expected_gap = ((1.0 + initial_gap) * drift_factor - 1.0) * (0.93**mgf)

    assert next_s.efficiency_gap == pytest.approx(expected_gap)
