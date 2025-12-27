# Specification: Advanced Game Theoretic Enhancements

## 1. Overview
This track introduces three high-scientific-value mechanistic enhancements:
1. **Queuing Game (Endogenous Demand):** Models patient choice (ED vs. GP) based on endogenous wait times and primary care costs.
2. **Renegotiation / Hold-Up Game:** Models the 5-year NHRA Agreement cycle and strategic leverage at the expiry deadline.
3. **Workforce Competition:** Models how LHNs compete for a shared, finite pool of clinical staff (cannibalization).

## 2. Functional Requirements

### FR1: Wardrop Equilibrium (Queuing Game)
- Define a `PatientUtility` function: $U = Benefit - (Wait \cdot Cost\_Time) - Out\_of\_Pocket$.
- Replace exogenous `demand_step` with a solver that finds the equilibrium demand level where ED and GP utilities are equalized.
- Mechanistically link GP co-pays and bulk-billing rates to ED pressure.

### FR2: The "Agreement Clock" (Renegotiation)
- Implement a countdown to the 5-year Agreement expiry.
- At the deadline, execute a high-stakes Extensive Form game where States can "Hold Up" the Commonwealth by threatening failure to extract better funding shares.

### FR3: Shared Resource Coupling (Workforce)
- Couple vectorized LHNs through a shared `WorkforcePool`.
- Actions by one LHN (e.g., overtime surge) must impact the available capacity or cost for others.

## 3. Acceptance Criteria
- Demonstration of "Access Block Spillover": Rising GP costs lead to a mechanistic spike in ED demand without manual parameter adjustment.
- Successful simulation of a 5-year "Cliff" where strategic behavior shifts sharply as the deadline approaches.
- Visualization of "Workforce Cannibalization" in the LHN variance tab.
