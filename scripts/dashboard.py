from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from nhra_gt.visualization.interactive import (
    plot_risk_pressure,
    plot_share_drift,
    plot_ghost_overlay,
    plot_stability_heatmap,
)
from nhra_gt.visualization.sensitivity import (
    plot_sobol_indices as viz_plot_sobol_indices,
    plot_sobol_heatmap as viz_plot_sobol_heatmap,
    plot_morris_tornado as viz_plot_morris_tornado,
)
from nhra_gt.visualization.config import PlotConfig

# Add src to path if needed for relative imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nhra_gt.domain.registry import EvidenceEntry, EvidenceRegistry
from nhra_gt.domain.stability import analyze_cost_shifting_stability
from nhra_gt.domain.validation import RecursiveResult, aggregate_metrics
from nhra_gt.engine import Params, apply_intervention, run_hybrid, summarise_outcome
from nhra_gt.sensitivity import get_parameter_lineage


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
    """Generate a rule-based automated prose summary of the Strategic Scenario Analysis results."""
    risk_change = summary_game["rr_2030"] - summary_base["rr_2030"]
    share_change = summary_game["effshare_effective_2030"] - summary_base["effshare_effective_2030"]

    narrative = "### 📜 Automated Policy Brief\n"

    if risk_change > 0.05:
        narrative += (
            f"⚠️ **Warning:** System risk is projected to increase by {risk_change:.2f} units. "
        )
    elif risk_change < -0.05:
        narrative += f"✅ **Improvement:** System risk is projected to decrease by {abs(risk_change):.2f} units. "
    else:
        narrative += "⚖️ **Stability:** System risk remains stable under this configuration. "

    if share_change > 0.02:
        narrative += f"Despite a {share_change*100:.1f}% gain in Effective Commonwealth Share, "
    elif share_change < -0.02:
        narrative += f"Compounded by a {abs(share_change)*100:.1f}% loss in Effective Share, "

    narrative += "Access Block and ED performance remain the primary drivers of system pressure."

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


