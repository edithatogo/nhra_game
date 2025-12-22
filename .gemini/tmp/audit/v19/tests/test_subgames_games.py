from __future__ import annotations

from nhra_game_theory.subgames.games import (
    GameParams,
    bargaining_game,
    compliance_game,
    cost_shifting_game,
    definition_game,
    discharge_coordination_game,
    governance_integration_game,
)
from nhra_game_theory.subgames.nash import all_nash


def test_each_game_has_equilibrium() -> None:
    gp = GameParams(
        pressure=1.2,
        efficiency_gap=0.3,
        discharge_delay=1.1,
        political_salience=0.4,
        audit_pressure=0.5,
    )
    games = [
        definition_game(gp),
        bargaining_game(gp),
        cost_shifting_game(gp),
        discharge_coordination_game(gp),
        governance_integration_game(gp),
        compliance_game(gp),
    ]
    for g in games:
        eqs = all_nash(g)
        assert len(eqs) >= 1
