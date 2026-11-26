"""Tests for calibration constraints."""

from __future__ import annotations

import numpy as np

from nhra_gt.engine import Params, baseline_state, run_hybrid

_EXPECTED_YEARS = 2


def test_effective_share_v2_structural_parity():
    """Verify that current effective share logic matches the legacy mathematical form."""
    # The previous model used the nominal share scaled by effective costs.
    # The change under test applies the efficiency gap to the base share.
    # These are identical if efficiency_gap = g / E

    p = Params(effective_cth_share_base=0.38)
    s = baseline_state(p=p)

    # In baseline_state:
    # s.effective_cth_share (stored) is actually the NOMINAL share derived from base and gap
    # The engine multiplies the base share by one plus the gap.

    nom = s.effective_cth_share
    gap = s.efficiency_gap
    eff = nom / (1.0 + gap)

    assert np.isclose(eff, p.effective_cth_share_base)


def test_model_stability_at_v2_bounds():
    """Ensure the model runs at the extreme bounds used in legacy calibration."""
    # Legacy Linspace bounds: g up to 20000 (eff_gap ~ 0.75), O up to 0.20
    p = Params(
        nep_to_cost_ratio_remote=0.5,  # High gap
        political_salience=0.9,  # High salience
        cost_shifting_intensity=0.8,  # High intensity
    )
    years = [2025, 2026]
    traj, _strat = run_hybrid(years, p, n_mc=10)
    assert len(traj) == _EXPECTED_YEARS
    assert not traj["pressure_mean"].isnull().any()
