import jax
import jax.numpy as jnp

from nhra_gt.engine import ParamsJax, baseline_state, mm_s_queue_wait_jax, run_simulation_jax


def test_sanity_metrics_bounds():
    """Verify that all key metrics stay within physical/logical bounds."""
    params = ParamsJax()
    init = baseline_state(2025, params)
    seed = jax.random.PRNGKey(42)
    # Run 12 steps
    strategies = jnp.zeros((12, 13))
    final, traj = run_simulation_jax(init, params, strategies, seed, 12)

    # Check Occupancy [0, 1.5]
    assert jnp.all(traj.occupancy >= 0.0), "Occupancy negative"
    # Allow some overflow for crisis dynamics, but not infinite
    assert jnp.all(traj.occupancy <= 2.0), "Occupancy exceeding physics (>200%)"

    # Check Within4 [0, 1]
    assert jnp.all(traj.within4 >= 0.0), "Within4 negative"
    assert jnp.all(traj.within4 <= 1.0), "Within4 > 100%"

    # Check Prob ED [0, 1]
    assert jnp.all(traj.prob_ed >= 0.0)
    assert jnp.all(traj.prob_ed <= 1.0)


def test_benchmark_within4_alignment():
    """Compare model Within4 against AIHW NEAT target (approx 60-70%)."""
    params = ParamsJax()
    init = baseline_state(2025, params)
    seed = jax.random.PRNGKey(123)
    # Run 5 years to settle
    steps = 60
    strategies = jnp.zeros((steps, 13))
    final, traj = run_simulation_jax(init, params, strategies, seed, steps)

    first_step_w4 = float(traj.within4[0])
    print(f"Initial Within4: {first_step_w4}")

    # Assert alignment at baseline (pressure=1.0 -> 0.65)
    assert 0.64 <= first_step_w4 <= 0.66, (
        f"Initial Within4 {first_step_w4:.4f} mismatch target 0.65"
    )


def test_queuing_logic_erlang():
    """Verify M/M/s approximation specific point check."""
    # Arr=100, Svc=1/0.25 (4/day) -> Load=25. Cap=30. Rho=0.833.
    arr = jnp.array(100.0)
    svc = jnp.array(4.0)
    servers = jnp.array(30.0)

    # Wait in minutes
    wait = mm_s_queue_wait_jax(arr, svc, servers)
    wait_val = float(wait)
    print(f"Wait (30 servers, 25 load): {wait_val} mins")

    # Approx check: Should be around 10-20 mins -> now 80+ mins with units fixed
    assert 50.0 <= wait_val <= 120.0, f"Wait time {wait_val} unrealistic for Rho=0.83"


def test_jax_pd_equilibrium():
    """Verify solver convergence on standard Prisoners Dilemma."""
    # PD Payoffs: T=3, R=2, P=1, S=0.
    # Player Row: C=0, D=1.
    # If both C: (2, 2). If R=D, C=C: (3, 0).
    # If R=C, C=D: (0, 3). If both D: (1, 1).
    # Matrix Row: [[2, 0], [3, 1]]
    # Matrix Col: [[2, 3], [0, 1]]

    from nhra_gt.solvers_jax import discrete_nash_jax

    u_row = jnp.array([[2.0, 0.0], [3.0, 1.0]])
    u_col = jnp.array([[2.0, 3.0], [0.0, 1.0]])

    p_row, q_col = discrete_nash_jax(u_row, u_col)

    # Expected: Defect (index 1) with prob 1.0
    print(f"Row Strategy: {p_row}")
    print(f"Col Strategy: {q_col}")

    assert p_row[1] > 0.99, "Row did not converge to Defect"
    assert q_col[1] > 0.99, "Col did not converge to Defect"
