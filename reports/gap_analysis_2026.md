# Gap Analysis Report: NHRA Game Artifacts (January 2026)

## 1. Executive Summary

The NHRA Game project has achieved a high level of functional implementation, with the JAX-based simulation engine (`src/nhra_gt`) closely mirroring the core logic of the qualitative (P1) and quantitative (P2) manuscripts. However, the codebase and Streamlit dashboard have evolved significantly ahead of the manuscripts, introducing advanced forensic, visualization, and validation features that are currently undocumented in the scientific record. Conversely, some specific theoretical mechanisms mentioned in the early manuscripts (e.g., sequential Rubinstein bargaining) remain simplified in the code.

**Status:** The artifacts are *divergent but compatible*. Synchronization requires updating the manuscripts to reflect the "maximal" feature set found in the dashboard, rather than downgrading the code.

## 2. Manuscript P1 (Qualitative Mapping) Analysis

**Goal:** Map game-theoretic mechanisms to code.

| Mechanism / Concept | Implementation Status | Discrepancy / Action |
| :--- | :--- | :--- |
| **Action Situations (AS2)** | **Implemented** | `coding_audit_game`, `cost_shifting_game` in `subgames/games.py`. Matches text. |
| **Information Lags** | **Implemented** | `signal_lag_months` in `state.py`. Matches text logic. |
| **Rubinstein Bargaining** | **Simplified** | Text implies sequential alternating offers; Code uses simultaneous 2x2 Nash or static bargaining weights. **Gap:** Update text to reflect "Simultaneous Nash Bargaining" or flag for future. |
| **Stackelberg Leadership** | **Simplified** | Code uses simultaneous moves. Leader-Follower dynamics are emergent via parameter sensitivity, not structural turns. |
| **Risk Dominance** | **Missing** | Code solves for Nash Equilibria but does not explicitly calculate Risk Dominance scores for selection. |
| **Fragility Nodes** | **Implicit** | Logic exists (lags, thresholds), but the specific term "Fragility Node" is not used in the codebase. |

**Recommendation:** Update P1 to accurately describe the "Simultaneous/Static" approximations used for bargaining, or add a "Future Work" section for sequential extensions.

## 3. Manuscript P2 (Quantitative Modeling) Analysis

**Goal:** Cross-reference parameters and validation.

| Manuscript Term | Code Parameter | Status |
| :--- | :--- | :--- |
| **Reputation Weight ($eta$)** | `kpi_satisfaction` / `ramping_penalty` | **Mismatch:** Naming convention differs significantly. Needs Glossary. |
| **Revenue Weight ($\alpha$)** | `nwau_utility` | **Mismatch:** Greek vs. English. |
| **Coding Intensity ($ heta$)** | `coding_intensity` | **Match.** |
| **Audit Pressure ($P_{audit}$)** | `audit_pressure` | **Match.** |
| **Transparency Surge** | *None* | **Gap:** Modeled as a scenario (high `audit_pressure`), not a distinct mechanism/function. |
| **Morris Method** | `src/nhra_gt/sensitivity.py` | **Match:** Implemented but needs verification that configuration matches text. |

**Recommendation:** Create a definitive `glossary_abbreviations.md` mapping Greek symbols to Python variable names. Update P2 parameter tables to include both.

## 4. Dashboard (Streamlit) Audit

**Goal:** Identify undocumented features.

The dashboard (`https://gameofnhra.streamlit.app/`) contains significant "Value-Add" features absent from the manuscripts:

1. **Forensic Audit & Solver Integrity:** Real-time monitoring of "Regulator Suspicion" and "Nash Stability".
2. **Intra-State LHN Variance:** Scatter plots showing strategic divergence between individual LHNs (a hierarchical feature not fully detailed in P1/P2).
3. **Game Tree Explorer:** Interactive visualization of extensive form trees (PyGambit integration).
4. **Strategic Map:** D3.js topology of game influences.
5. **Ex-Post Narrator:** Auto-generated prose summarizing simulation outcomes (`generate_prose_summary`).

**Recommendation:** These are major scientific contributions. P2 (Modelling) should be updated to include the "Forensic" and "Variance" modules. P1 (Mapping) should reference the "Strategic Map" visualization.

## 5. Strategic Plan & Recommendations

### Immediate Actions (Phase 3 & 4)

1. **Glossary Unification:** Create a master dictionary mapping Manuscript Terms <-> Code Variables.
2. **Manuscript Update (P1):** Refine "Bargaining" section to reflect current implementation; add "Fragility Node" explicit labeling to code documentation.
3. **Manuscript Update (P2):** Add sections describing the "Forensic Audit" and "LHN Variance" modules.
4. **Dashboard Snapshot:** Tag the current dashboard version (`v2026.1`) in git and reference this specific version in the OSF protocol.

### Future Tracks (Post-Sync)

1. **Sequential Bargaining Engine:** Implement true Rubinstein/Stackelberg logic (requires major engine refactor).
2. **Risk Dominance Selector:** Add equilibrium selection logic based on Risk Dominance.
