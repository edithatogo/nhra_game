# Audit Recommendations: New Game Theoretic Models

**Date:** 2025-12-26
**Status:** Proposals for Future Tracks

## 1. Principal-Agent Funding Games (Constitutional/Financial Layer)

* **Concept:** Model the "Commonwealth vs. State" interaction explicitly as a Principal-Agent problem rather than a 2x2 matrix.
* **Mechanics:**
  * **Principal (Commonwealth):** Sets `NEP` (price), `Cap` (budget limit), and `Audit_Intensity`. Goal: Minimize Cost + Maximize Public Health Outcomes.
  * **Agent (State/LHN):** Observes policy, chooses `Effort` (Efficiency) and `Gaming` (Coding Intensity, Cost Shifting). Goal: Maximize Revenue + Minimize Political Heat.
  * **Asymmetry:** Principal cannot perfectly observe `Effort` vs `Gaming` (Hidden Action).
* **Why:** Replaces the heuristic `policy_step` drift with an optimal contract logic. Fits the missing "Agreement Cycle" layer.

## 2. Queuing Games (Operational Layer)

* **Concept:** Endogenous patient choice driving demand, rather than exogenous `demand_step`.
* **Mechanics:**
  * **Players:** Patients (N=Large).
  * **Choice:** ED (Free, Long Wait) vs GP/Urgent Care (Cost, Short Wait).
  * **Payoff:** `U = Health_Benefit - Wait_Cost * Time - Monetary_Cost`.
  * **Equilibrium:** Wardrop Equilibrium where marginal patient is indifferent.
* **Why:** Explains "GP Access Block" impact on ED ramping mechanistically.

## 3. Multi-Hospital Competition (Network Layer)

* **Concept:** LHNs compete for elective volume or staff.
* **Mechanics:**
  * **Players:** LHN A vs LHN B.
  * **Actions:** `Invest` in capacity, `Marketing` (Signal Quality).
  * **Coupling:** Shared pool of patients (elective referrals) or workforce (locums).
* **Why:** Captures "Cannibalization" effects where one hospital's efficiency drains resources/staff from another.

## 4. Renegotiation / Hold-Up Games (Cycle Layer)

* **Concept:** Explicitly model the 5-year Agreement expiration.
* **Mechanics:**
  * **State:** "Hold-Up" (Threaten to walk away/fail) to extract better `alpha` (contribution share).
  * **Commonwealth:** "Take-it-or-leave-it" offers vs Political Cost of failure.
* **Why:** Provides the "Crisis" trigger logic that is currently just a random shock or pressure threshold.
