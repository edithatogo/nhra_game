from __future__ import annotations
from typing import List, Dict, Optional, Any, Callable
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from SALib.sample import morris as morris_sampler
from SALib.analyze import morris as morris_analyzer
from SALib.sample import saltelli as sobol_sampler
from SALib.analyze import sobol as sobol_analyzer
from nhra_game_theory.v8 import Params

def plot_morris_tornado(df: pd.DataFrame, output_path: Path) -> None:
    """Generates a Morris Tornado plot (mu_star ranking)."""
    # Filter non-zero influence if needed, but here we show all
    df = df.sort_values("mu_star", ascending=True)
    
    plt.figure(figsize=(10, 6))
    plt.barh(df.index, df["mu_star"], xerr=df["mu_star_conf"], color="skyblue", capsize=5)
    plt.xlabel("mu_star (Absolute mean elementary effect)")
    plt.ylabel("Parameter")
    plt.title("Morris Screening: Parameter Influence")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    # Save in multiple formats as per spec
    plt.savefig(output_path.with_suffix(".png"), dpi=300)
    plt.savefig(output_path.with_suffix(".svg"))
    plt.savefig(output_path.with_suffix(".pdf"))
    plt.close()

def get_salib_problem(
    param_names: List[str], 
    bounds_override: Optional[Dict[str, List[float]]] = None,
    default_variation: float = 0.20
) -> Dict[str, Any]:
    """Generates a SALib-compatible problem dictionary from the Params dataclass.
    
    Args:
        param_names: List of parameter names to include in the GSA.
        bounds_override: Optional dictionary mapping parameter names to [min, max] bounds.
        default_variation: If no override, bounds are set to [default * (1-var), default * (1+var)].
        
    Returns:
        A dictionary with 'num_vars', 'names', and 'bounds'.
    """
    bounds_override = bounds_override or {}
    defaults = Params().__dict__
    
    problem_names = []
    problem_bounds = []
    
    for name in param_names:
        if name not in defaults:
            raise ValueError(f"Parameter '{name}' not found in Params dataclass.")
        
        problem_names.append(name)
        
        if name in bounds_override:
            problem_bounds.append(bounds_override[name])
        else:
            val = float(defaults[name])
            # Handle boolean or binary-like flags if they exist (Params v8 is mostly floats)
            problem_bounds.append([val * (1.0 - default_variation), val * (1.0 + default_variation)])
            
    return {
        "num_vars": len(problem_names),
        "names": problem_names,
        "bounds": problem_bounds
    }

def evaluate_parallel(
    model_func: Callable[[np.ndarray], float],
    param_values: np.ndarray,
    n_procs: int = 4
) -> np.ndarray:
    """Evaluates the model function in parallel across multiple processes.
    
    Args:
        model_func: Function that takes a parameter array and returns a scalar result.
        param_values: 2D array of shape (n_samples, n_vars).
        n_procs: Number of worker processes to use.
        
    Returns:
        A 1D array of results.
    """
    with ProcessPoolExecutor(max_workers=n_procs) as executor:
        # map preserves order
        results = list(executor.map(model_func, param_values))
        
    return np.array(results)

def run_morris_analysis(
    problem: Dict[str, Any],
    model_func: Callable[[np.ndarray], float],
    n_trajectories: int = 10,
    n_procs: int = 4,
    seed: int = 42
) -> pd.DataFrame:
    """Performs Morris analysis (Elementary Effects screening).
    
    Returns:
        A pandas DataFrame with mu_star and sigma indices.
    """
    param_values = morris_sampler.sample(problem, N=n_trajectories, seed=seed)
    
    # Run the model
    results = evaluate_parallel(model_func, param_values, n_procs=n_procs)
    
    # Perform analysis
    si = morris_analyzer.analyze(problem, param_values, results, conf_level=0.95, seed=seed)
    
    # Convert to DataFrame
    df = pd.DataFrame({
        "mu": si["mu"],
        "mu_star": si["mu_star"],
        "sigma": si["sigma"],
        "mu_star_conf": si["mu_star_conf"]
    }, index=problem["names"])
    
    return df.sort_values("mu_star", ascending=False)

def run_sobol_analysis(
    problem: Dict[str, Any],
    model_func: Callable[[np.ndarray], float],
    n_samples: int = 128,
    n_procs: int = 4,
    seed: int = 42
) -> Dict[str, Any]:
    """Performs Sobol variance-based sensitivity analysis.
    
    Args:
        n_samples: The number of samples to generate (must be a power of 2).
        
    Returns:
        A dictionary containing S1, ST, and S2 indices.
    """
    param_values = sobol_sampler.sample(problem, N=n_samples, calc_second_order=True)
    
    # Run the model
    results = evaluate_parallel(model_func, param_values, n_procs=n_procs)
    
    # Perform analysis
    si = sobol_analyzer.analyze(problem, results, calc_second_order=True, conf_level=0.95, seed=seed)
    
    return si
