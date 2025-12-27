# Specification: Visual & Reporting Modernization

## 1. Overview
This track implements the high-impact communication and transparency gaps identified in the Dec 26th audits. It focuses on translating complex game-theoretic outputs into intuitive policy "stories".

## 2. Functional Requirements

### FR1: VFI Funding Waterfall (Policy Story)
- **Concept:** Visualize the "leakage" from nominal commitment to effective funding.
- **Components:** 
  1. Nominal Share (Target)
  2. (-) Indexation Gap (Input Cost > NEP)
  3. (-) Cap Limit (6.5% constraint)
  4. (-) Audit Clawback (Integrity detections)
  5. (=) Effective Share (Actual realized)
- **Implementation:** Interactive Plotly Waterfall chart in the dashboard.

### FR2: System Phase-Space Trajectories (Dynamics)
- **Concept:** 2D plot of `Pressure` vs. `Occupancy` to visualize hysteresis and tipping points.
- **Features:** 
  - Color-coded by `SystemMode` (Normal, Stress, Crisis, Recovery).
  - Trace of system state over time.

### FR3: Data Provenance "Traffic Light" (Transparency)
- **Concept:** Visual indicator of parameter grounding status.
- **States:** 
  - 🟢 **Live:** AIHW/IHACPA API connected.
  - 🟡 **Validated:** Matched to peer-reviewed or official historical data.
  - 🔴 **Assumption:** Hardcoded model parameter.

### FR4: Numerical Stability Monitor (Game Integrity)
- **Concept:** Plot of "Iterations to Converge" for Nash solvers.
- **Why:** Signals "Strategic Volatility" to the user.

## 3. Acceptance Criteria
- Dashboard includes a "Policy Leakage" waterfall for any selected scenario.
- Phase-space plots clearly show the "Crisis Loop" (hysteresis).
- Every model parameter in the UI is accompanied by a provenance color indicator.
