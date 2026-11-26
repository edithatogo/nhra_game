"""Collection rules for the NHRA test suite."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def pytest_ignore_collect(collection_path: Path) -> bool:
    """Collect the tests whose runtime dependencies are installed."""
    if collection_path.suffix != ".py" or "tests" not in collection_path.parts:
        return False
    if "archive" in collection_path.parts:
        return True

    try:
        text = collection_path.read_text(encoding="utf-8")
    except OSError:
        return False

    markers = {
        "polars": ("import polars", "from polars"),
        "jax": (
            "import jax",
            "jax.numpy",
            "engine_jax",
            "solvers_jax",
            "hierarchical_jax",
            "optimization_jax",
            "Params",
        ),
        "pygambit": ("import pygambit", "from pygambit"),
        "graphviz": ("render_tree_static",),
    }
    return any(
        any(marker in text for marker in imports) and not _has_module(dependency)
        for dependency, imports in markers.items()
    )
