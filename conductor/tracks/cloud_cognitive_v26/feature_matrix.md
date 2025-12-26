# Feature Options Matrix: NHRA Strategic Model (v26)

**Purpose:** Evaluation of new features from the "Modelling Checklist" against the current codebase (`v9/engine.py`) to determine inclusion in the **Cloud & Cognitive Agents** track.

## Legend
- **Status:** `Existing`, `Partial`, `Missing`
- **Impact:** `High` (Core to strategic narrative), `Medium` (Adds nuance), `Low` (Nice to have)
- **Complexity:** `High` (Requires major refactor), `Medium` (New mechanics), `Low` (Parameter tweak)
- **Recommendation:** `Adopt`, `Defer`, `Ignore`

---

## 1. Inputs (State & Parameters)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auditor / NHFB Players** | `Partial` (audit_pressure param) | Medium | Medium | `Adopt` | Model as a stochastic agent (random inspections) rather than static pressure. |
| **Side Payments** | `Missing` | High | Low | `Adopt` | Critical for "Political Settlement" outcomes in bargaining. |
| **Coding Intensity** | `Missing` | High | Medium | `Adopt` | Major strategic lever for providers. Links to Audit game. |
| **Block vs ABF Split** | `Missing` (All ABF implicit) | Medium | Medium | `Defer` | Adds accounting complexity. Focus on NWAU first. |
| **Fixed/Variable Costs** | `Missing` (Single cost index) | Medium | Medium | `Defer` | Useful for short-run vs long-run efficiency, but maybe too detailed for now. |
| **Electoral Cycle** | `Partial` (political_salience) | High | Low | `Adopt` | Simple sine wave or time-decay function to vary `political_salience`. |
| **Reconciliation Lag** | `Missing` | Medium | Low | `Adopt` | Important for "Soft Budget" dynamics (pay now, pain later). |

## 2. Mechanisms (Games)

| Mechanism | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Coding / Upcoding Game** | `Missing` | High | Medium | `Adopt` | "Performative Compliance" layer. Trade risk of audit vs revenue. |
| **Cap Redistribution** | `Missing` | Medium | High | `Defer` | Requires multi-state model (State A vs State B). Current model is Cth vs "The States" (aggregated). |
| **Stackelberg Pricing** | `Partial` (Drift parameters) | Medium | Medium | `Adopt` | Explicit "Price Setting" move by Cth/IHACPA at start of turn. |
| **Service Shifting** | `Missing` (Block vs ABF) | Low | Medium | `Defer` | Requires Block funding implementation first. |
| **Bailout / Soft Budget** | `Planned` (Task 1.4) | High | Medium | `Adopt` | Already in plan, confirmed by checklist. |

## 3. Outputs (Observables)

| Output | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Coding Index** | `Missing` | High | Low | `Adopt` | Track "Artificial NWAU" vs "Real NWAU". |
| **Reconciliation Adjustments** | `Missing` | Medium | Low | `Adopt` | Track ex-post clawbacks. |
| **Quality/Safety Proxies** | `Partial` (Harm Index) | Medium | Low | `Adopt` | Refine Harm Index to include "Readmission Risk" (proxy for premature discharge). |

---

## Implementation Plan (Additions to Track v26)

### A. The "Coding & Audit" Module (High Priority)
*   **New State:** `coding_intensity` (float 1.0 = honest, >1.0 = upcoding).
*   **New Game:** `CODING` (Provider chooses intensity, Auditor chooses scrutiny).
*   **Feedback:** High coding = High revenue but High audit risk (penalty).

### B. The "Political Cycle" Module (Quick Win)
*   **New Param:** `election_year` (cycle).
*   **Logic:** `political_salience` peaks in election years, softening Cth bargaining stance.

### C. The "Financial Reality" Module (Strategic Depth)
*   **New Mechanism:** `side_payments` (lump sum transfers to seal a deal).
*   **New Mechanism:** `reconciliation_balance` (lagged debt/credit).

### D. Multi-State Architecture (Long Term / Defer)
*   The checklist implies competition *between* states for the redistribution pool.
*   **Decision:** Stick to "Representative State" for now to keep JAX/Agent complexity manageable.

---

## Batch 2: Advanced Realism (Inputs & Mechanisms)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Public Health Funding** | `Missing` | Medium | Medium | `Defer` | "Tri-stream" choice adds venue shifting complexity. Focus on ABF vs Block first. |
| **Schedule K Top-ups** | `Missing` | Medium | Low | `Adopt` | Specific case of "Side Payments" (already adopted). Implement as exogenous shock in 2025. |
| **Equity / Closing the Gap** | `Missing` | High | Low | `Adopt` | Add `equity_index` to State. Utility penalty if equity drops. Models "Political Pain" of inequality. |
| **Mid-term Review Pressure** | `Missing` | Medium | Low | `Adopt` | Time-dependent probability of "Rules Change". Makes agents cautious in years 3-4. |
| **Policy Uncertainty** | `Missing` | High | Low | `Adopt` | Run scenarios where `cap_growth` has high variance/uncertainty in future years. |
| **Cashflow Stress** | `Missing` | Low | High | `Ignore` | Requires monthly resolution. Simulation is currently annual. Too granular for strategic high-level. |
| **Data Matching Rules** | `Missing` | Low | Medium | `Defer` | "Technical" gaming. Abstract into general `coding_intensity` parameter for now. |

