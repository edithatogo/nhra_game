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


def test_issue_log_populated() -> None:
    audit_path = Path("conductor/tracks/model_audit_20260101/audit.md")
    content = audit_path.read_text(encoding="utf-8")
    section = _section_lines(content, "## Issue Log")
    rows = _table_rows(section)
    assert rows, "Issue Log table should have entries (even if just one)"

    for row in rows:
        if len(row) < 6:
            continue
        issue_id = row[0]
        severity = row[1]
        _model = row[2]
        _desc = row[3]
        _evidence = row[4]
        status = row[5]

        if issue_id.upper() == "ID":
            continue

        assert issue_id.startswith("ISSUE-") or issue_id == "TBD", f"Invalid ID: {issue_id}"
        assert severity.upper() in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "LOW (WARN)", "TBD"], (
            f"Invalid severity: {severity}"
        )
        assert status.upper() in ["OPEN", "CLOSED", "WONTFIX", "TBD"], f"Invalid status: {status}"
