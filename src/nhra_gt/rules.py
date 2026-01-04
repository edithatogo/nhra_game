"""
Modular Rules Engine for NHRA simulation.

This module defines the policy rules (caps, audits, eligibility, reconciliation)
as JAX-compatible PyTrees. This allows rules to be swapped dynamically and
for gradients to flow through rule logic during optimization.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

try:
    import jax.numpy as jnp
    from flax import struct
    from jax import lax
except ImportError:  # pragma: no cover
    import numpy as jnp  # type: ignore[no-redef]

    lax = None

    class _Struct:  # minimal replacement for `flax.struct`
        dataclass = staticmethod(dataclass)

    struct = _Struct()

if TYPE_CHECKING:
    # Use Any or a Protocol if needed to avoid circular imports during JIT
    Params = Any
    State = Any


@struct.dataclass
class CapRule:
    """
    Handles growth cap logic for Commonwealth funding.

    Supports both 'Hard' (strict limit) and 'Soft' (marginal reduction) caps.
    """

    # rule_type: 0 = Hard, 1 = Soft
    rule_type: int = 0
    cap_limit: float = 0.065

    def apply(self, nwau_growth: float) -> float:
        """Calculate the cap effect on funding share.

        Args:
            nwau_growth: The realized growth in NWAU relative to baseline.

        Returns:
            A multiplier (0.0 to 1.0) to be applied to the marginal funding.
        """

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
    """
    Handles integrity and audit pressure logic.

    Defines how coding intensity translates into detection risk or financial penalties.
    """

    # rule_type: 0 = Proportional, 1 = Threshold
    rule_type: int = 0
    audit_pressure: float = 0.50
    threshold: float = 1.15

    def evaluate(self, coding_intensity: float, active_pressure: float) -> float:
        """Calculate the probability of detection or audit penalty."""
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
    """
    Determines NWAU eligibility and activity stream partitioning.

    Defines the boundary between Activity Based Funding (ABF) and Block funding.
    """

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
    """
    Handles annual financial true-ups and emergency transfers.

    Simulates the "Safety Net" or bailout mechanisms triggered by system pressure.
    """

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
    # This works for both Params and Params
    updates = {}
    curr_cap = getattr(p, "cap_rule", None)
    if curr_cap is None or isinstance(curr_cap, str):
        rule_type = getattr(p, "cap_rule_type", 0)
        # Handle string types from legacy Params
        if isinstance(rule_type, str):
            rule_type = 1 if rule_type == "soft" else 0
        updates["cap_rule"] = CapRule(rule_type=rule_type, cap_limit=p.cap_growth)

    curr_audit = getattr(p, "audit_rule", None)
    if curr_audit is None or isinstance(curr_audit, str):
        rule_type = getattr(p, "audit_rule_type", 0)
        if isinstance(rule_type, str):
            rule_type = 1 if rule_type == "threshold" else 0
        updates["audit_rule"] = AuditRule(rule_type=rule_type, audit_pressure=p.audit_pressure)

    if getattr(p, "eligibility_rule", None) is None or isinstance(p.eligibility_rule, str):
        updates["eligibility_rule"] = EligibilityRule(block_funding_base=p.block_funding_base)

    if getattr(p, "reconciliation_rule", None) is None or isinstance(p.reconciliation_rule, str):
        updates["reconciliation_rule"] = ReconciliationRule()

    if updates:
        return p.replace(**updates) if hasattr(p, "replace") else replace(p, **updates)
    return p
