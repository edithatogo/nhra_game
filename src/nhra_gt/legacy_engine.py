"""
Legacy Simulation Engine (Numpy-based).

Maintained for backward compatibility and verification against the JAX core.
Historical modules and the dashboard expect a Pydantic `Params` model and a small
set of helper functions.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from nhra_gt.domain.state import ParamsJax


class Params(BaseModel):
    """Pydantic Params wrapper for validation and tooling."""

    rurality_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    remote_weight: float = Field(default=0.07, ge=0.0, le=1.0)
    nominal_cth_share_target: float = Field(default=0.45, ge=0.0, le=1.0)
    effective_cth_share_base: float = Field(default=0.38, ge=0.0, le=1.0)

    nep_annual_growth: float = Field(default=0.03, ge=-1.0, le=1.0)
    input_cost_annual_growth: float = Field(default=0.04, ge=-1.0, le=1.0)
    demand_base: float = Field(default=0.85, ge=0.0, le=10.0)
    avoidable_ed_share: float = Field(default=0.18, ge=0.0, le=1.0)

    discharge_delay_base: float = Field(default=1.0, ge=0.0, le=10.0)
    bed_capacity_index: float = Field(default=1.0, ge=0.0, le=10.0)
    capacity_lag: float = Field(default=0.15, ge=0.0, le=10.0)
    expansion_lag: float = Field(default=0.10, ge=0.0, le=10.0)
    contraction_lag: float = Field(default=0.20, ge=0.0, le=10.0)
    adjustment_cost_beta: float = Field(default=5.0, ge=0.0, le=1e6)

    cost_shifting_intensity: float = Field(default=0.35, ge=0.0, le=10.0)
    fragmentation_index: float = Field(default=1.0, ge=0.0, le=10.0)
    audit_pressure: float = Field(default=0.50, ge=0.0, le=10.0)
    admin_burden_weight: float = Field(default=0.25, ge=0.0, le=10.0)
    cannibalization_beta: float = Field(default=0.10, ge=0.0, le=10.0)

    block_funding_base: float = Field(default=0.15, ge=0.0, le=1.0)
    shifting_friction: float = Field(default=0.05, ge=0.0, le=10.0)

    signal_lag_months: int = Field(default=1, ge=0, le=24)
    claims_lag_months: int = Field(default=3, ge=0, le=24)

    occupancy_base: float = Field(default=0.88, ge=0.0, le=10.0)
    offload_base_min: float = Field(default=18.0, ge=0.0, le=1e6)
    within4_base: float = Field(default=0.53, ge=0.0, le=1.0)

    rr_beta_pressure: float = Field(default=0.35, ge=0.0, le=10.0)
    rr_beta_offload: float = Field(default=0.015, ge=0.0, le=10.0)
    offload_threshold_min: float = Field(default=20.0, ge=0.0, le=1e6)

    tau: float = Field(default=0.25, ge=0.0, le=10.0)
    bargaining_cost: float = Field(default=0.12, ge=0.0, le=10.0)
    political_salience: float = Field(default=0.30, ge=0.0, le=10.0)

    gp_out_of_pocket: float = Field(default=40.0, ge=0.0, le=1e6)
    gp_wait_time_min: float = Field(default=15.0, ge=0.0, le=1e6)
    patient_time_value_hour: float = Field(default=25.0, ge=0.0, le=1e6)

    cap_growth: float = Field(default=0.065, ge=0.0, le=10.0)
    has_cumulative_cap: bool = False

    cap_rule_type: int = Field(default=0, ge=0, le=1)
    audit_rule_type: int = Field(default=0, ge=0, le=1)
    orchestration_mode: int = Field(default=0, ge=0, le=10)
    equilibrium_selection_rule: str = "nash"
    isolated_game: str | None = None
    use_stage_game_equilibria: bool = True

    use_equilibrium_bargaining: bool = False
    use_quantal_response: bool = False
    qre_lambda: float = Field(default=4.0, ge=0.0, le=1e6)
    use_burden_feedback: bool = False
    burden_to_throughput_beta: float = Field(default=0.06, ge=0.0, le=10.0)
    noise_sd: float = Field(default=0.03, ge=0.0, le=10.0)

    model_config = ConfigDict(validate_assignment=True)

    def to_params_jax(self) -> ParamsJax:
        return ParamsJax(**self.model_dump())


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
    from nhra_gt.engine import run_hybrid as run_hybrid_modern

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
    from nhra_gt.engine import apply_intervention
    from nhra_gt.engine import run_hybrid as run_hybrid_modern

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
    from nhra_gt.engine import apply_intervention
    from nhra_gt.engine import run_hybrid as run_hybrid_modern

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


__all__ = [
    "Params",
    "one_way_sensitivity",
    "probabilistic_sensitivity",
    "relative_risk",
    "run_hybrid",
    "scenario_summary",
]
