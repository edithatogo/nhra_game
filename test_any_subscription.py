from typing import Any

try:
    print(f"Any is: {Any}")
    x = Any[int, "something"]
    print(f"Any[...] worked: {x}")
except Exception as e:
    print(f"Any[...] failed: {e}")
