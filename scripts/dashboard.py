# Interactive Streamlit Dashboard for NHRA War Gaming.
# Provides a unified interface for:
# - Scenario Analysis
# - Strategic Network Visualization
# - Game Theoretic Encyclopedia
# - Evidence Management

from __future__ import annotations

import dataclasses
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
        render_tree_static,
    )
except ImportError:  # pragma: no cover
    create_extensive_game_from_matrix = None  # type: ignore[assignment]
    render_tree_static = None  # type: ignore[assignment]

from nhra_gt import __version__
from nhra_gt.domain.params import Params
from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import initialize_rules, summarise_outcome
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
    """Initializes session state for model parameters based on scenario defaults."""
    csv_defaults: dict[str, Any] = {}
    master_path = Path("context/04_parameter_registry.csv")
    if master_path.exists():
        try:
            df_reg = pd.read_csv(master_path)
            csv_defaults = dict(zip(df_reg["parameter"], df_reg["value"], strict=False))
        except Exception as e:
            st.warning(f"Could not load parameter registry: {e}")

    param_fields = dataclasses.fields(ParamsJax)
    default_scenario = scenarios.get("steady_state", {})
    scenario_params = default_scenario.get("params", {})

    for field in param_fields:
        key = field.name
        if key not in st.session_state:
            val = scenario_params.get(key, csv_defaults.get(key))
            if val is None:
                val = (
                    field.default
                    if not isinstance(field.default, dataclasses._MISSING_TYPE)
                    else 0.0
                )
            st.session_state[key] = val


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


def main() -> None:
    """Main dashboard entrypoint."""
    st.set_page_config(page_title="NHRA Strategic Dashboard", page_icon="🏥", layout="wide")
    scenarios = load_scenario_library()
    initialize_slider_state(scenarios)
    registry = get_populated_registry()

    git_hash = os.environ.get("COMMIT_SHA", "dev")[:7]
    st.sidebar.markdown(f"**Version:** `{git_hash}`")
    st.title(f"🏥 NHRA Strategic Simulator (v{__version__})")

    # Sidebar
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

    st.sidebar.markdown("---")
    full_strat = st.sidebar.toggle("💎 Full Strategic Mode", help="Enable Monthly Nash solving.")
    st.session_state.n_mc = st.sidebar.select_slider(
        "MC Samples", options=[10, 50, 200, 1000], value=int(st.session_state.get("n_mc", LITE_MC))
    )

    # Execution
    years = list(range(2025, 2031))
    p_base = Params()
    traj_base, _ = cached_run_model(p_base, years, n_mc=int(st.session_state.n_mc))
    summary_base = summarise_outcome(traj_base)

    p_game = Params.from_flat_dict(
        {k: v for k, v in st.session_state.items() if isinstance(k, str)}
    )
    p_game = initialize_rules(p_game)

    ovr = {"STRATEGIC_MODE": True} if full_strat else {}
    traj_game, _ = cached_run_model(p_game, years, n_mc=int(st.session_state.n_mc), overrides=ovr)
    summary_game = summarise_outcome(traj_game)

    # Execution
    years = list(range(2025, 2031))
    p_base = Params()
    traj_base, _ = cached_run_model(p_base, years, n_mc=int(st.session_state.n_mc))
    summary_base = summarise_outcome(traj_base)

    p_game = Params.from_flat_dict(
        {k: v for k, v in st.session_state.items() if isinstance(k, str)}
    )
    p_game = initialize_rules(p_game)

    ovr = {"STRATEGIC_MODE": True} if full_strat else {}
    traj_game, _ = cached_run_model(p_game, years, n_mc=int(st.session_state.n_mc), overrides=ovr)
    summary_game = summarise_outcome(traj_game)

    # Clear attrs for concat safety
    tb_plot = traj_base.assign(Scenario="Baseline")
    tg_plot = traj_game.assign(Scenario="Scenario")
    tb_plot.attrs = {}
    tg_plot.attrs = {}
    combined_plot = pd.concat([tb_plot, tg_plot])

    # Tabs
    tabs = st.tabs(
        [
            "📉 Analysis",
            "🕸️ Map",
            "🌲 Trees",
            "🏥 LHN",
            "🧬 Lineage",
            "⚖️ Validation",
            "🔬 Technical",
            "🛡️ Evidence",
            "📚 Encyclopedia",
        ]
    )

    with tabs[0]:  # Analysis
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

    with tabs[1]:  # Map
        st.markdown("### 🕸️ Interactive Strategic Map")
        d3_path = Path("outputs/interactive/games_network_d3.html")
        if d3_path.exists():
            with open(d3_path, encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        else:
            st.error("D3 assets not found.")

    with tabs[2]:  # Trees
        if create_extensive_game_from_matrix:
            u_row = np.array([[10, 0], [0, 5]])
            u_col = np.array([[10, 0], [0, 5]])
            g_tree = create_extensive_game_from_matrix(u_row, u_col, title="Subgame Tree")
            render_tree_static(g_tree, "outputs/diagrams/current_subgame")
            st.image("outputs/diagrams/current_subgame.svg", use_container_width=True)

    with tabs[3]:  # LHN
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

    with tabs[4]:  # Lineage
        st.markdown("### 🧬 Data Lineage")
        lineage = get_parameter_lineage()
        st.table(pd.DataFrame([{"Parameter": k, "Source": v} for k, v in lineage.items()]))

    with tabs[6]:  # Technical
        if st.button("Run Live Morris"):
            prob = get_salib_problem(["nominal_cth_share_target", "bed_capacity_index"])
            df_m = run_morris_analysis(prob, lambda x: x[:, 0] * 0.5)
            st.pyplot(plot_morris_tornado(df_m))
        st.plotly_chart(plot_strategic_stability(traj_game), use_container_width=True)
        st.plotly_chart(plot_agreement_cycle(traj_game), use_container_width=True)

    with tabs[8]:  # Encyclopedia
        render_game_encyclopedia(registry)


if __name__ == "__main__":
    main()
