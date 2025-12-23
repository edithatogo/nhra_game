from __future__ import annotations

import pytest
import numpy as np
from nhra_game_theory.domain.validation import (
    calculate_rmse,
    calculate_mape,
    calculate_theil_u,
    calculate_hit_rate
)

def test_calculate_rmse():
    actual = np.array([10, 20, 30])
    predicted = np.array([12, 18, 33])
    # squared diffs: 4, 4, 9. mean = 17/3 = 5.66. sqrt = 2.38
    expected = np.sqrt(np.mean((actual - predicted)**2))
    assert calculate_rmse(actual, predicted) == pytest.approx(expected)

def test_calculate_mape():
    actual = np.array([100, 200])
    predicted = np.array([110, 180])
    # abs pct diffs: 0.1, 0.1. mean = 0.1 (10%)
    assert calculate_mape(actual, predicted) == pytest.approx(0.1)

def test_calculate_theil_u():
    """Theil's U should be 0 for perfect prediction and > 0 otherwise."""
    actual = np.array([10, 20, 30])
    assert calculate_theil_u(actual, actual) == 0.0
    
    predicted = np.array([11, 19, 31])
    u = calculate_theil_u(actual, predicted)
    assert 0 < u < 1.0

def test_calculate_hit_rate():
    """Verify hit rate (directional accuracy)."""
    # Actuals: Up, Down, Up
    actual = np.array([10, 12, 11, 15]) 
    # Preds: Up, Down, Down
    predicted = np.array([10, 13, 10, 12]) 
    
    # Directions:
    # 1. Actual Up (10->12), Pred Up (10->13) - HIT
    # 2. Actual Down (12->11), Pred Down (13->10) - HIT
    # 3. Actual Up (11->15), Pred Down (10->12) - MISS (Pred went up 10->12 but 12 < 15 is irrelevant, it's the sign of change)
    # Wait, 10 -> 12 is UP. 11 -> 15 is UP. Both are UP. HIT.
    
    # Let's re-eval:
    # A: [10, 12, 11, 15] -> diffs: [+2, -1, +4]
    # P: [10, 13, 10, 14] -> diffs: [+3, -3, +4]
    # Hits: 3/3 = 100%
    
    a = np.array([10, 12, 11, 15])
    p = np.array([10, 13, 10, 14])
    assert calculate_hit_rate(a, p) == 1.0
    
    p2 = np.array([10, 11, 12, 13]) # All Up. Diffs: [+1, +1, +1]
    # Hits: Up/Up (Hit), Down/Up (Miss), Up/Up (Hit) -> 2/3 = 0.66
    assert calculate_hit_rate(a, p2) == pytest.approx(2/3)
