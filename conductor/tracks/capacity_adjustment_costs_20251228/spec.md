# Specification: Capacity Adjustment Costs & Friction

## 1. Overview

In the current model, capacity adjusts linearly toward a target. This track introduces **Adjustment Costs** (the fiscal and operational friction of scaling up/down) and **Hiring Lag** (asymmetric inertia where expansion is harder than contraction).

## 2. Functional Requirements

### FR1: Asymmetric Capacity Lag

- Expansion (Target > Current) should be slower than Contraction (Target < Current) to model recruitment bottlenecks.
- New parameters: `expansion_lag` vs `contraction_lag`.

### FR2: Fiscal Adjustment Costs

- Implement a convex adjustment cost function: $Cost = \alpha \cdot (\Delta Capacity)^2$.
- This cost represents recruitment bonuses, redundancy payments, or training overheads.
- This cost directly reduces the `reconciliation_balance`.

### FR3: Strategic Inertia

- Update LHN utility to include `capacity_friction_weight`.
- Agents should become more cautious about oscillating capacity targets.

## 3. Technical Constraints

- Maintain differentiability for JAX solvers.
- Ensure the cost function is grounded in the `ParamsJax` structure.

## 4. Acceptance Criteria

- Simulation demonstrates "Sticky Capacity": LHNs defer expansion until pressure is sustained.
- Dashboard shows "Adjustment Overhead" as a component of funding leakage or fiscal cost.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
