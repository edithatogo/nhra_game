# Audit Report: Stage Game Implementation
**Date:** 2025-12-26
**Scope:** `src/nhra_game_theory` vs `context/nhra_stage_game_spec.md`

## Executive Summary
The current codebase implements a **high-level, aggregate system dynamics model** informed by **abstract 2x2 matrix games**. It does **not** implement the detailed, multi-agent, extensive-form stage game described in the specification. The implementation flattens the LHN/Jurisdiction hierarchy into a single global state and approximates complex sequential moves (audits, claims, renegotiation) as simple monthly parameter updates.

## Key Discrepancies

### 1. Structural Mismatch (Extensive vs. Normal Form)
*   **Spec:** Defines a sequential **Extensive Form Game** with 8 distinct steps per month (World -> Nature -> State -> LHN -> Claims -> Payment -> Audit -> Signal).
*   **Code:** Implements a **System Dynamics Loop** (`engine.py::step`) where "Game Strategies" are inputs determined by isolated **2x2 Normal Form Games** (`games.py`).
    *   *Evidence:* `games.py` defines `definition_game`, `bargaining_game`, etc., as static `TwoPlayerGame` matrices.
    *   *Impact:* Temporal nuance (who moves first) and information asymmetry (what LHN knows vs. State) are lost.

### 2. Agent Granularity (Multi-Agent vs. Aggregate)
*   **Spec:** Distinguishes between **State/Territory (Principal)** and **LHNs/Hospitals (Agents)**. Each has its own state (`J_t` vs `P_t`) and decision variables.
*   **Code:** Uses a single `HeuristicAgent` that outputs a global `strategies` dictionary. There is no differentiation between a "State" player and an "LHN" player in the runtime; the system evolves as a single unit.
    *   *Evidence:* `engine.py::State` is a single flat dataclass. No `lhn_list` or `jurisdiction_list`.

### 3. Temporal Layers (Monthly/Annual/Cycle)
*   **Spec:** Explicitly separates **Monthly** (Ops), **Annual** (Financial/Cap), and **Cycle** (Constitutional/Renegotiation) layers.
*   **Code:** Flattens everything into a **Monthly** timestep.
    *   *Annual:* Handled via simple `if month > 12` checks in `step()`.
    *   *Cycle:* The "5-year agreement cycle" is missing. Renegotiation (`BARG` strategy) happens every month in `policy_step`, continuously drifting the `effective_cth_share`.

### 4. Missing State Variables
*   **Investment Pipeline:** Spec `inv_pipe_pt` (lags) is modeled only as a simple `capacity_lag` scalar in `ops_step`.
*   **Queues:** Spec `q_el_pt[u]` (elective queues by urgency) is simplified to a single `wait_min` metric.
*   **Coding Intensity:** Spec `theta_pt` is a global `coding_intensity` scalar, not per-provider.

## Recommendations for Phase 5
1.  **Acknowledge Abstraction:** Update `context/nhra_stage_game_spec.md` to reflect that the current code is a "Macro-Scale Approximation" of the spec, OR
2.  **Refactor for Agents:** Introduce `Jurisdiction` and `LHN` classes to hold distinct state, even if the interaction remains simplified.
3.  **Cycle Logic:** Implement an explicit "Constitution" state machine to handle the 5-year renegotiation shocks properly, rather than continuous drift.
