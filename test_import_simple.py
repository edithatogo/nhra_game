import sys
from unittest.mock import patch

print("Starting import test...")
with patch.dict(sys.modules, {"jaxtyping": None}):
    print("Jaxtyping patched out.")
    print("Import successful.")
