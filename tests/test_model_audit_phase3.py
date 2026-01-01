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
        metric = row[0]
        model_val = row[1]
        benchmark = row[2]
        _delta = row[3]
        result = row[4]

        # Allow header row if parser captured it, but we filtered "---"
        if metric == "Metric":
            continue

        assert model_val.upper() != "TBD", f"Model Value for {metric} is TBD"
        assert benchmark.upper() != "TBD", f"Benchmark for {metric} is TBD"
        assert result.upper() in ["FAIL", "PASS", "WARN", "TBD"], f"Result invalid: {result}"
        assert result.upper() != "TBD", f"Result for {metric} is TBD"


def test_sanity_checks_populated() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "### Sanity Checks")
    rows = _table_rows(section)
    assert rows, "Sanity Checks table should have entries"

    for row in rows:
        if len(row) < 3:
            continue
        check = row[0]
        status = row[1]
        _notes = row[2]

        if check == "Check":
            continue

        assert status.upper() != "TBD", f"Status for {check} is TBD"
        assert status.upper() in ["PASS", "FAIL", "WARN"], f"Status invalid: {status}"