## Implementation Plan (Batch 2 Additions)

### E. The "Equity & Scrutiny" Module
*   **New State:** `equity_index` (float).
*   **Logic:** Policy interventions (like "Strict Efficiency") degrade equity.
*   **Feedback:** If `equity_index` falls below threshold, `political_capital` takes a massive hit (Scandal).

### F. The "Review Horizon" Module
*   **New Mechanism:** `review_imminent` (boolean flag).
*   **Behavior:** When `True` (e.g., Year 2028), agents shift strategy from "Maximise Profit" to "Minimize Detectable Gaming" (Signal=High, Coding=Low).

---

## Batch 3: Decision-Grade Upgrades

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Non-linear Political Loss** | `Missing` | High | Low | `Adopt` | Threshold penalties for `ED > 4hr` breaches. Critical for "Crisis" dynamics. |
| **Queuing / Congestion** | `Partial` (Pressure) | High | High | `Adopt` | Upgrade `pressure_index` to a simple M/M/s approximation to get true "Wait Times". |
| **Capacity Adjustment Costs** | `Missing` | Medium | Medium | `Adopt` | "Hiring Lag" - prevent instant `bed_capacity` changes. Adds inertia. |
| **Multi-Level Principals** | `Missing` (State only) | Medium | High | `Defer` | Modeling LHNs/Hospitals individually is too computationally expensive for the current phase. |
| **Audit as Strategic Player** | `Planned` (Task 1.5) | High | Medium | `Adopt` | Confirmed. Auditor adapts probability based on anomalies. |
| **Explainability Hooks** | `Missing` | High | Medium | `Adopt` | "Why did I do this?" logs for LLM Agents. Essential for the "Cognitive" track goal. |
| **Modular Rules Engine** | `Partial` (Engine) | Medium | High | `Defer` | Current `engine.py` is monolithic. Refactor later if needed. |

## Implementation Plan (Batch 3 Additions)

### G. The "Crisis & Queues" Module
*   **Upgrade:** Replace `pressure_index` logistic curve with `mm_s_queue` function (Elang C formula approximation).
*   **New Logic:** Political cost spikes discontinuously when `wait_time > 4h`.

### H. The "Inertia" Module
*   **New State:** `target_capacity` vs `current_capacity`.
*   **Logic:** Capacity moves towards target with a `lag_parameter` (hiring friction).

### I. The "Cognitive Trace" Module
*   **New Output:** `agent_reasoning_log` (JSON).
*   **Mechanism:** Agents output a "Rationale" string alongside their move (e.g., "Increasing coding because audit risk is low").

---

