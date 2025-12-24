from pathlib import Path

import pytest
import yaml


def test_ci_workflow_has_permissions() -> None:
    """Verify that ci.yml has explicit permissions defined."""
    ci_path = Path(".github/workflows/ci.yml")
    if not ci_path.exists():
        pytest.skip("CI workflow not found")

    with open(ci_path) as f:
        ci_config = yaml.safe_load(f)

    assert "permissions" in ci_config, "ci.yml is missing top-level 'permissions' key"
    assert ci_config["permissions"] == {
        "contents": "read"
    }, "ci.yml permissions should be restricted to contents: read"
