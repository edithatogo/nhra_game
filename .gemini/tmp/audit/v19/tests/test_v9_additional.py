from __future__ import annotations

import numpy as np
import pandas as pd

from nhra_game_theory.v9 import (
    Params,
    apply_intervention,
    apply_intervention_partial,
    baseline_state,
    decide_strategies,
    nep_cost_series,
    relative_risk,
    run_hybrid,
    step,
)


def test_relative_risk_increases_with_pressure_offload() -> None:
    p = Params()
    rr0 = relative_risk(
        offload_min=p.offload_threshold_min,
        pressure=1.0,
        efficiency_gap=0.0,
        discharge_delay=1.0,
        p=p,
    )
    rr1 = relative_risk(
        offload_min=p.offload_threshold_min + 20.0,
        pressure=1.2,
        efficiency_gap=0.2,
        discharge_delay=1.2,
        p=p,
    )
    assert rr1 > rr0


def test_decide_strategies_returns_all_games_and_valid_actions() -> None:
    p = Params()
    s = baseline_state(2025, p)
    rng = np.random.default_rng(123)
    strat = decide_strategies(s, p, rng)
    assert set(strat.keys()) == {"DEF", "BARG", "SHIFT", "DISC", "GOV", "COMP"}
    # ensure non-empty string actions
    assert all(isinstance(v, str) and len(v) > 0 for v in strat.values())


def test_step_updates_nep_and_cost_and_keeps_bounds() -> None:
    p = Params(nep_annual_growth=0.02, input_cost_annual_growth=0.04)
    s = baseline_state(2025, p)
    rng = np.random.default_rng(1)
    strat = decide_strategies(s, p, rng)
    s2 = step(s, p, strat, rng)
    assert s2.year == 2026
    assert s2.nep_per_nwau > s.nep_per_nwau
    assert s2.input_cost_index > s.input_cost_index
    # key bounds
    assert 0.75 <= s2.pressure <= 1.80
    assert 0.15 <= s2.within4 <= 0.85
    assert 8.0 <= s2.offload_min <= 120.0
    assert 0.82 <= s2.occupancy <= 0.995


def test_run_hybrid_outputs_expected_columns_and_years() -> None:
    p = Params()
    years = [2025, 2026, 2027]
    agg, freq = run_hybrid(years, p, seed=42, n_mc=10)
    assert isinstance(agg, pd.DataFrame)
    assert isinstance(freq, pd.DataFrame)
    assert list(agg["year"]) == years
    required = {
        "pressure_mean",
        "offload_mean",
        "within4_mean",
        "rr_mean",
        "nep_mean",
        "cost_mean",
        "effgap_micro_mean",
        "effgap_macro_mean",
    }
    assert required.issubset(set(agg.columns))
    assert set(freq["game"].unique()).issubset({"DEF", "BARG", "SHIFT", "DISC", "GOV", "COMP"})
    assert freq["freq"].between(0.0, 1.0).all()


def test_nep_cost_series_ratio_consistent() -> None:
    p = Params(
        nep_per_nwau_start=1.0,
        input_cost_index_start=1.0,
        nep_annual_growth=0.02,
        input_cost_annual_growth=0.01,
    )
    years = [2025, 2026, 2027]
    df = nep_cost_series(years, p)
    assert list(df["year"]) == years
    # ratio should increase because NEP grows faster
    assert df["nep_to_cost_index"].iloc[-1] > df["nep_to_cost_index"].iloc[0]
    # ratio equals nep/cost
    calc = df["nep_per_nwau"] / df["input_cost_index"]
    assert np.allclose(calc.to_numpy(), df["nep_to_cost_index"].to_numpy())


def test_apply_intervention_and_partial_blending() -> None:
    base = Params(
        fragmentation_index=1.1,
        cost_shifting_intensity=0.4,
        nep_annual_growth=0.02,
        input_cost_annual_growth=0.04,
    )
    full = apply_intervention(base, "ucc_integration")
    # integration should reduce fragmentation and avoidable ED share
    assert full.fragmentation_index < base.fragmentation_index
    assert full.avoidable_ed_share < base.avoidable_ed_share

    # partial at 0 is base; at 1 equals full (for fields blended)
    p0 = apply_intervention_partial(base, "ucc_integration", strength=0.0)
    assert p0.fragmentation_index == base.fragmentation_index
    p1 = apply_intervention_partial(base, "ucc_integration", strength=1.0)
    assert np.isclose(p1.fragmentation_index, full.fragmentation_index)


def test_cap_effect_branch_executes_and_cumulative_cap_matters() -> None:
    # Construct a stressed state and strategies to force demand_growth > cap_growth
    base = Params(
        cap_growth=0.01,
        has_cumulative_cap=False,
        cost_shifting_intensity=0.9,
        admin_burden_weight=1.3,
        avoidable_ed_share=0.20,
    )
    s = baseline_state(2025, base)
    # force higher starting pressure/discharge
    s = s.__class__(**{**s.__dict__, "pressure": 1.25, "discharge_delay": 1.30, "occupancy": 0.95})
    rng = np.random.default_rng(7)
    strategies = {"DEF": "E", "BARG": "A", "SHIFT": "S", "DISC": "F", "GOV": "N", "COMP": "H"}
    s_no = step(s, base, strategies, rng)

    with_cap = Params(**{**base.__dict__, "has_cumulative_cap": True})
    rng2 = np.random.default_rng(7)
    s_yes = step(s, with_cap, strategies, rng2)

    # when cumulative cap is present, the multiplier is slightly less punitive
    assert s_no.pressure >= s_yes.pressure


def test_apply_intervention_covers_all_branches_and_unknown_raises() -> None:
    base = Params(
        cost_shifting_intensity=0.5,
        discharge_delay_base=1.1,
        has_cumulative_cap=False,
        nep_annual_growth=0.02,
        input_cost_annual_growth=0.05,
    )

    pooled = apply_intervention(base, "pooled_funding")
    assert pooled.cost_shifting_intensity < base.cost_shifting_intensity

    aged = apply_intervention(base, "aged_ndis_capacity")
    assert aged.discharge_delay_base < base.discharge_delay_base

    cap = apply_intervention(base, "cumulative_cap")
    assert cap.has_cumulative_cap is True

    realism = apply_intervention(base, "nep_realism")
    assert realism.nep_to_cost_ratio_remote >= base.nep_to_cost_ratio_remote

    nep_growth = apply_intervention(base, "nep_growth")
    assert nep_growth.nep_annual_growth > base.nep_annual_growth

    wage = apply_intervention(base, "wage_compact")
    assert wage.input_cost_annual_growth < base.input_cost_annual_growth

    import pytest

    with pytest.raises(ValueError):
        apply_intervention(base, "not_a_real_intervention")
