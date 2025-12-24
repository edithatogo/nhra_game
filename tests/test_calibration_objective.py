from __future__ import annotations

import numpy as np


from typing import Any

def stochastic_objective(
    means: np.ndarray[Any, Any], targets: np.ndarray[Any, Any], variances: np.ndarray[Any, Any], lam: float = 0.5
) -> float:
    """Composite objective: MSE of means plus lambda * average variance."""
    mse = np.mean((means - targets) ** 2)
    penalty = lam * np.mean(variances)
    return float(mse + penalty)


def test_stochastic_objective_penalizes_variance() -> None:
    """Verify that higher variance results in a higher (worse) objective score."""
    targets = np.array([0.5, 0.5])
    means = np.array([0.5, 0.5])  # Perfect mean match

    low_var = np.array([0.01, 0.01])
    high_var = np.array([0.5, 0.5])

    score_low = stochastic_objective(means, targets, low_var, lam=1.0)
    score_high = stochastic_objective(means, targets, high_var, lam=1.0)

    # Low variance should be better (0.01 vs 0.5)
    assert score_low == 0.01
    assert score_high == 0.5
    assert score_high > score_low


def test_stochastic_objective_mean_drift() -> None:
    """Verify that mean error still drives the score."""
    targets = np.array([0.5])
    var = np.array([0.0])

    score_perfect = stochastic_objective(np.array([0.5]), targets, var)
    score_drift = stochastic_objective(np.array([0.6]), targets, var)

    assert score_drift > score_perfect
