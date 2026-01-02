from __future__ import annotations

import re
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


def _reference_dois() -> dict[str, str]:
    reference_path = Path("publications/shared/references/library.yaml")
    content = reference_path.read_text(encoding="utf-8")
    current_id = None
    dois: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("- id:"):
            current_id = line.split(":", 1)[1].strip().strip('"')
            continue
        if current_id and line.startswith("doi:"):
            doi = line.split(":", 1)[1].strip().strip('"')
            if doi:
                dois[current_id] = doi
    return dois


def _assumption_ids(content: str) -> set[str]:
    section = _section_lines(content, "## Assumption & Risk Register")
    rows = _table_rows(section)
    ids: set[str] = set()
    for row in rows:
        if not row:
            continue
        match = re.match(r"(ASSUMP-[A-Z0-9-]+)", row[0].strip())
        if match:
            ids.add(match.group(1))
    return ids


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


def test_input_sources_have_reference_details() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Input & Parameter Sources")
    rows = _table_rows(section)
    assert rows, "Input & Parameter Sources table should include data rows"
    for row in rows:
        if len(row) < 7:
            raise AssertionError("Input & Parameter Sources rows must include reference details")
        source_id = row[2].strip()
        doi_url = row[3].strip()
        pub_date = row[4].strip()
        units = row[5].strip()
        scaling = row[6].strip()
        assert source_id, "Source ID is required"
        assert source_id.upper() != "TBD", "Source ID is required"
        assert doi_url, "DOI/URL required"
        if source_id.upper().startswith("ASSUMP-"):
            assert "assumption" in doi_url.lower() or "register" in doi_url.lower(), (
                "Assumption sources must reference the Assumption Register"
            )
        else:
            assert "http" in doi_url or "doi:" in doi_url.lower(), "DOI/URL required"
        assert pub_date, "Publication date required"
        assert pub_date.upper() != "TBD", "Publication date required"
        assert units, "Units required"
        assert units.upper() != "TBD", "Units required"
        assert scaling, "Scaling required"
        assert scaling.upper() != "TBD", "Scaling required"


def test_input_sources_include_doi_when_available() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Input & Parameter Sources")
    rows = _table_rows(section)
    dois = _reference_dois()
    assert rows, "Input & Parameter Sources table should include data rows"
    for row in rows:
        if len(row) < 4:
            continue
        doi_url = row[3].strip().lower()
        source_ids = [source_id.strip() for source_id in row[2].split(";")]
        for source_id in source_ids:
            if source_id.upper().startswith("ASSUMP-"):
                continue
            doi = dois.get(source_id)
            if not doi:
                continue
            assert doi.lower() in doi_url, f"DOI for {source_id} missing from DOI/URL column"


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


def test_assumption_register_has_entries() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Assumption & Risk Register")
    rows = _table_rows(section)
    assert rows, "Assumption & Risk Register table should include entries"


def test_assumption_register_no_tbd() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Assumption & Risk Register")
    rows = _table_rows(section)
    for row in rows:
        if len(row) < 5:
            continue
        assumption = row[0].strip()
        rationale = row[1].strip()
        risk = row[2].strip()
        impact = row[3].strip()
        mitigation = row[4].strip()

        assert assumption, "Assumption description required"
        assert assumption.upper() != "TBD", "Assumption description required"
        assert rationale, "Rationale required"
        assert rationale.upper() != "TBD", "Rationale required"
        assert risk, "Risk level required"
        assert risk.upper() != "TBD", "Risk level required"
        assert impact, "Impact note required"
        assert impact.upper() != "TBD", "Impact note required"
        assert mitigation, "Mitigation required"
        assert mitigation.upper() != "TBD", "Mitigation required"


def test_input_sources_match_reference_registry() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")

    # Get Input Sources
    input_section = _section_lines(content, "## Input & Parameter Sources")
    input_rows = _table_rows(input_section)
    cited_sources = set()
    for row in input_rows:
        if len(row) > 2:
            # Handle multiple sources separated by semicolon
            ids = row[2].split(";")
            for source_id in ids:
                cited_sources.add(source_id.strip())

    # Get Registry Entries
    registry_section = _section_lines(content, "## Reference Registry")
    registry_rows = _table_rows(registry_section)
    registered_sources = {row[0].strip() for row in registry_rows if row and len(row) > 0}

    # Verify all cited sources are registered
    missing = cited_sources - registered_sources
    missing = {s for s in missing if not s.upper().startswith("ASSUMP-")}
    # Filter out TBD if it helps validation during dev, but for strictness we want actuals
    missing = {s for s in missing if s.upper() != "TBD"}

    assert not missing, f"Cited sources not found in Reference Registry: {sorted(missing)}"


def test_input_sources_assumptions_listed() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    input_section = _section_lines(content, "## Input & Parameter Sources")
    input_rows = _table_rows(input_section)
    assumption_ids = _assumption_ids(content)

    cited_assumptions = set()
    for row in input_rows:
        if len(row) < 3:
            continue
        ids = [source_id.strip() for source_id in row[2].split(";")]
        for source_id in ids:
            if source_id.upper().startswith("ASSUMP-"):
                cited_assumptions.add(source_id)

    missing = cited_assumptions - assumption_ids
    assert not missing, f"Assumption IDs missing from register: {sorted(missing)}"
