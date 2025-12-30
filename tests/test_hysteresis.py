from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from nhra_gt.domain.stability import calculate_hysteresis_area, calculate_recovery_metrics
from nhra_gt.engine import summarise_outcome


def test_hysteresis_area_simple():
    # Square loop
    x = np.array([0, 1, 1, 0])
    y = np.array([0, 0, 1, 1])
    # Area should be 1.0
    assert calculate_hysteresis_area(x, y) == pytest.approx(1.0)


def test_recovery_metrics():
    modes = ["normal", "stress", "crisis", "crisis", "recovery", "normal"]
    metrics = calculate_recovery_metrics(modes)

    assert metrics["recovery_time"] == 4  # stress, crisis, crisis, recovery
    assert metrics["crisis_count"] == 1
    assert metrics["resilience_index"] == pytest.approx(1.0 - 4 / 6)


def test_summarise_outcome_integration():
    data = {
        "year": [2025, 2026, 2027],
        "pressure_mean": [1.0, 1.2, 1.1],
        "occupancy_mean": [0.88, 0.95, 0.90],
        "within4_mean": [0.53, 0.40, 0.50],
        "offload_mean": [18.0, 30.0, 20.0],
        "rr_mean": [1.0, 1.5, 1.1],
        "cth_nominal_mean": [0.45, 0.45, 0.45],
        "cth_effective_mean": [0.38, 0.35, 0.37],
        "cumulative_pressure_mean": [1.0, 2.2, 3.3],
        "index_gap_mean": [0.05, 0.06, 0.05],
        "cap_gap_mean": [0.01, 0.02, 0.01],
        "audit_gap_mean": [0.01, 0.01, 0.01],
        "adjustment_costs_mean": [0.0, 0.1, 0.05],
        "system_mode": ["normal", "stress", "recovery"],
    }
    df = pd.DataFrame(data)
    summary = summarise_outcome(df)

    assert "hysteresis_area" in summary
    assert "recovery_time" in summary
    assert "resilience_index" in summary
    assert summary["recovery_time"] == 2.0
