# Forensic Parity Audit & Recovery Plan - 25 December 2025

## 1. Executive Summary
The forensic audit confirmed that while the core simulation engine is statistically identical to the user-facing dashboard (<1% divergence), several high-value "ghost" features from legacy versions and diagrams are currently missing from the UI.

## 2. Prioritized Recovery Candidates (Phase 6 Implementation)

### High Priority (Functional Gaps)
1. **Interactive Games Network (D3):** Recover the interactive strategic map visualization from `scripts/interactive/` and integrate it as a new dashboard tab.
2. **Sobol Variance Decomposition:** Implement UI support for displaying Sobol indices and interaction heatmaps from the GSA pipeline.
3. **Direct Subgame Overrides:** Add a "Policy Expert" sidebar to allow manual selection of game strategies (e.g., forcing a 'Strict' definition).

### Medium Priority (Technical Depth)
4. **Convergence Guard:** Add a statistical convergence indicator to the UI to warn users when low MC samples (Lite mode) might be unstable.
5. **Signalling Game Visualization:** Explicitly parameterize and plot the signalling/transparency game logic.

### Low Priority (Hygiene)
6. **Legacy Ref Cleanup:** Remove metadata-only references to `v1`, `v2`, `v3` in the dashboard script to reduce forensic noise.

## 3. Audit Artifacts
- **Matrix:** `reports/parity_matrix.csv`
- **Orphan Check:** `reports/orphaned_logic.json`
- **Full Report:** `reports/parity_audit_20251225.md`
