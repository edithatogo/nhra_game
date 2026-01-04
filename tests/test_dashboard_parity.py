from __future__ import annotations

import numpy as np
from scripts.dashboard import cached_run_model

from nhra_gt.engine import Params, State, baseline_state, decide_strategies, run_hybrid, step


def test_engine_dashboard_parity_logic():
    """
    Verify that the dashboard's cached_run_model produces statistically
    similar mean trajectories to the core engine's run_hybrid.
    """
    years = list(range(2025, 2031))
    p = Params()  # Ensure deterministic params if used

    # Dashboard typically runs 50 MC
    n_mc_dash = 50
    # Engine production run
    n_mc_engine = 1000

    # 1. Run Engine (Production)
    agg_engine, _ = run_hybrid(years, p, seed=42, n_mc=n_mc_engine)

    # 2. Run Dashboard (Lite)
    # The dashboard uses cached_run_model which calls run_hybrid internally
    agg_dash, _ = cached_run_model(p, years, n_mc=n_mc_dash)

    # 3. Compare mean trajectories for key metrics
    metrics = ["pressure_mean", "within4_mean", "rr_mean", "effgap_mean"]

    for metric in metrics:
        e_val = agg_engine.iloc[-1][metric]
        d_val = agg_dash.iloc[-1][metric]

        # We expect Lite mode to be within a reasonable margin of the Full mode
        # 5% margin for stochastic convergence
        diff = abs(e_val - d_val) / (max(1e-9, abs(e_val)))
        print(f"Metric: {metric}, Engine: {e_val:.4f}, Dash: {d_val:.4f}, Diff: {diff:.2%}")

        # Assertion with tolerance for stochastic variation
        assert diff < 0.10, f"Divergence in {metric} exceeds 10% ({diff:.2%})"


def test_step_logic_parity():
    """
    Directly verify that the step function used by the dashboard
    (imported from engine) behaves exactly as expected.
    """
    p = Params()
    s = baseline_state(2025, p)
    rng = np.random.default_rng(42)
    strats = decide_strategies(s, p, rng)

    s_next = step(s, p, strats, rng)

    assert isinstance(s_next, State)
    assert s_next.month == s.month + 1
    assert 0.78 <= s_next.occupancy <= 0.98
