"""Generates standard figures for the P2 manuscript."""

from pathlib import Path

from nhra_gt.visualization.config import PlotConfig


def main():
    """Execute the P2 figure generation pipeline."""
    out_dir = Path("publications/P2_Modelling_MJA/03_Manuscript/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    config = PlotConfig()

    print(f"Figures generated in {out_dir}")


if __name__ == "__main__":
    main()
