import sys
from unittest.mock import patch

import pytest


def test_visualization_imports_without_jaxtyping():
    """
    Verify that importing nhra_gt.visualization.game_trees does not crash
    when jaxtyping is missing.
    """
    with patch.dict(sys.modules, {"jaxtyping": None}):
        try:
            # Force reload if it's already imported
            if "nhra_gt.visualization.game_trees" in sys.modules:
                del sys.modules["nhra_gt.visualization.game_trees"]

            # This import currently fails if jaxtyping is missing
            from nhra_gt.visualization import game_trees
        except ImportError as e:
            pytest.fail(f"Import failed when jaxtyping is missing: {e}")
        except ModuleNotFoundError as e:
            pytest.fail(f"Module not found when jaxtyping is missing: {e}")
