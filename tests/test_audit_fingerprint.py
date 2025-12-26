from __future__ import annotations

from pathlib import Path

# We'll import the implementation (which doesn't exist yet)
from src.nhra_game_theory.audit.fingerprint import extract_fingerprint


def test_extract_fingerprint_from_code() -> None:
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
    assert fingerprint["constants"]["CONSTANT_A"] == 100
    assert fingerprint["constants"]["CONSTANT_B"] == "hello"

    # Verify functions (top level)
    assert "function_one" in fingerprint["functions"]
    assert fingerprint["functions"]["function_one"] == ["a", "b"]

    # Verify classes/methods (optional depth)
    assert "MyClass" in fingerprint["classes"]
    assert "method_one" in fingerprint["classes"]["MyClass"]["methods"]


def test_fingerprint_zip_file(tmp_path: Path) -> None:
    import zipfile

    from src.nhra_game_theory.audit.fingerprint import fingerprint_zip

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
    assert fingerprints["nested/other.py"]["constants"]["Y"] == 2

    assert "ignored.txt" not in fingerprints
