from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from nhra_game_theory import legacy_engine as v8
from nhra_game_theory.plotting import (
    build_games_graph,
    plot_strategy_heatmap,
    plot_trajectory,
    render_games_graph_interactive,
    tornado_from_rankcorr,
)


def test_nep_series_increases() -> None:
    years = [2025, 2026, 2027]
    p = v8.Params(nep_per_nwau_start=1.0, nep_annual_growth=0.05, representative_nwau=1.5)
    df = v8.nep_series(years, p)
    assert list(df["year"]) == years
    assert df["nep_per_nwau"].iloc[2] > df["nep_per_nwau"].iloc[0]
    assert float(df["efficient_payment"].iloc[0]) == float(
        df["nep_per_nwau"].iloc[0] * p.representative_nwau
    )


def test_interventions_cover_branches() -> None:
    base = v8.Params()
    # cover apply_intervention branches
    for iv in [
        "pooled",
        "integration",
        "indexation",
        "discharge",
        "workforce",
        "cap",
        "audit_relief",
    ]:
        p2 = v8.apply_intervention(base, iv)
        assert isinstance(p2, v8.Params)
    # scenario_params chaining
    p3 = v8.scenario_params(base, ["pooled", "discharge"])
    assert isinstance(p3, v8.Params)
    # unknown intervention should be a no-op (default fall-through)
    pu = v8.apply_intervention(base, "unknown")
    assert pu == base

    # partial strength
    p0 = v8.apply_intervention_partial(base, "pooled", strength=0.0)
    p1 = v8.apply_intervention_partial(base, "pooled", strength=1.0)
    full = v8.apply_intervention(base, "pooled")
    assert p0 == base
    assert p1.cost_shifting_intensity == full.cost_shifting_intensity


def test_decide_strategies_and_step_smoke() -> None:
    rng = np.random.default_rng(1)
    p = v8.Params()
    s = v8.baseline_state(2025, p)
    strat = v8.decide_strategies(s, p, rng)
    # minimal labels for game-theory map
    for node in ["BARG", "DEF", "SHIFT", "DISC", "GOV", "COMP", "SIGNAL"]:
        assert node in strat
        assert isinstance(strat[node], str)
        assert 1 <= len(strat[node]) <= 3

    s2 = v8.step(s, p, strat, rng)
    assert s2.year == s.year + 1
    assert 0.0 <= s2.within4 <= 1.0
    assert s2.offload_min >= 0.0

    rr = v8.relative_risk(s2.pressure, s2.offload_min, p)
    assert rr > 0.0


def test_sensitivity_helpers() -> None:
    years = [2025, 2026, 2027]
    base = v8.Params()

    scen = v8.scenario_summary(
        years,
        base,
        {"baseline": [], "bundle": ["pooled", "discharge", "indexation"]},
        seed=1,
        n_mc=20,
    )
    assert len(scen) == 2

    grid = {"noise_sd": [0.01, 0.03], "discharge_delay_base": [0.8, 1.2]}
    ow = v8.one_way_sensitivity(years, base, grid, seed=1, n_mc=15)
    assert not ow.empty

    psa = v8.probabilistic_sensitivity(years, base, ["pooled"], seed=1, n_param=10, n_mc=10)
    assert len(psa) == 10

    samp = v8.sensitivity_sample(base, n=20, seed=1)
    assert len(samp) == 20
    assert "noise_sd" in samp.columns

    traj, _ = v8.run_hybrid(years, base, seed=1, n_mc=10)
    summ = v8.summarise_outcome(traj)
    assert "rr_2030" in summ


def test_plotting_functions(tmp_path: Path) -> None:
    # trajectory plots (with and without bands)
    df = pd.DataFrame(
        {
            "year": [2025, 2026, 2027],
            "pressure_mean": [1.0, 1.1, 1.2],
            "pressure_p10": [0.9, 1.0, 1.1],
            "pressure_p90": [1.1, 1.2, 1.3],
        }
    )
    out1 = tmp_path / "traj.png"
    plot_trajectory(df, "pressure_mean", "Pressure", out1, "pressure_p10", "pressure_p90")
    assert out1.exists() and out1.stat().st_size > 0

    out1b = tmp_path / "traj2.png"
    plot_trajectory(df, "pressure_mean", "Pressure", out1b)
    assert out1b.exists() and out1b.stat().st_size > 0

    # strategy heatmap expects columns: year, game, strategy, share
    freq = pd.DataFrame(
        {
            "year": [2025, 2025, 2026, 2026],
            "game": ["BARG", "BARG", "BARG", "BARG"],
            "strategy": ["E", "A", "E", "A"],
            "share": [0.6, 0.4, 0.55, 0.45],
        }
    )
    out2 = tmp_path / "heat.png"
    plot_strategy_heatmap(freq, out2)
    assert out2.exists() and out2.stat().st_size > 0

    # tornado expects parameter columns and outcome column
    df2 = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "b": [1.0, 1.0, 1.0, 1.0],
            "rr_end": [0.2, 0.25, 0.35, 0.4],
        }
    )
    out3 = tmp_path / "tornado.png"
    tornado_from_rankcorr(df2, outcome_col="rr_end", params=["a", "b"], outpath=out3, topk=2)
    assert out3.exists() and out3.stat().st_size > 0

    # network graph + interactive
    G = build_games_graph()
    assert G.number_of_nodes() > 5
    out4 = tmp_path / "graph.html"
    G2, html = render_games_graph_interactive(out4)
    assert html.exists() and html.stat().st_size > 0
