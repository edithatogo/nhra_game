from __future__ import annotations

import numpy as np

from nhra_gt.domain.stability import analyze_cost_shifting_stability


def test_analyze_cost_shifting_stability():
    """Verify stability data generation."""
    intensities = np.array([0.0, 1.0])
    pressures = np.array([1.0])

    df = analyze_cost_shifting_stability(intensities, pressures)

    assert len(df) == 2
    assert "outcome" in df.columns
    # With csi=0.0, pr=1.0, shift_gain=0.50. coop_gain=0.91. pr_cost=0.65.
    # Payoff I: 1.26. Payoff S: 1.15. -> I (0)
    # With csi=1.0, pr=1.0, shift_gain=1.50.
    # Payoff S: 2.15. -> S (1)

    # Check outcomes
    row_0 = df[df["cost_shifting_intensity"] == 0.0].iloc[0]
    assert row_0["outcome"] == 0

    row_1 = df[df["cost_shifting_intensity"] == 1.0].iloc[0]
    assert row_1["outcome"] == 1
