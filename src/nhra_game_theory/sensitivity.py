from __future__ import annotations
from typing import List, Dict, Optional, Any, Callable
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from nhra_game_theory.v8 import Params

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
