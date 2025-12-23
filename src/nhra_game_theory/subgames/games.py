from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nhra_game_theory.subgames.nash import TwoPlayerGame


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
    u_row = np.array([
        [1.0 + realism_benefit - realism_cost, 1.0 - 0.15 - realism_cost],
        [1.0 + strict_benefit - strict_cost, 1.0 - 0.45 - strict_cost],
    ], dtype=float)
    u_col = np.array([
        [1.0 + realism_benefit - 0.15, 1.0 - 0.20],
        [1.0 - 0.35, 1.0 - 0.55],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("R", "E"), col_actions=("R", "E"))


def bargaining_game(gp: GameParams) -> TwoPlayerGame:
    """Bargaining game: 'A' agree to converge vs 'D' defer/escalate.

    Actions:
        A: agree / converge (moves nominal share toward target)
        D: defer / escalate (slow movement; higher conflict cost under pressure)
    """
    pr = gp.pressure
    ps = gp.political_salience

    converge_gain = 0.45 + 0.25 * (pr - 1.0)
    conflict_cost = 0.55 + 0.90 * pr
    narrative_gain = 0.25 + 0.50 * ps

    u_row = np.array([
        [1.0 + converge_gain - 0.10 * ps, 1.0 - 0.25 - 0.15 * pr],
        [1.0 + narrative_gain - 0.10 * pr, 1.0 - conflict_cost],
    ], dtype=float)
    u_col = np.array([
        [1.0 + converge_gain - 0.05 * ps, 1.0 - 0.30 - 0.20 * pr],
        [1.0 - 0.20, 1.0 - conflict_cost],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("A", "D"), col_actions=("A", "D"))


def cost_shifting_game(gp: GameParams) -> TwoPlayerGame:
    """Cost shifting game: invest upstream 'I' vs shift downstream 'S'."""
    pr = gp.pressure
    eg = gp.efficiency_gap

    coop_gain = 0.55 + 0.45 * (1.0 - eg)
    shift_gain = 0.35 + 0.75 * eg
    pr_cost = 0.65 * pr

    u_row = np.array([
        [1.0 + coop_gain - pr_cost, 1.0 - 0.25 - pr_cost],
        [1.0 + shift_gain - 0.35 * pr, 1.0 - 0.60 - 1.00 * pr],
    ], dtype=float)
    u_col = np.array([
        [1.0 + coop_gain - pr_cost, 1.0 + shift_gain - 0.35 * pr],
        [1.0 - 0.25 - pr_cost, 1.0 - 0.60 - 1.00 * pr],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def discharge_coordination_game(gp: GameParams) -> TwoPlayerGame:
    """Discharge coordination: coordinate 'C' vs fragment 'F'."""
    pr = gp.pressure
    d_excess = max(0.0, gp.discharge_delay - 1.0)
    benefit = 0.70 + 0.80 * d_excess
    cost = 0.30 + 0.10 * (1.0 - min(1.0, d_excess))
    pr_penalty = 0.45 * pr

    u_row = np.array([
        [1.0 + benefit - cost - pr_penalty, 1.0 - 0.40 - pr_penalty],
        [1.0 - 0.25 - pr_penalty, 1.0 - 0.70 - 1.10 * pr],
    ], dtype=float)
    u_col = np.array([
        [1.0 + benefit - cost - pr_penalty, 1.0 - 0.35 - pr_penalty],
        [1.0 - 0.25 - pr_penalty, 1.0 - 0.70 - 1.00 * pr],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("C", "F"), col_actions=("C", "F"))


def governance_integration_game(gp: GameParams) -> TwoPlayerGame:
    """Governance integration: integrate 'I' vs separate 'S'."""
    pr = gp.pressure
    ps = gp.political_salience

    safety_gain = 0.55 + 0.35 * (pr - 1.0)
    integration_cost = 0.20 + 0.35 * ps
    fragmentation_risk = 0.40 + 0.60 * pr

    u_row = np.array([
        [1.0 + safety_gain - integration_cost, 1.0 - 0.25 - integration_cost],
        [1.0 + 0.10 - fragmentation_risk, 1.0 - 0.45 - fragmentation_risk],
    ], dtype=float)
    u_col = np.array([
        [1.0 + safety_gain - 0.10, 1.0 - 0.20],
        [1.0 - 0.35, 1.0 - 0.55],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("I", "S"), col_actions=("I", "S"))


def compliance_game(gp: GameParams) -> TwoPlayerGame:
    """Compliance game: 'T' tight vs 'L' light."""
    ai = gp.audit_pressure
    eg = gp.efficiency_gap

    # Tight compliance reduces leakage but increases admin cost.
    leakage = 0.40 + 0.70 * eg
    admin = 0.18 + 0.45 * ai

    u_row = np.array([
        [1.0 - admin + 0.15, 1.0 - admin],
        [1.0 + leakage, 1.0 + leakage - 0.80 * ai],
    ], dtype=float)
    u_col = np.array([
        [1.0 - 0.10, 1.0 - 0.35 * ai],
        [1.0 - leakage, 1.0 - 0.35 * ai + 0.20],
    ], dtype=float)

    return TwoPlayerGame(u_row=u_row, u_col=u_col, row_actions=("T", "L"), col_actions=("T", "L"))
