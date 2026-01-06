"""Runs simulation experiments for the P2 manuscript."""

from pathlib import Path


def main() -> None:
    """Run all simulation experiments required for the P2 paper."""
    # Setup output paths
    out_dir = Path("publications/P2_Modelling_MJA/02_Analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    print("Running P2 experiments...")


if __name__ == "__main__":
    main()
