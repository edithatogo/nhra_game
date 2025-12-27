import jax
import jax.numpy as jnp
import pytest
from nhra_gt.engine_jax import step_jax, lhn_step_jax, ParamsJax, baseline_state_jax
from nhra_gt.domain.state import StateJax

def test_hierarchical_vectorization_smoke():
    """Verify that we can vmap the LHN step over multiple sub-agents."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p)
    
    n_lhn = 5
    key = jax.random.PRNGKey(42)
    keys = jax.random.split(key, n_lhn)
    
    # Inputs for LHNs
    demand = jnp.linspace(0.8, 1.2, n_lhn)
    mgf = 1.0/12.0
    offload_noises = jax.random.normal(key, (n_lhn,))
    discharge_target = 0.95 # Tight target from state
    strategies = jnp.zeros(10)
    
    # Vectorized LHN step
    vmap_lhn_step = jax.vmap(lambda k, d, o: lhn_step_jax(
        s, p, strategies, d, mgf, o, jnp.array(discharge_target), jnp.array(1.0)
    ))
    
    results = vmap_lhn_step(keys, demand, offload_noises)
    
    # results[5] is pidx (pressure index)
    pidx_results = results[5]
    assert pidx_results.shape == (n_lhn,)
    # Verify variance (different noise/keys should lead to different pressures)
    assert jnp.unique(pidx_results).size > 1

def test_state_delegation_impact():
    """Verify that the state's discharge target actually influences LHN outcomes."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p)
    strategies = jnp.zeros(10)
    key = jax.random.PRNGKey(0)
    
    # LHN with loose target
    res_loose = lhn_step_jax(s, p, strategies, jnp.array(1.0), 1.0/12.0, jnp.array(0.0), jnp.array(1.5), jnp.array(1.0))
    # LHN with tight target
    res_tight = lhn_step_jax(s, p, strategies, jnp.array(1.0), 1.0/12.0, jnp.array(0.0), jnp.array(0.75), jnp.array(1.0))
    
    # Tight target should lead to lower discharge delay (more efficiency)
    assert res_tight[0] < res_loose[0]
