# Specification: Multi-Agent Logic Refactor (Constitutional Spec)

## 1. Overview

This track refactors the monolithic JAX simulation into a hierarchical Multi-Agent System (MAS). It formally models the NHRA as a nested game:

1. **Macro-Fiscal Game:** Commonwealth vs. States (Funding shares, caps).
2. **Internal Contracting Game:** State vs. LHNs (KPIs, budget allocation, performance management).
3. **Operational Game:** LHNs vs. Reality (Ramping, coding, throughput).

## 2. Functional Requirements

### FR1: Agent-Centric Architecture

- **LHNAgent:** Focuses on "Political Shielding" (minimizing ramping/pressure) and "Budget Hunting" (NWAU capture).
- **StateAgent:** Manages Vertical Fiscal Imbalance (VFI) and delegates operational risk to LHNs via KPIs.
- **CommonwealthAgent:** Enforces the 6.5% cap and defines the "Efficient Growth" parameters.

### FR2: Hierarchical 1:N Vectorization

- The engine must support a 1:State:N_LHN mapping.
- Each `State` manages a vector of `LHN` states.
- JAX `vmap` will be used to parallelize both Jurisdictions and the LHNs within them.

### FR3: Ramping-Centric Utility Functions

- LHN utility is dominated by a non-linear penalty for **Ramping** (ED LOS breaches).
- States derive utility from minimizing their fiscal gap while meeting Commonwealth KPIs.

## 3. Technical Constraints

- **JAX Pytree Compatibility:** All agent logic must remain pure functional and compatible with `jax.jit`.
- **Backward Compatibility:** The refactored engine must be able to replicate the current "unified" logic as a special case where $N=1$.

## 4. Acceptance Criteria

- Successful execution of a 1:8:10 simulation (1 Cth, 8 States, 10 LHNs each).
- Visualization of "Intra-State Variance": Showing how different LHNs within the same State react to the same policy change.
- Demonstration of the "Ramping Signal" as a result of LHN strategic trade-offs.
