from __future__ import annotations
import pytest
from nhra_game_theory.v8 import Params
from nhra_game_theory.sensitivity import get_salib_problem

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
