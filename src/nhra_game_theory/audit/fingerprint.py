from __future__ import annotations

import ast
import zipfile
from pathlib import Path
from typing import TypedDict, Any


class ClassInfo(TypedDict):
    methods: list[str]
    bases: list[str]


class Fingerprint(TypedDict):
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

    for node in ast.iter_fields(tree):
        # We only look at top-level body
        pass

    # Better to just iterate over body
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
            methods = []
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            for item in node.body:
                 if isinstance(item, ast.FunctionDef):
                     methods.append(item.name)
            
            fingerprint["classes"][node.name] = {
                "methods": methods,
                "bases": bases
            }

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
                        # Skip files we can't read/parse
                        continue
    except Exception:
        pass
    return results
