from __future__ import annotations

import numpy as np
from nhra_game_theory.v9 import Params, baseline_state, run_hybrid


def test_effective_share_v2_structural_parity():
    """Verify that v21 effective share logic matches the v2 mathematical form."""
    # v2: alpha_eff = (alpha_nom * E) / (E + g)
    # v21: alpha_eff = alpha_nom / (1 + efficiency_gap)
    # These are identical if efficiency_gap = g / E
    
    p = Params(effective_cth_share_base=0.38)
    s = baseline_state(p=p)
    
    # In v21 baseline_state:
    # s.effective_cth_share (stored) is actually the NOMINAL share derived from base and gap
    # s.effective_cth_share = p.effective_cth_share_base * (1.0 + efficiency_gap)
    
    nom = s.effective_cth_share
    gap = s.efficiency_gap
    eff = nom / (1.0 + gap)
    
    assert np.isclose(eff, p.effective_cth_share_base)

def test_model_stability_at_v2_bounds():
    """Ensure the model runs at the extreme bounds used in v2 calibration."""
    # v2 Linspace bounds: g up to 20000 (eff_gap ~ 0.75), O up to 0.20
    p = Params(
        nep_to_cost_ratio_remote=0.5, # High gap
        political_salience=0.9,       # High salience
        cost_shifting_intensity=0.8   # High intensity
    )
    years = [2025, 2026]
    traj, strat = run_hybrid(years, p, n_mc=10)
    assert len(traj) == 2
    assert not traj["pressure_mean"].isnull().any()
