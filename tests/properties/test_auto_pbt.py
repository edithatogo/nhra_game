from __future__ import annotations

import math
from hypothesis_auto import auto_test
from nhra_game_theory.equilibrium import bargaining_from_state, BargainingPayoffs

def test_bargaining_from_state_auto():
    """
    Automated property-based test for bargaining_from_state.
    Verifies that for any floats, it returns a BargainingPayoffs with p_hard in [0, 1].
    """
    def property_check(pressure: float, effgap: float, k: float = 4.0):
        # Skip if inputs are NaN or Inf as they lead to unstable payoffs
        if not all(math.isfinite(x) for x in [pressure, effgap, k]):
            return
            
        result = bargaining_from_state(pressure, effgap, k)
        # Using __name__ check because icontract might wrap the class
        assert type(result).__name__ == "BargainingPayoffs"
        assert 0.0 <= result.p_hard <= 1.0
        return result

    auto_test(property_check)
