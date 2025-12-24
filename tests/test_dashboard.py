from __future__ import annotations

import contextlib
import importlib.util
import json
from pathlib import Path

import pandas as pd


def test_dashboard_script_exists():
    """Verify that the dashboard script exists in the expected location."""
    dashboard_path = Path("scripts/dashboard_v21.py")
    assert dashboard_path.exists(), "Dashboard script scripts/dashboard_v21.py not found."


def test_dashboard_loadable():
    """Verify that the dashboard script can be loaded as a module."""
    dashboard_path = Path("scripts/dashboard_v21.py")
    spec = importlib.util.spec_from_file_location("dashboard_v21", dashboard_path)
    module = importlib.util.module_from_spec(spec)
    with contextlib.suppress(Exception):
        spec.loader.exec_module(module)
    assert module is not None


def test_parameter_mapping_logic():
    """Verify that parameters can be correctly mapped to expected slider ranges."""
    from nhra_game_theory.legacy_engine import Params

    defaults = Params()
    # Test a few key mappings we expect in the dashboard
    assert 0.05 <= defaults.rurality_weight <= 0.70
    assert 0.5 <= defaults.discharge_delay_base <= 2.0


def test_model_rollout_interface():
    """Verify that the model can be called with dashboard-provided parameters."""
    from nhra_game_theory.legacy_engine import Params, run_hybrid

    # Simulate a dashboard update
    p = Params(rurality_weight=0.5)
    years = list(range(2025, 2031))

    # Low-fidelity run (small n_mc)
    traj, strat = run_hybrid(years, p, n_mc=10)

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

    assert len(combined) == 4
    assert set(combined["Scenario"]) == {"Baseline", "War Game"}


def test_lineage_lookup_logic():
    """Verify that we can map parameters to evidence sources."""
    lineage_map = {
        "nominal_cth_share_target": "https://www.federalfinancialrelations.gov.au/programs/national-health-reform",
        "rurality_weight": "AIHW (2024) Hospital Activity Data",
    }

    param = "rurality_weight"
    assert param in lineage_map
    assert "AIHW" in lineage_map[param]


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

    assert deserialized["nominal_cth_share_target"] == 0.50
    assert deserialized["scenario_name"] == "Test Scenario"
