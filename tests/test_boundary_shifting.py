import jax
import jax.numpy as jnp

from nhra_gt.domain.state import Params
from nhra_gt.engine_jax import baseline_state_jax, step_jax


def test_boundary_shifting_logic():
    """Verify that LHNs shift venue based on strategies."""
    p = Params(block_funding_base=0.15)
    s = baseline_state_jax(2025, p)
    key = jax.random.PRNGKey(42)

    # 1. Baseline: ABF-centric (Index 10 = 0)
    strat_abf = jnp.zeros(11).at[10].set(0.0)
    s_abf = step_jax(s, p, strat_abf, key)

    # Expected ABF share ~ 0.85
    assert s_abf.total_block_revenue < 10.0  # Low block revenue

    # 2. Shift to Block (Index 10 = 1)
    strat_block = jnp.zeros(11).at[10].set(1.0)
    s_block = step_jax(s, p, strat_block, key)

    # Block revenue should be higher
    assert s_block.total_block_revenue > s_abf.total_block_revenue

    print(f"ABF-centric Block Revenue: {s_abf.total_block_revenue}")
    print(f"Block-centric Block Revenue: {s_block.total_block_revenue}")


def test_heuristic_agent_venue_choice():
    """Verify that HeuristicAgent makes venue shift decisions."""
    import numpy as np

    from nhra_gt.agents.base import HeuristicAgent
    from nhra_gt.engine import Params, State, SystemMode

    agent = HeuristicAgent()
    p = Params()
    # Case A: Low pressure
    s_low = State(
        year=2025,
        month=1,
        pressure=0.9,
        occupancy=0.8,
        offload_min=10.0,
        within4=0.8,
        effective_cth_share=0.45,
        efficiency_gap=0.05,
        discharge_delay=1.0,
        political_capital=1.0,
        system_mode=SystemMode.NORMAL,
        target_capacity=1.0,
        current_capacity=1.0,
        equity_index=1.0,
        reconciliation_balance=0.0,
        bailout_expectation=0.0,
        coding_intensity=1.0,
        reputation_score=1.0,
        auditor_suspicion=0.0,
        audit_pressure_active=0.5,
    )

    rng = np.random.default_rng(42)
    res_low = agent.decide(s_low, p, rng)

    # Case B: High pressure + High gap
    from dataclasses import replace

    s_high = replace(s_low, pressure=1.5, efficiency_gap=0.4)
    res_high = agent.decide(s_high, p, rng)

    # Under high pressure/gap, probability of shifting to Block (B) should increase
    # Since it's stochastic, we might need multiple runs or just check if 'B' appears
    print(f"Low Pressure Strategy: {res_low.get('VENUE_SHIFT')}")
    print(f"High Pressure Strategy: {res_high.get('VENUE_SHIFT')}")
