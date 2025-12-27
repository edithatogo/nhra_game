import jax
import jax.numpy as jnp
import pytest
from nhra_gt.engine_jax import run_simulation_jax, ParamsJax, baseline_state_jax

def test_workforce_depletion():
    """Verify that high recruitment intensity depletes the shared workforce pool."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p).replace(workforce_pool=1.0)
    
    # 1. High Intensity Scenario
    num_months = 24
    strat_high = jnp.zeros((num_months, 10)).at[:, 8].set(1.0) # Repurpose COMP as WF_INTENSITY
    key = jax.random.PRNGKey(0)
    
    _, traj_high = run_simulation_jax(s, p, strat_high, key, num_months)
    
    # 2. Low Intensity Scenario
    strat_low = jnp.zeros((num_months, 10)).at[:, 8].set(0.0)
    _, traj_low = run_simulation_jax(s, p, strat_low, key, num_months)
    
    # High intensity should lead to lower workforce pool
    assert traj_high.workforce_pool[-1] < traj_low.workforce_pool[-1]
    
def test_cannibalization_impact():
    """Verify that lower workforce pool increases discharge delay (Access Block)."""
    p = ParamsJax()
    # Scenario 1: Abundant workforce
    s_full = baseline_state_jax(2025, p).replace(workforce_pool=1.5)
    # Scenario 2: Depleted workforce
    s_empty = baseline_state_jax(2025, p).replace(workforce_pool=0.5)
    
    num_months = 12
    strat = jnp.zeros((num_months, 10))
    key = jax.random.PRNGKey(0)
    
    _, traj_full = run_simulation_jax(s_full, p, strat, key, num_months)
    _, traj_empty = run_simulation_jax(s_empty, p, strat, key, num_months)
    
    # Depleted workforce should lead to higher discharge delay
    assert traj_empty.discharge_delay[-1] > traj_full.discharge_delay[-1]
