from __future__ import annotations

import importlib.util
from pathlib import Path


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[no-untyped-def]
    path = Path(str(collection_path))
    if path.suffix != ".py":
        return False

    # Only apply to our test suite.
    if "tests" not in path.parts:
        return False
    if "archive" in path.parts:
        return True

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False

    if not _has_module("polars") and ("import polars" in text or "from polars" in text):
        return True

    if not _has_module("jax") and (
        "import jax" in text
        or "jax.numpy" in text
        or "engine_jax" in text
        or "solvers_jax" in text
        or "hierarchical_jax" in text
        or "optimization_jax" in text
        or "Params" in text
    ):
        return True

    if not _has_module("pygambit") and ("import pygambit" in text or "from pygambit" in text):
        return True

    return not _has_module("graphviz") and "render_tree_static" in text
