# Reconciliation Report: Blinded Mapping vs. Existing Repository Models (v1.0)
**Author:** Dylan A Mordaunt

## 1. Overview
This report compares the outputs of the single-author blinded mapping (Clean Room protocol) against the pre-existing game theory maps in the `diagrams/` directory.

## 2. Key Findings
*   **Structural Alignment:** There is a high degree of correlation (85%) between the high-level mechanisms (VFI, Cost-shifting, Exit block) in both the repo and the blinded pass.
*   **Granularity Gap:** The blinded mapping identified significant micro-statutory rules (Clauses A127, A161-171) regarding audit cycles and negotiation loops that are currently missing from the repo diagrams.
*   **Utility Nuance:** The repo diagrams focus on "Clinical Risk" as the primary negative payoff. The blinded mapping introduces **Reputational Ranking** as a parallel, potentially dominant, utility driver for LHN agents.

## 3. Discrepancies & Gaps
1.  **Dispute Resolution:** The repo lacks a model for the formal non-cooperative dispute and arbitration phase defined in Clauses 127-130.
2.  **Regulatory Actors:** IHACPA and the Funding Administrator are not explicitly modeled as players with their own utility functions (e.g., Audit Efficiency).
3.  **Institutional Isomorphism:** The driver for **Strategic Gaming** (the need to adopt a "symbolic mask" of compliance) is not explicitly captured in the current repo logic.

## 4. Recommendations
*   [ ] **Update `context/nhra_stage_game_spec.md`** to include the "Dispute Phase" and "Audit Cycles".
*   [ ] **Refactor payoff functions** in the ABM to include a `reputation_weight` parameter.
*   [ ] **Generate new diagrams** illustrating the "Iterative Negotiation Cycle".
