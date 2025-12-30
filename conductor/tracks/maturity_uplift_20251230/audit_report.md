# Engine Consolidation Audit Report

## 1. Engine Taxonomy
- **Legacy (`legacy_engine.py`)**: Original stylised v8 model. Yearly steps. Key feature: Explicit Nash equilibrium solving for discrete strategic choices.
- **Intermediate (`engine.py`)**: Bridge model. Monthly steps. Hierarchical state (Jurisdictions/LHNs). Uses `HeuristicAgent`.
- **Target (`engine_jax.py`)**: High-performance JAX implementation. Monthly steps. Hierarchical state. Optimized for sensitivity analysis and policy search.

## 2. Parity Gaps (Legacy -> JAX)

| Feature | Legacy/Intermediate Status | JAX Status | Migration Action |
| :--- | :--- | :--- | :--- |
| **Interventions** | `apply_intervention()` mapping in `engine.py`. | Missing direct mapping. | Port `apply_intervention` to `engine_jax.py` or a shared utility. |
| **Strategic Logic** | Explicit discrete Nash solvers (`all_nash`). | Continuous strategy vector (width 13). | Implement a "Decision Layer" in JAX that maps discrete game outcomes to the strategy vector. |
| **Renegotiation** | Detailed Hold-Up game in `renegotiation_step`. | Simplified logic. | Enhance `step_jax` with the Hold-Up game mechanics using JAX solvers. |
| **Hierarchy** | Jurisdictions & LHNs implemented. | Parity achieved. | Standardize on JAX State structure. |
| **Lags** | Basic roll buffers. | Sophisticated `update_lag_buffers`. | JAX version is superior; adopt as standard. |

## 3. Implementation Strategy
1. **Unify Interventions**: Centralize scenario definitions in a YAML or shared config that both engines can use (or just move to JAX).
2. **Standardize Agent Interface**: Ensure `HeuristicAgent` can output the 13-element vector required by JAX.
3. **Deprecation Path**:
    - Step 1: Update dashboard to use `engine_jax.py` for all core trajectories.
    - Step 2: Keep `legacy_engine.py` as a 'Verification Oracle' but move to `archive/`.
    - Step 3: Delete `engine.py` once JAX parity is verified.
