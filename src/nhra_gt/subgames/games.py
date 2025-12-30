from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nhra_gt.subgames.nash import TwoPlayerGame


@dataclass(frozen=True)
class GameParams:
    """Inputs used to parameterise stage games (dimensionless indices).

    Notes:
        - pressure: system pressure index (>=~0.8 typical)
        - efficiency_gap: divergence between input costs and NEP indexation (0..~0.6)
        - discharge_delay: multiplier relative to baseline (1.0 = baseline)
        - political_salience: higher values favour narrative simplicity and bounded commitment
        - audit_pressure: higher values increase compliance scrutiny
    """

    pressure: float
    efficiency_gap: float
    discharge_delay: float
    political_salience: float
    audit_pressure: float
    cost_shifting_intensity: float
    political_capital: float


def definition_game(gp: GameParams) -> TwoPlayerGame:
    """Definition game: 'R' realism vs 'E' strict efficient-price framing.

    Row player represents the policy narrative / Commonwealth framing.
    Column player represents the State insistence / implementation reality.

    Actions:
        R: realism (acknowledge cost reality; reduce efficiency gap drift)
        E: strict efficient-price framing (efficiency narrative; gap drifts upward)
    """
    pr = gp.pressure
    eg = gp.efficiency_gap
    ps = gp.political_salience

    # Realism has fiscal and political costs but stabilises pressure.
    realism_benefit = 0.5 + 0.8 * eg + 0.4 * (pr - 1.0)
    realism_cost = 0.25 + 0.35 * ps

    strict_benefit = 0.35 + 0.45 * ps
    strict_cost = 0.30 + 0.50 * pr

    # Payoffs (R vs E)
    u_row = np.array(
        [
            [1.0 + realism_benefit - realism_cost, 1.0 - 0.15 - realism_cost],
            [1.0 + strict_benefit - strict_cost, 1.0 - 0.45 - strict_cost],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 + realism_benefit - 0.15, 1.0 - 0.20],
            [1.0 - 0.35, 1.0 - 0.55],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("R", "E"), col_actions=("R", "E"))


def bargaining_game(gp: GameParams) -> TwoPlayerGame:
    """Bargaining game: 'A' agree to converge vs 'D' defer/escalate.

    Actions:
        A: agree / converge (moves nominal share toward target)
        D: defer / escalate (slow movement; higher conflict cost under pressure)
    """
    pr = gp.pressure
    ps = gp.political_salience
    pc = gp.political_capital

    # Political capital boosts the effectiveness of agreement (v25 re-integration)
    converge_gain = 0.45 + 0.25 * (pr - 1.0) + 0.20 * pc
    conflict_cost = 0.55 + 0.90 * pr
    narrative_gain = 0.25 + 0.50 * ps

    u_row = np.array(
        [
            [1.0 + converge_gain - 0.10 * ps, 1.0 - 0.25 - 0.15 * pr],
            [1.0 + narrative_gain - 0.10 * pr, 1.0 - conflict_cost],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 + converge_gain - 0.05 * ps, 1.0 - 0.30 - 0.20 * pr],
            [1.0 - 0.20, 1.0 - conflict_cost],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("A", "D"), col_actions=("A", "D"))


