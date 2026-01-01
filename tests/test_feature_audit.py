from pathlib import Path


def test_feature_audit_report_exists():
    path = Path("docs/reports/feature_audit_2026.md")
    assert path.exists(), "Feature Audit Report is missing"


def test_feature_audit_report_populated():
    path = Path("docs/reports/feature_audit_2026.md")
    content = path.read_text(encoding="utf-8")

    # Check for main sections
    assert "## 1. High-Level Product Features" in content
    assert "## 2. Model Inputs & Parameters" in content
    assert "## 3. Mechanisms & Rules Engine" in content
    assert '## 7. Discovered "Hidden" Features' in content

    # Check for implemented features
    assert "Implemented" in content
    assert "src/nhra_gt/engine.py" in content

    # Check for hidden features specifically
    assert "Constitutional Game Layer" in content
