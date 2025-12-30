import jax
import jax.numpy as jnp

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine_jax import baseline_state_jax, lhn_step_jax


def test_hierarchical_vectorization_smoke():
    """Verify that we can vmap the LHN step over multiple sub-agents."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p)

    n_lhn = 5
    key = jax.random.PRNGKey(42)

    # Inputs for LHNs
    demand = jnp.linspace(0.8, 1.2, n_lhn)
    mgf = 1.0 / 12.0
    offload_noises = jax.random.normal(key, (n_lhn,))
    discharge_target = 0.95  # Tight target from state
    strategies = jnp.zeros(12)

    lhns = jax.tree_util.tree_map(lambda x: x[0], s.jurisdictions.lhn_states)

    # Vectorized LHN step
    results = jax.vmap(
        lambda lhn, d, o: lhn_step_jax(lhn, p, strategies, d, mgf, o, discharge_target, 1.0)
    )(lhns, demand, offload_noises)

    assert results.pressure.shape == (n_lhn,)
    # Verify variance (different noise/keys should lead to different pressures)
    assert jnp.unique(results.pressure).size > 1


def test_state_delegation_impact():
    """Verify that the state's discharge target actually influences LHN outcomes."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p)
    strategies = jnp.zeros(12)
    lhn = jax.tree_util.tree_map(lambda x: x[0, 0], s.jurisdictions.lhn_states)

    # LHN with loose target
    res_loose = lhn_step_jax(lhn, p, strategies, 1.0, 1.0 / 12.0, 0.0, 1.5, 1.0)
    # LHN with tight target
    res_tight = lhn_step_jax(lhn, p, strategies, 1.0, 1.0 / 12.0, 0.0, 0.75, 1.0)

    # Tight target should lead to lower discharge delay (more efficiency)
    assert res_tight.discharge_delay < res_loose.discharge_delay
