"""Core engine benchmark script for throughput measurement."""

import time

import pandas as pd

from nhra_gt.domain.params import Params
from nhra_gt.engine import run_hybrid


class Recorder:
    """Mock recorder for benchmark."""

    def record(self, *args, **kwargs):
        """No-op recording."""


def run_benchmark(n_mc=100, n_years=10):
    """Run a performance benchmark."""
    years = list(range(2025, 2025 + n_years))
    params = Params()
    recorder = Recorder()

    print(f"Starting benchmark: {n_mc} MC runs, {n_years} years...")

    start_time = time.time()
    run_hybrid(years, params, n_mc=n_mc, recorder=recorder)
    duration = time.time() - start_time

    total_steps = n_mc * n_years * 12
    steps_per_sec = total_steps / duration

    print(f"Benchmark Complete in {duration:.4f} seconds.")
    print(f"Performance: {steps_per_sec:.2f} state-transitions/sec")

    # Save result to a baseline file for later comparison
    out_path = "benchmarks/baseline_throughput.csv"
    results = pd.DataFrame(
        [
            {
                "timestamp": time.time(),
                "n_mc": n_mc,
                "n_years": n_years,
                "duration": duration,
                "steps_per_sec": steps_per_sec,
            }
        ]
    )
    results.to_csv(out_path, index=False)
    print(f"Baseline saved to {out_path}")


if __name__ == "__main__":
    run_benchmark()
