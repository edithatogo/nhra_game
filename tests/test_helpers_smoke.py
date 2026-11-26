"""Tests for helpers smoke."""

import nhra_gt
import nhra_gt.engine
from nhra_gt.domain.params import Params
from nhra_gt.helpers import (
    one_way_sensitivity,
    probabilistic_sensitivity,
    run_hybrid,
    scenario_summary,
)
from nhra_gt.interfaces import NormalFormGame, Strategy

_EXPECTED_SCENARIOS = 2
_PSA_SAMPLES = 10


def test_run_hybrid_smoke():
    """Check run hybrid smoke."""
    years = [2025, 2026, 2027]
    agg, freq = run_hybrid(years, Params(), seed=1, n_mc=30)
    assert not agg.empty
    assert {"year", "pressure_mean", "within4_mean"}.issubset(agg.columns)
    assert not freq.empty


def test_scenario_summary_smoke():
    """Check scenario summary smoke."""
    years = [2025, 2026, 2027]
    p = Params()
    scen = scenario_summary(years, p, {"baseline": [], "pooled": ["pooled"]}, seed=1, n_mc=20)
    assert {"scenario", "rr_mean", "pressure_mean"}.issubset(scen.columns)
    assert len(scen) == _EXPECTED_SCENARIOS


def test_one_way_sensitivity_smoke():
    """Check one way sensitivity smoke."""
    years = [2025, 2026, 2027]
    p = Params()
    out = one_way_sensitivity(years, p, {"noise_sd": [0.01, 0.03]}, seed=1, n_mc=15)
    assert not out.empty
    assert {"param", "value", "rr_end"}.issubset(out.columns)


def test_psa_smoke():
    """Check probabilistic sensitivity analysis smoke."""
    years = [2025, 2026, 2027]
    p = Params()
    psa = probabilistic_sensitivity(years, p, ["pooled"], seed=1, n_param=10, n_mc=10)
    assert len(psa) == _PSA_SAMPLES


def test_imports():
    """Verify that core modules can be imported."""
    assert nhra_gt.__version__ is not None
    assert Strategy is not None
    assert NormalFormGame is not None
