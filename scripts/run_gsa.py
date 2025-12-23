from __future__ import annotations
import argparse
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nhra_game_theory.v8 import Params, run_hybrid, summarise_outcome
from nhra_game_theory.sensitivity import get_salib_problem, evaluate_parallel

def model_wrapper(param_values: np.ndarray, names: list[str], years: list[int]) -> float:
    """Wraps the hybrid model for SALib evaluation.
    
    Returns a single scalar outcome (e.g., pressure_2030).
    """
    # Create Params object
    p_dict = {name: val for name, val in zip(names, param_values)}
    p = replace(Params(), **p_dict)
    
    # Run simulation
    # Using a fixed seed for the internal MC logic to ensure stability per parameter set
    traj, _ = run_hybrid(years, p, seed=42, n_mc=100)
    
    # Extract summary
    summary = summarise_outcome(traj)
    return summary["pressure_2030"]

def mock_func(x):
    return float(np.sum(x))

def main() -> None:
    parser = argparse.ArgumentParser(description="Global Sensitivity Analysis Suite")
    parser.add_argument("--method", type=str, choices=["morris", "sobol", "mock"], default="morris")
    parser.add_argument("--samples", type=int, default=10, help="N samples (or trajectories for Morris)")
    parser.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--output", type=Path, default=Path("data/gsa_v21/raw_results.csv"))
    
    args = parser.parse_args()
    
    # Parameters to analyze
    target_params = [
        "rurality_weight",
        "cost_shifting_intensity",
        "fragmentation_index",
        "discharge_delay_base",
        "admin_burden_weight",
        "political_salience"
    ]
    
    problem = get_salib_problem(target_params)
    years = list(range(2025, 2031))
    
    if args.method == "mock":
        print(f"Running mock parallelism test with {args.procs} processes...")
        param_values = np.random.rand(args.samples, len(target_params))
        
        results = evaluate_parallel(mock_func, param_values, n_procs=args.procs)
        print(f"Collected {len(results)} mock results.")
        return

    # TODO: Phase 2/3 will add actual SALib sampling and analysis
    print(f"Method {args.method} sampling not yet implemented. Task 2 complete.")

if __name__ == "__main__":
    main()
