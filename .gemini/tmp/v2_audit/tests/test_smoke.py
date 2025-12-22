import subprocess
import sys
from pathlib import Path

def test_run_mpe_fast():
    repo = Path(__file__).resolve().parents[1]
    p = subprocess.run([sys.executable, "scripts/run_mpe.py", "--fast"], cwd=repo, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    # check key outputs exist
    out = repo / "outputs" / "mpe_v72" / "v72_interventions_summary.csv"
    assert out.exists()