## Batch 4: The "All-In" Spec (Validation & Reproducibility)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Multi-Target Calibration** | `Partial` (NEP/Occ) | High | High | `Adopt` | Calibrate to Spend, NWAU Growth, Mix, AND Access KPIs simultaneously. |
| **Structural Sensitivity** | `Missing` | High | High | `Adopt` | Toggle *mechanisms* (e.g., cap rule type), not just parameters. |
| **Scenario Library** | `Partial` (Scenarios) | Medium | Low | `Adopt` | Standardize "Cap Removed", "Audit Surge", etc. into `yaml` config files. |
| **Sanity Invariants** | `Partial` (Tests) | Medium | Low | `Adopt` | Add runtime checks for "Conservation of Activity" and "Non-negative Entitlements". |
| **Information Structure** | `Implicit` | High | Medium | `Adopt` | Explicitly model "Who knows what" (e.g., Cth doesn't know true cost). |
| **Efficient Growth Accounting** | `Implicit` | Medium | Medium | `Adopt` | Explicit "Efficient Frontier" calculation. |

## Implementation Plan (Batch 4 Additions)

### J. The "Robust Validation" Module
*   **Upgrade:** `optimize_calibration.py` to use a multi-objective loss function (Spend + NWAU + Wait Times).
*   **New Artifact:** `scenario_library/` folder with standard JSON configs for policy counterfactuals.

### K. The "Structural Switch" Module
*   **Mechanism:** Strategy Pattern for rules. `CapRule` interface with `HardCap`, `SoftCap`, `NoCap` implementations.
*   **Goal:** Allow swapping *entire logic blocks* via config, not just changing `cap_growth` float.

---

## Batch 5: The Formal Stage Game (Architecture)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Time Structure (Month/Year/Cycle)** | `Year Only` | High | High | `Adopt` | Move to Monthly steps for `queue` and `cashflow` dynamics. Aggregated annually. |
| **Lags / Measurement Layer** | `Missing` | Medium | Medium | `Adopt` | `claims_lag_t` and `signal_lag_t`. Critical for "Surprise" dynamics. |
| **Principal-Agent (State-LHN)** | `Missing` | Low | High | `Defer` | Keep "State" as the atomic agent for now to manage complexity. |
| **Mass Balance Invariant** | `Implicit` | High | Low | `Adopt` | Enforce NWAU comes from episodes. No "Free NWAU". |
| **Transition Functions** | `Monolithic` | Medium | Medium | `Adopt` | Refactor `step()` into `demand_step`, `provider_move`, `payment_engine` etc. |

## Implementation Plan (Batch 5 Additions)

### L. The "Timekeeper" Module
*   **Refactor:** `engine.py` loop to run `12` monthly steps per year.
*   **State:** Add `month` index to `State`.

### M. The "Refactored Transitions" Module
*   **Action:** Break `step()` into functional components: `demand()`, `policy()`, `ops()`, `pay()`.
*   **Benefit:** Allows easier injection of the "Queuing" and "Audit" modules.

---

## Batch 6: The Build Order (Execution Strategy)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Core v1: Threshold/Timing** | `Missing` | High | High | `Adopt` | Implemented via "Timekeeper" (Batch 5). |
| **Core v1: Coding Drift** | `Missing` | High | Medium | `Adopt` | Implemented via "Coding & Audit Game" (Batch 1). |
| **Core v1: Queues** | `Partial` | High | High | `Adopt` | Implemented via "Crisis & Queues" (Batch 3). |
| **v2: Boundary Shifting** | `Missing` | Medium | Medium | `Defer` | Postpone to "Phase 3" of plan. Focus on Core v1 first. |
| **v2: Internal Contracting** | `Missing` | Low | High | `Defer` | "Nested Principal-Agent" is too complex for current cycle. |
| **v3: Audit Arms Race** | `Planned` | High | Medium | `Adopt` | Merged into "Coding & Audit Game" (Batch 1). |
| **v4: Renegotiation** | `Planned` | Medium | Medium | `Adopt` | "LLM Negotiator" (Task 1.2) covers this. |

## Implementation Plan (Phasing Update)

*   **Phase 1 (Core v1):** Timekeeper, Queues, Coding Game.
*   **Phase 2 (Cognitive):** LLM Negotiator, Explainability.
*   **Phase 3 (Extensions):** Boundary Shifting, Cost Shifting.

---

## Batch 8: Agent Recommendations (System Dynamics)

| Feature | Current State | Impact | Complexity | Rec. | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Signal Quality** | `Implicit` | Medium | Low | `Adopt` | Providers choose `signal_quality` (0.0-1.0). High noise = low trust. |
| **Crisis State Machine** | `Missing` | High | Medium | `Adopt` | `system_mode` enum (NORMAL/CRISIS). Hysteresis loops. |
| **Expert Witness Loop** | `Missing` | High | Medium | `Adopt` | Use "Auditor Persona" LLM to qualitative validate agent traces. |

## Implementation Plan (Batch 8 Additions)

### N. The "Fog of War" Module
*   **New Action:** `signal_quality` (State/LHN choice).
*   **Mechanic:** Affects `belief_update()` accuracy for the other player.

### O. The "Code Red" Module
*   **New State:** `system_mode` (Enum).
*   **Logic:** Hysteretic switching. `CRISIS` mode relaxes budget constraints but burns political capital.

### P. The "Qualitative Validator" Module
*   **Integration:** In the `validation` pipeline, add a step that sends `agent_reasoning_log` to an LLM "Auditor" for a "Realism Score".

---

## Batch 7: Priority Behaviours (Signature Pathology)

| Behaviour | Implementation Status | Plan Task | Signature Output |
| :--- | :--- | :--- | :--- |
| **1) Threshold/Timing** | `Planned` | 1.2 (Timekeeper) | NWAU Monthly Spikes |
| **2) Coding Drift** | `Planned` | 1.3 (Coding Game) | Coding Intensity Index |
| **3) Boundary Shift** | `Planned` | 3.2 (VFI/Venu) | Share by Stream |
| **4) Access/Queues** | `Planned` | 1.2 (Crisis/Queue) | Wait-time breaches |
| **5) Internal Deleg.** | `Deferred` | - | LHN-level variance |
| **6) Cost Shifting** | `Planned` | 1.3 (Interface) | Displacement indicators |
| **7) Audit Arms Race**| `Planned` | 1.3 (Audit Game) | Deterrence curves |
| **8) Renegotiation** | `Planned` | 2.1 (LLM Negot.) | Settlement transfers |

## Analysis of Behaviour Map
The combined map highlights that **Access under Capacity (#4)** is the central mediator between **Rules** and **Politics/Renegotiation**. 

### Refinement for Plan:
*   Ensure **Task 1.2 (Crisis & Queues)** outputs the "Threshold Breaches" needed for the **Political Loss Function**.
*   Ensure **Task 1.3 (Interface Games)** specifically tracks "Ambulance/ED" spillovers as a signature of Behavior #6.
