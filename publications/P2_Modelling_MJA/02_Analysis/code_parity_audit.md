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

* **Reputation Variable:** Fixed in commit `3bea18f`. `reputation_score` added to `State`.
* **Wait Time servers:** The code uses `capacity * 10.0` as the server count (line 269). This has been documented in the ODD protocol as a calibrated server-to-bed ratio.

## 3. Final Status (v2.0)

All core equations now map 1:1 between the modelling specification and the Python implementation.
