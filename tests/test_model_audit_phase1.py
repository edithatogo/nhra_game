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


def test_audit_report_structure_exists() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    assert audit_path.exists(), "audit.md should exist"
    content = audit_path.read_text(encoding="utf-8")
    required_headings = [
        "# Model Audit Report",
        "## Audit Artifacts",
        "## Audit Methodology",
        "## Model Inventory",
        "## Reference Registry",
        "## Assumption & Risk Register",
        "## Validation Results",
        "## Issue Log",
        "## Fix Log",
        "## Provenance",
    ]
    for heading in required_headings:
        assert heading in content, f"Missing section: {heading}"


def test_audit_artifacts_section_lists_deliverables() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    required_items = [
        "Model inventory table",
        "Reference registry",
        "Assumption & risk register",
        "Validation results tables",
    ]
    for item in required_items:
        assert item in content, f"Missing audit artifact item: {item}"


def test_model_inventory_has_non_tbd_entries() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    try:
        start_index = lines.index("## Model Inventory")
    except ValueError as exc:
        raise AssertionError("Missing Model Inventory section") from exc

    table_lines = []
    for line in lines[start_index + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table_lines.append(line)

    assert len(table_lines) >= 3, "Model Inventory table should include at least one data row"
    data_lines = table_lines[2:]
    assert any("TBD" not in line for line in data_lines), "Model Inventory needs non-TBD entries"
