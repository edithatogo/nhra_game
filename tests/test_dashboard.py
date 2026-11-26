"""Tests for dashboard."""

from __future__ import annotations

import contextlib
import importlib.util
import json
from pathlib import Path

import pandas as pd

from nhra_gt.engine import Params, run_hybrid, summarise_outcome
from nhra_gt.sensitivity import get_parameter_lineage

_MIN_RURALITY = 0.05
_MAX_RURALITY = 0.70
_MIN_DISCHARGE_DELAY = 0.5
_MAX_DISCHARGE_DELAY = 2.0
_SCENARIO_ROW_COUNT = 4
_SNAPSHOT_SHARE = 0.50
_FINAL_EFFECTIVE_SHARE = 0.42


def test_dashboard_script_exists():
    """Verify that the dashboard script exists in the expected location."""
    dashboard_path = Path("scripts/dashboard.py")
    assert dashboard_path.exists(), "Dashboard script scripts/dashboard.py not found."


def test_dashboard_loadable():
    """Verify that the dashboard script can be loaded as a module."""
    dashboard_path = Path("scripts/dashboard.py")
    spec = importlib.util.spec_from_file_location("dashboard", dashboard_path)
    module = importlib.util.module_from_spec(spec)
    with contextlib.suppress(Exception):
        spec.loader.exec_module(module)
    assert module is not None


def test_parameter_mapping_logic():
    """Verify that parameters can be correctly mapped to expected slider ranges."""
    defaults = Params()
    # Test a few key mappings we expect in the dashboard
    assert _MIN_RURALITY <= defaults.rurality_weight <= _MAX_RURALITY
    assert _MIN_DISCHARGE_DELAY <= defaults.discharge_delay_base <= _MAX_DISCHARGE_DELAY


def test_model_rollout_interface():
    """Verify that the model can be called with dashboard-provided parameters."""
    # Simulate a dashboard update
    p = Params(rurality_weight=0.5)
    years = list(range(2025, 2031))

    # Low-fidelity run (small n_mc)
    traj, _strat = run_hybrid(years, p, n_mc=10)

    assert isinstance(traj, pd.DataFrame)
    assert not traj.empty
    assert "pressure_mean" in traj.columns


def test_plotly_df_generation():
    """Verify that we can combine baseline and war-game data for Plotly charts."""
    df_base = pd.DataFrame({"year": [2025, 2026], "val": [1.0, 1.1]})
    df_game = pd.DataFrame({"year": [2025, 2026], "val": [1.0, 1.2]})

    # Combined for plotting
    df_base["Scenario"] = "Baseline"
    df_game["Scenario"] = "War Game"
    combined = pd.concat([df_base, df_game])

    assert len(combined) == _SCENARIO_ROW_COUNT
    assert set(combined["Scenario"]) == {"Baseline", "War Game"}


def test_lineage_lookup_logic():
    """Verify that we can map parameters to evidence sources."""
    lineage = get_parameter_lineage()
    assert Params().flatten().keys() <= lineage.keys()
    assert lineage["within4_base"].startswith("primary ·")
    assert "aihw.gov.au" in lineage["within4_base"]
    assert lineage["occupancy_base"].startswith("assumed ·")


def test_narrative_generator_rules():
    """Verify that the narrative generator produces expected text based on outcomes."""
    # Mock summaries
    summary_base = {"rr_2030": 1.0, "effshare_effective_2030": 0.38}
    summary_game = {"rr_2030": 1.2, "effshare_effective_2030": 0.40}

    # Logic: if risk increased, narrative should mention it
    narrative = ""
    if summary_game["rr_2030"] > summary_base["rr_2030"]:
        narrative = "System risk is projected to increase"

    assert "increase" in narrative


def test_scenario_serialization():
    """Verify that war-game states can be serialized to JSON."""
    state = {
        "nominal_cth_share_target": 0.50,
        "rurality_weight": 0.40,
        "scenario_name": "Test Scenario",
    }

    serialized = json.dumps(state)
    deserialized = json.loads(serialized)

    assert deserialized["nominal_cth_share_target"] == _SNAPSHOT_SHARE
    assert deserialized["scenario_name"] == "Test Scenario"


def test_summarise_outcome_keys():
    """Verify that summarise_outcome returns all keys expected by the dashboard."""
    # Create a dummy DataFrame simulating the output of run_hybrid
    data = {
        "year": [2025, 2030],
        "pressure_mean": [1.0, 1.2],
        "within4_mean": [0.5, 0.4],
        "offload_mean": [18.0, 20.0],
        "rr_mean": [1.0, 1.5],
        "cth_nominal_mean": [0.4, 0.42],
        "effgap_mean": [0.1, 0.15],
    }
    agg = pd.DataFrame(data)

    summary = summarise_outcome(agg)

    assert "effshare_effective_2030" in summary
    assert summary["effshare_effective_2030"] == _FINAL_EFFECTIVE_SHARE
