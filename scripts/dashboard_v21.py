from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path if needed for relative imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

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
    # Main Content Area
    # ----------------------------
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### System Trajectories")
        st.info("Visualizations will appear here in Phase 2.")
        
    with col2:
        st.markdown("#### Executive Summary")
        st.metric("Effective Cth Share", f"{nominal_share*100:.1f}%", delta="0.0%")
        st.metric("Relative Risk Proxy", "1.00", delta="0.0")

if __name__ == "__main__":
    main()
