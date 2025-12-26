from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nhra_game_theory.engine import Params, State


class CapRule(ABC):
    """Abstract base class for growth cap rules."""

    @abstractmethod
    def apply(self, state: State, params: Params, nwau_growth: float) -> float:
        """Calculate the cap effect on funding share."""
        pass


class HardCapRule(CapRule):
    """A strict national funding growth cap (e.g. 6.5%)."""

    def apply(self, state: State, params: Params, nwau_growth: float) -> float:
        if nwau_growth > params.cap_growth:
            # Funding is limited to the cap
            return params.cap_growth / nwau_growth
        return 1.0


class SoftCapRule(CapRule):
    """A cap that allows some overage but with a high penalty."""

    def apply(self, state: State, params: Params, nwau_growth: float) -> float:
        if nwau_growth > params.cap_growth:
            overage = nwau_growth - params.cap_growth
            return (params.cap_growth + 0.5 * overage) / nwau_growth
        return 1.0


class AuditRule(ABC):
    """Abstract base class for audit/integrity rules."""

    @abstractmethod
    def evaluate(self, state: State, params: Params, coding_intensity: float) -> float:
        """Calculate the probability of detection."""
        pass


class ProportionalAuditRule(AuditRule):
    """Detection risk is proportional to upcoding intensity."""

    def evaluate(self, state: State, params: Params, coding_intensity: float) -> float:
        return params.audit_pressure * (coding_intensity - 1.0) * 2.0


class ThresholdAuditRule(AuditRule):
    """Audit risk spikes only after a certain threshold."""

    def evaluate(self, state: State, params: Params, coding_intensity: float) -> float:
        if coding_intensity > 1.15:
            return params.audit_pressure * 3.0
        return params.audit_pressure * 0.1
