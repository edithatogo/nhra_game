"""Tests for queuing game."""

from __future__ import annotations

from nhra_gt.domain.params import Params
from nhra_gt.domain.state import ParamsJax
from nhra_gt.subgames.queuing import (
    PatientUtilityParams,
    solve_queuing_equilibrium_jax,
    solve_queuing_equilibrium_legacy,
)

_MIN_HIGH_CAPACITY_DEMAND = 0.1


def test_queuing_impact_jax():
    """Verify that increasing GP cost drives more demand into ED in JAX."""
    demand_base = 1.0
    capacity = 1.0
    discharge_delay = 1.0
    global_params = ParamsJax()

    # 1. Low GP cost
    params_low = PatientUtilityParams(gp_out_of_pocket=0.0)
    d_low, p_low = solve_queuing_equilibrium_jax(
        demand_base, capacity, discharge_delay, params_low, global_params
    )

    # 2. High GP cost
    params_high = PatientUtilityParams(gp_out_of_pocket=100.0)
    d_high, p_high = solve_queuing_equilibrium_jax(
        demand_base, capacity, discharge_delay, params_high, global_params
    )

    assert float(d_high) > float(d_low)
    assert float(p_high) > float(p_low)


def test_queuing_impact_legacy():
    """Verify that increasing GP cost drives more demand into ED in legacy."""
    demand_base = 1.0
    capacity = 1.0
    discharge_delay = 1.0
    global_params = Params()

    # 1. Low GP cost
    params_low = PatientUtilityParams(gp_out_of_pocket=0.0)
    d_low, p_low = solve_queuing_equilibrium_legacy(
        demand_base, capacity, discharge_delay, params_low, global_params
    )

    # 2. High GP cost
    params_high = PatientUtilityParams(gp_out_of_pocket=100.0)
    d_high, p_high = solve_queuing_equilibrium_legacy(
        demand_base, capacity, discharge_delay, params_high, global_params
    )

    assert d_high > d_low
    assert p_high > p_low


def test_wait_time_feedback_jax():
    """Check the first demand update at two capacities from the same initial load."""
    demand_base = 0.5
    discharge_delay = 1.0
    global_params = ParamsJax()
    # High time value makes wait times more impactful
    params = PatientUtilityParams(gp_out_of_pocket=10.0, patient_time_value_hour=50.0)

    # 1. High capacity (1.0 servers -> 10 capacity units)
    d_high_cap, p_high = solve_queuing_equilibrium_jax(
        demand_base, 1.0, discharge_delay, params, global_params, max_iter=1
    )

    # 2. Low capacity (0.1 servers -> 1 capacity units)
    d_low_cap, p_low = solve_queuing_equilibrium_jax(
        demand_base, 0.1, discharge_delay, params, global_params, max_iter=1
    )

    assert 0.0 <= float(p_low) < float(p_high) <= 1.0
    assert 0.0 <= float(d_low_cap) < float(d_high_cap) <= demand_base
    assert float(d_high_cap) > _MIN_HIGH_CAPACITY_DEMAND
