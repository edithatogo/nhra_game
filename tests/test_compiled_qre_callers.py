"""Two-player QRE admission against Gambit and through compiled NHRA callers."""

from __future__ import annotations

from functools import partial

import jax
import jax.numpy as jnp
import numpy as np
import pygambit as gambit
import pytest
from scipy.optimize import brentq
from scipy.special import expit

from nhra_gt import (
    engine,
    solve_constitutional_game_jax,
    solve_constitutional_game_with_diagnostics_jax,
)
from nhra_gt.agents.jax import HeuristicAgentJax
from nhra_gt.solvers_jax import QreStatus, qre_solver_jax, solve_qualified_two_player_qre

_TOLERANCE = 1e-6
_ORACLE_BOUND = 1e-10
_DIAGNOSTIC_BOUND = 1e-12
_COST_SHIFT_POSITION = 2
_FOUR_ARRAYS = 4


def _coupled_payoffs(bias=0.35):
    return jnp.array([[0.0, 0.0], [bias, bias - 1.0]]), jnp.array([[0.0, -0.6], [0.0, 0.4]])


def _gambit_profile(payoffs, lam):
    game = gambit.Game.from_arrays(*(np.asarray(matrix) for matrix in payoffs))
    points = gambit.qre.logit_solve_lambda(game, lam, use_strategic=True)
    assert len(points) == 1
    point = points[0]
    assert point.lam == pytest.approx(lam, abs=_TOLERANCE, rel=0)
    return tuple(
        np.array([point.profile[action] for action in player.strategies]) for player in game.players
    )


@pytest.mark.parametrize("lam", [0.5, 2.0])
def test_certified_unique_branch_matches_gambit(lam):
    """Compare both ordered strategies at a converged, unique root."""
    with jax.enable_x64():
        payoffs = _coupled_payoffs()
        row, col, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=lam))(
            *payoffs
        )
        reference = _gambit_profile(payoffs, lam)
    assert diagnostics.status == QreStatus.QUALIFIED
    assert float(diagnostics.residual) <= _ORACLE_BOUND
    np.testing.assert_allclose((row, col), reference, atol=_ORACLE_BOUND, rtol=0)


def test_rectangular_branch_matches_gambit():
    """Qualify an asymmetric input with a three-action response."""
    with jax.enable_x64():
        payoffs = (
            jnp.array([[0.07, -0.10, 0.18], [0.10, 0.12, -0.22]]),
            jnp.array([[0.11, 0.05, -0.20], [-0.03, 0.19, 0.15]]),
        )
        lam = 2.0
        row, col, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=lam))(
            *payoffs
        )
        ref_row, ref_col = _gambit_profile(payoffs, lam)
    assert diagnostics.status == QreStatus.QUALIFIED
    np.testing.assert_allclose(row, ref_row, atol=_ORACLE_BOUND, rtol=0)
    np.testing.assert_allclose(col, ref_col, atol=_ORACLE_BOUND, rtol=0)


def test_opposing_responses_are_unique_outside_the_contraction_bound():
    """Certify an isolated root even when the global slope product exceeds one."""
    with jax.enable_x64():
        a, _ = _coupled_payoffs(0.10)
        b = jnp.array([[0.0, -0.98], [0.0, 0.02]])
        lam = 5.0
        row, col, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=lam))(
            a, b
        )
        reference = _gambit_profile((a, b), lam)
    assert diagnostics.status == QreStatus.QUALIFIED
    assert float(diagnostics.residual) <= _ORACLE_BOUND
    np.testing.assert_allclose((row, col), reference, atol=_ORACLE_BOUND, rtol=0)


def test_gambit_agreement_is_insufficient_when_the_game_has_multiple_roots():
    """Withhold even a converged profile that agrees with Gambit's selected branch."""
    with jax.enable_x64():
        payoff = jnp.array([[1.1, 0.0], [0.0, 1.0]])
        payoffs = (payoff, payoff.T)
        lam = 5.0
        p, q, residual = qre_solver_jax(*payoffs, lam=lam)
        row, col, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=lam))(
            *payoffs
        )
        reference = _gambit_profile(payoffs, lam)

    np.testing.assert_allclose((p, q), reference, atol=_ORACLE_BOUND, rtol=0)

    # For equal probabilities x of action zero, both responses are
    # expit(lam * (2.1 * x - 1)). A second root lies below one half.
    def difference(x):
        return expit(lam * (2.1 * x - 1)) - x

    other = brentq(difference, 0.0, 0.25)
    assert abs(difference(other)) < _DIAGNOSTIC_BOUND
    assert abs(other - float(p[0])) > _TOLERANCE
    assert float(diagnostics.residual) == float(residual) <= _ORACLE_BOUND
    assert diagnostics.status == QreStatus.BRANCH_UNQUALIFIED
    assert np.isnan(row).all()
    assert np.isnan(col).all()


