"""Payoff matrix generators for NHRA strategic subgames."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from nhra_gt.domain.params import BehavioralParams
from nhra_gt.subgames.nash import TwoPlayerGame


@dataclass(frozen=True)
class GameParams:
    """Inputs used to parameterise stage games (dimensionless indices)."""

    pressure: float
    efficiency_gap: float
    discharge_delay: float
    political_salience: float
    audit_pressure: float
    cost_shifting_intensity: float
    political_capital: float
    cannibalization_beta: float = 0.1
    behavior: BehavioralParams = field(default_factory=BehavioralParams)


def definition_game(gp: GameParams) -> TwoPlayerGame:
    """Definition game: 'R' realism vs 'E' strict efficient-price framing."""
    pr = gp.pressure
    eg = gp.efficiency_gap
    ps = gp.political_salience
    b = gp.behavior

    # Realism has fiscal and political costs but stabilises pressure.
    realism_benefit = (
        b.def_realism_benefit_base
        + b.def_realism_eg_weight * eg
        + b.def_realism_pr_weight * (pr - 1.0)
    )
    realism_cost = b.def_realism_cost_base + b.def_realism_ps_weight * ps

    strict_benefit = b.def_strict_benefit_base + b.def_strict_ps_weight * ps
    strict_cost = b.def_strict_cost_base + b.def_strict_pr_weight * pr

    # Payoffs (R vs E)
    u_row = np.array(
        [
            [
                b.base_payoff + realism_benefit - realism_cost,
                b.base_payoff - b.def_row_realism_offset - realism_cost,
            ],
            [
                b.base_payoff + strict_benefit - strict_cost,
                b.base_payoff - b.def_row_strict_offset - strict_cost,
            ],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff + realism_benefit - b.def_col_realism_offset,
                b.base_payoff - b.def_col_realism_cost,
            ],
            [b.base_payoff - b.def_col_strict_cost_1, b.base_payoff - b.def_col_strict_cost_2],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("R", "E"), col_actions=("R", "E"))


def bargaining_game(gp: GameParams) -> TwoPlayerGame:
    """Bargaining game: 'A' agree to converge vs 'D' defer/escalate."""
    pr = gp.pressure
    ps = gp.political_salience
    pc = gp.political_capital
    b = gp.behavior

    # Political capital boosts the effectiveness of agreement
    converge_gain = (
        b.barg_converge_gain_base
        + b.barg_converge_pr_weight * (pr - b.base_payoff)
        + b.barg_converge_pc_weight * pc
    )
    conflict_cost = b.barg_conflict_cost_base + b.barg_conflict_pr_weight * pr
    narrative_gain = b.barg_narrative_gain_base + b.barg_narrative_ps_weight * ps

    u_row = np.array(
        [
            [
                b.base_payoff + converge_gain - b.barg_row_converge_ps_penalty * ps,
                b.base_payoff
                - b.barg_row_converge_base_penalty
                - b.barg_row_converge_pr_penalty * pr,
            ],
            [
                b.base_payoff + narrative_gain - b.barg_row_narrative_pr_penalty * pr,
                b.base_payoff - conflict_cost,
            ],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff + converge_gain - b.barg_col_converge_ps_penalty * ps,
                b.base_payoff
                - b.barg_col_converge_base_penalty
                - b.barg_col_converge_pr_penalty * pr,
            ],
            [b.base_payoff - b.barg_col_narrative_penalty, b.base_payoff - conflict_cost],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("A", "D"), col_actions=("A", "D"))


def cost_shifting_game(gp: GameParams) -> TwoPlayerGame:
    """Cost shifting game: invest upstream 'I' vs shift downstream 'S'."""
    pr = gp.pressure
    eg = gp.efficiency_gap
    csi = gp.cost_shifting_intensity
    b = gp.behavior

    coop_gain = b.shift_coop_gain_base + b.shift_coop_eg_weight * (b.base_payoff - eg)
    shift_gain = b.shift_gain_base + b.shift_eg_weight * eg + b.shift_csi_weight * csi
    pr_cost = b.shift_pr_cost_weight * pr

    u_row = np.array(
        [
            [
                b.base_payoff + coop_gain - pr_cost,
                b.base_payoff - b.shift_row_coop_penalty - pr_cost,
            ],
            [
                b.base_payoff + shift_gain - b.shift_row_shift_pr_penalty * pr,
                b.base_payoff
                - b.shift_row_shift_base_penalty
                - b.shift_row_shift_pr_heavy_penalty * pr,
            ],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff + coop_gain - pr_cost,
                b.base_payoff + shift_gain - b.shift_row_shift_pr_penalty * pr,
            ],
            [
                b.base_payoff - b.shift_row_coop_penalty - pr_cost,
                b.base_payoff
                - b.shift_row_shift_base_penalty
                - b.shift_row_shift_pr_heavy_penalty * pr,
            ],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def discharge_coordination_game(gp: GameParams) -> TwoPlayerGame:
    """Discharge coordination: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    b = gp.behavior
    d_excess = max(0.0, gp.discharge_delay - b.base_payoff)
    benefit = b.disc_benefit_base + b.disc_benefit_slope * d_excess
    cost = b.disc_cost_base + b.disc_cost_slope * (b.base_payoff - min(b.base_payoff, d_excess))
    pr_penalty = b.disc_pr_penalty_weight * pr

    u_row = np.array(
        [
            [
                b.base_payoff + benefit - cost - pr_penalty,
                b.base_payoff - b.disc_row_coop_penalty - pr_penalty,
            ],
            [
                b.base_payoff - b.disc_row_frag_base_penalty - pr_penalty,
                b.base_payoff - b.disc_row_frag_heavy_penalty - b.disc_row_frag_pr_penalty * pr,
            ],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff + benefit - cost - pr_penalty,
                b.base_payoff - b.disc_col_coop_penalty - pr_penalty,
            ],
            [
                b.base_payoff - b.disc_col_frag_base_penalty - pr_penalty,
                b.base_payoff - b.disc_col_frag_heavy_penalty - b.disc_col_frag_pr_penalty * pr,
            ],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def governance_integration_game(gp: GameParams) -> TwoPlayerGame:
    """Governance integration: integrate 'I' vs separate 'S'."""
    pr = gp.pressure
    ps = gp.political_salience
    b = gp.behavior

    safety_gain = b.gov_safety_gain_base + b.gov_safety_gain_slope * (pr - b.base_payoff)
    integration_cost = b.gov_int_cost_base + b.gov_int_cost_slope * ps
    fragmentation_risk = b.gov_frag_risk_base + b.gov_frag_risk_slope * pr

    u_row = np.array(
        [
            [
                b.base_payoff + safety_gain - integration_cost,
                b.base_payoff - b.gov_row_safety_penalty - integration_cost,
            ],
            [
                b.base_payoff + b.gov_row_frag_bonus - fragmentation_risk,
                b.base_payoff - b.gov_row_frag_penalty - fragmentation_risk,
            ],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff + safety_gain - b.gov_col_safety_penalty_1,
                b.base_payoff - b.gov_col_safety_penalty_2,
            ],
            [b.base_payoff - b.gov_col_frag_penalty_1, b.base_payoff - b.gov_col_frag_penalty_2],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def aged_care_interface_game(gp: GameParams) -> TwoPlayerGame:
    """Aged Care interface: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    b = gp.behavior
    # Payoffs influenced by pressure and discharge delay
    coord_benefit = b.aged_coord_benefit_base + b.aged_coord_benefit_slope * (
        gp.discharge_delay - b.base_payoff
    )
    frag_cost = b.aged_frag_cost_weight * pr

    u_row = np.array(
        [[b.base_payoff + coord_benefit, b.base_payoff], [b.base_payoff, b.base_payoff - frag_cost]]
    )
    u_col = np.array(
        [[b.base_payoff + coord_benefit, b.base_payoff], [b.base_payoff, b.base_payoff - frag_cost]]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def ndis_interface_game(gp: GameParams) -> TwoPlayerGame:
    """NDIS interface: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    b = gp.behavior
    coord_benefit = b.ndis_coord_benefit_base + b.ndis_coord_benefit_slope * (
        gp.discharge_delay - b.base_payoff
    )
    frag_cost = b.ndis_frag_cost_weight * pr

    u_row = np.array(
        [[b.base_payoff + coord_benefit, b.base_payoff], [b.base_payoff, b.base_payoff - frag_cost]]
    )
    u_col = np.array(
        [[b.base_payoff + coord_benefit, b.base_payoff], [b.base_payoff, b.base_payoff - frag_cost]]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def coding_audit_game(gp: GameParams) -> TwoPlayerGame:
    """Coding/Audit game: Provider Honest 'H' vs Upcode 'U'; Auditor Light 'L' vs Tight 'T'."""
    eg = gp.efficiency_gap
    ap = gp.audit_pressure
    b = gp.behavior

    # Provider payoff (Row)
    # Upcoding gain increases with efficiency gap
    upcode_gain = b.coding_upcode_gain_base + b.coding_upcode_gain_slope * eg
    penalty = b.coding_penalty_weight * ap

    u_row = np.array(
        [
            [b.base_payoff, b.base_payoff],  # Honest
            [b.base_payoff + upcode_gain, b.base_payoff + upcode_gain - penalty],  # Upcode
        ]
    )

    # Auditor payoff (Col)
    # Tight audit has cost but catches upcoding
    audit_cost = b.coding_audit_cost
    recovery = b.coding_recovery_weight * eg

    u_col = np.array(
        [
            [b.base_payoff, b.base_payoff - audit_cost],  # Light
            [b.base_payoff, b.base_payoff - audit_cost + recovery],  # Tight
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("H", "U"), col_actions=("L", "T"))


def compliance_game(gp: GameParams) -> TwoPlayerGame:
    """Compliance game: 'T' tight vs 'L' light."""
    ai = gp.audit_pressure
    eg = gp.efficiency_gap
    b = gp.behavior

    # Tight compliance reduces leakage but increases admin cost.
    leakage = b.comp_leakage_base + b.comp_leakage_slope * eg
    admin = b.comp_admin_base + b.comp_admin_slope * ai

    u_row = np.array(
        [
            [b.base_payoff - admin + b.comp_row_tight_bonus, b.base_payoff - admin],
            [b.base_payoff + leakage, b.base_payoff + leakage - b.comp_row_light_penalty * ai],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [
                b.base_payoff - b.comp_col_tight_penalty,
                b.base_payoff - b.comp_col_tight_ai_penalty * ai,
            ],
            [
                b.base_payoff - leakage,
                b.base_payoff - b.comp_col_tight_ai_penalty * ai + b.comp_col_light_base_bonus,
            ],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("T", "L"), col_actions=("T", "L"))


def venue_shifting_game(gp: GameParams) -> TwoPlayerGame:
    """Venue shifting game: LHN chooses ABF 'A' vs Block 'B'; Cth chooses Flexible 'F' vs Strict 'S'."""
    pr = gp.pressure
    eg = gp.efficiency_gap
    b = gp.behavior

    # Gain from shifting to Block increases when efficiency gap or pressure is high (cap avoidance)
    shift_gain = (
        b.venue_shift_gain_base
        + b.venue_shift_gain_eg_weight * eg
        + b.venue_shift_gain_pr_weight * (pr - b.base_payoff)
    )
    strict_penalty = b.venue_strict_penalty
    enforcement_cost = b.venue_enforce_cost

    u_row = np.array(
        [
            [b.base_payoff, b.base_payoff],  # ABF (Baseline)
            [b.base_payoff + shift_gain, b.base_payoff + shift_gain - strict_penalty],  # Block
        ]
    )

    u_col = np.array(
        [
            [b.base_payoff, b.base_payoff - enforcement_cost],  # Flexible
            [
                b.base_payoff - b.venue_col_strict_penalty_weight * shift_gain,
                b.base_payoff - enforcement_cost + b.venue_col_strict_base_bonus,
            ],  # Strict (Reduces 'leakage' gain)
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("A", "B"), col_actions=("F", "S"))


def competition_game(gp: GameParams) -> TwoPlayerGame:
    """Competition game between two neighboring LHNs.

    They compete for a fixed pool of workforce (locums) and elective volume.

    Actions:
        M: Maintain (Baseline investment/marketing)
        A: Aggressive (Aggressive hiring/marketing to capture volume)
    """
    pr = gp.pressure
    b = gp.behavior

    # Aggressive move captures volume but increases costs and drains neighbor
    capture_gain = b.comp_capture_base + b.comp_capture_slope * gp.cannibalization_beta
    cost_of_aggression = b.comp_cost_base + b.comp_cost_slope * pr

    # (M, M): Baseline stability
    # (A, M): LHN 1 drains LHN 2
    # (M, A): LHN 2 drains LHN 1
    # (A, A): Both spend high costs, neutral capture (Prisoners Dilemma style)

    u_row = np.array(
        [
            [b.base_payoff, b.base_payoff - capture_gain],
            [b.base_payoff + capture_gain - cost_of_aggression, b.base_payoff - cost_of_aggression],
        ]
    )

    u_col = np.array(
        [
            [b.base_payoff, b.base_payoff + capture_gain - cost_of_aggression],
            [b.base_payoff - capture_gain, b.base_payoff - cost_of_aggression],
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("M", "A"), col_actions=("M", "A"))


def renegotiation_game(gp: GameParams, _clock: int) -> TwoPlayerGame:
    """High-stakes Hold-Up game at the 5-year Agreement expiry.

    Players:
        Row: Commonwealth (Policy Principal)
        Col: State (Implementation Agent)

    Actions:
        C: Concede (Offer higher alpha/funding share)
        E: Enforce (Stick to strict 45% / efficient price target)

        A: Agree (Accept terms)
        H: Hold-Up (Threaten walk-away/service failure)
    """
    pr = gp.pressure
    b = gp.behavior

    # Commonwealth wants to minimize share but avoid political fallout of a 'Crisis'
    cth_fallout_cost = b.reneg_cth_fallout_weight * pr
    state_failure_cost = b.reneg_state_failure_weight * pr

    # (Enforce, Agree): Status Quo / Commonwealth Win
    # (Concede, Agree): Smooth Transition / Moderate Share Increase
    # (Enforce, Hold-Up): Crisis / Political Chaos
    # (Concede, Hold-Up): State Win / Max Share Increase

    u_row = np.array(
        [
            [
                b.base_payoff - b.reneg_concede_agree_cost,
                b.base_payoff - b.reneg_concede_holdup_cost,
            ],  # Concede: low cost if agree, higher cost if state still holds up
            [
                b.base_payoff,
                b.base_payoff - cth_fallout_cost,
            ],  # Enforce: zero cost if agree, MAX cost if hold-up triggers fallout
        ]
    )

    u_col = np.array(
        [
            [
                b.base_payoff + b.reneg_concede_agree_gain,
                b.base_payoff + b.reneg_concede_holdup_gain,
            ],  # Concede: Gain share if agree, MAX gain if hold-up forces even more
            [
                b.base_payoff,
                b.base_payoff - state_failure_cost,
            ],  # Enforce: Neutral if agree, BAD if hold-up leads to failure
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "E"), col_actions=("A", "H"))
