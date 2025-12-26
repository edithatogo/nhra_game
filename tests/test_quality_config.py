from pathlib import Path

import tomllib


def test_quality_configuration_completeness() -> None:
    """Verify pyproject.toml has comprehensive quality tool configurations."""
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    # Check for Bandit config
    assert "bandit" in config["tool"], "pyproject.toml missing [tool.bandit] section"
    # Ensure we exclude tests from bandit (strict asserts in src)
    assert "tests" in config["tool"]["bandit"].get("exclude_dirs", []), (
        "Bandit should exclude tests directory"
    )

    # Check for Stricter Ruff
    ruff_select = config["tool"]["ruff"]["lint"]["select"]
    expected_rules = ["A", "C4", "N", "PT"]
    for rule in expected_rules:
        assert rule in ruff_select, f"Ruff config missing strict rule: {rule}"