def test_mixed_precision_cannot_certify_a_multiple_root_game():
    """The certificate uses common precision near the contraction boundary."""
    a = jnp.diag(jnp.array([1.5, 1.5], dtype=jnp.float16))
    b = jnp.diag(jnp.array([2.667, 2.667], dtype=jnp.float32))
    row_gain = float(np.asarray(a)[0, 0])
    col_gain = float(np.asarray(b)[0, 0])

    def composed_error(probability):
        column = expit(col_gain * (2 * probability - 1))
        return expit(row_gain * (2 * column - 1)) - probability

    # At lambda 1 the uniform root is repelling. The end-point signs give
    # two additional roots, one on each side of that uniform profile.
    assert composed_error(0.0) > 0.0 > composed_error(0.4995)
    assert composed_error(1.0) < 0.0 < composed_error(0.5005)

    p, q, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=1.0))(a, b)
    _, _, admitted = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=0.5))(a, b)
    assert float(diagnostics.residual) <= _ORACLE_BOUND
    assert diagnostics.status == QreStatus.BRANCH_UNQUALIFIED
    assert np.isnan(p).all()
    assert np.isnan(q).all()
    assert admitted.status == QreStatus.QUALIFIED


def test_reciprocal_rescaling_does_not_certify_a_multiple_root_game():
    """Use the individual log terms to cover cancellation in larger games."""
    groups = jnp.array([0, 0, 1, 1])
    within_group = groups[:, None] == groups[None, :]
    rationality = float(2**26)
    scale = np.float32(2.0**-25 * (1.0 + np.finfo(np.float32).eps))
    payoffs = scale * within_group.astype(jnp.float32)
    gain = rationality * float(scale)

    def composed_error(mass):
        other = expit(gain * (2 * mass - 1))
        return expit(gain * (2 * other - 1)) - mass

    # The mass on either action group satisfies the same scalar logit map.
    # The uniform root has a distinct root on each side.
    assert composed_error(0.0) > 0.0 > composed_error(0.4999)
    assert composed_error(1.0) < 0.0 < composed_error(0.5001)

    for inputs, lam in ((payoffs, rationality), (payoffs * rationality, 1.0)):
        row, col, diagnostics = jax.jit(
            lambda matrix, lam=lam: solve_qualified_two_player_qre(matrix, matrix, lam=lam)
        )(inputs)
        assert diagnostics.status == QreStatus.BRANCH_UNQUALIFIED
        assert float(diagnostics.residual) <= _ORACLE_BOUND
        assert np.isnan(row).all()
        assert np.isnan(col).all()


def test_underflowed_payoff_difference_cannot_certify_uniqueness():
    """Bound payoff differences before a large scale can amplify flushed terms."""
    tiny = np.finfo(np.float32).tiny
    a = tiny * jnp.array([[1.75, 1.0], [1.0, 1.75]], dtype=jnp.float32)
    b = jnp.float32(2**124) * jnp.eye(2, dtype=jnp.float32)
    lam = 5.0

    # The uniform root is exact by symmetry. Its slope product exceeds one,
    # so the finite-logit endpoint signs imply another root on each side.
    slope_product = (lam * 0.75 * float(tiny) / 2.0) * (lam * 2**124 / 2.0)
    assert slope_product > 1.0

    solve = jax.jit(solve_qualified_two_player_qre)
    row, col, diagnostics = solve(a, b)
    assert diagnostics.status == QreStatus.BRANCH_UNQUALIFIED
    assert float(diagnostics.residual) <= _ORACLE_BOUND
    assert np.isnan(row).all()
    assert np.isnan(col).all()

    zeros = jnp.zeros_like(a)
    nested = jax.jit(
        lambda u, v: solve_constitutional_game_with_diagnostics_jax(
            u, v, lambda _i, _j: (zeros, zeros)
        )
    )(a, b)
    assert np.all(nested.micro.qualified)
    assert nested.macro.status == QreStatus.BRANCH_UNQUALIFIED
    assert float(nested.macro.residual) == float(diagnostics.residual)
    assert all(np.isnan(value).all() for value in nested.solution)


