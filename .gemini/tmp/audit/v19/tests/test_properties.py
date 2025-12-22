from __future__ import annotations

from nhra_game_theory.v8 import Params, relative_risk


def test_relative_risk_monotone_pressure() -> None:
    p = Params()
    off = 60.0
    pressures = [0.7, 1.0, 1.3, 1.6]
    rrs = [relative_risk(pr, off, p) for pr in pressures]
    assert all(rr > 0.0 for rr in rrs)
    assert rrs == sorted(rrs)


def test_relative_risk_monotone_offload() -> None:
    p = Params()
    pr = 1.3
    offloads = [0.0, 20.0, 60.0, 120.0, 240.0]
    rrs = [relative_risk(pr, off, p) for off in offloads]
    assert all(rr > 0.0 for rr in rrs)
    assert rrs == sorted(rrs)


def test_relative_risk_positive() -> None:
    p = Params()
    for pr in [0.6, 0.9, 1.1, 1.8]:
        for off in [0.0, 10.0, 50.0, 150.0, 300.0]:
            rr = relative_risk(pr, off, p)
            assert rr > 0.0
