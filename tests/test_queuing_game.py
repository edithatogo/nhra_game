import jax
import jax.numpy as jnp
import pytest
from nhra_gt.engine_jax import demand_step_jax, ParamsJax, baseline_state_jax

def test_gp_spillover_mechanistic():
    """Verify that increasing GP costs increases ED demand mechanistically."""
    p_low = ParamsJax(gp_out_of_pocket=0.0) # Bulk billing
    p_high = ParamsJax(gp_out_of_pocket=100.0) # High co-pay
    
    s = baseline_state_jax(2025, p_low)
    strat = jnp.zeros(11)
    noise = jnp.array(0.0)
    
    # Run demand step
    d_low = demand_step_jax(s, p_low, strat, noise)
    d_high = demand_step_jax(s, p_high, strat, noise)
    
    print(f"Demand (Bulk Bill): {d_low:.4f}")
    print(f"Demand (High Co-pay): {d_high:.4f}")
    
    # High GP cost should drive patients to 'free' ED
    assert d_high > d_low
    
def test_wait_time_feedback():
    """Verify that higher ED wait times (via lower capacity) suppresses ED demand."""
    p = ParamsJax(gp_out_of_pocket=2.0) # Very cheap GP to make it competitive
    s_high_cap = baseline_state_jax(2025, p).replace(current_capacity=10.0, target_capacity=10.0)
    s_low_cap = baseline_state_jax(2025, p).replace(current_capacity=0.1, target_capacity=0.1)
    
    strat = jnp.zeros(11)
    noise = jnp.array(0.0)
    
    d_high = demand_step_jax(s_high_cap, p, strat, noise)
    d_low = demand_step_jax(s_low_cap, p, strat, noise)
    
    print(f"Demand (High Capacity): {d_high:.4f}")
    print(f"Demand (Low Capacity): {d_low:.4f}")
    
    # Higher wait times in low capacity ED should suppress demand (Wardrop equilibrium)
    assert d_low < d_high
