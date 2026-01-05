"""
Helper functions for simulation analysis and legacy compatibility.

This module contains utility functions for running sensitivity analyses,
scenario summaries, and risk calculations, wrapping the core JAX engine.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from nhra_gt.domain.params import Params
from nhra_gt.engine import apply_intervention
from nhra_gt.engine import run_hybrid as run_hybrid_modern


def relative_risk(pressure: float, offload_min: float, params: Params | None = None) -> float:
    """Simple monotone risk proxy used by legacy tests."""
    _ = params
    p = max(0.0, float(pressure) - 1.0)
    o = max(0.0, float(offload_min)) / 60.0
    return float(np.exp(0.9 * p + 0.15 * o))


def run_hybrid(
    years: list[int],
    params: Params,
    seed: int = 123,
    n_mc: int = 300,
    recorder: Any | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Wrapper for the modern JAX engine that accepts Pydantic Params."""
    return run_hybrid_modern(
        years=years,
        p=params.to_params_jax(),
        seed=seed,
        n_mc=n_mc,
        recorder=recorder,
        overrides=overrides,
    )


def scenario_summary(
    years: list[int],
    params: Params,
    scenarios: dict[str, list[str]],
    seed: int = 123,
    n_mc: int = 100,
) -> pd.DataFrame:
    """Runs a batch of scenarios defined by intervention names."""
    rows: list[dict[str, Any]] = []
    for name, interventions in scenarios.items():
        p_jax = params.to_params_jax()
        for iv in interventions:
            p_jax = apply_intervention(p_jax, iv)
        agg, _ = run_hybrid_modern(years=years, p=p_jax, seed=seed, n_mc=n_mc)
        last = agg.sort_values("year").iloc[-1]
        rows.append(
            {
                "scenario": name,
                "rr_mean": float(last.get("rr_mean", last.get("pressure_mean", 0.0))),
                "pressure_mean": float(last.get("pressure_mean", 0.0)),
                "within4_mean": float(last.get("within4_mean", 0.0)),
            }
        )
    return pd.DataFrame(rows)


def one_way_sensitivity(
    years: list[int],
    params: Params,
    grid: dict[str, list[float]],
    seed: int = 123,
    n_mc: int = 50,
) -> pd.DataFrame:
    """Performs one-way sensitivity analysis over a grid of parameter values."""
    rows: list[dict[str, Any]] = []
    for param_name, values in grid.items():
        for v in values:
            p2 = Params(**params.model_dump())
            p2 = p2.model_copy(update={param_name: v})
            agg, _ = run_hybrid(years, p2, seed=seed, n_mc=n_mc)
            rr_end = float(agg.sort_values("year").iloc[-1].get("rr_mean", 0.0))
            rows.append({"param": param_name, "value": float(v), "rr_end": rr_end})
    return pd.DataFrame(rows)


def probabilistic_sensitivity(
    years: list[int],
    params: Params,
    interventions: list[str],
    seed: int = 123,
    n_param: int = 50,
    n_mc: int = 50,
) -> list[dict[str, Any]]:
    """Performs probabilistic sensitivity analysis (PSA) with noise sampling."""
    rng = np.random.default_rng(seed)
    out: list[dict[str, Any]] = []

    for _i in range(int(n_param)):
        sampled = Params(**params.model_dump())
        sampled = sampled.model_copy(update={"noise_sd": float(rng.uniform(0.01, 0.06))})
        p_jax = sampled.to_params_jax()
        for iv in interventions:
            p_jax = apply_intervention(p_jax, iv)

        agg, _ = run_hybrid_modern(
            years=years,
            p=p_jax,
            seed=int(rng.integers(0, 2**31 - 1)),
            n_mc=n_mc,
        )
        last = agg.sort_values("year").iloc[-1]
        out.append(
            {
                "noise_sd": float(sampled.noise_sd),
                "rr_end": float(last.get("rr_mean", 0.0)),
                "pressure_end": float(last.get("pressure_mean", 0.0)),
            }
        )

    return out
