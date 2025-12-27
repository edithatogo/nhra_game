# Implementation Plan: Multi-Agent Logic Refactor

## Phase 1: Agent Class & Utility Foundations
- [ ] Task: Implement `AgentState` and `AgentParams` Pytrees in `src/nhra_gt/domain/state.py`.
- [ ] Task: Define utility functions for **LHN (Ramping/NWAU)** and **State (VFI/KPI)** in a new `src/nhra_gt/agents.py`.
- [ ] Task: Create smoke tests for agent decision logic.

## Phase 2: Hierarchical Engine Refactor
- [ ] Task: Refactor `StateJax` to support nested LHN vectors (1:N mapping).
- [ ] Task: Update `engine_jax.py` to implement the "Delegation" step (State -> LHN).
- [ ] Task: Verify 1:1 parity with the current monolithic JAX core.

## Phase 3: Multi-Agent Scenarios & Visualization
- [ ] Task: Implement "Intra-State Competition" scenario (LHNs competing for a fixed pool).
- [ ] Task: Create a "Ramping vs. Revenue" trade-off visualization in the dashboard.
- [ ] Task: Final Conductor verification and documentation update.
