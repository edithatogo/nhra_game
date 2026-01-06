"""JAX-native Game Payload Definitions.

Optimized versions of subgame matrices for use in differentiable rollouts.
"""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
from beartype import beartype
from flax import struct
from jaxtyping import Array, Float

from nhra_gt.domain.state import BehavioralParamsJax


@struct.dataclass
class GameParamsJax:
    """Parameters passed to JAX-native subgame matrix generators."""

    pressure: Any
    efficiency_gap: Any
    discharge_delay: Any
    political_salience: Any
    audit_pressure: Any
    cost_shifting_intensity: Any
    political_capital: Any
    behavior: BehavioralParamsJax = struct.field(default_factory=BehavioralParamsJax)


@beartype
def renegotiation_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """JAX-native renegotiation game.

    Returns (u_row, u_col) matrices.
    Actions: Row(C, E), Col(A, H).
    """
    pr = gp.pressure
    b = gp.behavior
    cth_fallout_cost = b.reneg_cth_fallout_weight * pr
    state_failure_cost = b.reneg_state_failure_weight * pr

    u_row = jnp.array(
        [
            [
                b.base_payoff - b.reneg_concede_agree_cost,
                b.base_payoff - b.reneg_concede_holdup_cost,
            ],
            [b.base_payoff, b.base_payoff - cth_fallout_cost],
        ]
    )

    u_col = jnp.array(
        [
            [
                b.base_payoff + b.reneg_concede_agree_gain,
                b.base_payoff + b.reneg_concede_holdup_gain,
            ],
            [b.base_payoff, b.base_payoff - state_failure_cost],
        ]
    )

    return u_row, u_col


@beartype
def definition_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """Actions: Row(R, E), Col(R, E)."""
    pr, eg, ps = gp.pressure, gp.efficiency_gap, gp.political_salience
    b = gp.behavior

    realism_benefit = (
        b.def_realism_benefit_base
        + b.def_realism_eg_weight * eg
        + b.def_realism_pr_weight * (pr - b.base_payoff)
    )
    realism_cost = b.def_realism_cost_base + b.def_realism_ps_weight * ps
    strict_benefit = b.def_strict_benefit_base + b.def_strict_ps_weight * ps
    strict_cost = b.def_strict_cost_base + b.def_strict_pr_weight * pr

    u_row = jnp.array(
        [
            [
                b.base_payoff + realism_benefit - realism_cost,
                b.base_payoff - b.def_row_realism_offset - realism_cost,
            ],
            [
                b.base_payoff + strict_benefit - strict_cost,
                b.base_payoff - b.def_row_strict_offset - strict_cost,
            ],
        ]
    )
    u_col = jnp.array(
        [
            [
                b.base_payoff + realism_benefit - b.def_col_realism_offset,
                b.base_payoff - b.def_col_realism_cost,
            ],
            [b.base_payoff - b.def_col_strict_cost_1, b.base_payoff - b.def_col_strict_cost_2],
        ]
    )
    return u_row, u_col


@beartype
def bargaining_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """Bargaining game: 'A' agree to converge vs 'D' defer/escalate."""
    pr, ps, pc = gp.pressure, gp.political_salience, gp.political_capital
    b = gp.behavior

    converge_gain = (
        b.barg_converge_gain_base
        + b.barg_converge_pr_weight * (pr - b.base_payoff)
        + b.barg_converge_pc_weight * pc
    )
    conflict_cost = b.barg_conflict_cost_base + b.barg_conflict_pr_weight * pr
    narrative_gain = b.barg_narrative_gain_base + b.barg_narrative_ps_weight * ps

    u_row = jnp.array(
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
        ]
    )
    u_col = jnp.array(
        [
            [
                b.base_payoff + converge_gain - b.barg_col_converge_ps_penalty * ps,
                b.base_payoff
                - b.barg_col_converge_base_penalty
                - b.barg_col_converge_pr_penalty * pr,
            ],
            [b.base_payoff - b.barg_col_narrative_penalty, b.base_payoff - conflict_cost],
        ]
    )
    return u_row, u_col


@beartype
def cost_shifting_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """Cost shifting game: invest upstream 'I' vs shift downstream 'S'."""
    pr, eg, csi = gp.pressure, gp.efficiency_gap, gp.cost_shifting_intensity
    b = gp.behavior

    coop_gain = b.shift_coop_gain_base + b.shift_coop_eg_weight * (b.base_payoff - eg)
    shift_gain = b.shift_gain_base + b.shift_eg_weight * eg + b.shift_csi_weight * csi
    pr_cost = b.shift_pr_cost_weight * pr

    u_row = jnp.array(
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
        ]
    )
    u_col = jnp.array(
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
        ]
    )
    return u_row, u_col
