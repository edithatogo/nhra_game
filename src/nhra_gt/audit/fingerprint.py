"""Codebase Fingerprinting for Auditability.

Extracts structural signatures from Python files to detect drift or lost features.
"""

from __future__ import annotations

import ast
import logging
import zipfile
from pathlib import Path
from typing import Any, TypedDict

logger = logging.getLogger(__name__)


class ClassInfo(TypedDict):
    """Signature of a Python class, including its methods and bases."""

    methods: list[str]
    bases: list[str]


class Fingerprint(TypedDict):
    """Complete structural signature of a Python file."""

    constants: dict[str, Any]
    functions: dict[str, list[str]]
    classes: dict[str, ClassInfo]


def extract_fingerprint(code: str) -> Fingerprint:
    """Extract logic fingerprint from Python code using AST."""
    fingerprint: Fingerprint = {
        "constants": {},
        "functions": {},
        "classes": {},
    }

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Handling legacy syntax or encoding issues gracefully
        return fingerprint

    for node in tree.body:
        if isinstance(node, ast.Assign):
            # Extract constants
            # We assume constants are uppercase assignments
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Attempt to get literal value
                    value = _get_literal_value(node.value)
                    if value is not None:
                        fingerprint["constants"][target.id] = value

        elif isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            fingerprint["functions"][node.name] = args

        elif isinstance(node, ast.ClassDef):
            methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]

            fingerprint["classes"][node.name] = {"methods": methods, "bases": bases}

    return fingerprint


def _get_literal_value(node: ast.AST) -> Any:
    """Helper to extract literal values from AST nodes."""
    if isinstance(node, ast.Constant):
        return node.value
    # Python < 3.8 support for Num/Str/etc if needed, but 3.10+ uses Constant
    return None


def fingerprint_zip(zip_path: Path) -> dict[str, Fingerprint]:
    """Fingerprint all Python files in a zip archive."""
    results = {}
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".py"):
                    try:
                        content = zf.read(name).decode("utf-8")
                        results[name] = extract_fingerprint(content)
                    except Exception:
                        logger.warning(
                            "Could not fingerprint %s from %s", name, zip_path, exc_info=True
                        )
    except Exception:
        logger.warning("Could not read fingerprint archive %s", zip_path, exc_info=True)
    return results
