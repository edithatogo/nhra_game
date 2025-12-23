"""Lightweight equilibrium helpers.

This module is intentionally small:
- It provides a robust mixed-strategy chooser for 2-action subgames (e.g. bargaining).
- It is *not* intended as a general game solver.

The main use in v14 is to stabilise the bargaining node (E vs A) via a temperature/response parameter.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def logistic(x: float) -> float:
    # numerically stable logistic
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def mixed_strategy_logit(u_hard: float, u_soft: float, k: float = 4.0) -> float:
    """Return P(hard) from a logit / quantal-response rule."""
    k = max(0.0, float(k))
    return float(logistic(k * (float(u_hard) - float(u_soft))))


@dataclass(frozen=True)
class BargainingPayoffs:
    u_hard: float
    u_soft: float
    p_hard: float


def bargaining_from_state(pressure: float, effgap: float, k: float = 4.0) -> BargainingPayoffs:
    """Map (pressure, efficiency gap) -> (u_hard, u_soft, p_hard).

    Intuition:
      - When pressure is high and the effective share is low (high effgap),
        'hard' bargaining becomes more attractive.
      - This mapping is deliberately simple but *continuous* and well-behaved.
    """
    pressure = float(pressure)
    effgap = float(effgap)

    # utilities: calibrated so that u_soft is favoured at low pressure/low effgap
    u_soft = -0.25 * pressure - 0.35 * effgap
    u_hard = 0.35 * pressure + 0.55 * effgap

    p_hard = mixed_strategy_logit(u_hard, u_soft, k=k)
    return BargainingPayoffs(u_hard=u_hard, u_soft=u_soft, p_hard=p_hard)
