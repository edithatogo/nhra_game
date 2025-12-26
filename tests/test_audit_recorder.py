from __future__ import annotations

import json
from typing import Any

from nhra_gt.domain.audit import Recorder


def test_recorder_captures_metadata_and_versioned_path(tmp_path: Any) -> None:
    """Verify that Recorder correctly logs execution metadata and manages paths."""
    exp_dir = tmp_path / "experiments"
    recorder = Recorder(base_output_dir=exp_dir)

    recorder.start_experiment(experiment_name="test_run", seed=42)

    # Check artifact path generation
    art_path = recorder.get_artifact_path("data.csv")
    assert "test_run" in str(art_path)
    assert art_path.parent.exists()

    # Simulate work
    import time

    time.sleep(0.1)
    recorder.end_experiment()

    # Check metadata output
    # Path should be experiments/YYYY-MM-DD/test_run_HHMMSS/metadata.json
    metadata_files = list(exp_dir.rglob("metadata.json"))
    assert len(metadata_files) == 1

    with open(metadata_files[0]) as f:
        data = json.load(f)

    assert data["experiment_name"] == "test_run"
    assert data["seed"] == 42
    assert "git_hash" in data
    assert data["duration_seconds"] >= 0.1
    assert "timestamp" in data
