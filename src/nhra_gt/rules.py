from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

try:
    import jax.numpy as jnp
    from flax import struct
    from jax import lax
except ImportError:  # pragma: no cover
    import numpy as jnp  # type: ignore[assignment]

    lax = None  # type: ignore[assignment]

    class _Struct:  # minimal replacement for `flax.struct`
        dataclass = staticmethod(dataclass)

    struct = _Struct()  # type: ignore[assignment]

if TYPE_CHECKING:
    # Use Any or a Protocol if needed to avoid circular imports during JIT
    Params = Any
    State = Any


@struct.dataclass
class CapRule:
    """Base class for growth cap rules."""

    # rule_type: 0 = Hard, 1 = Soft
    rule_type: int = 0
    cap_limit: float = 0.065

    def apply(self, nwau_growth: float) -> float:
        """Calculate the cap effect on funding share."""

        # Hard Cap logic
        def hard_cap():
            return jnp.where(
                nwau_growth > self.cap_limit, self.cap_limit / jnp.maximum(1e-9, nwau_growth), 1.0
            )

        # Soft Cap logic
        def soft_cap():
            overage = jnp.maximum(0.0, nwau_growth - self.cap_limit)
            return jnp.where(
                nwau_growth > self.cap_limit,
                (self.cap_limit + 0.5 * overage) / jnp.maximum(1e-9, nwau_growth),
                1.0,
            )

        if lax is None:
            return hard_cap() if self.rule_type == 0 else soft_cap()

        return lax.cond(self.rule_type == 0, hard_cap, soft_cap)


@struct.dataclass
class AuditRule:
    """Base class for audit/integrity rules."""

    # rule_type: 0 = Proportional, 1 = Threshold
    rule_type: int = 0
    audit_pressure: float = 0.50
    threshold: float = 1.15

    def evaluate(self, coding_intensity: float, active_pressure: float) -> float:
        """Calculate the probability of detection."""

        # Proportional logic
        def proportional():
            return active_pressure * jnp.maximum(0.0, coding_intensity - 1.0) * 2.0

        # Threshold logic
        def threshold_rule():
            return jnp.where(
                coding_intensity > self.threshold, active_pressure * 3.0, active_pressure * 0.1
            )

        if lax is None:
            return proportional() if self.rule_type == 0 else threshold_rule()

        return lax.cond(self.rule_type == 0, proportional, threshold_rule)


@struct.dataclass
class EligibilityRule:
    """Rules for determining NWAU eligibility (e.g. ABF vs Block)."""

    # boundary_type: 0 = Default, 1 = Shifted
    boundary_type: int = 0
    block_funding_base: float = 0.15

    def get_abf_share(self, venue_shift_strat: float) -> float:
        """Determines the share of activity that remains in ABF."""
        base_abf_share = 1.0 - self.block_funding_base
        # If strategy is 'Shift' (1.0), we reduce ABF share (moving activity to Block)
        target_abf_share = jnp.where(
            venue_shift_strat == 1.0, base_abf_share - 0.10, base_abf_share
        )
        return jnp.clip(target_abf_share, 0.5, 1.0)


@struct.dataclass
class ReconciliationRule:
    """Rules for annual true-ups and safety nets."""

    # recon_type: 0 = Standard, 1 = Safety Net
    recon_type: int = 0
    safety_net_threshold: float = 1.2  # Pressure threshold for bailout

    def calculate_bailout(self, current_pressure: float, month_growth_factor: float) -> float:
        """Calculates the bailout amount based on system pressure."""
        bail_inc = jnp.where(
            current_pressure > self.safety_net_threshold, 0.05 * month_growth_factor, 0.0
        )

        # In 'Safety Net' mode, bailouts are more generous or triggered earlier
        generosity = jnp.where(self.recon_type == 1, 1.5, 1.0)
        return bail_inc * generosity


def initialize_rules(p: Any) -> Any:
    """Ensures all rule objects are initialized in a Params object."""
    # This works for both Params and ParamsJax
    updates = {}
    if getattr(p, "cap_rule", None) is None:
        rule_type = getattr(p, "cap_rule_type", 0)
        # Handle string types from legacy Params
        if isinstance(rule_type, str):
            rule_type = 1 if rule_type == "soft" else 0
        updates["cap_rule"] = CapRule(rule_type=rule_type, cap_limit=p.cap_growth)

    if getattr(p, "audit_rule", None) is None:
        rule_type = getattr(p, "audit_rule_type", 0)
        if isinstance(rule_type, str):
            rule_type = 1 if rule_type == "threshold" else 0
        updates["audit_rule"] = AuditRule(rule_type=rule_type, audit_pressure=p.audit_pressure)

    if getattr(p, "eligibility_rule", None) is None:
        updates["eligibility_rule"] = EligibilityRule(block_funding_base=p.block_funding_base)

    if getattr(p, "reconciliation_rule", None) is None:
        updates["reconciliation_rule"] = ReconciliationRule()

    if updates:
        return p.replace(**updates) if hasattr(p, "replace") else replace(p, **updates)
    return p
