"""
Run all bundled scripts and the MPE models, writing outputs into versioned folders.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path, cwd: Path) -> None:
    cwd.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, str(script_path)], cwd=cwd, capture_output=True, text=True)
    log = cwd / (script_path.stem + ".log")
    log.write_text(p.stdout + "\n\nSTDERR:\n" + p.stderr)
    if p.returncode != 0:
        raise RuntimeError(f"Script failed: {script_path.name}\nSee log: {log}")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    src = repo / "src"
    outputs = repo / "outputs"

    # Mechanism scripts V1-V5
    mapping = [
        ("nhra_games_v1.py", outputs / "v1"),
        ("nhra_games_v2_calibrated.py", outputs / "v2"),
        ("nhra_hybrid_v3.py", outputs / "v3"),
        ("nhra_hybrid_v4.py", outputs / "v4"),
        ("nhra_hybrid_v5.py", outputs / "v5"),
    ]
    for fname, outdir in mapping:
        run_script(src / fname, outdir)

    # MPE suite (V7.2 + V8)
    p = subprocess.run([sys.executable, "scripts/run_mpe.py", "--fast"], cwd=repo, capture_output=True, text=True)
    (outputs / "mpe_run.log").write_text(p.stdout + "\n\nSTDERR:\n" + p.stderr)
    if p.returncode != 0:
        raise RuntimeError("MPE run failed (see outputs/mpe_run.log)")


if __name__ == "__main__":
    main()
