from __future__ import annotations
import pytest
import numpy as np
from nhra_game_theory.v8 import Params
from nhra_game_theory.sensitivity import get_salib_problem, evaluate_parallel

def mock_model(params: np.ndarray) -> float:
    """A simple model function for testing parallelism."""
    return float(np.sum(params))

def test_get_salib_problem_basic() -> None:
    """Verify that the utility generates a correct SALib problem dictionary."""
    param_list = ["rurality_weight", "cost_shifting_intensity"]
    
    # We expect bounds to be roughly +/- 20% of default or explicitly provided
    problem = get_salib_problem(param_list)
    
    assert problem["num_vars"] == 2
    assert problem["names"] == param_list
    assert len(problem["bounds"]) == 2
    for bound in problem["bounds"]:
        assert len(bound) == 2
        assert bound[0] < bound[1]

def test_get_salib_problem_invalid_param() -> None:
    """Verify that providing an invalid parameter name raises a ValueError."""
    with pytest.raises(ValueError, match="not found in Params"):
        get_salib_problem(["invalid_param_name"])

def test_get_salib_problem_custom_bounds() -> None:
    """Verify that we can override default bounds."""
    param_list = ["rurality_weight"]
    custom_bounds = {"rurality_weight": [0.1, 0.9]}
    
    problem = get_salib_problem(param_list, bounds_override=custom_bounds)
    
    assert problem["bounds"][0] == [0.1, 0.9]

def test_evaluate_parallel_basic() -> None:
    """Verify that the parallel evaluator collects results from a simple function."""
    param_values = np.array([
        [1.0, 2.0],
        [3.0, 4.0],
        [5.0, 6.0]
    ])
    
    results = evaluate_parallel(mock_model, param_values, n_procs=2)
    
    assert len(results) == 3
    assert results[0] == 3.0
    assert results[1] == 7.0
    assert results[2] == 11.0

def test_run_morris_analysis() -> None:
    """Verify that Morris analysis produces a dataframe with mu_star and sigma."""
    from nhra_game_theory.sensitivity import run_morris_analysis
    
    param_list = ["rurality_weight", "cost_shifting_intensity"]
    problem = get_salib_problem(param_list)
    
    # Run with small N for testing
    df = run_morris_analysis(problem, mock_model, n_trajectories=4, n_procs=2)
    
    assert "mu_star" in df.columns
    assert "sigma" in df.columns
    assert len(df) == 2
    assert set(df.index) == set(param_list)

def test_run_sobol_analysis() -> None:
    """Verify that Sobol analysis produces a results dictionary with S1 and ST."""
    from nhra_game_theory.sensitivity import run_sobol_analysis
    
    param_list = ["rurality_weight", "cost_shifting_intensity"]
    problem = get_salib_problem(param_list)
    
    # Run with small N for testing (must be power of 2 for Sobol)
    results_dict = run_sobol_analysis(problem, mock_model, n_samples=8, n_procs=2)
    
    assert "S1" in results_dict
    assert "ST" in results_dict
    assert len(results_dict["S1"]) == 2
    assert len(results_dict["ST"]) == 2