# Developer Guide: Codebase Mapping

This guide maps the conceptual **System Map** to the actual **Directory Structure** of the `nhra_gt` package.

## 1. System Map to Module Mapping

| Conceptual Component | Functional Role | Code Module / Directory |
| :--- | :--- | :--- |
| **Upstream Levers** | Commonwealth policy, NEP pricing, Caps | `src/nhra_gt/rules.py`, `src/nhra_gt/domain/ihacpa_api.py` |
| **Interface Friction** | Cost-shifting, Lags, VFI | `src/nhra_gt/subgames/games.py`, `src/nhra_gt/domain/state.py` (Lags) |
| **Downstream Risk** | ED Throughput, Ramping, Access Block | `src/nhra_gt/subgames/queuing.py`, `src/nhra_gt/engine.py` |
| **Players / Agents** | Strategic decision making | `src/nhra_gt/agents/`, `src/nhra_gt/agent_logic.py` |
| **Game Solvers** | Nash / QRE Equilibrium calculation | `src/nhra_gt/solvers_jax.py`, `src/nhra_gt/hierarchical_jax.py` |
| **Economic Spine** | Historical NEP/WPI series | `src/nhra_gt/domain/state.py` (EconomicSpineJax) |

---

## 2. Directory Structure Overview

### `src/nhra_gt/` (Core Logic)

- **`engine.py`**: The consolidated JAX/XLA simulation core. Orchestrates state transitions.
- **`rules.py`**: Implementation of NHRA funding rules (6.5% Growth Cap, ABF vs Block eligibility).
- **`solvers_jax.py`**: JAX-native game theory solvers (QRE, Pure Nash, Regret Minimization).
- **`hierarchical_jax.py`**: The "Constitutional" layer modeling Cth -> State -> LHN delegation.

### `src/nhra_gt/domain/` (Data & State)

- **`state.py`**: JAX Pytree definitions for `StateJax` and `ParamsJax`.
- **`ihacpa_api.py`**: Logic for parsing local NWAU calculators (.xlsb) to extract NEP series.
- **`schemas.py`**: Pandera schemas for validating economic and operational data.

### `src/nhra_gt/subgames/` (Mechanism Models)

- **`games.py`**: Payoff matrix definitions for core games (Bargaining, Definition, Cost Shifting).
- **`queuing.py`**: M/M/s queuing model for Emergency Department wait times and demand.

### `src/nhra_gt/agents/` (Strategic Actors)

- **`jax.py`**: Heuristic agents that produce strategy vectors for the JAX engine.
- **`base.py`**: Base classes for agent interfaces.

### `src/nhra_gt/visualization/` (Reporting & UX)

- **`interactive.py`**: Plotly-based interactive charts for the dashboard.
- **`game_trees.py`**: Extensive-form game tree rendering using NetworkX/Matplotlib.
- **`sensitivity.py`**: Visualization tools for Sobol and Morris indices.

---

## 3. Development Workflow

The project follows a **Spec-Driven Development** approach using the **Conductor** framework.

1. **Specification**: Define the feature/fix in a Track `spec.md`.
2. **Planning**: Detail implementation steps in a Track `plan.md`.
3. **TDD**: Write failing tests in `tests/` before implementing logic.
4. **Implementation**: Functional, pure-JAX implementation in `src/nhra_gt/`.
5. **Verification**: Automated tests (`pytest`) and manual verification via the Streamlit dashboard (`streamlit_app.py`).
