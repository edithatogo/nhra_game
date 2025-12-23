from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add src to path if needed for relative imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nhra_game_theory.v8 import Params, run_hybrid, summarise_outcome

@st.cache_data
def cached_run_model(p: Params, years: list[int], n_mc: int = 50):
    """Run the model with caching to ensure responsive UI."""
    return run_hybrid(years, p, seed=42, n_mc=n_mc)

def apply_custom_theme():
    """Apply Teal/Minimalist Academic theme using custom CSS."""
    st.markdown("""
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
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="NHRA War Gaming Dashboard",
        page_icon="🏥",
        layout="wide"
    )
    apply_custom_theme()
    
    st.title("🏥 NHRA War Gaming Dashboard (v21)")
    st.markdown("### Strategic Negotiation & System Risk Simulator")
    
    # ----------------------------
    # Sidebar: War Gaming Levers
    # ----------------------------
    st.sidebar.title("🎮 War Gaming Levers")
    st.sidebar.info("Adjust the sliders below to simulate different NHRA negotiation outcomes.")

    # Funding Levers
    st.sidebar.subheader("💰 Funding & Valuation")
    nominal_share = st.sidebar.slider(
        "Nominal Cth Share Target", 0.30, 0.60, 0.45, 0.01,
        help="The headline funding percentage agreed in the NHRA (e.g. 45% or 50%)."
    )
    nep_growth = st.sidebar.slider(
        "NEP Annual Growth", 0.01, 0.08, 0.03, 0.005,
        help="The policy-defined growth rate of the National Efficient Price."
    )

    # Operational Levers
    st.sidebar.subheader("🚑 Operational Capacity")
    bed_capacity = st.sidebar.slider(
        "Bed Capacity Index", 0.70, 1.30, 1.00, 0.05,
        help="Relative index of available public hospital beds. Values > 1.0 indicate expanded capacity."
    )
    discharge_delay = st.sidebar.slider(
        "Discharge Delay Base", 0.50, 2.00, 1.00, 0.05,
        help="Impact of Aged Care and NDIS placement delays. Values < 1.0 indicate improved integration."
    )

    # Policy & Behavioural
    st.sidebar.subheader("⚖️ Policy & Behaviour")
    political_salience = st.sidebar.slider(
        "Political Salience", 0.05, 0.80, 0.30, 0.05,
        help="The intensity of political pressure on negotiation outcomes."
    )
    audit_pressure = st.sidebar.slider(
        "Audit Pressure", 0.05, 1.00, 0.50, 0.05,
        help="The degree of compliance scrutiny and administrative burden applied to funding."
    )

    # Clinical & Workforce
    st.sidebar.subheader("🩺 Clinical & Workforce")
    rurality_weight = st.sidebar.slider(
        "Rurality Weight", 0.05, 0.70, 0.35, 0.05,
        help="The fraction of healthcare activity occurring in regional and remote areas."
    )
    cost_shifting = st.sidebar.slider(
        "Cost-Shifting Intensity", 0.05, 0.80, 0.35, 0.05,
        help="The strength of incentives to shift pressures across Commonwealth/State interfaces."
    )

    # ----------------------------
    # Model Execution
    # ----------------------------
    years = list(range(2025, 2031))
    
    # Baseline
    p_base = Params()
    traj_base, _ = cached_run_model(p_base, years)
    summary_base = summarise_outcome(traj_base)
    
    # War Game
    p_game = Params(
        nominal_cth_share_target=nominal_share,
        nep_annual_growth=nep_growth,
        bed_capacity_index=bed_capacity,
        discharge_delay_base=discharge_delay,
        political_salience=political_salience,
        audit_pressure=audit_pressure,
        rurality_weight=rurality_weight,
        cost_shifting_intensity=cost_shifting
    )
    traj_game, _ = cached_run_model(p_game, years)
    summary_game = summarise_outcome(traj_game)

    # ----------------------------
    # Main Content Area
    # ----------------------------
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### System Trajectories")
        
        # Prepare Plotly Data
        traj_base["Scenario"] = "Baseline"
        traj_game["Scenario"] = "War Game"
        combined = pd.concat([traj_base, traj_game])
        
        # Risk Plot
        fig_risk = px.line(
            combined, x="year", y="rr_mean", color="Scenario",
            title="Relative Risk Proxy (Trajectories)",
            labels={"rr_mean": "Relative Risk", "year": "Year"},
            color_discrete_map={"Baseline": "grey", "War Game": "#008080"}
        )
        fig_risk.update_layout(template="simple_white", hovermode="x unified")
        st.plotly_chart(fig_risk, width="stretch")
        
        # Pressure Plot
        fig_pres = px.line(
            combined, x="year", y="pressure_mean", color="Scenario",
            title="System Pressure Index",
            labels={"pressure_mean": "Pressure Index", "year": "Year"},
            color_discrete_map={"Baseline": "grey", "War Game": "#008080"}
        )
        fig_pres.update_layout(template="simple_white", hovermode="x unified")
        st.plotly_chart(fig_pres, width="stretch")
        
    with col2:
        st.markdown("#### Executive Summary")
        
        # Effective Cth Share
        share_val = summary_game["effshare_effective_2030"]
        share_base = summary_base["effshare_effective_2030"]
        st.metric(
            "Effective Cth Share (2030)", 
            f"{share_val*100:.1f}%", 
            delta=f"{(share_val - share_base)*100:.1f}%"
        )
        
        # Relative Risk
        risk_val = summary_game["rr_2030"]
        risk_base = summary_base["rr_2030"]
        st.metric(
            "Relative Risk Proxy (2030)", 
            f"{risk_val:.2f}", 
            delta=f"{risk_val - risk_base:.2f}",
            delta_color="inverse"
        )
        
        # Within 4 Hours
        w4_val = summary_game["within4_2030"]
        w4_base = summary_base["within4_2030"]
        st.metric(
            "Within 4 Hours (2030)", 
            f"{w4_val*100:.1f}%", 
            delta=f"{(w4_val - w4_base)*100:.1f}%"
        )

if __name__ == "__main__":
    main()
