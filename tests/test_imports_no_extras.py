"""Tests for imports no extras."""

import sys
from importlib import import_module
from unittest.mock import patch

import pytest


def test_visualization_imports_without_jaxtyping():
    """Import the game tree renderer without the optional typing annotations."""
    with patch.dict(sys.modules, {"jaxtyping": None}):
        try:
            # Force reload if it's already imported
            if "nhra_gt.visualization.game_trees" in sys.modules:
                del sys.modules["nhra_gt.visualization.game_trees"]

            # This import currently fails if jaxtyping is missing
            imported_game_trees = import_module("nhra_gt.visualization.game_trees")

            assert imported_game_trees is not None
        except ImportError as e:
            pytest.fail(f"Import failed when jaxtyping is missing: {e}")
        except ModuleNotFoundError as e:
            pytest.fail(f"Module not found when jaxtyping is missing: {e}")
