from __future__ import annotations

import pytest
import json
from pathlib import Path
from nhra_game_theory.domain.audit import Recorder

def test_recorder_captures_metadata(tmp_path):
    """Verify that Recorder correctly logs execution metadata."""
    audit_dir = tmp_path / "audit"
    recorder = Recorder(output_dir=audit_dir)
    
    recorder.start_experiment(experiment_name="test_run", seed=42)
    # Simulate work
    import time
    time.sleep(0.1)
    recorder.end_experiment()
    
    # Check output
    log_files = list(audit_dir.glob("*.json"))
    assert len(log_files) == 1
    
    with open(log_files[0]) as f:
        data = json.load(f)
        
    assert data["experiment_name"] == "test_run"
    assert data["seed"] == 42
    assert "git_hash" in data
    assert data["duration_seconds"] >= 0.1
    assert "timestamp" in data
