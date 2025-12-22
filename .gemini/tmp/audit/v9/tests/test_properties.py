from __future__ import annotations

from hypothesis import given, strategies as st

from nhra_game_theory.v8 import Params, relative_risk


@given(
    pidx_low=st.floats(min_value=0.6, max_value=1.2, allow_nan=False, allow_infinity=False),
    pidx_high=st.floats(min_value=1.2, max_value=2.0, allow_nan=False, allow_infinity=False),
    off_low=st.floats(min_value=0.0, max_value=60.0, allow_nan=False, allow_infinity=False),
    off_high=st.floats(min_value=60.0, max_value=300.0, allow_nan=False, allow_infinity=False),
)
def test_relative_risk_monotone(pidx_low: float, pidx_high: float, off_low: float, off_high: float) -> None:
    """
    The risk proxy should be non-decreasing as system 'pressure' and 'offload' increase.
    This is a basic invariance test, not a calibration claim.
    """
    p = Params()
    rr_lo = relative_risk(pidx_low, off_low, p)
    rr_hi = relative_risk(pidx_high, off_high, p)
    assert rr_hi >= rr_lo


@given(
    pidx=st.floats(min_value=0.6, max_value=2.0, allow_nan=False, allow_infinity=False),
    off=st.floats(min_value=0.0, max_value=300.0, allow_nan=False, allow_infinity=False),
)
def test_relative_risk_positive(pidx: float, off: float) -> None:
    p = Params()
    rr = relative_risk(pidx, off, p)
    assert rr > 0.0
