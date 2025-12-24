from __future__ import annotations

import numpy as np
import pytest

from nhra_game_theory.sensitivity import run_psa


# Mock model must be top-level for pickling
def mock_model(params):
    return np.sum(params**2)


def test_run_psa_structure():
    """Verify PSA runner output structure."""

    # Mock distributions
    dists = {"a": lambda n: np.random.uniform(0, 1, n), "b": lambda n: np.random.normal(0, 1, n)}

    df = run_psa(dists, mock_model, n_samples=10, n_procs=1)

    assert len(df) == 10
    assert "a" in df.columns
    assert "b" in df.columns
    assert "outcome" in df.columns
    # Check calc for first row
    row = df.iloc[0]
    expected = row["a"] ** 2 + row["b"] ** 2
    assert row["outcome"] == pytest.approx(expected)