@pytest.mark.parametrize("lam", [5.0, 8.0])
def test_nonconvergence_reports_original_residual(lam):
    """Uniqueness alone cannot qualify a fixed-budget iterate."""
    with jax.enable_x64():
        payoffs = _coupled_payoffs()
        _p, _q, raw_error = qre_solver_jax(*payoffs, lam=lam)
        row, col, diagnostics = jax.jit(lambda a, b: solve_qualified_two_player_qre(a, b, lam=lam))(
            *payoffs
        )
    assert diagnostics.status == QreStatus.NONCONVERGED
    assert float(diagnostics.residual) > _TOLERANCE
    np.testing.assert_allclose(diagnostics.residual, raw_error, atol=_DIAGNOSTIC_BOUND, rtol=0)
    assert np.isnan(row).all()
    assert np.isnan(col).all()


def test_nonfinite_residual_is_preserved():
    """Keep a nonfinite diagnostic and withhold its profile."""
    first, second = _coupled_payoffs()
    row, col, diagnostics = jax.jit(solve_qualified_two_player_qre)(
        first.at[0, 0].set(jnp.nan), second
    )
    assert diagnostics.status == QreStatus.NONCONVERGED
    assert np.isnan(diagnostics.residual)
    assert np.isnan(row).all()
    assert np.isnan(col).all()


def test_compiled_qualified_derivative():
    """Keep the convergent branch differentiable through admission."""

    def action_one(bias):
        row, column, _diagnostics = solve_qualified_two_player_qre(*_coupled_payoffs(bias), lam=0.5)
        return jnp.stack([row[1], column[1]])

    with jax.enable_x64():
        derivative = jax.jit(jax.jacrev(action_one))(jnp.array(0.35))
    expected = (0.12293980658424102, 0.015354354057636370)
    np.testing.assert_allclose(derivative, expected, atol=_ORACLE_BOUND, rtol=0)


@pytest.mark.parametrize(
    ("changes", "expected_residual"),
    [
        ({}, 1.2771287119406338e-5),
        (
            {"reported_pressure": 1.35, "reported_efficiency_gap": 1.10, "political_capital": 0.4},
            1.9655173409943352,
        ),
    ],
    ids=["baseline", "elevated-pressure"],
)
def test_strategic_agent_withholds_nonconverged_choices(changes, expected_residual):
    """Reject the known cost-shifting iterates, retaining the diagnostics for all games."""
    with jax.enable_x64():
        params = engine.ParamsJax()
        state = engine.baseline_state(p=params).replace(**changes)
        agent = HeuristicAgentJax(solve_nash=True)
        vector, diagnostics = jax.jit(agent.decide_with_diagnostics)(state, params)
        assert np.isnan(jax.jit(agent.decide)(state, params)).all()

        convergent = HeuristicAgentJax(solve_nash=True, lambda_qre=0.5)
        accepted, converged = jax.jit(convergent.decide_with_diagnostics)(state, params)
        np.testing.assert_array_equal(accepted, jax.jit(convergent.decide)(state, params))

    assert np.isnan(vector).all()
    assert diagnostics is not None
    np.testing.assert_array_equal(
        diagnostics.status, (QreStatus.QUALIFIED, QreStatus.QUALIFIED, QreStatus.NONCONVERGED)
    )
    residual = float(np.asarray(diagnostics.residual)[_COST_SHIFT_POSITION])
    assert residual > _TOLERANCE
    assert residual == pytest.approx(expected_residual, abs=_DIAGNOSTIC_BOUND, rel=0)
    assert converged is not None
    assert np.all(converged.qualified)
    assert np.isfinite(accepted).all()


def test_hybrid_reports_rejection_before_aggregation(monkeypatch):
    """Reject the compiled batch before producing any simulation result."""

    def unexpected_aggregation(*_args):
        pytest.fail("A strategic rollout with an unqualified result reached aggregation")

    monkeypatch.setattr(engine, "_aggregate_rollouts", unexpected_aggregation)
    with pytest.raises(
        RuntimeError, match=r"QRE nonconverged for cost shifting in rollout 1, 2025-01"
    ) as exc:
        engine.run_hybrid([2025], engine.ParamsJax(), n_mc=2, overrides={"STRATEGIC_MODE": True})
    residual = float(str(exc.value).split("Residual ")[1])
    assert residual > _TOLERANCE


