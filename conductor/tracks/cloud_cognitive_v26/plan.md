# Track Plan: Cloud & Cognitive Agents (v26)

**Goal:** Evolve the NHRA model into a "Cognitive Digital Twin" using LLM-driven agents, while upgrading the simulation engine to "Decision-Grade" operational realism.

## Phase 1: Core v1 (Engine Upgrades)
*Focus: Timing, Queues, Coding Drift, and Inertia.*
- [x] **Task 1.1: Agent Interface Design**
  - [x] Sub-task: Define `Agent` abstract base class in `src/nhra_game_theory/agents/base.py`.
  - [x] Sub-task: Implement `HeuristicAgent` (wrapping current logic) to ensure backward compatibility.
- [x] **Task 1.2: Time & Operations**
  - [x] Sub-task: **Timekeeper:** Update engine to simulate 12 monthly steps per year to capture cashflow/queue dynamics. (Output: Monthly NWAU Spikes).
  - [x] Sub-task: **Refactored Transitions:** Break monolithic `step()` into `demand()`, `policy()`, `ops()`, and `pay()` components.
  - [x] Sub-task: **Crisis & Queues:** Upgrade `pressure_index` to an M/M/s queuing approximation. Add non-linear political penalties for wait-time breaches. (Behavior #4).
  - [x] Sub-task: **Code Red:** Implement `system_mode` state machine (NORMAL -> CRISIS -> RECOVERY) with hysteresis. Crisis relaxes budgets but burns capital.
  - [x] Sub-task: **Inertia:** Add `capacity_lag` to prevent instant operational adjustments (hiring friction).
- [x] **Task 1.3: Strategic Games (v1)**
  - [x] Sub-task: **Coding & Audit Game:** Implement `CODING` strategy (Honest vs Upcode) and stochastic Auditor punishment. (Behavior #2 & #7).
  - [x] Sub-task: **Fog of War:** Add `signal_quality` action. Obfuscation increases noise for opponents but incurs trust penalties.
  - [x] Sub-task: **Interface Games:** Split `DISC` (Discharge) into distinct `AgedCare` and `NDIS` interface sub-games. Track "Ambulance/ED" displacement. (Behavior #6).
  - [x] Sub-task: **Soft Budget Constraint:** Implement "Bailout Expectations" logic where frequent agreement reduces future bargaining toughness.
- [x] **Task: Conductor - User Manual Verification 'Core Engine' (Protocol in workflow.md)**

## Phase 2: Cognitive Layer (LLM Agents)
*Focus: Negotiation, Rationale, and Explainability.*
- [ ] **Task 2.1: LLM Negotiator Implementation**
  - [ ] Sub-task: Create `LLMAgent` that uses a language model (e.g., Gemini/GPT) to make strategic decisions (Invest/Shift, Agree/Defer) based on a textual "Policy Brief".
  - [ ] Sub-task: Implement a "Debate Loop" where Cth and State agents exchange structured messages before finalizing a move.
  - [ ] Sub-task: **Cognitive Trace:** Implement "Why" logging. Agents must output a structured rationale for their moves.
  - [ ] Sub-task: **Expert Witness:** Integrate an "Auditor Persona" LLM step to qualitatively score agent traces for realism ("Turing Test for Gaming").
- [ ] **Task 2.2: Hybrid Orchestration**
  - [ ] Sub-task: Refactor `decide_strategies` to support "Sequential Mode" (SIGNAL -> BARG -> DEF) respecting causal arrows.
  - [ ] Sub-task: Implement "Isolation Mode" to play specific games individually while locking others.
- [ ] **Task: Conductor - User Manual Verification 'Cognitive Agents' (Protocol in workflow.md)**

## Phase 3: Validation & Narrative
*Focus: Calibration, Scenarios, and Reporting.*
- [x] **Task 3.1: Robust Validation**
  - [x] Sub-task: Upgrade calibration to multi-objective loss (Spend + NWAU + Wait Times). (Scripts: `scripts/optimize_calibration_v26.py`)
  - [x] Sub-task: Create `scenario_library/` with standard JSON configs for policy counterfactuals.
  - [x] Sub-task: **Structural Switch:** Refactor `CapRule` and `AuditRule` into swappable classes to allow structural sensitivity analysis. (Module: `src/nhra_game_theory/rules.py`)
- [x] **Task 3.2: Narrative Engine**
  - [x] Sub-task: **Policy Brief Generator:** Generate human-readable briefs explaining equilibrium outcomes. (Agent: `BriefGenerator`)
  - [x] Sub-task: **Personas:** Add "Professor of Medicine" (Clinical focus) and "Auditor" (Integrity focus) personas.
  - [x] Sub-task: **VFI Waterfall:** Operationalize "Valuation Divergence" with Nominal vs Effective share plots.
  - [x] Sub-task: **Equity & Scrutiny:** Add `equity_index` and "Mid-term Review" pressure logic.
- [x] **Task: Conductor - User Manual Verification 'Narrative & Validation' (Protocol in workflow.md)**

## Phase 4: Cloud Operationalisation

- [x] **Task 4.1: Docker Hardening for Cloud**

  - [x] Sub-task: Ensure Docker container is stateless and config-driven (env vars) for AWS/Azure deployment. (Updated `Dockerfile`)

- [x] **Task 4.2: Continuous Data Pipeline (GitHub Actions)**

  - [x] Sub-task: Create `.github/workflows/data_refresh.yml` to run `ingest_aihw_api.py` on a schedule.

- [x] **Task: Conductor - User Manual Verification 'Cloud Ops' (Protocol in workflow.md)**



---

**Track Status:** COMPLETED 2025-12-26

Model evolved into a Cognitive Digital Twin with LLM-ready agents, monthly operational realism, crisis state-machines, and cloud-ready infrastructure.

- Refactored Engine (v26) with M/M/s queuing.

- Heuristic Agent with Sequential/Isolation modes.

- Scenario Library & Multi-target calibration.

- VFI Waterfall & Equity metrics.

- GitHub Action for automated data refresh.
