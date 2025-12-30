from __future__ import annotations

from dataclasses import replace

import jax
import jax.numpy as jnp
import numpy as np

from nhra_gt.engine import Params, baseline_state, step
from nhra_gt.engine_jax import ParamsJax, baseline_state_jax, step_jax
from nhra_gt.rules import AuditRule, CapRule, initialize_rules


def test_modular_cap_impact_jax():
    """Verify that changing the cap rule type affects JAX simulation outcomes."""
    # High growth scenario to trigger cap
    p_base = ParamsJax(cap_growth=0.01)  # Very tight cap
    p_base = initialize_rules(p_base)
    s = baseline_state_jax(p=p_base)
    key = jax.random.PRNGKey(42)

    # We need high occupancy to trigger NWAU growth in our simplified model
    s = s.replace(occupancy=0.98)

    # 1. Hard Cap
    p_hard = p_base.replace(cap_rule=CapRule(rule_type=0, cap_limit=0.01))
    strategies = jnp.zeros(12)
    s_hard = step_jax(s, p_hard, strategies, key)

    # 2. Soft Cap (more funding allowed)
    p_soft = p_base.replace(cap_rule=CapRule(rule_type=1, cap_limit=0.01))
    s_soft = step_jax(s, p_soft, strategies, key)

    # Soft cap should result in higher effective share than hard cap
    assert float(s_soft.effective_cth_share) > float(s_hard.effective_cth_share)


def test_modular_audit_impact_jax():
    """Verify that changing the audit rule type affects JAX simulation outcomes."""
    p_base = ParamsJax(audit_pressure=1.0)
    p_base = initialize_rules(p_base)
    s = baseline_state_jax(p=p_base)
    s = s.replace(coding_intensity=1.2)  # High upcoding

    # 1. Proportional Audit
    p_prop = p_base.replace(audit_rule=AuditRule(rule_type=0))
    # We'd need many samples to check probability impact,
    # but we can check if the rule itself returns different values
    prob_prop = p_prop.audit_rule.evaluate(1.2, 1.0)

    # 2. Threshold Audit (should be higher at 1.2)
    p_thresh = p_base.replace(audit_rule=AuditRule(rule_type=1, threshold=1.15))
    prob_thresh = p_thresh.audit_rule.evaluate(1.2, 1.0)

    assert float(prob_thresh) > float(prob_prop)


def test_legacy_modular_rules():
    """Verify modular rules work in legacy engine."""
    p = Params(cap_growth=0.001)  # Very low cap
    p = initialize_rules(p)
    s = baseline_state(p=p)
    s = replace(s, occupancy=1.2)  # High occupancy -> high NWAU growth

    rng = np.random.default_rng(42)

    # Hard Cap
    p_hard = replace(p, cap_rule=CapRule(rule_type=0, cap_limit=0.001))
    s_hard = step(s, p_hard, {}, rng)

    # Soft Cap
    p_soft = replace(p, cap_rule=CapRule(rule_type=1, cap_limit=0.001))
    s_soft = step(s, p_soft, {}, rng)

    assert s_soft.effective_cth_share > s_hard.effective_cth_share
