"""Tests for audit fingerprint."""

from __future__ import annotations

import zipfile
from pathlib import Path

# We'll import the implementation (which doesn't exist yet)
from src.nhra_gt.audit.fingerprint import extract_fingerprint, fingerprint_zip

_FIRST_CONSTANT = 100
_NESTED_CONSTANT = 2


def test_extract_fingerprint_from_code() -> None:
    """Check extract fingerprint from code."""
    code = """
CONSTANT_A = 100
CONSTANT_B = "hello"

def function_one(a, b=1):
    return a + b

class MyClass:
    def method_one(self):
        pass
"""
    fingerprint = extract_fingerprint(code)

    # Verify constants
    assert fingerprint["constants"]["CONSTANT_A"] == _FIRST_CONSTANT
    assert fingerprint["constants"]["CONSTANT_B"] == "hello"

    # Verify functions (top level)
    assert "function_one" in fingerprint["functions"]
    assert fingerprint["functions"]["function_one"] == ["a", "b"]

    # Verify classes/methods (optional depth)
    assert "MyClass" in fingerprint["classes"]
    assert "method_one" in fingerprint["classes"]["MyClass"]["methods"]


def test_fingerprint_zip_file(tmp_path: Path) -> None:
    """Check fingerprint zip file."""
    # Create a zip with python files
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("module.py", "X = 1\ndef foo(): pass")
        zf.writestr("nested/other.py", "Y = 2")
        zf.writestr("ignored.txt", "text")

    fingerprints = fingerprint_zip(zip_path)

    assert "module.py" in fingerprints
    assert fingerprints["module.py"]["constants"]["X"] == 1
    assert "foo" in fingerprints["module.py"]["functions"]

    assert "nested/other.py" in fingerprints
    assert fingerprints["nested/other.py"]["constants"]["Y"] == _NESTED_CONSTANT

    assert "ignored.txt" not in fingerprints
