import sys
from pathlib import Path
from unittest.mock import MagicMock

# Simulate jaxtyping not being installed
sys.modules["jaxtyping"] = None

# Mock other dependencies that might not be in this env
sys.modules["pygambit"] = MagicMock()
sys.modules["beartype"] = MagicMock()
# beartype decorator needs to return a function
sys.modules["beartype"].beartype = lambda x: x

print("Starting repro script with mocks...")

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

    print("Attempting to import nhra_gt.visualization.game_trees...")
    import nhra_gt.visualization.game_trees as game_trees

    print("SUCCESS: Import of game_trees succeeded.")

    # Check if Array and Float are defined correctly as _DummySubscriptable
    print(f"Array type: {game_trees.Array}")
    print(f"Testing subscription: {game_trees.Float[game_trees.Array, 'm n']}")
    print("SUCCESS: Subscription test passed.")

except ImportError as e:
    print(f"FAILURE: Import failed: {e}")
    import traceback

    traceback.print_exc()
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
    import traceback

    traceback.print_exc()
