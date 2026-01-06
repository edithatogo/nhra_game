# Implementation Plan: Multi-Agent Logic Refactor

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Agent Class & Utility Foundations [checkpoint: d76ceaa]

- [x] Task: Implement `AgentState` and `AgentParams` Pytrees in `src/nhra_gt/domain/state.py`.
- [x] Task: Define utility functions for **LHN (Ramping/NWAU)** and **State (VFI/KPI)** in a new `src/nhra_gt/agent_logic.py`.
- [x] Task: Create smoke tests for agent decision logic.

## Phase 2: Hierarchical Engine Refactor [checkpoint: d76ceaa]

- [x] Task: Refactor `StateJax` to support nested LHN vectors (1:N mapping).
- [x] Task: Update `engine_jax.py` to implement the "Delegation" step (State -> LHN).
- [x] Task: Verify 1:1 parity with the current monolithic JAX core.

## Phase 3: Multi-Agent Scenarios & Visualization [checkpoint: d76ceaa]

- [x] Task: Implement "Intra-State Competition" scenario (LHNs competing for a fixed pool).
- [x] Task: Create a "Ramping vs. Revenue" trade-off visualization in the dashboard.
- [x] Task: Final Conductor verification and documentation update.
