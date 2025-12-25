# Forensic Parity Audit Report

**Date:** 2025-12-25
**Goal:** Ensure 100% feature parity between origin (ChatGPT/Archives) and current repository.

## 1. Executive Summary
The forensic audit compared 30 archived zip files, 97 diagrams, and the captured ChatGPT intent against the current `engine.py` (v9).
While the core strategic games are implemented, several legacy solver functions and specific subgame nuances have been refactored or are missing in the current version.

## 2. Feature Parity Matrix
| Feature | Category | Status | Source |
| :--- | :--- | :--- | :--- |
| Influence: VFI -> Pressure | Visual | [Implemented] | Diagrams |
| Influence: AgedCare -> Discharge | Visual | [Implemented] | Diagrams |
| Influence: Audit -> Burden | Visual | [Implemented] | Diagrams |
| Influence: Pressure -> Signalling | Visual | [Implemented] | Diagrams |
| Logic: solve_equilibrium | Logic | [Refactored] | Legacy Zips |
| Logic: nash_manager | Logic | [Refactored] | Legacy Zips |
| Logic: monte_carlo_rollout | Logic | [Refactored] | Legacy Zips |
| Intent: Vertical Fiscal Imbalance | Intent | [Implemented] | ChatGPT Context |
| Intent: Efficiency Gap | Intent | [Implemented] | ChatGPT Context |
| Intent: Clinical Governance | Intent | [Implemented] | ChatGPT Context |
| Intent: Hatch/pyOpenSci | Intent | [Implemented] | ChatGPT Context |


## 3. Orphaned Logic (Legacy Artifacts)
Identified 326 instances of logic in archives that are not explicitly present in the current engine.
Top candidates for recovery review:
- `nash_eq` (found in 66 locations)
- `nash_best_response_iter` (found in 22 locations)
- `build_games_graph` (found in 17 locations)
- `render_games_graph_interactive` (found in 17 locations)
- `test_decide_strategies_equilibrium_branch_runs` (found in 11 locations)
- `pure_nash` (found in 10 locations)
- `mixed_nash_2x2` (found in 10 locations)
- `all_nash` (found in 10 locations)
- `select_equilibrium` (found in 10 locations)
- `TwoPlayerGame` (found in 10 locations)


## 4. Identified Critical Gaps
- **Bargaining Outside Option:** Diagrams show explicit 'Schedule K' and 'bailout' nodes which are currently simplified in the engine.
- **Audit Feedback Nuance:** Legacy versions had more granular 'coding effort' vs 'audit intensity' games that are now aggregated into a single `COMP` node.
- **Multi-Equilibrium Selection:** While implemented, the stability analysis across all discovered equilibria needs more robust visualization compared to legacy outputs.