def main():
    st.set_page_config(
        page_title="NHRA Strategic Scenario Dashboard", page_icon="🏥", layout="wide"
    )
    apply_custom_theme()

    st.title("🏥 NHRA Strategic Scenario Analysis (v26)")
    st.markdown("""
    ### Strategic Negotiation & System Risk Simulator (Cognitive Twin)
    This simulator models the interaction between policy levers (funding, capacity, integration)
    and the resulting strategic behavior of Commonwealth and State agents. Use the sidebar
    to adjust parameters and observe the projected impact on clinical risk and system pressure.
    """)

    with st.expander("ℹ️ How to read these results"):
        st.write("""
        - **Baseline (Grey):** Represents the system state with default configuration.
        - **Scenario (Teal):** Reflects the impact of your current lever selections.
        - **Relative Risk:** A composite proxy for patient safety risk based on access block and offload delays.
        - **System Pressure:** An index of hospital operational strain (occupancy and throughput constraints).
        """)

    # ----------------------------
    # Sidebar: Strategic Levers
    # ----------------------------
    st.sidebar.title("🎮 Strategic Levers")
    st.sidebar.info("Adjust the sliders below to simulate different NHRA negotiation outcomes.")

    # Funding Levers
    st.sidebar.subheader("💰 Funding & Valuation")
    nominal_share = st.sidebar.slider(
        "Nominal Cth Share Target",
        0.30,
        0.60,
        0.45,
        0.01,
        help="The headline funding percentage agreed in the NHRA (e.g. 45% or 50%).",
    )
    nep_growth = st.sidebar.slider(
        "NEP Annual Growth",
        0.01,
        0.08,
        0.03,
        0.005,
        help="The policy-defined growth rate of the National Efficient Price.",
    )

    # Operational Levers
    st.sidebar.subheader("🚑 Operational Capacity")
    bed_capacity = st.sidebar.slider(
        "Bed Capacity Index",
        0.70,
        1.30,
        1.00,
        0.05,
        help="Relative index of available public hospital beds. Values > 1.0 indicate expanded capacity.",
    )
    discharge_delay = st.sidebar.slider(
        "Discharge Delay Base",
        0.50,
        2.00,
        1.00,
        0.05,
        help="Impact of Aged Care and NDIS placement delays. Values < 1.0 indicate improved integration.",
    )

    # Policy & Behavioural
    st.sidebar.subheader("⚖️ Policy & Behaviour")
    political_salience = st.sidebar.slider(
        "Political Salience",
        0.05,
        0.80,
        0.30,
        0.05,
        help="The intensity of political pressure on negotiation outcomes.",
    )
    audit_pressure = st.sidebar.slider(
        "Audit Pressure",
        0.05,
        1.00,
        0.50,
        0.05,
        help="The degree of compliance scrutiny and administrative burden applied to funding.",
    )

    # Clinical & Workforce
    st.sidebar.subheader("🩺 Clinical & Workforce")
    rurality_weight = st.sidebar.slider(
        "Rurality Weight",
        0.05,
        0.70,
        0.35,
        0.05,
        help="The fraction of healthcare activity occurring in regional and remote areas.",
    )
    cost_shifting = st.sidebar.slider(
        "Cost-Shifting Intensity",
        0.05,
        0.80,
        0.35,
        0.05,
        help="The strength of incentives to shift pressures across Commonwealth/State interfaces.",
    )

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
        if "DEF" in overrides and overrides["DEF"] == "E" and nep_growth < 0.03:  # High growth implies Realism
            conflicts.append("Force 'Strict' Definition contradicts low 'NEP Growth' (Realism) intent.")
        if "SHIFT" in overrides and overrides["SHIFT"] == "S" and cost_shifting < 0.20:
            conflicts.append("Force 'Shift' strategy contradicts low 'Cost-Shifting Intensity' policy.")

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
    )
    traj_game, _ = cached_run_model(p_game, years, n_mc=st.session_state.n_mc, overrides=overrides)
    summary_game = summarise_outcome(traj_game)

    # ----------------------------
    # Main Content Area: Tabs
    # ----------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📈 Scenario Analysis",
            "🕸️ Strategic Map",
            "🧬 Data Lineage",
            "⚖️ Validation Scorecard",
            "🔬 Technical Analytics",
            "🛡️ Evidence Manager",
            "🔍 Forensic Audit",
        ]
    )

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
                fig_risk = plot_risk_pressure(combined, "rr_mean", "Relative Risk Proxy (Trajectories)", "Relative Risk")
                st.plotly_chart(fig_risk, width="stretch")
                st.caption(
                    "Lower is better. Reflects the estimated impact of system delays on clinical outcomes."
                )

                # Pressure Plot
                st.markdown("**Hospital System Pressure**")
                fig_pres = plot_risk_pressure(combined, "pressure_mean", "System Pressure Index", "Pressure Index")
                st.plotly_chart(fig_pres, width="stretch")
                st.caption(
                    "Index of operational strain. Values > 1.0 indicate severe capacity constraints."
                )
            with col2:
                st.markdown("#### Executive Summary")

                # Effective Cth Share
                share_val = summary_game["effshare_effective_2030"]
                share_base = summary_base["effshare_effective_2030"]
                st.metric(
                    "Effective Cth Share (2030)",
                    f"{share_val*100:.1f}%",
                    delta=f"{(share_val - share_base)*100:.1f}%",
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
                    f"{w4_val*100:.1f}%",
                    delta=f"{(w4_val - w4_base)*100:.1f}%",
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
        d3_path = Path("outputs/v26/interactive/games_network_d3.html")
        if d3_path.exists():
            with open(d3_path, encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        else:
            st.error(
                "D3 network assets not found. Ensure `scripts/interactive/make_d3_network_v26.py` has been run."
            )

        st.caption("Strategic nodes (BARG, DEF, etc.) parameterize the simulation logic.")

    with tab3:
        st.markdown("### Data & Variable Lineage")
        st.markdown("Trace how model parameters are grounded in public evidence.")

        lineage = get_parameter_lineage()
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
                    cv2.metric("MAPE", f"{vals['mape']*100:.1f}%")
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

        tab5_1, tab5_2 = st.tabs(["Stability Regions", "Global Sensitivity"])

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
                        "ST_conf": df_s["ST_conf"].tolist()
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
                        f"Source {i+1}: {e.source_url} (Grade: {e.nhmrc_level}) - Mean: {e.mean}"
                    )
                with col_b:
                    if st.button(f"Promote Source {i+1}", key=f"prom_{i}"):
                        st.success(f"Source {i+1} promoted to active model configuration.")
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
        st.markdown("### 🔍 Forensic Audit & State Introspection")
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
                    "Delta (%)": f"{(summary_game[k]/summary_base[k] - 1)*100:+.2f}%"
                    if summary_base[k] != 0
                    else "N/A",
                }
                for k in summary_base
            ]
        )
        st.table(diff_df)


if __name__ == "__main__":
    main()
