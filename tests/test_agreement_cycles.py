import jax
import jax.numpy as jnp

from nhra_gt.engine_jax import ParamsJax, baseline_state_jax, run_simulation_jax


def test_agreement_clock_reset():
    """Verify that the agreement clock resets after its cycle."""
    p = ParamsJax()
    s = baseline_state_jax(2025, p).replace(agreement_clock=5)

    # Run for 10 years (120 months)
    num_months = 120
    strat = jnp.zeros((num_months, 11))
    key = jax.random.PRNGKey(0)

    final_s, trajectory = run_simulation_jax(s, p, strat, key, num_months)

    # After 1 year (12 months), clock should be 4
    assert trajectory.agreement_clock[11] == 4
    # With a 5->4->3->2->1->0->5 cycle, it resets at month 72 (End of Year 6)
    assert trajectory.agreement_clock[71] == 5


def test_renegotiation_leverage():
    """Verify that high pressure leads to higher funding share in new agreement."""
    p = ParamsJax()

    # Run for 12 months, start at end of cycle (clock=0)
    # Scenario 1: Low pressure (low occupancy)
    s_low = baseline_state_jax(2025, p).replace(pressure=0.8, occupancy=0.80, agreement_clock=0)
    # Scenario 2: High pressure (high occupancy)
    s_high = baseline_state_jax(2025, p).replace(pressure=1.6, occupancy=0.98, agreement_clock=0)

    num_months = 12
    # Use BARG=A (index 2) to avoid Defer drift, and SHIFT=I (index 3) to minimize demand noise
    strat = jnp.zeros((num_months, 11)).at[:, 2].set(1.0)
    key = jax.random.PRNGKey(42)

    _, traj_low = run_simulation_jax(s_low, p, strat, key, num_months)
    _, traj_high = run_simulation_jax(s_high, p, strat, key, num_months)

    print(f"Low Pressure: {s_low.pressure:.2f}, High Pressure: {s_high.pressure:.2f}")
    print(f"Shares Low: {traj_low.effective_cth_share}")
    print(f"Shares High: {traj_high.effective_cth_share}")

    # At month 12, renegotiation happens.
    assert traj_high.effective_cth_share[11] > traj_low.effective_cth_share[11]