def test_hybrid_aggregates_qualified_strategic_rollouts(monkeypatch):
    """Carry the qualified strategy through a compiled batch to aggregation."""
    monkeypatch.setattr(engine, "HeuristicAgentJax", partial(HeuristicAgentJax, lambda_qre=0.5))
    trajectory, _ = engine.run_hybrid(
        [2025], engine.ParamsJax(), n_mc=2, overrides={"STRATEGIC_MODE": True}
    )
    assert trajectory["year"].tolist() == [2025]
    assert np.isfinite(trajectory["pressure_mean"]).all()


def test_nested_micro_failure_blocks_macro_and_reports_micro_residual():
    """Preserve the qualified solution and reject an unqualified continuation payoff."""
    with jax.enable_x64():
        a, b = _coupled_payoffs()
        scales = jnp.array([[0.15, 0.18], [1.0, 0.22]])
        offsets = jnp.array([[0.01, 0.08], [0.04, -0.03]])
        macro = jnp.array([[0.15, -0.10], [0.02, 0.10]]), jnp.array([[0.03, 0.10], [0.22, 0.02]])

        def micro(i, j):
            return scales[i, j] * a + offsets[i, j], scales[i, j] * b - offsets[i, j]

        accepted = jax.jit(
            lambda u, v: solve_constitutional_game_with_diagnostics_jax(u, v, micro, lam=0.5)
        )(*macro)
        rejected = jax.jit(
            lambda u, v: solve_constitutional_game_with_diagnostics_jax(u, v, micro)
        )(*macro)

    row, col, state, lhn = accepted.solution
    assert np.all(accepted.micro.qualified)
    assert accepted.qualified
    assert np.isfinite(state).all()
    assert np.isfinite(lhn).all()
    reference = (0.49584625605982013, 0.5053614666636838)
    np.testing.assert_allclose((row[0], col[0]), reference, atol=_ORACLE_BOUND, rtol=0)

    np.testing.assert_array_equal(
        rejected.micro.status,
        [[QreStatus.QUALIFIED, QreStatus.QUALIFIED], [QreStatus.NONCONVERGED, QreStatus.QUALIFIED]],
    )
    assert np.asarray(rejected.micro.residual)[1, 0] == pytest.approx(
        0.6478395204117232, abs=_DIAGNOSTIC_BOUND, rel=0
    )
    assert rejected.macro.status == QreStatus.SKIPPED
    assert np.isnan(rejected.macro.residual)
    assert not rejected.qualified
    assert all(np.isnan(value).all() for value in rejected.solution)


def test_nested_macro_failure_reports_macro_residual():
    """Distinguish an attempted macro failure from a skipped macro game."""
    zero = jnp.zeros((2, 2))
    with jax.enable_x64():
        # Both macro and micro arrays use the same precision within the JIT.
        zero = zero.astype(jnp.float64)
        payoffs = _coupled_payoffs()
        result = jax.jit(
            lambda a, b: solve_constitutional_game_with_diagnostics_jax(
                a, b, lambda _i, _j: (zero, zero)
            )
        )(*payoffs)
        _p, _q, residual = qre_solver_jax(*payoffs)
    assert np.all(result.micro.qualified)
    assert result.macro.status == QreStatus.NONCONVERGED
    np.testing.assert_allclose(result.macro.residual, residual, atol=_DIAGNOSTIC_BOUND, rtol=0)
    assert not result.qualified
    assert all(np.isnan(value).all() for value in result.solution)


def test_legacy_constitutional_result_keeps_four_output_vmap_axes():
    """Qualify and mask separate batch entries without changing the legacy tree."""
    a, b = _coupled_payoffs()
    zero = jnp.zeros_like(a)

    def solve(u, v):
        return solve_constitutional_game_jax(u, v, lambda _i, _j: (zero, zero))

    batched = jax.jit(jax.vmap(solve, out_axes=(0, 0, 0, 0)))
    result = batched(jnp.stack([0.10 * a, a]), jnp.stack([0.10 * b, b]))
    assert len(result) == _FOUR_ARRAYS
    assert len(jax.tree.leaves(result)) == _FOUR_ARRAYS
    assert all(np.isfinite(value[0]).all() for value in result)
    assert all(np.isnan(value[1]).all() for value in result)
