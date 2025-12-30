from __future__ import annotations

import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt

from nhra_gt.calibration.differentiable import PARAM_NAMES, calibrate_jax, map_to_params
from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine_jax import baseline_state_jax, run_simulation_jax


def main():
    print("🚀 Starting Differentiable Calibration (Gradient-based)...")

    # 1. Setup Ground Truth
    from nhra_gt.rules import initialize_rules

    p_base = initialize_rules(ParamsJax())
    s_init = baseline_state_jax(p=p_base)

    # True parameters we want to recover
    # Use more distinct values to ensure detectable signal
    true_values = jnp.array([0.80, 1.50, 1.40, 0.10])
    p_true = initialize_rules(map_to_params(true_values, p_base))

    num_steps = 60  # 5 years
    key = jax.random.PRNGKey(42)

    # Generate 'observed' data using true parameters
    # Note: Use a fixed strategy sequence for the 'twin' experiment
    fixed_strats = jnp.zeros((num_steps, 13))
    fixed_strats = fixed_strats.at[:, 1].set(0.5)  # DEF weight
    fixed_strats = fixed_strats.at[:, 2].set(0.5)  # BARG weight
    fixed_strats = fixed_strats.at[:, 3].set(0.5)  # SHIFT weight
    fixed_strats = fixed_strats.at[:, 5].set(0.5)  # AGED weight
    fixed_strats = fixed_strats.at[:, 6].set(0.5)  # NDIS weight

    _, traj_true = run_simulation_jax(s_init, p_true, fixed_strats, key, num_steps)
    target_data = {"within4": traj_true.within4}

    print(f"Target 'within4' mean: {jnp.mean(traj_true.within4):.3f}")

    # 2. Run Calibration
    # Initial guess is slightly offset
    initial_guess_params = initialize_rules(
        p_base.replace(
            cost_shifting_intensity=0.35,
            fragmentation_index=1.0,
            discharge_delay_base=1.0,
            political_salience=0.5,
        )
    )

    print("\nRunning Gradient Descent...")
    recovered_values = calibrate_jax(
        target_data, s_init, initial_guess_params, learning_rate=10.0, max_iter=500
    )

    # 3. Report Results
    print("\n--- Calibration Results ---")
    for i, name in enumerate(PARAM_NAMES):
        print(
            f"{name:25}: True={true_values[i]:.3f}, Recovered={recovered_values[i]:.3f}, Error={abs(recovered_values[i] - true_values[i]):.4f}"
        )

    # 4. Visualization
    p_rec = map_to_params(recovered_values, p_base)
    _, traj_rec = run_simulation_jax(s_init, p_rec, fixed_strats, key, num_steps)

    plt.figure(figsize=(10, 6))
    plt.plot(traj_true.within4, "k-", label="Ground Truth", linewidth=3, alpha=0.6)
    plt.plot(traj_rec.within4, "r--", label="Calibrated Fit", linewidth=2)
    plt.title("Differentiable Calibration: Parameter Recovery (within4)")
    plt.xlabel("Month")
    plt.ylabel("Performance")
    plt.legend()
    plt.grid(True, alpha=0.3)

    out_path = "outputs/validation/differentiable_fit.png"
    plt.savefig(out_path)
    print(f"\nSaved calibration plot to {out_path}")


if __name__ == "__main__":
    main()
