"""Regenerate the frozen trajectory using the pre-JAX scalar source checkout."""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from nhra_gt import engine

_REFERENCE = "ab65315de2d6be438f0655302f48cc568e0f851f"
_ENGINE_SHA256 = "b6c68afa2cd957ba87a7666ebed1334633e328361ab629c34f529f1eda32568b"
_BASELINE_ACTIONS = {
    "SIGNAL": "L",
    "DEF": "E",
    "BARG": "D",
    "SHIFT": "I",
    "DISC": "F",
    "AGED": "F",
    "NDIS": "F",
    "CODING": "H",
    "COMP": "L",
    "SIGNAL_QUALITY": 1.0,
}
_COORDINATED = {**_BASELINE_ACTIONS, "BARG": "A", "DISC": "C", "AGED": "C", "NDIS": "C"}
_STRESS = {**_BASELINE_ACTIONS, "SHIFT": "S", "WORKFORCE": "H"}


class _ZeroNoise:
    @staticmethod
    def normal(loc: float = 0.0, *_args, **_kwargs) -> float:
        return loc


def _observations(state: engine.State) -> dict[str, float]:
    return {
        "year": state.year,
        "month": state.month,
        "pressure": float(state.pressure),
        "effective_cth_share": float(state.effective_cth_share),
    }


def main() -> None:
    """Print the scalar fixture, after verifying that the historical engine was loaded."""
    if hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest() != _ENGINE_SHA256:
        msg = f"Run with the scalar source tree at {_REFERENCE} on PYTHONPATH"
        raise RuntimeError(msg)

    cases = []
    for name, demand, pressure, occupancy, single_actions, trajectory_actions in (
        ("baseline", 0.85, 1.0, 0.88, _BASELINE_ACTIONS, _COORDINATED),
        ("demand_stress", 1.10, 1.45, 0.95, _STRESS, _STRESS),
    ):
        params = engine.Params(demand_base=demand, occupancy_base=occupancy)
        state = engine.baseline_state(2025, params)
        jurisdictions = [
            replace(
                jur, lhns=[replace(lhn, pressure=pressure, occupancy=occupancy) for lhn in jur.lhns]
            )
            for jur in state.jurisdictions
        ]
        state = replace(state, pressure=pressure, occupancy=occupancy, jurisdictions=jurisdictions)
        initial = {**_observations(state), "efficiency_gap": float(state.efficiency_gap)}
        first = engine.step(state, params, single_actions, np.random.default_rng(42))
        months = []
        for _ in range(72):
            state = engine.step(state, params, trajectory_actions, _ZeroNoise())
            months.append(float(state.pressure))
        cases.append(
            {
                "id": name,
                "demand_base": demand,
                "initial": initial,
                "occupancy_base": occupancy,
                "single_actions": single_actions,
                "trajectory_actions": trajectory_actions,
                "single_step": _observations(first),
                "pressure_by_month": months,
            }
        )
    print(
        json.dumps(
            {
                "reference_revision": _REFERENCE,
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "cases": cases,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
