# Track Specification: Publication Series - NHRA Game Theory & Empirical Modelling

## 1. Overview
This track governs the systematic development, execution, and documentation of a series of three academic publications derived from the NHRA Game Theory codebase. The project emphasizes a rigorous, auditable research protocol, blinded validation of existing models, and OSF-compliant pre-registration.

## 2. Infrastructure & Standards

### 2.1 File System Structure (Mandatory)
The following directory structure must be created and enforced:
```text
publications/
├── shared/
│   ├── references/               # library.yaml, bibtex exports
│   ├── author_guidelines/        # Scraped MJA/RACMA guidelines
│   ├── experts/                  # Panel definitions and snowball logs
│   └── templates/                # OSF templates, Journal Word templates
├── P1_Qualitative_MJA/
│   ├── 01_Protocol/              # Selection Report, Protocol, OSF Reg, Review Logs
│   ├── 02_Analysis/              # Blinded Mapping, Reconciliation Report
│   ├── 03_Manuscript/            # Drafts, Outlines, Figures, Schema
│   └── 04_Submission/            # Cover Letter, Title Page, Final PDFs
├── P2_Modelling_MJA/
│   ├── 01_Protocol/              # ODD Protocol, Experiment Design, Review Logs
│   ├── 02_Analysis/              # Code Parity Audit, Simulation Logs, Model Spec
│   ├── 03_Manuscript/            # Drafts, Outlines, Figures, Schema
│   └── 04_Submission/            # Zenodo snapshot, Tech Appendix, Final PDFs
└── P3_RACMA_Position/
    ├── 01_Drafting/              # Drafts, Policy Brief, Schema
    └── 02_Final/                 # Final Statement, Cover Note
```

### 2.2 Reference Management System
*   **Source of Truth:** `publications/shared/references/library.yaml`
*   **Tooling:** Develop `scripts/pub_tools/manage_refs.py` to:
    *   Validate DOIs via CrossRef API.
    *   Deduplicate entries.
    *   Enforce metadata completeness (Author, Year, Journal, URL, DOI).
    *   Check recency (Flag > 10 years old unless seminal).
    *   Check quality heuristic (Impact Factor/High-impact journal list).
    *   Export to `.ris` and `.bib`.
*   **Citation Style:** Inline citations MUST follow `{Author, YYYY @Label #RecordNumber}`. A numbered bibliography MUST be generated for the final output.

### 2.3 Simulated Expert Review Protocol
*   **Panel:** Defined personas (Methodologist, Policy Expert, Game Theorist, etc.) using iterative snowball sampling.
*   **Cycles:** Two review cycles per document (Protocol, Report, Manuscript, Supplement, Tables, Figures).
*   **Process:** 
    1. Initial Feedback (noting coding constraints).
    2. Expert Expansion (Snowball).
    3. Deliberation & Prioritization (Consensus building).
    4. Refinement (v2).
*   **Documentation:** Detailed `review_log.md` tracking suggestions, deliberations, and implemented changes.

## 3. Publication 1: Qualitative Mapping Study (MJA)
### 3.1 Deliverables & Requirements
*   **Methodology:** Independent, blinded mapping of NHRA text to game nodes (Clean Room protocol).
*   **Reporting Checklist:** SRQR / COREQ.
*   **PRISMA-ScR/PRISMA-P:** Strict adherence for search strategy and protocol drafting.
*   **Reconciliation:** Formal parity matrix and report comparing blinded mapping vs. existing repo diagrams.
*   **Manuscript:** Title, Abstract, Body, Numbered References ONLY. Neutral, dispassionate tone (No hyperbole/AI-isms).

## 4. Publication 2: Empirical Modelling & Simulation (MJA)
### 4.1 Deliverables & Requirements
*   **Reporting Checklist:** ODD + STRESS-DES.
*   **Code Parity Audit:** 100% trace coverage from manuscript equations to `src/` code.
*   **Environment Freeze:** Publication-specific `requirements.lock` and `Dockerfile.repro`.
*   **Model Spec:** Comprehensive supplementary tables of inputs, equations, and outputs.
*   **Manuscript:** Title, Abstract, Body, Numbered References ONLY. Neutral, dispassionate tone.

## 5. Publication 3: RACMA Position Statement
### 5.1 Deliverables & Requirements
*   **Audience:** Government Ministers, Health Executives (Primary); RACMA Members, Public (Secondary).
*   **Tone:** Plain English (Grade 10-12), authoritative, reform-oriented.
*   **Content:** Distils P1/P2 findings into actionable policy recommendations.

## 6. Acceptance Criteria
*   [ ] **Folder Structure:** Exact schema from 2.1 exists.
*   [ ] **Guidelines:** `guidelines_summary.md` exists for MJA and RACMA with target word counts/schemas.
*   [ ] **Auditability:** `review_log.md` and `traceability_matrix.csv` present for each paper.
*   [ ] **Readability:** `readability_report.md` confirms sentence length and grade level targets via `textstat`.
*   [ ] **Tone:** Manual/Simulated audit confirms dispassionate, neutral writing without hyperbole or AI markers.
*   [ ] **References:** `manage_refs.py` passes 100% for recency, quality, and metadata (URL/DOI).
*   [ ] **Formatting:** Manuscripts contain ONLY Title, Abstract, Body, and Numbered References.
*   [ ] **Submission:** Complete packages including Title Page and Cover Letter for each.
