from __future__ import annotations

from pathlib import Path


def _section_lines(content: str, heading: str) -> list[str]:
    lines = content.splitlines()
    try:
        start_index = lines.index(heading)
    except ValueError:
        return []

    section = []
    for line in lines[start_index + 1 :]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def _table_rows(section_lines: list[str]) -> list[list[str]]:
    table_lines = [line for line in section_lines if line.startswith("|")]
    if len(table_lines) < 2:
        return []
    data_lines = table_lines[2:]
    rows = []
    for line in data_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def test_input_parameter_sources_section_exists() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    assert "## Input & Parameter Sources" in content, "Missing Input & Parameter Sources section"


def test_input_parameter_sources_table_has_entries() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Input & Parameter Sources")
    rows = _table_rows(section)
    assert rows, "Input & Parameter Sources table should include data rows"


def test_input_parameters_cover_inventory_models() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")

    inventory_section = _section_lines(content, "## Model Inventory")
    inventory_rows = _table_rows(inventory_section)
    inventory_models = {row[0] for row in inventory_rows if row and row[0]}
    assert inventory_models, "Model Inventory should include model names"

    input_section = _section_lines(content, "## Input & Parameter Sources")
    input_rows = _table_rows(input_section)
    input_models = {row[0] for row in input_rows if row and row[0]}

    missing = inventory_models - input_models
    assert not missing, f"Missing input parameter entries for models: {sorted(missing)}"


def test_input_parameters_are_enumerated() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Input & Parameter Sources")
    rows = _table_rows(section)
    for row in rows:
        if len(row) < 2:
            continue
        inputs = row[1].strip()
        assert inputs, "Inputs must be enumerated per model"
        assert inputs.upper() != "TBD", "Inputs must be enumerated per model"


def test_helper_edge_cases() -> None:
    assert _section_lines("no headings here", "## Missing") == []
    assert _table_rows([]) == []
    assert _table_rows(["| header only |"]) == []

    rows = _table_rows(["| col | col2 |", "| --- | --- |", "| onlyone |"])
    assert rows == [["onlyone"]]
    for row in rows:
        if len(row) < 2:
            continue
        raise AssertionError("Expected short row handling")
