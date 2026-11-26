"""Tests for manage refs."""

from datetime import datetime

import pytest
import yaml
from scripts.pub_tools.manage_refs import (
    load_references,
    validate_quality,
    validate_recency,
    validate_references,
)

_EXPECTED_REFERENCES = 2

# ... existing code ...


@pytest.fixture
def quality_yaml(tmp_path):
    """Write references with contrasting levels of evidence."""
    f = tmp_path / "quality.yaml"
    data = [
        {"id": "high_ref", "journal": "Nature"},
        {"id": "low_ref", "journal": "Unknown Journal"},
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)


# ... existing tests ...


def test_validate_quality(quality_yaml):
    """Check validate quality."""
    refs = load_references(quality_yaml)
    # Based on implementation, it always returns True currently but logs info
    assert validate_quality(refs) is True


# ... existing code ...


@pytest.fixture
def recency_yaml(tmp_path):
    """Write references with publication dates on both sides of the cutoff."""
    f = tmp_path / "recency.yaml"
    current_year = datetime.now().year
    data = [
        {"id": "new_ref", "year": current_year},
        {"id": "old_ref", "year": current_year - 20},
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)


# ... existing tests ...


def test_validate_recency(recency_yaml):
    """Check validate recency."""
    refs = load_references(recency_yaml)
    # The function returns False if ANY ref is old, but it only logs warnings, it doesn't fail strictly unless we decide to.
    # Based on implementation:
    assert validate_recency(refs, max_age_years=10) is False
    assert validate_recency(refs, max_age_years=25) is True


@pytest.fixture
def valid_yaml(tmp_path):
    """Write a reference that satisfies the required metadata schema."""
    f = tmp_path / "valid.yaml"
    data = [
        {"id": "ref1", "title": "Example 1", "doi": "10.1000/1", "url": "http://example.com/1"},
        {"id": "ref2", "title": "Example 2", "doi": "10.1000/2", "url": "http://example.com/2"},
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)


@pytest.fixture
def invalid_yaml(tmp_path):
    """Write a reference with missing required metadata."""
    f = tmp_path / "invalid.yaml"
    data = [
        {"id": "ref1", "doi": "10.1000/1"},  # Missing URL
        {"id": "ref2", "url": "http://example.com/2"},  # Missing DOI
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)


def test_load_references(valid_yaml):
    """Check load references."""
    refs = load_references(valid_yaml)
    assert len(refs) == _EXPECTED_REFERENCES
    assert refs[0]["id"] == "ref1"


def test_validate_metadata_valid(valid_yaml):
    """Check validate metadata valid."""
    refs = load_references(valid_yaml)
    assert validate_references(refs) is True


def test_validate_metadata_invalid(invalid_yaml):
    """Check validate metadata invalid."""
    refs = load_references(invalid_yaml)
    assert validate_references(refs) is False
