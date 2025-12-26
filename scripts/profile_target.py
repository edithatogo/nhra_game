from __future__ import annotations

import argparse
import importlib
import sys
import subprocess
from pathlib import Path

def run_profiler(target: str, profiler: str, output_dir: Path):
    """Run the specified profiler against the target."""
    output_dir.mkdir(exist_ok=True)
    
    if profiler == "scalene":
        outfile = output_dir / f"scalene_{target.replace(':', '_')}.html"
        print(f"Running Scalene... output to {outfile}")
        # Scalene is usually run as a CLI tool: python -m scalene --html --outfile out.html your_script.py
        cmd = ["python", "-m", "scalene", "--html", "--outfile", str(outfile)]
    elif profiler == "pyinstrument":
        outfile = output_dir / f"pyinstrument_{target.replace(':', '_')}.html"
        print(f"Running Pyinstrument... output to {outfile}")
        cmd = ["python", "-m", "pyinstrument", "--html", "-o", str(outfile)]
    else:
        raise ValueError(f"Unknown profiler: {profiler}")

    if ":" in target:
        # Import module:function
        mod_name, func_name = target.split(":")
        # We'll create a temp wrapper script to call the function
        wrapper = Path("temp_profile_wrapper.py")
        wrapper.write_text(f"from {mod_name} import {func_name}\nif __name__ == '__main__':\n    {func_name}()")
        cmd.append(str(wrapper))
        try:
            subprocess.run(cmd, check=True)
        finally:
            if wrapper.exists():
                wrapper.unlink()
    else:
        # Run module as script
        cmd.extend(["-m", target])
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOTA Profiling Runner")
    parser.add_argument("target", help="Module name (e.g. nhra_gt.engine) or mod:func (e.g. scripts.run_baseline_v21:main)")
    parser.add_argument("--profiler", choices=["scalene", "pyinstrument"], default="pyinstrument")
    parser.add_argument("--outdir", default="profiles", help="Output directory")
    
    args = parser.parse_args()
    try:
        run_profiler(args.target, args.profiler, Path(args.outdir))
    except Exception as e:
        print(f"Profiling failed: {e}")
        sys.exit(1)
