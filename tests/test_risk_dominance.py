import numpy as np

from nhra_gt.subgames.nash import TwoPlayerGame, all_nash, select_equilibrium


def test_risk_dominance_stag_hunt():
    # Stag Hunt
    # R/C: 0=Stag, 1=Hare
    # (S,S)=4,4; (S,H)=0,3; (H,S)=3,0; (H,H)=3,3
    u_row = np.array([[4, 0], [3, 3]])
    u_col = np.array([[4, 3], [0, 3]])

    game = TwoPlayerGame(
        u_row=u_row, u_col=u_col, row_actions=("Stag", "Hare"), col_actions=("Stag", "Hare")
    )

    eqs = all_nash(game)
    # Expect 3 eqs: (S,S), (H,H), and Mixed
    assert len(eqs) == 3

    # 1. Test Payoff Dominance (should be Stag,Stag)
    sel_pd = select_equilibrium(eqs, rule="payoff_dominant", u_row=u_row, u_col=u_col)
    # (S,S) is index 0,0 -> row=[1,0], col=[1,0]
    assert sel_pd.equilibrium.row[0] == 1.0
    assert sel_pd.equilibrium.col[0] == 1.0

    # 2. Test Risk Dominance (should be Hare,Hare)
    sel_rd = select_equilibrium(eqs, rule="risk_dominant", u_row=u_row, u_col=u_col)
    # (H,H) is index 1,1 -> row=[0,1], col=[0,1]
    assert sel_rd.equilibrium.row[1] == 1.0
    assert sel_rd.equilibrium.col[1] == 1.0


def test_risk_dominance_prisoner_dilemma():
    # PD has only one unique Nash (Defect, Defect), so Risk Dominance should pick it.
    u_row = np.array([[3, 0], [5, 1]])
    u_col = np.array([[3, 5], [0, 1]])
    # Nash is (1,1) -> (5,5) NO wait.
    # Row: if col=0(3), row=1(5). If col=1(0), row=1(1). Domstrat = 1.
    # Nash is (1,1) -> payoff (1,1).

    game = TwoPlayerGame(u_row, u_col, ("C", "D"), ("C", "D"))
    eqs = all_nash(game)
    assert len(eqs) == 1

    sel = select_equilibrium(eqs, rule="risk_dominant", u_row=u_row, u_col=u_col)
    assert sel.equilibrium.row[1] == 1.0
