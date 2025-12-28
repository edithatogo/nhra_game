import jax.numpy as jnp
import pytest
from nhra_gt.agent_logic import AgentWeights, lhn_utility, state_utility

def test_lhn_utility_ramping_penalty():
    weights = AgentWeights(ramping_penalty=10.0)
    
    # Case 1: No ramping (pressure <= 1.0)
    u_base = lhn_utility(pressure=jnp.array(1.0), revenue=jnp.array(100.0), cost=jnp.array(80.0), is_shifting=False, weights=weights)
    
    # Case 2: Ramping (pressure = 1.2)
    u_high = lhn_utility(pressure=jnp.array(1.2), revenue=jnp.array(100.0), cost=jnp.array(80.0), is_shifting=False, weights=weights)
    
    # High pressure should have significantly lower utility
    assert u_high < u_base
    # Penalty is 10 * (0.2)^2 = 0.4
    assert jnp.isclose(u_base - u_high, 0.4)

def test_state_utility_vfi():
    weights = AgentWeights(vfi_disutility=5.0, kpi_satisfaction=1.0)
    
    # Case 1: No fiscal gap
    u_base = state_utility(fiscal_gap=jnp.array(0.0), lhn_performance=jnp.array(50.0), weights=weights)
    
    # Case 2: Positive fiscal gap
    u_gap = state_utility(fiscal_gap=jnp.array(10.0), lhn_performance=jnp.array(50.0), weights=weights)
    
    assert u_gap < u_base
