# Technical Audit: Version Comparison & Feature Gaps

**Audit Date:** 2025-12-22  
**Versions Sampled:** v1, v5, v9, v15, v19, v21

## 1. Overview of Model Evolution
The project has transitioned from isolated "stage game" scripts (v1-v5) to a unified Hybrid Simulation Framework (v8+). The core logic relies on Monte Carlo rollouts to simulate NHRA negotiation dynamics and downstream system pressures (ED crowding, access block).

## 2. Identified Feature Gaps & Logic Variations

### A. Calibration Logic (v2 vs v21)
- **Status:** Partially Omitted.
- **Finding:** `nhra_games_v2_calibrated.py` contained specific logic for parameter tuning against hypothetical "calibration targets". While `v9` introduced Optuna optimization, the specific constraints and objective functions used in `v2` appear more granular for certain bargaining games.
- **Action:** Review `v2` objective functions for re-integration into the `v21` Optuna suite.

### B. Heuristic Divergence (v5 vs v8+)
- **Status:** Variation found.
- **Finding:** `nhra_hybrid_v5.py` used a simpler heuristic for discharge coordination than the Nash Equilibrium solver introduced in `v8`. While the Equilibrium approach is more rigorous, the v5 heuristic might be useful as a "bounded rationality" baseline for comparison.
- **Action:** Implement the v5 heuristic as an optional "Strategy Rule" in the `v21` framework.

### C. Narrative Reporting (v16/v19 vs v21)
- **Status:** Drift found.
- **Finding:** Between `v16` and `v19`, the narrative generator (`build_report_v*.py`) underwent significant changes in how it synthesizes "Reviewer Comments" into the summary. The current `v21` logic is concise, but some of the detailed qualitative synthesis from `v19` was dropped.
- **Action:** Restore the expanded narrative synthesis logic from `v19` to support the MJA publication goal.

## 3. Preservation Status
- **Monte Carlo Engine:** Stable and improved.
- **D3 Network Visualization:** Integrated and functional.
- **Snakemake Pipeline:** Formalized in `v21`.
- **MJA Manuscript Drafts:** Successfully tracked and versioned.

## 4. Recommendations for Roadmap
1. **Re-integrate** the "v5 Heuristic" as a strategy option.
2. **Standardize** Optuna objective functions using the v2 calibration principles.
3. **Enhance** the report generator with the lost qualitative synthesis from v19.
