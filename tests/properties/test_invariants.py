from __future__ import annotations

import numpy as np
from hypothesis import given, strategies as st
from numpy.typing import NDArray

def is_valid_probability_distribution(dist: NDArray[np.float64]) -> bool:
    """Check if a 1D array is a valid probability distribution."""
    if dist.ndim != 1:
        return False
    if np.any(dist < 0):
        return False
    return np.isclose(np.sum(dist), 1.0)

@given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=1))
def test_normalization_invariant(values: list[float]):
    """
    Property: Any list of non-negative floats can be normalized 
    to a probability distribution (sum=1), provided the sum > 0.
    """
    arr = np.array(values, dtype=np.float64)
    total = np.sum(arr)
    
    if total > 0:
        normalized = arr / total
        assert is_valid_probability_distribution(normalized)
    else:
        # If total is 0 (all zeros), it cannot be normalized
        pass
