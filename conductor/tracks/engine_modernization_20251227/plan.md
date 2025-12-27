# Implementation Plan: NHRA Engine Modernization (JAX & Polars)

## Phase 1: JAX Foundation & Logic Parity
- [ ] Task: Define `Pytree` state structures and pure functional `step()` logic.
- [ ] Task: Implement multi-year rollout logic using `jax.lax.scan`.
- [ ] Task: Implement **Mirror Test Harness** to verify parity with v26 logic.
- [ ] Task: Conductor - User Manual Verification 'JAX Foundation' (Protocol in workflow.md)

## Phase 2: Differentiable Solvers & Equilibrium Oracle
- [ ] Task: Implement QRE, Regret-Min, and Discrete (JVP) solvers in JAX.
- [ ] Task: Implement **PyGambit Oracle** test suite to validate solvers.
- [ ] Task: Conductor - User Manual Verification 'Differentiable Solvers' (Protocol in workflow.md)

## Phase 3: Polars Integration & Multi-Agent Expansion
- [ ] Task: Rewrite data ingestion using Polars.
- [ ] Task: Implement `vmap` for parallel Jurisdictions and Hierarchical (Cth -> State -> LHN) logic.
- [ ] Task: Implement `jaxopt` policy optimization mode.
- [ ] Task: Conductor - User Manual Verification 'Data & Multi-Agent' (Protocol in workflow.md)

## Phase 4: Strategic Visualization & Game Tree Explorer
- [ ] Task: Implement Extensive Form SVG generator for **2-player, Multi-player, and Hybrid** games.
- [ ] Task: Integrate interactive **Game Tree Explorer** (dynamic GTE-style) in Streamlit.
- [ ] Task: Map tree nodes to Bibliography system and "Live Gradient" sidebar indicators.
- [ ] Task: Conductor - User Manual Verification 'Visualization' (Protocol in workflow.md)

## Phase 5: Calibration, Caching & Documentation
- [ ] Task: Implement NumPyro HMC calibration and persistent XLA kernel caching.
- [ ] Task: Generate **Performance Modernization Report** and update `dev.md` guidelines.
- [ ] Task: Conductor - User Manual Verification 'Calibration & Performance' (Protocol in workflow.md)
