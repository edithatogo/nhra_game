"""Profiling utilities for measuring simulation performance."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_profiler(target: str, profiler: str, output_dir: Path) -> None:
    """Execute the specified profiler on a target module or function."""
    if profiler == "scalene":
        outfile = output_dir / f"scalene_{target.replace(':', '_')}.html"
        print(f"Running Scalene... output to {outfile}")
        cmd = ["python", "-m", "scalene", "--html", "--outfile", str(outfile), "-m", target]
        subprocess.run(cmd, check=True)
    elif profiler == "pyinstrument":
        outfile = output_dir / f"pyinstrument_{target.replace(':', '_')}.html"
        print(f"Running Pyinstrument... output to {outfile}")
        cmd = ["python", "-m", "pyinstrument", "--html", "-o", str(outfile), "-m", target]
        subprocess.run(cmd, check=True)


def main() -> None:
    """Run performance profiling."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, default="nhra_gt.engine")
    parser.add_argument(
        "--profiler", type=str, choices=["scalene", "pyinstrument"], default="scalene"
    )
    parser.add_argument("--outdir", type=str, default="outputs/profiles")
    args = parser.parse_args()

    out_path = Path(args.outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    try:
        run_profiler(args.target, args.profiler, out_path)
    except Exception as e:
        print(f"Profiling failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
