from __future__ import annotations

import pytest
from nhra_game_theory.equilibrium import bargaining_from_state

def test_benchmark_bargaining(benchmark):
    """Benchmark core bargaining logic."""
    def run():
        return bargaining_from_state(pressure=1.2, effgap=0.15, k=4.0)
    
    result = benchmark(run)
    assert result.p_hard is not None
