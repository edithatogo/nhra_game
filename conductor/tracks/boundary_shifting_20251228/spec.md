# Specification: Boundary Shifting & Stream Mix Game

## 1. Overview
In the NHRA, services are funded via either Activity Based Funding (ABF) or Block Funding (for small rural hospitals, teaching, and research). This track models the strategic "Boundary Shifting" game where LHNs choose to allocate activity across these streams to bypass caps or maximize revenue.

## 2. Functional Requirements

### FR1: Stream Choice (ABF vs Block)
- LHNs now make a "Stream Allocation" move.
- ABF is subject to volume-based caps (6.5%).
- Block funding is fixed but may have higher marginal utility if ABF caps are saturated.

### FR2: Strategic Shifting Logic
- Implement `boundary_shift_jax` logic in the engine.
- Shifting activity to Block funding reduces reported NWAU (ABF) but increases "Fixed Revenue".
- Shifting is subject to a "Transformation Cost" (inertia).

### FR3: Policy Levers
- New parameter: `block_funding_share_target` (The intended split).
- New strategy: `VENUE_SHIFT` (Index 10) in the multi-agent decision vector.

## 3. Technical Constraints
- Must maintain JAX vectorization (vmap over LHNs).
- Ensure parity with legacy engine logic for dashboard usage.

## 4. Acceptance Criteria
- LHNs under pressure (hitting ABF caps) should automatically shift activity to Block-funded categories if profitable.
- Dashboard shows the "Stream Mix" distribution across LHNs.
