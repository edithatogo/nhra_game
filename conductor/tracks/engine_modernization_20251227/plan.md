# Implementation Plan: NHRA Engine Modernization (JAX & Polars)

## Phase 1: JAX Foundation & Logic Parity [checkpoint: b6b480a]
- [x] Task: Define `Pytree` state structures and pure functional `step()` logic.
- [x] Task: Implement multi-year rollout logic using `jax.lax.scan`.
- [x] Task: Implement **Mirror Test Harness** to verify parity with v26 logic.
- [x] Task: Conductor - User Manual Verification 'JAX Foundation' (Protocol in workflow.md) b6b480a

## Phase 2: Differentiable Solvers & Equilibrium Oracle [checkpoint: 5a952c7]
- [x] Task: Implement QRE, Regret-Min, and Discrete (JVP) solvers in JAX.
- [x] Task: Implement **PyGambit Oracle** test suite to validate solvers.
- [x] Task: Conductor - User Manual Verification 'Differentiable Solvers' (Protocol in workflow.md) 5a952c7

## Phase 3: Polars Integration & Multi-Agent Expansion [checkpoint: 45c4bb3]
- [x] Task: Rewrite data ingestion scripts (`scripts/run_baseline.py`, etc.) to use Polars.
- [x] Task: Expand JAX core to support vectorized multi-jurisdiction (N-State) simulation.
- [x] Task: Implement Hierarchical (Cth -> State -> LHN) game logic hooks.
- [x] Task: Implement `jaxopt` policy optimization mode.
- [x] Task: Conductor - User Manual Verification 'Data & Multi-Agent' (Protocol in workflow.md) 45c4bb3

## Phase 4: Strategic Visualization & Game Tree Explorer
- [~] Task: Implement Extensive Form SVG generator for **2-player, Multi-player, and Hybrid** games.
- [ ] Task: Integrate interactive **Game Tree Explorer** (dynamic GTE-style) in Streamlit.
- [ ] Task: Map tree nodes to Bibliography system and "Live Gradient" sidebar indicators.
- [ ] Task: Conductor - User Manual Verification 'Visualization' (Protocol in workflow.md)

## Phase 5: Calibration, Caching & Documentation
- [ ] Task: Implement NumPyro HMC calibration and persistent XLA kernel caching.
- [ ] Task: Generate **Performance Modernization Report** and update `dev.md` guidelines.
- [ ] Task: Conductor - User Manual Verification 'Calibration & Performance' (Protocol in workflow.md)
