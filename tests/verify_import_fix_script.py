import importlib
import sys
from unittest.mock import patch


def verify_fix():
    print("Starting verification...")
    with patch.dict(sys.modules, {"jaxtyping": None}):
        # Ensure jaxtyping is NOT importable
        try:
            importlib.import_module("jaxtyping")
            print("ERROR: jaxtyping was imported!")
            sys.exit(1)
        except ImportError:
            print("Confirmed: jaxtyping is missing.")

        # Now try to import the module that uses it
        try:
            importlib.import_module("nhra_gt.visualization.game_trees")
            print("SUCCESS: game_trees imported successfully without jaxtyping.")
        except Exception as e:
            print(f"FAILURE: Import failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    verify_fix()
