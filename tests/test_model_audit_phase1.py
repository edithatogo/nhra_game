from __future__ import annotations

from pathlib import Path


def test_model_candidates_file_exists_and_has_definition() -> None:
    candidates_path = Path("conductor/tracks/model_audit_20260101/model_candidates.md")
    assert candidates_path.exists(), "model_candidates.md should exist"
    content = candidates_path.read_text(encoding="utf-8")
    assert (
        "Any computational component that transforms inputs into outputs for simulation, "
        "prediction, optimization, calibration, or decision analysis." in content
    ), "Model definition should be recorded"


def test_model_candidates_list_is_not_empty() -> None:
    candidates_path = Path("conductor/tracks/model_audit_20260101/model_candidates.md")
    content = candidates_path.read_text(encoding="utf-8")
    candidate_lines = [line for line in content.splitlines() if line.startswith("- ")]
    assert candidate_lines, "At least one candidate model entry is required"
