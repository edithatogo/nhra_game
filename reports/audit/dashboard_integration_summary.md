# Dashboard & Engine Integration Audit Summary (January 2026)

## Overview
This audit evaluated the depth of integration between the Streamlit Dashboard (`scripts/dashboard.py`) and the JAX-native simulation engine. While the dashboard is visually sophisticated, several advanced features rely on partial mocks or hardcoded parameter lists, preventing full data-driven strategic analysis.

## Feature Scorecard

| Feature | Status | Grade | Key Findings |
| :--- | :--- | :--- | :--- |
| **Evidence Manager** | Partially Mocked | 🔴 Red | Reads CSV for display only. Model input is limited to 10 hardcoded sliders. 'Promote' only works for those keys. |
| **Intra-State LHN Variance** | Partially Integrated | 🟡 Amber | Successfully pulls Pressure/NWAU vectors from JAX snapshot. However, LHN 'Type' and 'Block Revenue' are still randomized in the UI. |
| **Sequential Bargaining UI** | Missing | 🔴 Red | Backend supports `use_sequential_bargaining`, but no sidebar toggle or scenario configuration exists to enable it in the UI. |
| **Forensic Audit** | Integrated | 🟢 Green | Successfully traces `suspicion_mean` and `active_pressure` from engine outputs. |

## Detailed Findings

### 1. Evidence Manager (Tab 6)
The dashboard lacks a dynamic parameter bootstrap. `initialize_slider_state` and the `Params` constructor in `main()` manually list a subset of the registry. Consequently, any parameter added to `parameter_registry.csv` that isn't in this list remains invisible to the simulation logic in the UI.
- **Action:** Refactor parameter handling to use `ParamsJax.from_yaml` or a dynamic loop over `st.session_state` keys that match the dataclass fields.

### 2. LHN Variance (Tab 2_6)
The plumbing for "Live" data exists via `traj_game.attrs['lhn_snapshot']`. However:
- The `Type` (Metro/Regional/Remote) is assigned via `np.random.choice`.
- The `Block Revenue` is calculated via `np.random.uniform` based on a global parameter.
- **Action:** Expand `StateJax` or the snapshot logic to capture LHN-level types and specific funding streams.

### 3. Sequential Bargaining
This feature is currently a "Dark Mode" backend capability.
- **Action:** Add `st.sidebar.toggle("Enable Sequential Bargaining")` and pass the value to `Params(...)`.

## Conclusion
The dashboard is currently a **High-Fidelity Wireframe** for several SOTA features. Moving to a fully "Live" integrated state requires refactoring the parameter override logic and expanding the LHN-level telemetry captured during the simulation rollout.
