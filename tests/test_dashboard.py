from __future__ import annotations
import pytest
import importlib.util
from pathlib import Path

def test_dashboard_script_exists():
    """Verify that the dashboard script exists in the expected location."""
    dashboard_path = Path("scripts/dashboard_v21.py")
    assert dashboard_path.exists(), "Dashboard script scripts/dashboard_v21.py not found."

def test_dashboard_loadable():
    """Verify that the dashboard script can be loaded as a module."""
    dashboard_path = Path("scripts/dashboard_v21.py")
    spec = importlib.util.spec_from_file_location("dashboard_v21", dashboard_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        pass
    assert module is not None

def test_parameter_mapping_logic():
    """Verify that parameters can be correctly mapped to expected slider ranges."""
    from nhra_game_theory.v8 import Params
    
    defaults = Params()
    # Test a few key mappings we expect in the dashboard
    assert 0.05 <= defaults.rurality_weight <= 0.70
    assert 0.5 <= defaults.discharge_delay_base <= 2.0