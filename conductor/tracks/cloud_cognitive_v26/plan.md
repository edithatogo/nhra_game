# Track Plan: Cloud & Cognitive Agents (v26)

**Goal:** Evolve the NHRA model into a "Cognitive Digital Twin" using LLM-driven agents and operationalize it for cloud deployment.

## Phase 1: Cognitive Simulation (LLM Agents)
- [~] **Task 1.1: Agent Interface Design**
  - [ ] Sub-task: Define `Agent` abstract base class in `src/nhra_game_theory/agents/base.py`.
  - [ ] Sub-task: Implement `HeuristicAgent` (wrapping current logic) to ensure backward compatibility.
- [ ] **Task 1.2: LLM Negotiator Implementation**
  - [ ] Sub-task: Create `LLMAgent` that uses a language model (e.g., Gemini/GPT) to make strategic decisions (Invest/Shift, Agree/Defer) based on a textual "Policy Brief".
  - [ ] Sub-task: Implement a "Debate Loop" where Cth and State agents exchange structured messages before finalizing a move.
- [ ] **Task: Conductor - User Manual Verification 'Cognitive Agents' (Protocol in workflow.md)**

## Phase 2: Narrative Generation & RAG
- [ ] **Task 2.1: Policy Brief Generator**
  - [ ] Sub-task: Implement a system to generate human-readable policy briefs describing the *reasoning* behind an equilibrium outcome.
- [ ] **Task 2.2: RAG Integration**
  - [ ] Sub-task: Connect agents to the `context/` folder so they can cite specific clauses of the NHRA when "arguing".
- [ ] **Task: Conductor - User Manual Verification 'Narrative Engine' (Protocol in workflow.md)**

## Phase 3: Cloud Operationalisation
- [ ] **Task 3.1: Docker Hardening for Cloud**
  - [ ] Sub-task: Ensure Docker container is stateless and config-driven (env vars) for AWS/Azure deployment.
- [ ] **Task 3.2: Continuous Data Pipeline (GitHub Actions)**
  - [ ] Sub-task: Create `.github/workflows/data_refresh.yml` to run `ingest_aihw_api.py` on a schedule.
- [ ] **Task: Conductor - User Manual Verification 'Cloud Ops' (Protocol in workflow.md)**
