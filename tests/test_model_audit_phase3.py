from pathlib import Path


def _section_lines(content: str, section_header: str) -> list[str]:
    lines = content.splitlines()
    found = False
    section_content = []
    for line in lines:
        if line.strip().startswith("#") and section_header in line:
            found = True
            continue
        if found and line.strip().startswith("#") and section_header not in line:
            break
        if found:
            section_content.append(line)
    return section_content


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts:
                rows.append(parts)
    return rows


def test_benchmark_comparisons_populated() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "### Benchmark Comparisons")
    rows = _table_rows(section)
    assert rows, "Benchmark Comparisons table should have entries"

    for row in rows:
        if len(row) < 5:
            continue
        if row[0] == "Model":
            continue

        model_name = row[0]
        _benchmark_desc = row[1]
        _acceptance = row[2]
        result = row[3]
        _notes = row[4]

        # assert model_name.upper() != "TBD", f"Model Name for row is TBD" # The model name is fixed
        assert result.upper() in ["FAIL", "PASS", "WARN", "TBD"], f"Result invalid: {result}"
        assert result.upper() != "TBD", f"Result for {model_name} is TBD"


def test_sanity_checks_populated() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "### Sanity Checks")
    rows = _table_rows(section)
    assert rows, "Sanity Checks table should have entries"

    for row in rows:
        if len(row) < 5:
            continue
        if row[0] == "Model":
            continue

        _model = row[0]
        check = row[1]
        _expected = row[2]
        status = row[3]
        _notes = row[4]

        assert status.upper() != "TBD", f"Status for {check} is TBD"
        assert status.upper() in ["PASS", "FAIL", "WARN"], f"Status invalid: {status}"
