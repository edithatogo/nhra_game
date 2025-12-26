from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist


def nhra_model(years: jnp.ndarray, observed_data: dict[str, jnp.ndarray] | None = None) -> None:
    """NumPyro implementation of the NHRA simulation for Bayesian inference."""

    # --- Priors ---
    cost_shifting_intensity = numpyro.sample("cost_shifting_intensity", dist.Uniform(0.05, 0.80))  # noqa: F841
    fragmentation_index = numpyro.sample("fragmentation_index", dist.Uniform(0.60, 1.50))  # noqa: F841
    discharge_delay_base = numpyro.sample("discharge_delay_base", dist.Uniform(0.60, 1.40))  # noqa: F841
    political_salience = numpyro.sample("political_salience", dist.Uniform(0.05, 0.90))  # noqa: F841

    # Observation noise
    sigma = numpyro.sample("sigma", dist.HalfNormal(0.1))  # noqa: F841

    # --- Simulation Loop (Skeleton) ---
    # Note: Transition logic must be written in pure JAX (no side effects, no mutation)
    # Using jax.lax.scan for the time-series rollout.

    def transition_fn(state: Any, year: Any) -> tuple[Any, Any]:
        # Placeholder for step() logic translated to JAX
        # next_state = jax_step(state, params, year)
        return state, state

    # initial_state = ...
    # _, trajectories = jax.lax.scan(transition_fn, initial_state, years)

    # --- Likelihood ---
    if observed_data is not None:
        # Example: Match 'within4' metric
        # numpyro.sample("obs_within4", dist.Normal(trajectories["within4"], sigma), obs=observed_data["within4"])
        pass


def run_inference(years: Any, data: Any, num_samples: int = 1000, num_warmup: int = 500) -> Any:
    """Runs MCMC to infer parameter posteriors."""
    from numpyro.infer import MCMC, NUTS

    nuts_kernel = NUTS(nhra_model)
    mcmc = MCMC(nuts_kernel, num_samples=num_samples, num_warmup=num_warmup)

    rng_key = jax.random.PRNGKey(42)
    mcmc.run(rng_key, years=years, observed_data=data)

    return mcmc.get_samples()
