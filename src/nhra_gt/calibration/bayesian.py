"""Bayesian Calibration using NumPyro.

Performs probabilistic inference to estimate model parameters from observed data.
"""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS


def nhra_model(years: jnp.ndarray, observed_data: dict[str, jnp.ndarray] | None = None) -> None:
    """Sample the NHRA priors for the calibration scaffold."""
    # The rollout and likelihood have yet to be wired into this model.
    del years, observed_data
    numpyro.sample("cost_shifting_intensity", dist.Uniform(0.05, 0.80))
    numpyro.sample("fragmentation_index", dist.Uniform(0.60, 1.50))
    numpyro.sample("discharge_delay_base", dist.Uniform(0.60, 1.40))
    numpyro.sample("political_salience", dist.Uniform(0.05, 0.90))
    numpyro.sample("sigma", dist.HalfNormal(0.1))


def run_inference(years: Any, data: Any, num_samples: int = 1000, num_warmup: int = 500) -> Any:
    """Runs MCMC to infer parameter posteriors."""
    nuts_kernel = NUTS(nhra_model)
    mcmc = MCMC(nuts_kernel, num_samples=num_samples, num_warmup=num_warmup)

    rng_key = jax.random.PRNGKey(42)
    mcmc.run(rng_key, years=years, observed_data=data)

    return mcmc.get_samples()
