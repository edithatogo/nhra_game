from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import Params, baseline_state, step
from nhra_gt.engine_jax import baseline_state_jax, step_jax


def test_legacy_signal_lag():
    """Verify that signal lag correctly delays reported metrics in legacy engine."""
    p = Params(signal_lag_months=2)  # 2 month lag
    s = baseline_state(p=p)

    # Run 3 steps
    rng = np.random.default_rng(42)
    s1 = step(s, p, {}, rng)
    s2 = step(s1, p, {}, rng)
    s3 = step(s2, p, {}, rng)

    # With 2 month lag:
    # After step 1: reported is from initial state
    # After step 2: reported is from step 1
    # After step 3: reported is from step 1 (because lag=2 means we see t-2)
    # Actually, if lag=1, we see t-1. If lag=2, we see t-2.

    # Initial pressure was 1.0.
    # s1.pressure is some new value.
    # s2.pressure is some new value.
    # s3.reported_pressure should be s1.pressure

    assert s3.reported_pressure == pytest.approx(s1.pressure)


def test_jax_signal_lag():
    """Verify that signal lag correctly delays reported metrics in JAX engine."""
    p = ParamsJax(signal_lag_months=2)
    s = baseline_state_jax(2025, p)
    key = jax.random.PRNGKey(42)

    strategies = jnp.zeros(12)
    s1 = step_jax(s, p, strategies, key)
    s2 = step_jax(s1, p, strategies, key)
    s3 = step_jax(s2, p, strategies, key)

    assert float(s3.reported_pressure) == pytest.approx(float(s1.pressure))


def test_jax_claims_lag():
    """Verify that claims lag (NWAU) is separate from signal lag."""
    p = ParamsJax(signal_lag_months=1, claims_lag_months=3)
    s = baseline_state_jax(2025, p)
    key = jax.random.PRNGKey(42)

    strategies = jnp.zeros(12)
    states = [s]
    for _ in range(5):
        states.append(step_jax(states[-1], p, strategies, key))

    # states[0] = initial
    # states[1] = step 1
    # states[2] = step 2
    # states[3] = step 3
    # states[4] = step 4
    # states[5] = step 5

    # reported_nwau in states[5] should be from states[2] (lag=3)
    # Note: sum(lhn_nwau) is used for the buffer in step_jax
    # wait, the buffer is updated AT THE END of the step with the NEW values.
    # So states[1].lag_buffer[-1] = states[1].current_value
    # states[2].reported (lag 1) = states[1].current
    # states[4].reported (lag 3) = states[1].current
    # states[5].reported (lag 3) = states[2].current

    assert float(states[5].reported_nwau) == pytest.approx(float(jnp.sum(states[2].lhn_nwau)))
    assert float(states[5].reported_pressure) == pytest.approx(float(states[4].pressure))
