from __future__ import annotations

import time
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from nhra_game_theory.engine import Params, run_hybrid
from nhra_game_theory.domain.audit import Recorder

def benchmark_engine(n_mc: int = 300, n_years: int = 6):
    """Measures samples per second for the core simulation engine."""
    p = Params()
    years = list(range(2025, 2025 + n_years))
    
    recorder = Recorder()
    
    print(f"Starting benchmark: {n_mc} MC runs, {n_years} years...")
    
    start_time = time.time()
    traj, freq = run_hybrid(years=years, p=p, n_mc=n_mc, seed=42, recorder=recorder)
    end_time = time.time()
    
    duration = end_time - start_time
    # Total state transitions = n_mc * (n_years - 1)
    total_steps = n_mc * (n_years - 1)
    steps_per_sec = total_steps / duration
    
    print(f"Benchmark Complete in {duration:.4f} seconds.")
    print(f"Performance: {steps_per_sec:.2f} state-transitions/sec")
    
    # Save result to a baseline file for later comparison
    results = pd.DataFrame([{
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_mc": n_mc,
        "n_years": n_years,
        "duration": duration,
        "steps_per_sec": steps_per_sec,
        "version": "v9_numpy_base"
    }])
    
    out_path = Path("reports/benchmarks/engine_baseline.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Append if exists
    if out_path.exists():
        existing = pd.read_csv(out_path)
        results = pd.concat([existing, results], ignore_index=True)
        
    results.to_csv(out_path, index=False)
    print(f"Baseline saved to {out_path}")

if __name__ == "__main__":
    benchmark_engine()
