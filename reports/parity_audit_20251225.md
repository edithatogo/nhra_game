# Forensic Parity Audit Report - 25 December 2025

## 1. Executive Summary

This audit evaluated the alignment between the NHRA game-theory simulation engine (`src/`) and the user-facing Streamlit dashboard (`v21`). Overall, functional parity for the core simulation loop is excellent, with <1% statistical divergence. However, several advanced visualizations and strategic nuances present in the codebase are currently missing from the UI.

## 2. Parity Baseline Results

| Metric | Divergence (Lite vs Full) | Status |
| :--- | :--- | :--- |
| System Pressure | 0.13% | ✅ Pass |
| ED Within 4h | 0.13% | ✅ Pass |
| Relative Risk | 0.02% | ✅ Pass |
| Efficiency Gap | 0.00% | ✅ Pass |

## 3. Findings: Lost & Missing Features

### A. Visualizations

- **Interactive Games Network:** The D3-based interactive strategic map (`scripts/interactive/`) is missing from the dashboard.
- **Global Sensitivity (Sobol):** While Morris tornado plots are present, Sobol variance decomposition and interaction heatmaps are not yet integrated.
- **Convergence Audit:** The UI lacks a tool to verify MC convergence for specific scenarios.

### B. Logic & Strategy

- **Direct Game Selection:** Subgames (Bargaining, Compliance, etc.) are only adjustable via indirect policy interventions rather than direct strategy overrides.
- **Signalling Game:** The Signalling (Transparency) game logic from `engine.py` is not explicitly visualized or parameterized in the sidebar.

### C. Technical Debt

- **Legacy References:** Minor "ghost" references to `v1`, `v2`, and `v3` were found in the dashboard script metadata but do not affect runtime.

## 4. Recovered Features (This Track)

- **Forensic Audit Tab:** A new "🔍 Forensic Audit" tab has been added to the dashboard, providing real-time introspection of raw `State` and `Params` objects.
- **Parity Regression Suite:** `tests/test_dashboard_parity.py` now enforces functional consistency between the engine and UI.

## 5. Recommended Roadmap Updates

1. **Phase 8:** Integrate D3 Interactive Network into a new dashboard tab.
2. **Phase 9:** Implement full GSA (Sobol) visualization suite.
3. **Phase 10:** Add direct subgame strategy overrides for "expert" users.
