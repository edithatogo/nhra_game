# Code-to-Text Parity Audit (P2 Manuscript)
**Author:** Dylan A Mordaunt

## 1. Core Equations Audit

| Equation | Protocol/Spec Definition | Implementation (src/nhra_gt/engine.py) | Parity Status |
| :--- | :--- | :--- | :--- |
| **Wait Time (M/M/s)** | Kingman-like approximation | `mm_s_queue_wait` function (lines 51-68) | **Match** |
| **Utility Function** | $U_i = \alpha F + \beta R - C$ | Not explicitly unified in a single class method; distributed in `HeuristicAgent.decide` payoffs. | **Partial** |
| **Pressure Index** | Composite of occ, offload, and discharge lag. | `pressure_index` (lines 118-123) and `ops_step` (lines 265-271). | **Match** |
| **Within-4h Map** | Logistic transfer function. | `within4_from_pressure` (lines 71-73) | **Match** |

## 2. Identified Discrepancies
*   **Reputation Variable:** The protocol mentions `reputation_score` ($R$), but this variable is not explicitly tracked in the `State` dataclass in `engine.py`.
*   **Wait Time servers:** The code uses `capacity * 10.0` as the server count (line 269), which is a hardcoded heuristic. The protocol should justify this multiplier.

## 3. Recommended Code Refinements
*   [ ] Add `reputation_score` to `State` dataclass.
*   [ ] Unify the `decide` logic to use an explicit utility calculation method for better traceability.
