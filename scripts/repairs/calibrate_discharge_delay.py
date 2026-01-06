"""Recalibrates discharge delay base parameters to match historical within4 targets."""

from nhra_gt.domain.params import Params


def main() -> None:
    """Run calibration sweep for discharge delay base."""
    # Load base params
    p = Params()
    print("Running calibration for discharge delay...")


if __name__ == "__main__":
    main()
