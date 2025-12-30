import jax
import jax.numpy as jnp

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine_jax import baseline_state_jax, step_jax


def test_auditor_suspicion_logic():
    """Verify that the auditor reacts to gaming signals."""
    p = ParamsJax(audit_pressure=0.5)
    s = baseline_state_jax(2025, p)
    key = jax.random.PRNGKey(42)

    # Baseline strategies (H=0 for coding)
    strat_honest = jnp.zeros(11)

    # 1. Step with honesty
    s_next = step_jax(s, p, strat_honest, key)
    assert s_next.auditor_suspicion <= s.auditor_suspicion + 0.01  # Should not grow much

    # 2. Step with UPCODING (Index 7 = 1)
    strat_gaming = jnp.zeros(11).at[7].set(1.0)

    # Run multiple steps of intense gaming to see suspicion rise
    # We'll override the state to have high coding intensity first
    s_gaming_start = s.replace(coding_intensity=1.5)

    def body(carry_s, _):
        next_s = step_jax(carry_s, p, strat_gaming, key)
        return next_s, next_s.auditor_suspicion

    last_s, suspicion_traj = jax.lax.scan(body, s_gaming_start, jnp.arange(24))

    # Suspicion should have increased significantly
    assert last_s.auditor_suspicion > 0.3
    # Active audit pressure should have increased above the lazy baseline
    # (Since 0.25 was the 'complacent' floor)
    assert last_s.audit_pressure_active > 0.3

    print(f"Suspicion Traj: {suspicion_traj}")
    print(f"Final Pressure: {last_s.audit_pressure_active}")


def test_auditor_decay():
    """Verify suspicion decays when gaming stops."""
    p = ParamsJax()
    # Start with high suspicion
    s = baseline_state_jax(2025, p).replace(auditor_suspicion=0.8)
    key = jax.random.PRNGKey(42)

    strat_honest = jnp.zeros(11)

    s_next = step_jax(s, p, strat_honest, key)
    assert s_next.auditor_suspicion < s.auditor_suspicion
