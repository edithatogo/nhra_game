"""
Run MPE models (V7.2 and V8) and write outputs.

Designed for:
- deterministic local execution
- a "fast" mode suitable for CI
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ensure repo root on path so `import src.*` works when executed as scripts/run_mpe.py
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.mpe_models import v72_write_bundle, v8_write_bundle  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="Use fast settings (default).")
    _ = ap.parse_args()

    out72 = REPO / "outputs" / "mpe_v72"
    out8 = REPO / "outputs" / "mpe_v8"

    v72_write_bundle(str(out72), fast=True)
    v8_write_bundle(str(out8))


if __name__ == "__main__":
    main()
