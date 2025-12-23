from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nhra_game_theory.sensitivity import (
    evaluate_parallel,
    export_sensitivity_indices,
    generate_sensitivity_summary,
    get_salib_problem,
    plot_morris_tornado,
    plot_sobol_heatmap,
    plot_sobol_indices,
    run_morris_analysis,
    run_sobol_analysis,
)
from nhra_game_theory.v8 import Params, run_hybrid, summarise_outcome


def model_wrapper(param_values: np.ndarray, names: list[str], years: list[int]) -> float:
    """Wraps the hybrid model for SALib evaluation.
    
    Returns a single scalar outcome (e.g., pressure_2030).
    """
    # Create Params object
    p_dict = {name: val for name, val in zip(names, param_values, strict=False)}
    p = replace(Params(), **p_dict)
    
    # Run simulation
    # Using a fixed seed for the internal MC logic to ensure stability per parameter set
    traj, _ = run_hybrid(years, p, seed=42, n_mc=50)
    
    # Extract summary
    summary = summarise_outcome(traj)
    return summary["pressure_2030"]

def model_func_for_salib(param_values: np.ndarray) -> float:
    """Global wrapper for multiprocessing pickling."""
    # Note: problem_names and years must be defined at the module level or passed
    # For now, we'll use a hacky global-like access or closure if not using multiprocessing
    # But since we use ProcessPoolExecutor, we need a clean top-level function.
    return model_wrapper(param_values, GSA_PARAM_NAMES, GSA_YEARS)

# Globals for multiprocessing pickling
GSA_PARAM_NAMES = [
    "rurality_weight",
    "cost_shifting_intensity",
    "fragmentation_index",
    "discharge_delay_base",
    "admin_burden_weight",
    "political_salience"
]
GSA_YEARS = list(range(2025, 2031))

def mock_func(x):
    return float(np.sum(x))

def main() -> None:
    parser = argparse.ArgumentParser(description="Global Sensitivity Analysis Suite")
    parser.add_argument("--method", type=str, choices=["morris", "sobol", "mock"], default="morris")
    parser.add_argument("--samples", type=int, default=10, help="N samples (or trajectories for Morris)")
    parser.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--output", type=Path, default=Path("data/gsa_v21/raw_results.csv"))
    
    args = parser.parse_args()
    
    # Ensure output dir exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    problem = get_salib_problem(GSA_PARAM_NAMES)
    
    if args.method == "mock":
        print(f"Running mock parallelism test with {args.procs} processes...")
        param_values = np.random.rand(args.samples, len(GSA_PARAM_NAMES))
        results = evaluate_parallel(mock_func, param_values, n_procs=args.procs)
        print(f"Collected {len(results)} mock results.")
        return

    if args.method == "morris":
        print(f"Running Morris Analysis (N={args.samples}, Procs={args.procs})...")
        df = run_morris_analysis(problem, model_func_for_salib, n_trajectories=args.samples, n_procs=args.procs)
        df.to_csv(args.output)
        
        # Generate plot
        plot_path = args.output.parent / "morris_tornado"
        plot_morris_tornado(df, plot_path)
        
        print(f"Morris results saved to {args.output}")
        print(f"Morris plot saved to {plot_path}.png/.svg/.pdf")
        print("\nTop influential parameters (mu_star):")
        print(df.head(10))
        return

    if args.method == "sobol":
        print(f"Running Sobol Analysis (N={args.samples}, Procs={args.procs})...")
        # Ensure N is power of 2 for Sobol
        if not (args.samples > 0 and (args.samples & (args.samples - 1)) == 0):
            print("Warning: Sobol N should be a power of 2. Results may be sub-optimal.")
            
        si = run_sobol_analysis(problem, model_func_for_salib, n_samples=args.samples, n_procs=args.procs)
        
        # Export indices
        export_sensitivity_indices(si, args.output)
        
        # Generate plots
        plot_sobol_indices(si, args.output.parent / "sobol_indices")
        plot_sobol_heatmap(si, args.output.parent / "sobol_heatmap")
        
        print(f"Sobol results saved to {args.output}")
        print(f"Sobol plots saved to {args.output.parent}/sobol_*.png/.svg/.pdf")
        
        # Generate summary (requires both to exist for best result)
        summary_path = args.output.parent / "sensitivity_summary.md"
        generate_sensitivity_summary(
            args.output.parent / "morris_results.csv",
            args.output.parent / "sobol_results.csv",
            summary_path
        )
        print(f"Summary report generated: {summary_path}")
        return

    print(f"Method {args.method} sampling not yet implemented.")

if __name__ == "__main__":
    main()
