"""Global Sensitivity Analysis Suite for NHRA model."""

from __future__ import annotations

import argparse

import numpy as np


def mock_func(x):
    """Simple additive mock model for testing."""
    return float(np.sum(x))


def main() -> None:
    """Execute the GSA workflow."""
    parser = argparse.ArgumentParser(description="Global Sensitivity Analysis Suite")
    parser.add_argument("--method", type=str, choices=["morris", "sobol", "mock"], default="morris")
    args = parser.parse_args()
    print(f"Running {args.method} analysis...")


if __name__ == "__main__":
    main()