def cost_shifting_game(gp: GameParams) -> TwoPlayerGame:
    """Cost shifting game: invest upstream 'I' vs shift downstream 'S'."""
    pr = gp.pressure
    eg = gp.efficiency_gap
    csi = gp.cost_shifting_intensity

    coop_gain = 0.55 + 0.45 * (1.0 - eg)
    # CSI increases the payoff of shifting relative to investing
    # Boosted to 1.0 to ensure sensitivity visibility
    shift_gain = 0.35 + 0.75 * eg + 1.0 * csi
    pr_cost = 0.65 * pr

    u_row = np.array(
        [
            [1.0 + coop_gain - pr_cost, 1.0 - 0.25 - pr_cost],
            [1.0 + shift_gain - 0.35 * pr, 1.0 - 0.60 - 1.00 * pr],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 + coop_gain - pr_cost, 1.0 + shift_gain - 0.35 * pr],
            [1.0 - 0.25 - pr_cost, 1.0 - 0.60 - 1.00 * pr],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def discharge_coordination_game(gp: GameParams) -> TwoPlayerGame:
    """Discharge coordination: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    d_excess = max(0.0, gp.discharge_delay - 1.0)
    benefit = 0.70 + 0.80 * d_excess
    cost = 0.30 + 0.10 * (1.0 - min(1.0, d_excess))
    pr_penalty = 0.45 * pr

    u_row = np.array(
        [
            [1.0 + benefit - cost - pr_penalty, 1.0 - 0.40 - pr_penalty],
            [1.0 - 0.25 - pr_penalty, 1.0 - 0.70 - 1.10 * pr],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 + benefit - cost - pr_penalty, 1.0 - 0.35 - pr_penalty],
            [1.0 - 0.25 - pr_penalty, 1.0 - 0.70 - 1.00 * pr],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def governance_integration_game(gp: GameParams) -> TwoPlayerGame:
    """Governance integration: integrate 'I' vs separate 'S'."""
    pr = gp.pressure
    ps = gp.political_salience

    safety_gain = 0.55 + 0.35 * (pr - 1.0)
    integration_cost = 0.20 + 0.35 * ps
    fragmentation_risk = 0.40 + 0.60 * pr

    u_row = np.array(
        [
            [1.0 + safety_gain - integration_cost, 1.0 - 0.25 - integration_cost],
            [1.0 + 0.10 - fragmentation_risk, 1.0 - 0.45 - fragmentation_risk],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 + safety_gain - 0.10, 1.0 - 0.20],
            [1.0 - 0.35, 1.0 - 0.55],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def aged_care_interface_game(gp: GameParams) -> TwoPlayerGame:
    """Aged Care interface: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    # Payoffs influenced by pressure and discharge delay
    coord_benefit = 0.6 + 0.4 * (gp.discharge_delay - 1.0)
    frag_cost = 0.5 * pr

    u_row = np.array([[1.0 + coord_benefit, 1.0], [1.0, 1.0 - frag_cost]])
    u_col = np.array([[1.0 + coord_benefit, 1.0], [1.0, 1.0 - frag_cost]])

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def ndis_interface_game(gp: GameParams) -> TwoPlayerGame:
    """NDIS interface: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    coord_benefit = 0.5 + 0.5 * (gp.discharge_delay - 1.0)
    frag_cost = 0.6 * pr

    u_row = np.array([[1.0 + coord_benefit, 1.0], [1.0, 1.0 - frag_cost]])
    u_col = np.array([[1.0 + coord_benefit, 1.0], [1.0, 1.0 - frag_cost]])

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def coding_audit_game(gp: GameParams) -> TwoPlayerGame:
    """Coding/Audit game: Provider Honest 'H' vs Upcode 'U'; Auditor Light 'L' vs Tight 'T'."""
    eg = gp.efficiency_gap
    ap = gp.audit_pressure

    # Provider payoff (Row)
    # Upcoding gain increases with efficiency gap
    upcode_gain = 0.3 + 0.7 * eg
    penalty = 0.8 * ap

    u_row = np.array(
        [
            [1.0, 1.0],  # Honest
            [1.0 + upcode_gain, 1.0 + upcode_gain - penalty],  # Upcode
        ]
    )

    # Auditor payoff (Col)
    # Tight audit has cost but catches upcoding
    audit_cost = 0.2
    recovery = 0.4 * eg

    u_col = np.array(
        [
            [1.0, 1.0 - audit_cost],  # Light
            [1.0, 1.0 - audit_cost + recovery],  # Tight
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("H", "U"), col_actions=("L", "T"))


def compliance_game(gp: GameParams) -> TwoPlayerGame:
    """Compliance game: 'T' tight vs 'L' light."""
    ai = gp.audit_pressure
    eg = gp.efficiency_gap

    # Tight compliance reduces leakage but increases admin cost.
    leakage = 0.40 + 0.70 * eg
    admin = 0.18 + 0.45 * ai

    u_row = np.array(
        [
            [1.0 - admin + 0.15, 1.0 - admin],
            [1.0 + leakage, 1.0 + leakage - 0.80 * ai],
        ],
        dtype=float,
    )
    u_col = np.array(
        [
            [1.0 - 0.10, 1.0 - 0.35 * ai],
            [1.0 - leakage, 1.0 - 0.35 * ai + 0.20],
        ],
        dtype=float,
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("T", "L"), col_actions=("T", "L"))


def venue_shifting_game(gp: GameParams) -> TwoPlayerGame:
    """Venue shifting game: LHN chooses ABF 'A' vs Block 'B'; Cth chooses Flexible 'F' vs Strict 'S'."""
    pr = gp.pressure
    eg = gp.efficiency_gap

    # Gain from shifting to Block increases when efficiency gap or pressure is high (cap avoidance)
    shift_gain = 0.25 + 0.5 * eg + 0.3 * (pr - 1.0)
    strict_penalty = 0.45
    enforcement_cost = 0.15

    u_row = np.array(
        [
            [1.0, 1.0],  # ABF (Baseline)
            [1.0 + shift_gain, 1.0 + shift_gain - strict_penalty],  # Block
        ]
    )

    u_col = np.array(
        [
            [1.0, 1.0 - enforcement_cost],  # Flexible
            [
                1.0 - 0.15 * shift_gain,
                1.0 - enforcement_cost + 0.10,
            ],  # Strict (Reduces 'leakage' gain)
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("A", "B"), col_actions=("F", "S"))


def competition_game(gp: GameParams, cannibalization_beta: float = 0.1) -> TwoPlayerGame:
    """
    Competition game between two neighboring LHNs.
    They compete for a fixed pool of workforce (locums) and elective volume.

    Actions:
        M: Maintain (Baseline investment/marketing)
        A: Aggressive (Aggressive hiring/marketing to capture volume)
    """
    pr = gp.pressure

    # Aggressive move captures volume but increases costs and drains neighbor
    capture_gain = 0.4 + 0.6 * cannibalization_beta
    cost_of_aggression = 0.3 + 0.2 * pr

    # (M, M): Baseline stability
    # (A, M): LHN 1 drains LHN 2
    # (M, A): LHN 2 drains LHN 1
    # (A, A): Both spend high costs, neutral capture (Prisoners Dilemma style)

    u_row = np.array(
        [
            [1.0, 1.0 - capture_gain],
            [1.0 + capture_gain - cost_of_aggression, 1.0 - cost_of_aggression],
        ]
    )

    u_col = np.array(
        [
            [1.0, 1.0 + capture_gain - cost_of_aggression],
            [1.0 - capture_gain, 1.0 - cost_of_aggression],
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("M", "A"), col_actions=("M", "A"))


def renegotiation_game(gp: GameParams, clock: int) -> TwoPlayerGame:
    """
    High-stakes Hold-Up game at the 5-year Agreement expiry.

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

    # Commonwealth wants to minimize share but avoid political fallout of a 'Crisis'
    cth_fallout_cost = 0.8 * pr
    state_failure_cost = 0.6 * pr

    # (Enforce, Agree): Status Quo / Commonwealth Win
    # (Concede, Agree): Smooth Transition / Moderate Share Increase
    # (Enforce, Hold-Up): Crisis / Political Chaos
    # (Concede, Hold-Up): State Win / Max Share Increase

    u_row = np.array(
        [
            [
                1.0 - 0.1,
                1.0 - 0.3,
            ],  # Concede: low cost if agree, higher cost if state still holds up
            [
                1.0,
                1.0 - cth_fallout_cost,
            ],  # Enforce: zero cost if agree, MAX cost if hold-up triggers fallout
        ]
    )

    u_col = np.array(
        [
            [
                1.0 + 0.2,
                1.0 + 0.5,
            ],  # Concede: Gain share if agree, MAX gain if hold-up forces even more
            [
                1.0,
                1.0 - state_failure_cost,
            ],  # Enforce: Neutral if agree, BAD if hold-up leads to failure
        ]
    )

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "E"), col_actions=("A", "H"))
