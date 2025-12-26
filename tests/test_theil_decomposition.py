from __future__ import annotations

import numpy as np
import pytest

from nhra_gt.domain.validation import calculate_theil_decomposition


def test_theil_decomposition_sum():
    """Verify that components sum to 1.0."""
    actual = np.array([10, 20, 30, 40])
    predicted = np.array([12, 18, 35, 38])

    decomp = calculate_theil_decomposition(actual, predicted)
    assert decomp["um"] + decomp["us"] + decomp["uc"] == pytest.approx(1.0)


def test_theil_decomposition_bias():
    """Verify that constant offset produces high UM."""
    actual = np.array([10, 20, 30])
    predicted = actual + 10  # Pure bias

    decomp = calculate_theil_decomposition(actual, predicted)
    assert decomp["um"] > 0.9
    assert decomp["us"] == pytest.approx(0.0)
    assert decomp["uc"] == pytest.approx(0.0)
