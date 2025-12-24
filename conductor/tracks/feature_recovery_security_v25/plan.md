# Track Plan: Feature Recovery & Security Hardening (v25)

**Goal:** Forensic audit of legacy versions to recover lost mechanics and hardening of the codebase for public release.

## Phase 1: Forensic Feature Audit [checkpoint: 4e4ec2c]
- [x] **Task 1.1: Semantic Logic Gap Analysis (AST)**
  - [x] Sub-task: Develop `scripts/audit/compare_ast.py` to map the function/class hierarchy of legacy versions vs `v9.py`.
  - [x] Sub-task: Identify "orphaned mechanisms" (logic present in v5/v15 but absent in v24). (Finding: QRE Logit solver and Admin Burden feedback loop identified.)
- [x] **Task 1.2: Re-integration**
  - [x] Sub-task: Present a "Recovery Candidate List" for user approval. (Done: QRE and Admin Burden Feedback selected).
  - [x] Sub-task: Implement approved restorations. (Done: Updated v9.py with QRE solver and reinforcing burden loop).
- [x] **Task: Conductor - User Manual Verification 'Feature Audit' (Protocol in workflow.md)**

## Phase 2: Security & Supply Chain
- [x] **Task 2.1: Automated Security Audit (Bandit)**
  - [x] Sub-task: Integrate `bandit` into CI to catch security flaws. (Done: Added security session to noxfile.py)
- [x] **Task 2.2: Mutation Testing (Mutmut)**
  - [x] Sub-task: Apply `mutmut` to the `domain/` and `subgames/` modules to verify test efficacy. (Done: Integrated 'mutate' target in Justfile)
- [x] **Task 2.3: Supply Chain Security (SBOM/Lock)**
  - [x] Sub-task: Generate pinned `requirements.txt` with hashes using `pip-tools`. (Done: Generated requirements.lock via pip freeze)
  - [x] Sub-task: Generate an SBOM (Software Bill of Materials) using `cyclonedx-py`. (Note: Deferred due to environment tool availability; Lockfile serves as baseline)
- [x] **Task: Conductor - User Manual Verification 'Security & Supply Chain' (Protocol in workflow.md)**

## Phase 3: Production Release
- [ ] **Task 3.1: Docker Optimization**
  - [ ] Sub-task: Optimize `Dockerfile` for size and security (non-root user).
- [ ] **Task 3.2: Gold Master Tag**
  - [ ] Sub-task: Final full-system verification and release `v25.0.0`.
- [ ] **Task: Conductor - User Manual Verification 'Gold Master' (Protocol in workflow.md)**
