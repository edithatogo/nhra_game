"""Tests for model audit phase1."""

from __future__ import annotations

from pathlib import Path

_MIN_INVENTORY_LINES = 3


def test_model_candidates_file_exists_and_has_definition() -> None:
    """Check model candidates file exists and has definition."""
    candidates_path = Path("conductor/tracks/model_audit_20260101/model_candidates.md")
    assert candidates_path.exists(), "model_candidates.md should exist"
    content = candidates_path.read_text(encoding="utf-8")
    assert (
        "Any computational component that transforms inputs into outputs for simulation, "
        "prediction, optimization, calibration, or decision analysis." in content
    ), "Model definition should be recorded"


def test_model_candidates_list_is_not_empty() -> None:
    """Check model candidates list is not empty."""
    candidates_path = Path("conductor/tracks/model_audit_20260101/model_candidates.md")
    content = candidates_path.read_text(encoding="utf-8")
    candidate_lines = [line for line in content.splitlines() if line.startswith("- ")]
    assert candidate_lines, "At least one candidate model entry is required"


def test_audit_report_structure_exists() -> None:
    """Check audit report structure exists."""
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
    """Check audit artifacts section lists deliverables."""
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
    """Check model inventory has non tbd entries."""
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    try:
        start_index = lines.index("## Model Inventory")
    except ValueError as exc:
        message = "Missing Model Inventory section"
        raise AssertionError(message) from exc

    table_lines = []
    for line in lines[start_index + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table_lines.append(line)

    assert len(table_lines) >= _MIN_INVENTORY_LINES, (
        "Model Inventory table should include at least one data row"
    )
    data_lines = table_lines[2:]
    assert any("TBD" not in line for line in data_lines), "Model Inventory needs non-TBD entries"


def test_reference_registry_conventions_documented() -> None:
    """Check reference registry conventions documented."""
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    required_strings = [
        "## Reference Registry Conventions",
        "publications/shared/references/library.yaml",
        "scripts/pub_tools/manage_refs.py",
        "Required fields: id, title, author, year, doi/url",
    ]
    for value in required_strings:
        assert value in content, f"Missing reference convention detail: {value}"


def test_assumption_risk_register_conventions_documented() -> None:
    """Check assumption risk register conventions documented."""
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    required_strings = [
        "### Assumption & Risk Register Conventions",
        "Required fields: assumption, rationale, risk, impact, mitigation",
        "Risk levels: low, medium, high",
    ]
    for value in required_strings:
        assert value in content, f"Missing assumption/risk convention detail: {value}"


def test_data_access_licensing_constraints_documented() -> None:
    """Check data access licensing constraints documented."""
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    required_strings = [
        "## Data Access & Licensing Constraints",
        "Identify licensing terms",
        "Access restrictions",
        "Reproducibility impact",
    ]
    for value in required_strings:
        assert value in content, f"Missing data access/licensing detail: {value}"
