"""Compare the JAX rollout with the pre-consolidation scalar model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.engine import ParamsJax, StateJax, baseline_state, run_simulation_jax, step_jax
from nhra_gt.rules import initialize_rules

_CASES = json.loads(
    (Path(__file__).parent / "reference" / "scalar_trajectory.json").read_text(encoding="utf-8")
)["cases"]
_MONTHS = 72
_STEP_PRESSURE_LIMIT = 0.5
_STEP_SHARE_LIMIT = 0.1
_TRAJECTORY_PRESSURE_LIMIT = 1.0


def _setup(case: dict[str, Any]) -> tuple[ParamsJax, StateJax]:
    initial = case["initial"]
    params = ParamsJax(demand_base=case["demand_base"], occupancy_base=case["occupancy_base"])
    params = initialize_rules(
        params.replace(ops=params.ops.replace(init_efficiency_gap=initial["efficiency_gap"]))
    )
    state = baseline_state(initial["year"], params).replace(pressure=initial["pressure"])
    jurisdictions = state.jurisdictions
    assert jurisdictions is not None
    return params, state.replace(
        jurisdictions=jurisdictions.replace(
            effective_cth_share=jnp.full_like(
                jurisdictions.effective_cth_share, initial["effective_cth_share"]
            ),
            efficiency_gap=jnp.full_like(jurisdictions.efficiency_gap, initial["efficiency_gap"]),
        )
    )


def _action_vector(actions: dict[str, Any]) -> jax.Array:
    return jnp.array(
        [
            float(actions.get("SIGNAL") == "H"),
            float(actions.get("DEF") == "R"),
            float(actions.get("BARG") == "A"),
            float(actions.get("SHIFT") == "S"),
            float(actions.get("DISC") == "C"),
            float(actions.get("AGED") == "C"),
            float(actions.get("NDIS") == "C"),
            float(actions.get("CODING") == "U"),
            float(actions.get("COMP") == "H" or actions.get("WORKFORCE") == "H"),
            float(actions.get("SIGNAL_QUALITY", 1.0)),
            float(actions.get("VENUE_SHIFT") == "B"),
            float(actions.get("CAPACITY_MOVE", 0.0)),
            float(actions.get("COMPETITION") == "A"),
        ]
    )


@pytest.mark.parametrize("case", _CASES, ids=[case["id"] for case in _CASES])
def test_step_parity(case: dict[str, Any]) -> None:
    """Compare the next date, pressure and effective Commonwealth share."""
    params, state = _setup(case)
    result = step_jax(state, params, _action_vector(case["single_actions"]), jax.random.PRNGKey(42))
    expected = case["single_step"]

    assert (int(result.year), int(result.month)) == (expected["year"], expected["month"])
    assert abs(result.pressure - expected["pressure"]) < _STEP_PRESSURE_LIMIT
    assert abs(result.effective_cth_share - expected["effective_cth_share"]) < _STEP_SHARE_LIMIT


def test_run_simulation_jax() -> None:
    """Check the compiled batch has one trajectory per rollout and advances a year."""
    baseline = _CASES[0]
    params, state = _setup(baseline)
    months, rollouts = 12, 5
    actions = jnp.tile(_action_vector(baseline["single_actions"]), (months, 1))
    keys = jax.random.split(jax.random.PRNGKey(123), rollouts)

    final, trajectory = jax.jit(
        jax.vmap(lambda key: run_simulation_jax(state, params, actions, key, months))
    )(keys)

    assert final.year.shape == (rollouts,)
    assert (int(final.year[0]), int(final.month[0])) == (baseline["initial"]["year"] + 1, 1)
    assert trajectory.pressure.shape == (rollouts, months)


@pytest.mark.parametrize("case", _CASES, ids=[case["id"] for case in _CASES])
def test_full_trajectory_mirror(case: dict[str, Any]) -> None:
    """Compare pressure against the independent scalar result for every month."""
    params, state = _setup(case)
    action_sequence = jnp.tile(_action_vector(case["trajectory_actions"]), (_MONTHS, 1))
    _, trajectory = run_simulation_jax(
        state, params.replace(noise_sd=0.0), action_sequence, jax.random.PRNGKey(0), _MONTHS
    )
    assert trajectory.pressure.shape == (len(case["pressure_by_month"]),) == (_MONTHS,)
    differences = np.abs(np.asarray(trajectory.pressure) - case["pressure_by_month"])
    worst_month = int(differences.argmax())
    assert differences[worst_month] < _TRAJECTORY_PRESSURE_LIMIT, (
        f"Pressure divergence at month {worst_month + 1}: {differences[worst_month]}"
    )
