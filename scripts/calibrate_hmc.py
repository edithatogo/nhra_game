from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
import polars as pl

# Add src
sys.path.append("src")

from nhra_gt.domain.state import ParamsJax, StateJax, MetricsJax
from nhra_gt.engine_jax import run_simulation_jax
from nhra_gt.solvers_jax import qre_solver_jax

def model(historical_years, observed_within4, observed_occupancy):
    # 1. Priors
    demand_base = numpyro.sample("demand_base", dist.Normal(1.0, 0.1))
    discharge_delay_base = numpyro.sample("discharge_delay_base", dist.Normal(1.0, 0.1))
    capacity_lag = numpyro.sample("capacity_lag", dist.Uniform(0.05, 0.3))
    
    # Pack into ParamsJax
    p = ParamsJax(
        demand_base=demand_base,
        discharge_delay_base=discharge_delay_base,
        capacity_lag=capacity_lag
    )
    
    # 2. Initial State (2011)
    # We'll use a simplified baseline start for 2011
    init_state = StateJax(
        year=int(historical_years[0]),
        month=1,
        pressure=1.0,
        occupancy=0.85, # Starting point from data
        offload_min=18.0,
        within4=0.70,   # Starting point from data
        effective_cth_share=0.45,
        efficiency_gap=0.1,
        discharge_delay=1.0,
        political_capital=1.0,
        system_mode=0
    )
    
    # 3. Rollout
    num_steps = len(historical_years) * 12
    # Assume default strategies for calibration
    strat = jnp.zeros((num_steps, 10))
    
    # Use a fixed key for the simulation inside the model to ensure differentiability
    # though HMC handles some stochasticity if we were using a different sampler.
    # For HMC we want the function to be as deterministic as possible wrt the parameters.
    sim_key = jax.random.PRNGKey(0)
    
    _, trajectory = run_simulation_jax(init_state, p, strat, sim_key, num_steps)
    
    # 4. Aggregation (Monthly to Yearly)
    # trajectory is shape (num_steps,)
    # We want yearly means to compare with historical data
    yearly_within4 = trajectory.within4.reshape(-1, 12).mean(axis=1)
    yearly_occupancy = trajectory.occupancy.reshape(-1, 12).mean(axis=1)
    
    # 5. Likelihood
    sigma = numpyro.sample("sigma", dist.Exponential(10.0))
    numpyro.observe("obs_within4", dist.Normal(yearly_within4, sigma), obs=observed_within4)
    numpyro.observe("obs_occupancy", dist.Normal(yearly_occupancy, sigma), obs=observed_occupancy)

def main():
    parser = argparse.ArgumentParser(description="NumPyro HMC Calibration")
    parser.add_argument("--samples", type=int, default=500)
    parser.add_argument("--warmup", type=int, default=200)
    parser.add_argument("--chains", type=int, default=1)
    args = parser.parse_args()

    # Load Data
    hist_path = Path("data/calibration/historical_normalized.csv")
    if not hist_path.exists():
        print("Historical data not found. Run preprocessing first.")
        return
        
    df = pl.read_csv(hist_path)
    years = df["year"].to_numpy()
    within4 = df["within4"].to_numpy()
    occupancy = df["occupancy"].to_numpy()

    # Setup MCMC
    nuts_kernel = NUTS(model)
    mcmc = MCMC(nuts_kernel, num_samples=args.samples, num_warmup=args.warmup, num_chains=args.chains)
    
    print(f"Starting HMC Calibration (Samples={args.samples}, Warmup={args.warmup})...")
    mcmc.run(jax.random.PRNGKey(42), years, within4, occupancy)
    
    mcmc.print_summary()
    
    # Save Results
    out_dir = Path("outputs/calibration")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save posterior samples
    samples = mcmc.get_samples()
    # Convert to serializable format
    serializable_samples = {k: np.array(v).tolist() for k, v in samples.items()}
    with open(out_dir / "posterior_samples.json", "w") as f:
        import json
        json.dump(serializable_samples, f)
        
    print(f"Results saved to {out_dir}")

if __name__ == "__main__":
    # Enable XLA caching
    cache_dir = Path("~/.cache/jax_cache").expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["JAX_COMPILATION_CACHE_DIR"] = str(cache_dir)
    # config.update("jax_compilation_cache_dir", str(cache_dir)) # Optional alternative
    
    main()
