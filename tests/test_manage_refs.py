import os
import yaml
import pytest
from scripts.pub_tools.manage_refs import load_references, validate_metadata

@pytest.fixture
def valid_yaml(tmp_path):
    f = tmp_path / "valid.yaml"
    data = [
        {"id": "ref1", "doi": "10.1000/1", "url": "http://example.com/1"},
        {"id": "ref2", "doi": "10.1000/2", "url": "http://example.com/2"},
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)

@pytest.fixture
def invalid_yaml(tmp_path):
    f = tmp_path / "invalid.yaml"
    data = [
        {"id": "ref1", "doi": "10.1000/1"}, # Missing URL
        {"id": "ref2", "url": "http://example.com/2"}, # Missing DOI
    ]
    with open(f, "w") as file:
        yaml.dump(data, file)
    return str(f)

def test_load_references(valid_yaml):
    refs = load_references(valid_yaml)
    assert len(refs) == 2
    assert refs[0]["id"] == "ref1"

def test_validate_metadata_valid(valid_yaml):
    refs = load_references(valid_yaml)
    assert validate_metadata(refs) is True

def test_validate_metadata_invalid(invalid_yaml):
    refs = load_references(invalid_yaml)
    assert validate_metadata(refs) is False
