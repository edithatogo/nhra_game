"""Streamlit dashboard for NHRA scenarios, strategy and evidence."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml

# Ensure src is in path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from nhra_gt.visualization.game_trees import (
        create_extensive_game_from_matrix,
        game_tree_graph,
    )
except ImportError:  # pragma: no cover
    create_extensive_game_from_matrix = None  # type: ignore[assignment]
    game_tree_graph = None  # type: ignore[assignment]

from nhra_gt import __version__
from nhra_gt.domain.params import Params
from nhra_gt.engine import apply_intervention, initialize_rules, summarise_outcome
from nhra_gt.game_theory.content import get_populated_registry
from nhra_gt.game_theory.ui import render_game_encyclopedia
from nhra_gt.helpers import probabilistic_sensitivity, run_hybrid
from nhra_gt.sensitivity import get_parameter_lineage, get_salib_problem, run_morris_analysis
from nhra_gt.visualization.interactive import (
    plot_agreement_cycle,
    plot_patient_choice,
    plot_phase_space,
    plot_risk_pressure,
    plot_strategic_stability,
    plot_workforce_dynamics,
)
from nhra_gt.visualization.sensitivity import plot_morris_tornado

# Constants
LITE_MC = 50
PRESSURE_LIMIT = 1.3
RISK_THRESHOLD = 0.1
SHARE_THRESHOLD = 0.03


def load_scenario_library() -> dict:
    """Load scenarios from YAML."""
    path = Path("configs/scenarios.yaml")
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f).get("scenarios", {})
    return {}


def initialize_slider_state(scenarios: dict) -> None:
    """Seed the model controls from typed runtime defaults and the steady scenario."""
    defaults = Params().flatten()
    defaults.update(scenarios.get("steady_state", {}).get("params", {}))
    for name, value in defaults.items():
        st.session_state.setdefault(name, value)


def _strategy_overrides(full_strat: bool) -> dict[str, Any]:
    overrides: dict[str, Any] = {"STRATEGIC_MODE": True} if full_strat else {}
    if st.sidebar.toggle("🧠 Expert Strategic Mode", help="Override individual game strategies."):
        st.sidebar.subheader("Strategy Overrides")
        for code, label, options in (
            ("DEF", "Definition Game", ("Auto", "R", "E")),
            ("BARG", "Bargaining Game", ("Auto", "A", "D")),
            ("SHIFT", "Cost-Shifting Game", ("Auto", "I", "S")),
            ("DISC", "Discharge Game", ("Auto", "C", "F")),
            ("COMP", "Compliance Game", ("Auto", "T", "L")),
        ):
            choice = st.sidebar.selectbox(label, options)
            if choice != "Auto":
                overrides[code] = choice
    return overrides


def prepare_share_drift_data(
    traj: pd.DataFrame, threshold: float
) -> tuple[pd.DataFrame, list[dict]]:
    """Calculate effective share drift and identify threshold breaches."""
    df = traj.copy()
    df["drift_gap"] = df["cth_nominal_mean"] - df["cth_effective_mean"]

    breaches = [
        {"year": int(row["year"]), "value": float(row["cth_effective_mean"])}
        for _, row in df.loc[df["cth_effective_mean"] < threshold].iterrows()
    ]

    return df, breaches


def rank_interventions(base_params: Params, intervention_list: list[str]) -> pd.DataFrame:
    """Ranks interventions by their impact on 2030 pressure."""
    years = list(range(2025, 2031))

    # Run Baseline
    traj_base, _ = run_hybrid(years, base_params, n_mc=50, seed=42)
    base_pressure = float(traj_base.iloc[-1]["pressure_mean"])

    results = []
    for name in intervention_list:
        # Apply intervention
        p_iv = apply_intervention(base_params.to_params_jax(), name)
        traj_iv, _ = run_hybrid(years, p_iv, n_mc=50, seed=42)

        iv_pressure = float(traj_iv.iloc[-1]["pressure_mean"])
        iv_rr = float(traj_iv.iloc[-1]["rr_mean"])

        # Uncertainty (using p90 - p10 from the trajectory as a proxy for CI width)
        iv_rr_width = float(traj_iv.iloc[-1]["rr_p90"] - traj_iv.iloc[-1]["rr_p10"])

        results.append(
            {
                "Intervention": name,
                "Pressure (2030)": iv_pressure,
                "Pressure Impact": base_pressure - iv_pressure,
                "Relative Risk (2030)": iv_rr,
                "Uncertainty (90% Width)": iv_rr_width,
            }
        )

    return pd.DataFrame(results).sort_values("Pressure Impact", ascending=False)


@st.cache_data
def cached_run_model(
    p: Params, years: list[int], n_mc: int = 50, overrides: dict[str, Any] | None = None
):
    """Cached simulation run."""
    return run_hybrid(years, p, seed=42, n_mc=n_mc, overrides=overrides)


def generate_prose_summary(summary_base: dict, summary_game: dict) -> str:
    """Generate summary text."""
    risk_change = summary_game["rr_2030"] - summary_base["rr_2030"]
    narrative = "### 🏛️ Strategic Synthesis\n\n"
    if risk_change < -RISK_THRESHOLD:
        narrative += "✅ **Stabilization:** High confidence in risk decoupling."
    elif risk_change > RISK_THRESHOLD:
        narrative += "⚠️ **Deterioration:** Significant risk of system failure."
    else:
        narrative += "⚖️ **Stability:** Marginal structural shifts observed."
    return narrative


def _render_map() -> None:
    st.markdown("### 🕸️ Interactive Strategic Map")
    d3_path = Path("outputs/interactive/games_network_d3.html")
    if d3_path.exists():
        with open(d3_path, encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600, scrolling=True)
    else:
        st.error("D3 assets not found.")


def _render_game_tree() -> None:
    if create_extensive_game_from_matrix:
        u_row = np.array([[10, 0], [0, 5]])
        u_col = np.array([[10, 0], [0, 5]])
        g_tree = create_extensive_game_from_matrix(u_row, u_col, title="Subgame Tree")
        st.graphviz_chart(game_tree_graph(g_tree), width="stretch")


def _render_lhn(traj_game: pd.DataFrame) -> None:
    st.subheader("Intra-State LHN Variance")
    if "lhn_snapshot" in traj_game.attrs:
        lhn_df = traj_game.attrs["lhn_snapshot"]
        fig_lhn = px.scatter(
            lhn_df,
            x="Pressure Index",
            y="NWAU Capture (Relative)",
            color="LHN_ID",
            title="LHN Strategic Distribution",
        )
        st.plotly_chart(fig_lhn, use_container_width=True)
    else:
        st.info("High-fidelity LHN data available in SOTA mode.")


def _render_technical(traj_game: pd.DataFrame) -> None:
    if st.button("Run Live Morris"):
        prob = get_salib_problem(["nominal_cth_share_target", "bed_capacity_index"])
        df_m = run_morris_analysis(prob, lambda x: x[:, 0] * 0.5)
        st.pyplot(plot_morris_tornado(df_m))
    st.plotly_chart(plot_strategic_stability(traj_game), use_container_width=True)
    st.plotly_chart(plot_agreement_cycle(traj_game), use_container_width=True)


def _render_analysis(
    traj_game: pd.DataFrame,
    combined_plot: pd.DataFrame,
    years: list[int],
    p_game: Params,
    summaries: tuple[dict, dict],
) -> None:
    summary_base, summary_game = summaries
    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(
            plot_risk_pressure(combined_plot, "rr_mean", "System Risk", "Risk Index"),
            use_container_width=True,
        )
        st.plotly_chart(plot_phase_space(traj_game), use_container_width=True)
        if st.button("Run Live PSA"):
            with st.spinner("Sampling..."):
                psa = probabilistic_sensitivity(years, p_game, [], n_param=20, n_mc=10)
                st.plotly_chart(
                    px.scatter(pd.DataFrame(psa), x="noise_sd", y="rr_end", trendline="lowess"),
                    use_container_width=True,
                )
    with c2:
        st.metric("Resilience", f"{summary_game['resilience_index'] * 100:.0f}%")
        st.markdown(generate_prose_summary(summary_base, summary_game))
        st.plotly_chart(plot_patient_choice(traj_game), use_container_width=True)
        st.plotly_chart(plot_workforce_dynamics(traj_game), use_container_width=True)


def _scenario_controls(scenarios: dict) -> tuple[str, Params, int, dict[str, Any]]:
    initialize_slider_state(scenarios)
    git_hash = os.environ.get("COMMIT_SHA", "dev")[:7]
    st.sidebar.markdown(f"**Version:** `{git_hash}`")
    st.sidebar.title("🎮 Levers")
    scenario_options = ["Manual / Custom"] + [scenarios[k]["name"] for k in scenarios]
    sel_scen = st.sidebar.selectbox("Scenario:", scenario_options)
    if sel_scen != "Manual / Custom":
        sk = next(k for k in scenarios if scenarios[k]["name"] == sel_scen)
        for pk, pv in scenarios[sk]["params"].items():
            st.session_state[pk] = pv

    st.session_state.nominal_cth_share_target = st.sidebar.slider(
        "Cth Share", 0.30, 0.60, float(st.session_state.nominal_cth_share_target), 0.01
    )
    st.session_state.bed_capacity_index = st.sidebar.slider(
        "Bed Index", 0.70, 1.30, float(st.session_state.bed_capacity_index), 0.05
    )
    st.session_state.rurality_weight = st.sidebar.slider(
        "Rurality Weight", 0.05, 0.70, float(st.session_state.rurality_weight), 0.05
    )

    st.sidebar.markdown("---")
    full_strat = st.sidebar.toggle("💎 Full Strategic Mode", help="Enable Monthly Nash solving.")
    st.session_state.n_mc = st.sidebar.select_slider(
        "MC Samples", options=[10, 50, 200, 1000], value=int(st.session_state.get("n_mc", LITE_MC))
    )

    p_game = Params.from_flat_dict({name: st.session_state[name] for name in Params().flatten()})
    return (
        sel_scen,
        initialize_rules(p_game),
        int(st.session_state.n_mc),
        _strategy_overrides(full_strat),
    )


def main() -> None:
    """Main dashboard entrypoint."""
    st.set_page_config(page_title="NHRA Strategic Dashboard", page_icon="🏥", layout="wide")
    st.title(f"🏥 NHRA Strategic Simulator (v{__version__})")
    sel_scen, p_game, n_mc, overrides = _scenario_controls(load_scenario_library())
    p_base = Params()
    registry = get_populated_registry()
    years = list(range(2025, 2031))
    st.sidebar.download_button(
        "📥 Download Snapshot (JSON)",
        data=json.dumps(
            {
                "scenario_name": sel_scen,
                "params": p_game.flatten(),
                "years": years,
                "n_mc": n_mc,
                "seed": 42,
                "overrides": overrides,
            },
            indent=2,
        ),
        file_name="nhra_scenario_snapshot.json",
        mime="application/json",
    )

    traj_base, _ = cached_run_model(p_base, years, n_mc=n_mc)
    summary_base = summarise_outcome(traj_base)
    traj_game, _ = cached_run_model(p_game, years, n_mc=n_mc, overrides=overrides)
    summary_game = summarise_outcome(traj_game)

    # Clear attrs for concat safety
    tb_plot = traj_base.assign(Scenario="Baseline")
    tg_plot = traj_game.assign(Scenario="Scenario")
    tb_plot.attrs = {}
    tg_plot.attrs = {}
    combined_plot = pd.concat([tb_plot, tg_plot])

    # Tabs
    (
        theory,
        analysis,
        game_map,
        trees,
        lhn,
        lineage_tab,
        validation,
        technical,
        audit,
        encyclopedia,
    ) = st.tabs(
        [
            "📖 Theory & Background",
            "📈 Scenario Analysis",
            "🕸️ Strategic Map",
            "🌲 Game Tree Explorer",
            "🏥 LHN",
            "🧬 Data Lineage",
            "⚖️ Validation",
            "🔬 Technical",
            "🔍 Forensic Audit",
            "📚 Encyclopedia",
        ],
        default="📈 Scenario Analysis",
    )

    with theory:
        st.markdown(
            "The simulator compares Commonwealth funding and state responses under alternative "
            "hospital capacity and policy settings. The Encyclopedia describes the stage games. "
            "Data Lineage records the sources and scope of the model parameters."
        )

    with analysis:
        _render_analysis(traj_game, combined_plot, years, p_game, (summary_base, summary_game))

    with game_map:
        _render_map()

    with trees:
        _render_game_tree()

    with lhn:
        _render_lhn(traj_game)

    with lineage_tab:
        st.markdown("### 🧬 Data Lineage")
        lineage = get_parameter_lineage()
        st.dataframe(pd.DataFrame([{"Parameter": k, "Source": v} for k, v in lineage.items()]))

    with validation:
        st.markdown(
            "[Historical validation inputs and scope](https://github.com/edithatogo/nhra_game/blob/main/context/06_data_provenance.md)"
        )

    with technical:
        _render_technical(traj_game)

    with audit:
        st.subheader("Forensic Audit & Solver Integrity")
        st.json(p_game.flatten(), expanded=False)
        st.dataframe(traj_game)
        comparison = pd.DataFrame({"Baseline": summary_base, "Scenario": summary_game})
        st.dataframe(comparison)

    with encyclopedia:
        render_game_encyclopedia(registry)


if __name__ == "__main__":
    main()
