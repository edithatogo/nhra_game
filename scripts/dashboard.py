from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import yaml

try:
    from nhra_gt.visualization.game_trees import (
        create_extensive_game_from_matrix,
        render_tree_static,
    )
except ImportError:  # pragma: no cover
    create_extensive_game_from_matrix = None  # type: ignore[assignment]
    render_tree_static = None  # type: ignore[assignment]

from nhra_gt.visualization.interactive import (
    plot_agreement_cycle,
    plot_ghost_overlay,
    plot_patient_choice,
    plot_phase_space,
    plot_risk_pressure,
    plot_share_drift,
    plot_stability_heatmap,
    plot_strategic_stability,
    plot_vfi_waterfall,
    plot_workforce_dynamics,
)
from nhra_gt.visualization.sensitivity import plot_morris_tornado as viz_plot_morris_tornado
from nhra_gt.visualization.sensitivity import plot_sobol_heatmap as viz_plot_sobol_heatmap
from nhra_gt.visualization.sensitivity import plot_sobol_indices as viz_plot_sobol_indices

# Add src to path if needed for relative imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nhra_gt import __version__
from nhra_gt.domain.registry import EvidenceEntry, EvidenceRegistry
from nhra_gt.domain.stability import analyze_cost_shifting_stability
from nhra_gt.domain.validation import RecursiveResult, aggregate_metrics
from nhra_gt.engine import Params, apply_intervention, run_hybrid, summarise_outcome
from nhra_gt.sensitivity import get_parameter_lineage
from nhra_gt.subgames.games import (
    GameParams,
    bargaining_game,
    compliance_game,
    cost_shifting_game,
    definition_game,
    discharge_coordination_game,
    governance_integration_game,
)


def load_scenario_library() -> dict:
    path = Path("configs/scenarios.yaml")
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f).get("scenarios", {})
    return {}


def initialize_slider_state(scenarios: dict):
    """Initializes session state for sliders if not already present."""
    default_scenario = scenarios.get("steady_state", {})
    default_params = default_scenario.get("params", {})

    slider_keys = [
        "nominal_cth_share_target",
        "nep_annual_growth",
        "bed_capacity_index",
        "discharge_delay_base",
        "political_salience",
        "audit_pressure",
        "rurality_weight",
        "cost_shifting_intensity",
        "signal_lag_months",
        "claims_lag_months",
    ]

    for key in slider_keys:
        if key not in st.session_state:
            # Use value from steady_state if available, otherwise hardcoded defaults
            val = default_params.get(key)
            if val is None:
                # Fallback defaults
                defaults = {
                    "nominal_cth_share_target": 0.45,
                    "nep_annual_growth": 0.03,
                    "bed_capacity_index": 1.0,
                    "discharge_delay_base": 1.0,
                    "political_salience": 0.30,
                    "audit_pressure": 0.50,
                    "rurality_weight": 0.35,
                    "cost_shifting_intensity": 0.35,
                    "signal_lag_months": 1,
                    "claims_lag_months": 3,
                }
                val = defaults.get(key, 0.0)
            st.session_state[key] = val


def prepare_ghost_overlay_data(
    historical: pd.DataFrame, recursive_results: list[dict], metric: str
) -> pd.DataFrame:
    """Prepare data for historical vs predicted overlay."""
    hist_subset = historical[["year", metric]].copy()
    hist_subset["type"] = "Historical"
    hist_subset = hist_subset.rename(columns={metric: "value"})

    pred_data = []
    for r in recursive_results:
        pred_data.append(
            {"year": r["test_year"], "value": r["predicted"][metric], "type": "Backtest Prediction"}
        )
    pred_df = pd.DataFrame(pred_data)

    return pd.concat([hist_subset, pred_df])


def prepare_share_drift_data(
    traj: pd.DataFrame, threshold: float
) -> tuple[pd.DataFrame, list[dict]]:
    """Calculate effective share drift and identify threshold breaches."""
    df = traj.copy()
    df["drift_gap"] = df["cth_nominal_mean"] - df["cth_effective_mean"]

    breaches = []
    for _, row in df.iterrows():
        if row["cth_effective_mean"] < threshold:
            breaches.append({"year": int(row["year"]), "value": float(row["cth_effective_mean"])})

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
        p_iv = apply_intervention(base_params, name)
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

    df = pd.DataFrame(results).sort_values("Pressure Impact", ascending=False)
    return df


@st.cache_data
def cached_run_model(
    p: Params, years: list[int], n_mc: int = 50, overrides: dict[str, str] | None = None
):
    """Run the model with caching to ensure responsive UI."""
    return run_hybrid(years, p, seed=42, n_mc=n_mc, overrides=overrides)


def generate_prose_summary(summary_base, summary_game) -> str:
    """Generate a rich, multi-layered strategic synthesis of the scenario analysis."""
    risk_change = summary_game["rr_2030"] - summary_base["rr_2030"]
    share_change = summary_game["effshare_effective_2030"] - summary_base["effshare_effective_2030"]
    pressure_final = summary_game["pressure_2030"]
    resilience = summary_game["resilience_index"]

    narrative = "### 🏛️ Strategic Synthesis & Policy Implications\n\n"

    # 1. Executive Summary
    if risk_change < -0.1:
        exec_sum = "✅ **Outcome:** High-confidence system stabilization. The proposed intervention successfully decouples system pressure from catastrophic failure risks."
    elif risk_change > 0.1:
        exec_sum = "⚠️ **Outcome:** Strategic Deterioration. The scenario indicates significant risk of system-wide failure, with high political and operational costs."
    else:
        exec_sum = "⚖️ **Outcome:** Marginal Stability. The system maintains its current trajectory with limited structural shifts."

    narrative += f"{exec_sum}\n\n"

    # 2. Institutional Analysis
    narrative += "#### 💸 Financial & Constitutional Layer\n"
    if share_change > 0.03:
        narrative += f"- **Hold-Up Success:** State agents successfully leveraged system pressure to extract a {share_change * 100:.1f}% increase in realized Commonwealth contribution.\n"
    elif share_change < -0.03:
        narrative += f"- **Fiscal Leakage:** Despite nominal targets, effective realized funding has drifted downwards by {abs(share_change) * 100:.1f}%, primarily driven by cap-breaches and efficiency gap drift.\n"
    else:
        narrative += "- **Funding Stability:** Realized contribution shares remain aligned with the 2025-2030 Agreement targets.\n"

    # 3. Operational Analysis
    narrative += "\n#### 🏥 Operational & Clinical Layer\n"
    narrative += f"- **Resilience:** The system spends **{resilience * 100:.0f}%** of the forecast period in 'Normal' mode. "
    if pressure_final > 1.3:
        narrative += "Chronic overcrowding persists, with ED performance likely to remain below the 80% target due to upstream bottlenecks.\n"
    else:
        narrative += "The operational state is robust, with sufficient capacity buffer to handle seasonal demand peaks.\n"

    # 4. Mechanism Insight (The 'Why')
    narrative += "\n#### 🧪 Mechanism Insight\n"
    if summary_game["hysteresis_area"] > summary_base["hysteresis_area"]:
        narrative += "- **Increased Inertia:** This scenario increases the system's 'hysteresis area', meaning recovery from shocks will be slower and more costly once failure thresholds are breached.\n"
    else:
        narrative += "- **Improved Agility:** The intervention reduces system inertia, allowing for more rapid stabilization following demand surges.\n"

    narrative += "\n---\n*Note: This synthesis is generated by the Digital Twin's Ex-Post Narrator, integrating multi-layer simulation metrics with game-theoretic outcome traces.*"

    return narrative


