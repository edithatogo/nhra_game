# Track Spec: Interactive Web Dashboard (Streamlit)

## Overview
This track implements a multi-tiered interactive web dashboard using Streamlit. The dashboard serves as the primary "War Gaming" interface for the NHRA model, providing a spectrum of insights ranging from accessible policy-level executive summaries to granular technical analytics for health department researchers.

## Target Audience
- **RACMA Policy Leaders:** Executive-level decision support.
- **Health Department Analysts:** Technical parameter and data verification.
- **Academic/MJA Readers:** Methodological transparency and results replication.

## Key Features
- **Multi-Tiered Layering:**
    - *Executive Summary:* High-level cards for policy leaders showing impact on system risk and funding equity.
    - *War Gaming Sidebar:* Categorized interactive sliders (Funding, Operational, Policy, Clinical).
    - *Technical Deep-Dive:* Detailed tabs for sensitivity and uncertainty analysis.
- **Explainability & Lineage (SOTA):**
    - *Mechanism Tooltips:* Educational popups explaining the theoretical logic of each lever.
    - *Data Provenance Mapping:* A "Lineage" view showing the path from evidence source -> model parameter -> final analytic.
    - *Dynamic Narrative Generation:* Automated prose summary of the current scenario results.
- **Scenario Management:**
    - *Side-by-Side Comparison:* Multi-series Plotly charts for counterfactual analysis against the baseline.
    - *Snapshot Suite:* Ability to save/load specific war-game configurations as JSON.
- **Performance Engine:**
    - *Hybrid-Fidelity Rollouts:* Real-time low-latency updates with caching, plus optional high-fidelity execution.

## Non-Functional Requirements
- **Academic Standard Styling:** Compliance with MJA visual requirements (teal/minimalist palette, vector exports).
- **Explainability First:** Clinical metrics defined in plain English tooltips.
- **Computational Efficiency:** Use of `st.cache_data` to ensure responsive UI during Monte Carlo rollouts.

## Acceptance Criteria
- Dashboard loads locally via `streamlit run scripts/dashboard_v21.py`.
- The "Lineage" feature correctly displays the source URL for at least one primary model input from the context pack.
- Users can interactively modify levers and see side-by-side Plotly chart updates.
- Users can export a PDF/JSON "Scenario Snapshot" containing the narrative and figures.
