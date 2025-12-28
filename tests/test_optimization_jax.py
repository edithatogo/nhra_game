from __future__ import annotations

import jax
import jax.numpy as jnp
import pytest
from nhra_gt.domain.state import ParamsJax, StateJax, MetricsJax
from nhra_gt.optimization_jax import optimize_policy_jax

def test_policy_optimization():
    # Setup a simple optimization task
    # Minimize cumulative pressure by varying nominal_cth_share_target
    
    p = ParamsJax()
    
    num_months = 12
    sj = StateJax(
        year=2025, month=1, pressure=1.0, occupancy=0.88, offload_min=18.0,
        within4=0.53, effective_cth_share=0.45, efficiency_gap=0.1,
        discharge_delay=1.0, political_capital=1.0, system_mode=0,
        lhn_pressure=jnp.zeros(5), lhn_nwau=jnp.zeros(5),
        agreement_clock=5, workforce_pool=1.0
    )
    
    # Fill in vector fields if needed (not needed for scalar rollout)
    strat = jnp.zeros((num_months, 11))
    key = jax.random.PRNGKey(42)

    def objective(final_s, trajectory):
        # We want to minimize final pressure
        return final_s.pressure

    # Optimize nominal_cth_share_target
    # Increasing Cth share should generally reduce pressure in our model
    # (via Agreement boosting political capital and reducing efficiency gap)
    res = optimize_policy_jax(
        sj, p, strat, key, num_months, 
        "nominal_cth_share_target", 
        (0.35, 0.55), 
        objective
    )
    
    assert res["success"]
    assert 0.35 <= res["optimized_value"] <= 0.55
    print(f"Optimized Cth Share: {res['optimized_value']:.4f}")