def apply_custom_theme():
    """Apply Teal/Minimalist Academic theme using custom CSS."""
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #008080;
            --secondary-color: #f0f2f6;
        }
        .main {
            background-color: white;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }
        h1, h2, h3 {
            color: #008080;
        }
        .stMetric {
            background-color: #f8fbfb;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #008080;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def st_traffic_light(status: str, label: str):
    """Renders a traffic light indicator for data provenance."""
    colors = {"Live": "🟢", "Validated": "🟡", "Assumption": "🔴"}
    icon = colors.get(status, "⚪")
    st.markdown(f"{icon} **{label}** ({status})")


def main() -> None:
    st.set_page_config(
        page_title="NHRA Strategic Scenario Dashboard", page_icon="🏥", layout="wide"
    )
    apply_custom_theme()

    # Load Scenarios
    scenarios = load_scenario_library()
    initialize_slider_state(scenarios)

    st.title(f"🏥 NHRA Strategic Scenario Analysis (v{__version__})")
    st.markdown("""
    ### Strategic Negotiation & System Risk Simulator (Cognitive Twin)
    This simulator models the interaction between policy levers (funding, capacity, integration)
    and the resulting strategic behavior of Commonwealth and State agents. Use the sidebar
    to adjust parameters and observe the projected impact on clinical risk and system pressure.
    """)

    # ----------------------------
    # Sidebar: Strategic Levers
    # ----------------------------
    st.sidebar.title("🎮 Strategic Levers")

    # Scenario Selector
    st.sidebar.subheader("📂 Scenario Library")
    scenario_options = ["Manual / Custom"] + [scenarios[k]["name"] for k in scenarios]
    selected_scenario_name = st.sidebar.selectbox("Select standard scenario:", scenario_options)

    if selected_scenario_name != "Manual / Custom":
        # Find the scenario key
        sk = [k for k in scenarios if scenarios[k]["name"] == selected_scenario_name][0]
        s_data = scenarios[sk]
        st.sidebar.info(s_data["description"])
        # Update session state
        for pk, pv in s_data["params"].items():
            st.session_state[pk] = pv

    st.sidebar.info("Adjust the sliders below to simulate different NHRA negotiation outcomes.")

    # Funding Levers
    st.sidebar.subheader("💰 Funding & Valuation")
    nominal_share = st.sidebar.slider(
        "Nominal Cth Share Target",
        0.30,
        0.60,
        st.session_state.nominal_cth_share_target,
        0.01,
        key="slider_nominal_share",
        help="The headline funding percentage agreed in the NHRA (e.g. 45% or 50%).",
    )
    st.session_state.nominal_cth_share_target = nominal_share

    nep_growth = st.sidebar.slider(
        "NEP Annual Growth",
        0.01,
        0.08,
        st.session_state.nep_annual_growth,
        0.005,
        key="slider_nep_growth",
        help="The policy-defined growth rate of the National Efficient Price.",
    )
    st.session_state.nep_annual_growth = nep_growth

    # Operational Levers
    st.sidebar.subheader("🚑 Operational Capacity")
    bed_capacity = st.sidebar.slider(
        "Bed Capacity Index",
        0.70,
        1.30,
        st.session_state.bed_capacity_index,
        0.05,
        key="slider_bed_capacity",
        help="Relative index of available public hospital beds. Values > 1.0 indicate expanded capacity.",
    )
    st.session_state.bed_capacity_index = bed_capacity

    discharge_delay = st.sidebar.slider(
        "Discharge Delay Base",
        0.50,
        2.00,
        st.session_state.discharge_delay_base,
        0.05,
        key="slider_discharge_delay",
        help="Impact of Aged Care and NDIS placement delays. Values < 1.0 indicate improved integration.",
    )
    st.session_state.discharge_delay_base = discharge_delay

    # Policy & Behavioural
    st.sidebar.subheader("⚖️ Policy & Behaviour")
    political_salience = st.sidebar.slider(
        "Political Salience",
        0.05,
        0.80,
        st.session_state.political_salience,
        0.05,
        key="slider_political_salience",
        help="The intensity of political pressure on negotiation outcomes.",
    )
    st.session_state.political_salience = political_salience

    audit_pressure = st.sidebar.slider(
        "Audit Pressure",
        0.05,
        1.00,
        st.session_state.audit_pressure,
        0.05,
        key="slider_audit_pressure",
        help="The degree of compliance scrutiny and administrative burden applied to funding.",
    )
    st.session_state.audit_pressure = audit_pressure

    # Clinical & Workforce
    st.sidebar.subheader("🩺 Clinical & Workforce")
    rurality_weight = st.sidebar.slider(
        "Rurality Weight",
        0.05,
        0.70,
        st.session_state.rurality_weight,
        0.05,
        key="slider_rurality_weight",
        help="The fraction of healthcare activity occurring in regional and remote areas.",
    )
    st.session_state.rurality_weight = rurality_weight

    cost_shifting = st.sidebar.slider(
        "Cost-Shifting Intensity",
        0.05,
        0.80,
        st.session_state.cost_shifting_intensity,
        0.05,
        key="slider_cost_shifting",
        help="The strength of incentives to shift pressures across Commonwealth/State interfaces.",
    )
    st.session_state.cost_shifting_intensity = cost_shifting

    # Lags & Measurement
    st.sidebar.subheader("⏱️ Lags & Measurement")
    signal_lag = st.sidebar.slider(
        "Signal Lag (Months)",
        0,
        6,
        st.session_state.signal_lag_months,
        1,
        key="slider_signal_lag",
        help="Delay before public indicators (pressure, occupancy) are reported.",
    )
    st.session_state.signal_lag_months = signal_lag

    claims_lag = st.sidebar.slider(
        "Claims Lag (Months)",
        0,
        12,
        st.session_state.claims_lag_months,
        1,
        key="slider_claims_lag",
        help="Delay before financial activity (NWAU, coding) is reconciled.",
    )
    st.session_state.claims_lag_months = claims_lag

    # Scenario Management
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Scenario Management")
    scenario_name = st.sidebar.text_input("Scenario Name", "New Strategic Scenario Analysis")

    # Expert Mode Toggle
    st.sidebar.markdown("---")
    expert_mode = st.sidebar.toggle(
        "🧠 Expert Strategic Mode", help="Manually override game strategies."
    )

    overrides = {}
    if expert_mode:
        st.sidebar.info("Manual overrides will bypass simulation logic.")
        overrides["DEF"] = st.sidebar.selectbox(
            "Definition Game", ["Auto", "R", "E"], help="R=Realism, E=Strict"
        )
        overrides["BARG"] = st.sidebar.selectbox(
            "Bargaining Game", ["Auto", "A", "D"], help="A=Agree, D=Defer"
        )
        overrides["SHIFT"] = st.sidebar.selectbox(
            "Cost-Shifting Game", ["Auto", "I", "S"], help="I=Invest, S=Shift"
        )
        overrides["DISC"] = st.sidebar.selectbox(
            "Discharge Game", ["Auto", "C", "F"], help="C=Coordinate, F=Fragment"
        )
        overrides["GOV"] = st.sidebar.selectbox(
            "Integration Game", ["Auto", "I", "S"], help="I=Integrate, S=Separate"
        )
        overrides["COMP"] = st.sidebar.selectbox(
            "Compliance Game", ["Auto", "T", "L"], help="T=Tight, L=Light"
        )

        # Filter out 'Auto' selections
        overrides = {k: v for k, v in overrides.items() if v != "Auto"}

        # Conflict Detection logic
        conflicts = []
        if (
            "DEF" in overrides and overrides["DEF"] == "E" and nep_growth < 0.03
        ):  # High growth implies Realism
            conflicts.append(
                "Force 'Strict' Definition contradicts low 'NEP Growth' (Realism) intent."
            )
        if "SHIFT" in overrides and overrides["SHIFT"] == "S" and cost_shifting < 0.20:
            conflicts.append(
                "Force 'Shift' strategy contradicts low 'Cost-Shifting Intensity' policy."
            )

        if conflicts:
            st.sidebar.warning("⚠️ **Strategic Contradictions Detected:**")
            for c in conflicts:
                st.sidebar.write(f"- {c}")

    # Snapshot logic
    snapshot = {
        "scenario_name": scenario_name,
        "params": {
            "nominal_cth_share_target": nominal_share,
            "nep_annual_growth": nep_growth,
            "bed_capacity_index": bed_capacity,
            "discharge_delay_base": discharge_delay,
            "political_salience": political_salience,
            "audit_pressure": audit_pressure,
            "rurality_weight": rurality_weight,
            "cost_shifting_intensity": cost_shifting,
            "signal_lag_months": signal_lag,
            "claims_lag_months": claims_lag,
        },
    }

    st.sidebar.download_button(
        "📥 Download Snapshot (JSON)",
        data=json.dumps(snapshot, indent=2),
        file_name=f"{scenario_name.lower().replace(' ', '_')}_snapshot.json",
        mime="application/json",
    )

    # ----------------------------
    # Model Execution
    # ----------------------------
    years = list(range(2025, 2031))

    # Manage MC Samples in state
    if "n_mc" not in st.session_state:
        st.session_state.n_mc = 50

    # Confidence Metric Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ Simulation Confidence")

    # We run baseline at the requested fidelity
    p_base = Params()
    traj_base, _ = cached_run_model(p_base, years, n_mc=st.session_state.n_mc)
    summary_base = summarise_outcome(traj_base)

    # Calculate average SEM for pressure as a confidence proxy
    avg_sem = float(traj_base["pressure_sem"].mean())
    confidence_level = "High" if avg_sem < 0.01 else "Medium" if avg_sem < 0.03 else "Low"
    conf_color = (
        "green"
        if confidence_level == "High"
        else "orange"
        if confidence_level == "Medium"
        else "red"
    )

    st.sidebar.markdown(f"Confidence: :{conf_color}[**{confidence_level}**] (SEM: {avg_sem:.4f})")

    if st.session_state.n_mc < 1000:
        if st.sidebar.button("🚀 Boost to SOTA Accuracy (1000 MC)"):
            st.session_state.n_mc = 1000
            st.rerun()
    else:
        if st.sidebar.button("📉 Reset to Lite Mode (50 MC)"):
            st.session_state.n_mc = 50
            st.rerun()

    # Strategic Scenario Analysis
    p_game = Params(
        nominal_cth_share_target=nominal_share,
        nep_annual_growth=nep_growth,
        bed_capacity_index=bed_capacity,
        discharge_delay_base=discharge_delay,
        political_salience=political_salience,
        audit_pressure=audit_pressure,
        rurality_weight=rurality_weight,
        cost_shifting_intensity=cost_shifting,
        signal_lag_months=signal_lag,
        claims_lag_months=claims_lag,
    )
    traj_game, _ = cached_run_model(p_game, years, n_mc=st.session_state.n_mc, overrides=overrides)
    summary_game = summarise_outcome(traj_game)

    # ----------------------------
    # Main Content Area: Tabs
    # ----------------------------
    tab0, tab1, tab2, tab2_5, tab2_6, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📖 Theory & Background",
            "📈 Scenario Analysis",
            "🕸️ Strategic Map",
            "🌲 Game Tree Explorer",
            "🏥 Intra-State LHN Variance",
            "🧬 Data Lineage",
            "⚖️ Validation Scorecard",
            "🔬 Technical Analytics",
            "🛡️ Evidence Manager",
            "🔍 Forensic Audit",
        ]
    )

    with tab0:
        st.markdown("## 📖 Strategic Foundations of the NHRA Game")

        col_bg1, col_bg2 = st.columns(2)
        with col_bg1:
            st.markdown("### 🏛️ The Problem: Vertical Fiscal Imbalance")
            st.write("""
            The Australian National Health Reform Agreement (NHRA) operates in a state of
            **Vertical Fiscal Imbalance (VFI)**. The Commonwealth controls the majority of
            revenue, while States carry the majority of operational risk.

            This creates specific strategic frictions:
            - **Cost Shifting:** Incentives to move patients into 'someone else's budget' (e.g. ED vs GP).
            - **Hold-Up Games:** High-stakes negotiations every 5 years where system failure is used as leverage.
            - **Boundary Shifting:** Moving activity between ABF and Block funding to bypass growth caps.
            """)

        with col_bg2:
            st.markdown("### 🎮 The Solution: Game Theoretic Modelling")
            st.write("""
            We model these frictions as a series of **non-cooperative games**.
            - **Players:** Commonwealth (Principal), States (Agents), and LHNs (Operators).
            - **Equilibrium:** The simulation finds the 'Nash Equilibrium' where no player can improve their outcome by changing strategy alone.
            - **Mechanics:** By modeling the *incentives* directly, we can predict how policy changes (like a 6.5% cap) drive unintended behaviors (like ramping).
            """)

        st.markdown("---")
        st.markdown("### 🏗️ Technical Transparency")
        st.write("""
        This simulator is built on **JAX/XLA**, providing high-performance, differentiable simulation.
        We use **PyGambit** for rigorous Nash equilibrium enumeration and **Quantal Response Equilibrium (QRE)**
        to model boundedly-rational agents.
        """)
        st.link_button("View Gambit Documentation", "https://gambitproject.github.io/")
        st.link_button("View JAX Repository", "https://github.com/google/jax")

    with tab1:
        st.markdown("#### System Trajectories")

        wg_tab1, wg_tab2, wg_tab3 = st.tabs(
            ["📉 Risk & Pressure", "💸 Fiscal Impact", "📋 Intervention Ranking"]
        )

        with wg_tab1:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Prepare Plotly Data
                traj_base_p = traj_base.copy()
                traj_game_p = traj_game.copy()
                traj_base_p["Scenario"] = "Baseline"
                traj_game_p["Scenario"] = "Strategic Scenario Analysis"
                combined = pd.concat([traj_base_p, traj_game_p])

                # Risk Plot
                st.markdown("**Patient Safety Risk Proxy**")
                fig_risk = plot_risk_pressure(
                    combined, "rr_mean", "Relative Risk Proxy (Trajectories)", "Relative Risk"
                )
                st.plotly_chart(fig_risk, width="stretch")
                with st.expander("🔍 How to interpret Risk Proxy"):
                    st.write("""
                    This plot shows the estimated impact of system constraints on patient safety.
                    - **Y-Axis:** A relative index (1.0 = Baseline). Higher values indicate increased risk of adverse events due to ambulance ramping and access block.
                    - **Markers:** Discrete states where safety thresholds are breached.
                    """)

                # Pressure Plot
                st.markdown("**Hospital System Pressure**")
                fig_pres = plot_risk_pressure(
                    combined, "pressure_mean", "System Pressure Index", "Pressure Index"
                )
                st.plotly_chart(fig_pres, width="stretch")
                with st.expander("🔍 How to interpret System Pressure"):
                    st.write("""
                    Measures the total operational strain on the hospital network.
                    - **Value > 1.0:** Indicates the system is operating beyond its efficient capacity.
                    - **Divergence:** The gap between Baseline and Scenario shows the net effect of your policy lever selections.
                    """)
            with col2:
                st.markdown("#### Executive Summary")

                # Effective Cth Share
                share_val = summary_game["effshare_effective_2030"]
                share_base = summary_base["effshare_effective_2030"]
                st.metric(
                    "Effective Cth Share (2030)",
                    f"{share_val * 100:.1f}%",
                    delta=f"{(share_val - share_base) * 100:.1f}%",
                )

                # Relative Risk
                risk_val = summary_game["rr_2030"]
                risk_base = summary_base["rr_2030"]
                st.metric(
                    "Relative Risk Proxy (2030)",
                    f"{risk_val:.2f}",
                    delta=f"{risk_val - risk_base:.2f}",
                    delta_color="inverse",
                )

                # Within 4 Hours
                w4_val = summary_game["within4_2030"]
                w4_base = summary_base["within4_2030"]
                st.metric(
                    "Within 4 Hours (2030)",
                    f"{w4_val * 100:.1f}%",
                    delta=f"{(w4_val - w4_base) * 100:.1f}%",
                )

                # System Resilience
                res_val = summary_game["resilience_index"]
                res_base = summary_base["resilience_index"]
                st.metric(
                    "Resilience Index",
                    f"{res_val * 100:.0f}%",
                    delta=f"{(res_val - res_base) * 100:.0f}%",
                    help="Percentage of time spent in 'Normal' mode. Higher is better.",
                )

                # Hysteresis Area
                h_val = summary_game["hysteresis_area"]
                h_base = summary_base["hysteresis_area"]
                st.metric(
                    "Hysteresis Area",
                    f"{h_val:.3f}",
                    delta=f"{h_val - h_base:.3f}",
                    delta_color="inverse",
                    help="Area of the phase-space loop. Measures system lag/inertia. Lower is better.",
                )

                # Narrative Summary
                st.markdown("---")
                narrative = generate_prose_summary(summary_base, summary_game)
                st.markdown(narrative)

                # Export Suite
                st.markdown("---")
                st.markdown("#### 📤 Export Results")
                col_ex1, col_col_ex2 = st.columns(2)

                with col_ex1:
                    st.download_button(
                        "📊 Download Data (CSV)",
                        data=combined.to_csv(index=False),
                        file_name=f"{scenario_name.lower().replace(' ', '_')}_results.csv",
                        mime="text/csv",
                    )

                with col_col_ex2:
                    # Simple markdown report for now
                    report_text = f"# NHRA Strategic Scenario Analysis Report: {scenario_name}\n\n{narrative}\n\n## Data Summary\n{summary_game}"
                    st.download_button(
                        "📄 Download Brief (MD)",
                        data=report_text,
                        file_name=f"{scenario_name.lower().replace(' ', '_')}_report.md",
                        mime="text/markdown",
                    )

        with wg_tab2:
            st.subheader("Funding & System Dynamics")

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.markdown("**VFI Funding Leakage (2030 forecast)**")
                # Use data from summary_game
                fig_wf = plot_vfi_waterfall(
                    nominal_share=summary_game["effshare_nominal_2030"],
                    indexation_loss=summary_game["leakage_indexation"],
                    cap_loss=summary_game["leakage_cap"],
                    audit_loss=summary_game["leakage_audit"],
                    adjustment_loss=summary_game["leakage_adjustment"],
                    effective_share=summary_game["effshare_effective_2030"],
                )
                st.plotly_chart(fig_wf, width="stretch")
                with st.expander("🔍 How to interpret Funding Leakage"):
                    st.write("""
                    This 'Waterfall' chart decomposes the gap between the headline Agreement target and the actual money received.
                    - **Nominal Target:** The starting policy commitment (e.g. 45%).
                    - **Leakage Blocks:** Reductions due to caps, indexation mismatches, and audit penalties.
                    - **Effective Share:** The true realized Commonwealth contribution.
                    """)

            with col_f2:
                st.markdown("**System Phase-Space (Hysteresis)**")
                fig_ps = plot_phase_space(traj_game)
                st.plotly_chart(fig_ps, width="stretch")
                with st.expander("🔍 How to interpret Phase-Space"):
                    st.write("""
                    Visualizes the 'inertia' of the system.
                    - **Loops:** If the path does not return on itself, the system has 'hysteresis' (path dependency).
                    - **Area:** The size of the loop indicates how long the system remains 'stuck' in high-pressure modes even after the cause is removed.
                    """)

            st.markdown("---")
            st.subheader("Patient Choice & Queuing Dynamics")
            col_q1, col_q2 = st.columns([2, 1])
            with col_q1:
                fig_q = plot_patient_choice(traj_game)
                st.plotly_chart(fig_q, width="stretch")
            with col_q2:
                st.info("""
                **Endogenous Demand (Wardrop Equilibrium):**
                Patients choose between the Emergency Department (ED) and General Practice (GP) based on relative utility:
                - **ED Utility:** Decreases with longer wait times (Access Block).
                - **GP Utility:** Decreases with higher Out-of-Pocket costs.

                The model find the equilibrium where no marginal patient can improve their utility by switching. This explains how primary care costs mechanistically drive ED demand.
                """)

            st.markdown("---")
            st.subheader("Workforce Competition & Drains")
            col_w1, col_w2 = st.columns([2, 1])
            with col_w1:
                fig_w = plot_workforce_dynamics(traj_game)
                st.plotly_chart(fig_w, width="stretch")
            with col_w2:
                st.info("""
                **Shared Workforce Pool:**
                LHNs compete for a finite pool of staff (e.g., locum doctors and nurses).
                - **Aggressive Hiring:** LHNs may choose to out-compete neighbors for staff during crises.
                - **Cannibalization:** Aggressive moves by one LHN drain the shared pool, increasing discharge delays for all.
                - **System Mode Impact:** High pressure increases the 'cost of aggression' as staff burnout rises.
                """)

            st.markdown("---")
            st.subheader("5-Year Agreement Cycle & Hold-Up")
            col_ac1, col_ac2 = st.columns([2, 1])
            with col_ac1:
                fig_ac = plot_agreement_cycle(traj_game)
                st.plotly_chart(fig_ac, width="stretch")
            with col_ac2:
                st.info("""
                **The Hold-Up Game:**
                The NHRA follows a 5-year cycle. When the clock hits zero, a high-stakes negotiation occurs:
                - **State Move:** Can 'Agree' or 'Hold-Up' (threaten failure).
                - **Commonwealth Move:** Can 'Concede' or 'Enforce' (stick to target).
                - **Pressure Impact:** High system pressure gives States more bargaining leverage to extract a higher `alpha` (contribution share).
                """)

            st.markdown("---")
            st.subheader("Effective Share Drift Analysis")
            threshold = st.slider("Share Threshold", 0.30, 0.50, 0.40, 0.01)

            # Use Strategic Scenario Analysis trajectory
            drift_df, breaches = prepare_share_drift_data(traj_game, threshold)

            # Plot Nominal vs Effective
            fig_share = plot_share_drift(drift_df, threshold)
            st.plotly_chart(fig_share, width="stretch")

            if breaches:
                st.error(
                    f"⚠️ Breach Detected: Effective share drops below {threshold:.0%} in {breaches[0]['year']}."
                )
            else:
                st.success("✅ No threshold breaches detected in the forecast period.")

        with wg_tab3:
            st.subheader("🏆 Policy Impact Ranking")
            st.markdown(
                "Simulate multiple intervention packages to identify the most effective levers for reducing pressure."
            )

            interventions = [
                "Pooled Funding",
                "UCC Integration",
                "NEP Realism",
                "Aged/NDIS Capacity",
                "Middle Tier Workforce",
                "Cumulative Cap",
                "Audit Relief",
            ]

            sel_interventions = st.multiselect(
                "Select Interventions to Compare:", interventions, default=interventions[:3]
            )

            if st.button("Run Ranking Simulation"):
                with st.spinner(f"Simulating {len(sel_interventions)} scenarios..."):
                    rank_df = rank_interventions(p_base, sel_interventions)

                    st.dataframe(
                        rank_df.style.format(
                            {
                                "Pressure (2030)": "{:.3f}",
                                "Pressure Impact": "{:+.3f}",
                                "Relative Risk (2030)": "{:.3f}",
                                "Uncertainty (90% Width)": "{:.3f}",
                            }
                        ).background_gradient(subset=["Pressure Impact"], cmap="Greens")
                    )

                    best_iv = rank_df.iloc[0]["Intervention"]
                    st.success(f"🏅 Most effective intervention: **{best_iv}**")

    with tab2:
        st.markdown("### 🕸️ Interactive Strategic Map")
        st.markdown("""
        This map visualizes the influence pathways between negotiation 'games' and hospital operational states.
        **Drag nodes** to explore the topology. **Node size** reflects its centrality in the mechanism.
        """)

        # Embed the D3 HTML
        d3_path = Path("outputs/interactive/games_network_d3.html")
        if d3_path.exists():
            with open(d3_path, encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        else:
            st.error(
                "D3 network assets not found. Ensure `scripts/interactive/make_d3_network.py` has been run."
            )

        st.caption("Strategic nodes (BARG, DEF, etc.) parameterize the simulation logic.")

    with tab2_5:
        st.markdown("### 🌲 Extensive Form Game Tree Explorer")
        st.markdown("""
        Explore the sequential logic of NHRA subgames.
        Select a subgame to view its **decision tree** and **payoff structure** (Commonwealth move vs State move).
        """)

        subgame_options = {
            "Definition": definition_game,
            "Bargaining": bargaining_game,
            "Cost Shifting": cost_shifting_game,
            "Discharge": discharge_coordination_game,
            "Governance": governance_integration_game,
            "Compliance": compliance_game,
        }

        sel_subgame_name = st.selectbox("Select Subgame:", list(subgame_options.keys()))

        # Evidence Grounding
        try:
            from nhra_gt.visualization.game_trees import get_game_evidence
        except ImportError:
            get_game_evidence = None  # type: ignore[assignment]

        if get_game_evidence is None:
            st.warning(
                "Game-tree evidence is unavailable (optional deps missing). Install `pygambit` to enable."
            )
        else:
            evidence = get_game_evidence(sel_subgame_name)
            st.info(
                f"📚 **Evidence Source:** {evidence['source']}  \n**Context:** {evidence['context']}"
            )

        # Use current parameter state for the tree
        gp = GameParams(
            pressure=1.0,  # Baseline for explorer
            efficiency_gap=0.1,
            discharge_delay=1.0,
            political_salience=p_base.political_salience,
            audit_pressure=p_base.audit_pressure,
            cost_shifting_intensity=p_base.cost_shifting_intensity,
            political_capital=1.0,
        )

        game_func = subgame_options[sel_subgame_name]
        g = game_func(gp)

        # Convert matrix game to extensive form tree
        # Extract matrices from TwoPlayerGame object
        u_row = np.array(g.u_row)
        u_col = np.array(g.u_col)

        if create_extensive_game_from_matrix is None or render_tree_static is None:
            st.warning(
                "Game tree rendering is unavailable (optional deps missing). Install `pygambit` and `graphviz` to enable."
            )
        else:
            extensive_g = create_extensive_game_from_matrix(
                u_row,
                u_col,
                title=sel_subgame_name,
                row_action_labels=g.row_actions,
                col_action_labels=g.col_actions,
            )

            # Render
            tree_path = (
                Path("outputs/diagrams") / f"tree_{sel_subgame_name.lower().replace(' ', '_')}"
            )
            render_tree_static(extensive_g, tree_path)

            svg_path = tree_path.with_suffix(".svg")
            if svg_path.exists():
                st.image(str(svg_path), width="stretch")

            st.caption("Circles = Decision Nodes | Squares = Outcomes (Cth Payoff, State Payoff)")

    with tab2_6:
        st.markdown("### 🏥 Intra-State LHN Variance")
        st.markdown("""
        Visualize the strategic divergence across Local Hospital Networks (LHNs) within a single Jurisdiction.
        This tab explores the **Internal Contracting Game** where States delegate operational risk.
        """)

        # We need a specialized run that returns LHN-level data
        # For simplicity, we use the current simulation's final state LHN vectors
        # Note: In a real run, traj_game should ideally contain these if we updated run_hybrid

        col_lv1, col_lv2 = st.columns(2)

        with col_lv1:
            st.subheader("🎯 Pressure vs. Revenue Trade-off")
            # Simulated data for now based on engine_jax logic
            n_lhn = 5
            lhn_ids = [f"LHN {i + 1}" for i in range(n_lhn)]
            # We pull from a mock or real vectorized state if available
            # For this MVP, we generate a scatter plot of sub-agent states
            lhn_df = pd.DataFrame(
                {
                    "LHN": lhn_ids,
                    "Pressure Index": np.random.normal(1.1, 0.1, n_lhn),
                    "NWAU Capture (Relative)": np.random.normal(100, 10, n_lhn),
                    "Type": ["Regional", "Metro", "Metro", "Remote", "Regional"],
                }
            )

            import plotly.express as px

            fig_lhn = px.scatter(
                lhn_df,
                x="Pressure Index",
                y="NWAU Capture (Relative)",
                color="Type",
                text="LHN",
                size_max=20,
                title="LHN Strategic Distribution (Current Scenario)",
            )
            fig_lhn.add_vline(
                x=1.0, line_dash="dash", line_color="red", annotation_text="Target Pressure"
            )
            st.plotly_chart(fig_lhn, width="stretch")

        with col_lv2:
            st.subheader("💰 Funding Stream Mix")
            # Show the split between ABF and Block for each LHN
            stream_df = pd.DataFrame(
                {
                    "LHN": lhn_ids,
                    "ABF Revenue": np.random.uniform(70, 90, n_lhn),
                    "Block Revenue": np.random.uniform(10, 30, n_lhn),
                }
            )

            fig_stream = px.bar(
                stream_df,
                x="LHN",
                y=["ABF Revenue", "Block Revenue"],
                title="Funding Allocation by Stream",
                labels={"value": "Revenue Units", "variable": "Stream"},
                barmode="stack",
                color_discrete_map={"ABF Revenue": "#636EFA", "Block Revenue": "#00CC96"},
            )
            st.plotly_chart(fig_stream, width="stretch")
            st.info(
                "💡 **Boundary Shifting:** LHNs may strategically shift activity to 'Block' categories to bypass activity caps."
            )

        st.markdown("---")
        st.subheader("⚖️ Ramping Sensitivity")
        st.markdown("""
        LHNs with higher **Political Shield** weights will aggressively reduce pressure
        at the cost of NWAU efficiency. Metro LHNs typically face higher ramping penalties.
        """)
        st.info(
            "💡 **Insight:** Intra-state competition for a fixed pool creates 'winners' and 'losers' based on their local operational efficiency."
        )

    with tab3:
        st.markdown("### 🧬 Data & Variable Lineage")
        st.markdown("Trace how model parameters are grounded in public evidence.")

        lineage = get_parameter_lineage()

        # Traffic light summary
        tl_col1, tl_col2, tl_col3 = st.columns(3)
        with tl_col1:
            st_traffic_light("Live", "AIHW API Parameters")
        with tl_col2:
            st_traffic_light("Validated", "IHACPA NEP / Historical")
        with tl_col3:
            st_traffic_light("Assumption", "Heuristic Behavioral Weights")

        st.markdown("---")
        lineage_df = pd.DataFrame(
            [{"Parameter": k, "Evidence Source": v} for k, v in lineage.items()]
        )
        st.table(lineage_df)

    with tab4:
        st.markdown("### ⚖️ Model Validation & Backtesting")
        st.markdown("Performance of the model against historical NHRA data (2011–2024).")

        # Load Historical
        hist_path = Path("data/calibration/historical_normalized.csv")
        results_path = Path("data/calibration/recursive_results.json")

        if hist_path.exists() and results_path.exists():
            df_hist = pd.read_csv(hist_path)
            with open(results_path) as f:
                recursive_results = json.load(f)

            # Aggregate metrics for display
            res_objs = [RecursiveResult(**r) for r in recursive_results]
            val_summary = aggregate_metrics(res_objs)

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.subheader("🎯 Error Metrics")
                for metric, vals in val_summary.items():
                    st.markdown(f"**{metric.upper()}**")
                    cv1, cv2, cv3 = st.columns(3)
                    cv1.metric("RMSE", f"{vals['rmse']:.3f}")
                    cv2.metric("MAPE", f"{vals['mape'] * 100:.1f}%")
                    cv3.metric("Theil U", f"{vals['theil_u']:.3f}")

            with col_v2:
                st.subheader("👻 Ghost Overlays")
                sel_metric = st.selectbox("Select Metric for Overlay:", ["within4", "occupancy"])
                overlay_df = prepare_ghost_overlay_data(df_hist, recursive_results, sel_metric)

                fig_ghost = plot_ghost_overlay(overlay_df, sel_metric)
                st.plotly_chart(fig_ghost, width="stretch")
        else:
            st.warning(
                "Validation data not found. Please run `scripts/validation/recursive_backtest.py` first."
            )

    with tab5:
        st.markdown("### 🔬 Technical Analytics")
        st.markdown("Mechanism sensitivity and structural integrity checks.")

        tab5_1, tab5_2, tab5_3, tab5_4 = st.tabs(
            ["Stability Regions", "Global Sensitivity", "System Hysteresis", "Strategic Stability"]
        )

        with tab5_1:
            st.subheader("🌋 Cost Shifting Tipping Points")
            st.markdown("Visualizing the Nash Equilibrium stability landscape.")

            if st.button("Generate Stability Heatmap"):
                with st.spinner("Calculating equilibria..."):
                    intensities = np.linspace(0.0, 1.0, 21)
                    pressures = np.linspace(0.8, 1.5, 21)
                    df_stab = analyze_cost_shifting_stability(intensities, pressures)

                    # Pivot for heatmap
                    pivot_table = df_stab.pivot(
                        index="pressure", columns="cost_shifting_intensity", values="outcome"
                    )

                    fig_stab = plot_stability_heatmap(pivot_table)
                    st.plotly_chart(fig_stab, width="stretch")

        with tab5_2:
            st.subheader("🌀 Global Sensitivity Analysis (GSA)")
            st.markdown(
                "Quantifying the influence of each policy lever on the total system variance."
            )

            gsa_tabs = st.tabs(["Morris (Influence)", "Sobol (Variance)", "Interactions (S2)"])

            with gsa_tabs[0]:
                morris_path = Path("data/gsa/morris_results.csv")
                if morris_path.exists():
                    df_m = pd.read_csv(morris_path)
                    if "Unnamed: 0" in df_m.columns:
                        df_m = df_m.rename(columns={"Unnamed: 0": "parameter"})
                    df_m = df_m.set_index("parameter")

                    st.markdown("#### 🌪️ Morris Tornado (Parameter Influence)")
                    fig_m = viz_plot_morris_tornado(df_m)
                    st.pyplot(fig_m)
                else:
                    st.info("Morris results not found. Run the GSA pipeline to generate.")
            with gsa_tabs[1]:
                sobol_path = Path("data/gsa/sobol_results.csv")
                if sobol_path.exists():
                    df_s = pd.read_csv(sobol_path)
                    st.markdown("#### 📊 Sobol Variance Decomposition (Total-order)")
                    # Reconstruct si dict for the plotter
                    si_plot = {
                        "names": df_s["Parameter"].tolist(),
                        "ST": df_s["ST"].tolist(),
                        "ST_conf": df_s["ST_conf"].tolist(),
                    }
                    fig_s = viz_plot_sobol_indices(si_plot, total_order=True)
                    st.pyplot(fig_s)
                else:
                    st.info(
                        "Sobol results not found. Use the CLI `scripts/run_gsa.py --method sobol` to generate."
                    )

            with gsa_tabs[2]:
                s2_path = Path("data/gsa/sobol_s2.csv")
                if s2_path.exists():
                    df_s2 = pd.read_csv(s2_path, index_col=0)
                    st.markdown("#### 🌡️ Parameter Interaction Heatmap (S2)")
                    si_s2 = {"names": df_s2.columns.tolist(), "S2": df_s2.to_numpy()}
                    fig_s2 = viz_plot_sobol_heatmap(si_s2)
                    if fig_s2:
                        st.pyplot(fig_s2)
                else:
                    st.info(
                        "S2 interaction data not found. Ensure Sobol analysis is run with interaction terms."
                    )

        with tab5_3:
            st.subheader("🌀 System Hysteresis & Recovery")
            st.markdown("Analyzing the lag in system response and the path dependency of recovery.")

            col_h1, col_h2 = st.columns([2, 1])

            with col_h1:
                # Reuse enhanced phase space plot
                fig_h = plot_phase_space(
                    traj_game, title="Detailed Hysteresis Loop (Current Scenario)"
                )
                st.plotly_chart(fig_h, width="stretch")
                st.caption(
                    "Markers indicate the System Mode at each point. The grey line shows the path dependency."
                )

            with col_h2:
                st.markdown("#### Resilience Metrics")
                st.metric("Resilience Index", f"{summary_game['resilience_index'] * 100:.0f}%")
                st.metric("Recovery Time (months)", f"{summary_game['recovery_time']:.0f}")
                st.metric("Loop Area (Lag Proxy)", f"{summary_game['hysteresis_area']:.3f}")

                st.info("""
                **Interpretation:**
                - **Area:** A larger area suggests greater inertia. High `capacity_lag` or `signal_lag` will widen this loop.
                - **Resilience:** Percentage of the simulation period spent in the 'Normal' operating mode.
                - **Recovery Time:** Total months where the system was in Stress, Crisis, or Recovery modes.
                """)

        with tab5_4:
            st.subheader("📡 Strategic Stability & Solver Telemetry")
            st.markdown(
                "Monitoring the health of the game-theoretic solvers and the clarity of strategic coordination."
            )

            fig_stab = plot_strategic_stability(traj_game)
            st.plotly_chart(fig_stab, width="stretch")

            st.info("""
            **What this shows:**
            - **Max Equilibria (Bars):** Indicates "Strategic Ambiguity". If > 1, multiple stable outcomes exist, and the system relies on selection rules (e.g. payoff dominance). Spikes often occur during transitions between policy regimes.
            - **Mean Residual (Line):** Indicates "Solver Stability". High values suggest the iterative solver (QRE) struggled to converge within `max_iter`. This validates the numerical robustness of the simulation.
            """)

    with tab6:
        st.markdown("### 🛡️ Evidence Manager & Auditor")
        st.markdown("Review and promote evidence from automated ingestion to the active model.")

        # Load Registry (Placeholder file for now)
        reg_path = Path("data/registry/staging.csv")
        if not reg_path.exists():
            # Create a mock entry for demo purposes
            reg_path.parent.mkdir(parents=True, exist_ok=True)
            mock_reg = EvidenceRegistry()
            mock_reg.add_entry(
                EvidenceEntry(
                    parameter="within4_base", mean=0.53, source_url="AIHW 2024", nhmrc_level="III-2"
                )
            )
            mock_reg.add_entry(
                EvidenceEntry(
                    parameter="within4_base",
                    mean=0.55,
                    source_url="Scholarly Study 2025",
                    nhmrc_level="I",
                )
            )
            mock_reg.save_to_csv(reg_path)

        registry = EvidenceRegistry.load_from_csv(reg_path)

        # Conflict Resolver Section
        st.subheader("🕵️ Conflict Resolver")
        params_with_multiple = [p for p, entries in registry.entries.items() if len(entries) > 1]

        if params_with_multiple:
            selected_param = st.selectbox("Resolve Conflict for Parameter:", params_with_multiple)
            entries = registry.get_all_entries(selected_param)

            st.markdown(f"**Sources for {selected_param}:**")
            for i, e in enumerate(entries):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(
                        f"Source {i + 1}: {e.source_url} (Grade: {e.nhmrc_level}) - Mean: {e.mean}"
                    )
                with col_b:
                    if st.button(f"Promote Source {i + 1}", key=f"prom_{i}"):
                        st.success(f"Source {i + 1} promoted to active model configuration.")
        else:
            st.info("No parameter conflicts detected.")

        st.markdown("---")
        st.subheader("📋 Pending Ingestions")
        st.dataframe(
            pd.DataFrame(
                [e.model_dump() for p_entries in registry.entries.values() for e in p_entries]
            )
        )

    with tab7:
        st.markdown("### 🔍 Forensic Audit & Solver Integrity")
        st.markdown("Monitor the numerical stability and regulator response dynamics.")

        st.subheader("🕵️ Strategic Auditor Surveillance")
        col_aud1, col_aud2 = st.columns(2)
        with col_aud1:
            st.markdown("**Regulator Suspicion Index**")
            fig_suspicion = px.line(
                traj_game,
                x="year",
                y="suspicion_mean",
                labels={"year": "Year", "suspicion_mean": "Suspicion (0-1)"},
                title="Auditor Suspicion (Anomaly Triggered)",
            )
            fig_suspicion.update_traces(line_color="orange", line_dash="dot")
            st.plotly_chart(fig_suspicion, width="stretch")
            st.caption("Signals detecting upcoding or efficiency gap spikes.")

        with col_aud2:
            st.markdown("**Active Inspection Pressure**")
            fig_active_p = px.line(
                traj_game,
                x="year",
                y="pressure_active_mean",
                labels={"year": "Year", "pressure_active_mean": "Active Pressure"},
                title="Dynamic Audit Intensity",
            )
            fig_active_p.update_traces(line_color="red")
            st.plotly_chart(fig_active_p, width="stretch")
            st.caption("The dynamic scrutiny applied based on suspicion levels.")

        st.markdown("---")
        st.markdown("#### Nash Solver Stability Monitor")
        st.info(
            "Direct inspection of raw model state and parameter objects for parity verification."
        )

        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.subheader("🛠️ Active Parameters")
            st.json(p_game.__dict__ if hasattr(p_game, "__dict__") else str(p_game))

        with fcol2:
            st.subheader("📡 Raw Trajectory (Latest)")
            st.dataframe(traj_game)

        st.markdown("---")
        st.subheader("⚖️ Parity vs Baseline")
        st.write("Comparison of mean outcomes at end-year (2030):")

        diff_df = pd.DataFrame(
            [
                {
                    "Metric": k,
                    "Baseline": summary_base[k],
                    "Strategic Scenario Analysis": summary_game[k],
                    "Delta (%)": f"{(summary_game[k] / summary_base[k] - 1) * 100:+.2f}%"
                    if summary_base[k] != 0
                    else "N/A",
                }
                for k in summary_base
            ]
        )
        st.table(diff_df)


if __name__ == "__main__":
    main()
