# Implementation Plan: Advanced Game Theoretic Enhancements

## Phase 1: Queuing Game & Endogenous Demand
- [ ] Task: Implement `patient_utility_jax` and `demand_equilibrium_solver` in `src/nhra_gt/engine_jax.py`.
- [ ] Task: Replace exogenous demand logic with the endogenous solver.
- [ ] Task: Verify the "GP Spillover" effect via unit tests.

## Phase 2: Renegotiation & Hold-Up Dynamics
- [ ] Task: Implement the "Agreement Clock" in `StateJax`.
- [ ] Task: Implement the deadline renegotiation subgame logic (Extensive Form).
- [ ] Task: Integrate renegotiation outcomes into the multi-year rollout (`lax.scan`).

## Phase 3: Workforce Competition (Shared Pool)
- [ ] Task: Implement `WorkforcePool` state and coupling logic.
- [ ] Task: Add "Recruitment Intensity" as a strategic choice for LHNs.
- [ ] Task: Final verification and dashboard updates.
