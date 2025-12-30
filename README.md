# NHRA Game Theory: Cognitive Digital Twin

[![CI](https://github.com/edithatogo/nhra_gt/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/nhra_gt)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-teal.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Decision-grade game-theory mechanism models for National Health Reform Agreement (NHRA) negotiations.**

This project implements a "Cognitive Digital Twin" of the Australian health funding system, simulating strategic interactions between Commonwealth and State actors. It models the downstream consequences of negotiation choices on hospital operational states, including access block, ED crowding, and ambulance offload delays.

> **Disclaimer:** These models are illustrative mechanisms intended for policy reasoning and strategic sensitivity exploration. They are not point-forecasts of real-world clinical endpoints.

---

## 🎯 Key Features

### 1. Cognitive Simulation (v26 Upgrade)
- **Strategic Agents:** Modular `LLMAgent` and `HeuristicAgent` frameworks.
- **Negotiation Loops:** Structured "Debate Loops" between Commonwealth and State agents.
- **Explainable AI:** "Cognitive Trace" logging providing natural language rationales for agent moves.

### 2. Decision-Grade Operational Realism
- **Monthly Time-steps:** Captures seasonal demand peaks, claim timing games, and monthly cashflow dynamics.
- **M/M/s Queuing:** Explicit queuing theory implementation converting demand/capacity into waiting times.
- **Crisis State Machine:** Hysteretic "Code Red" logic simulating system failure and recovery cycles.

### 3. Institutional Realism
- **VFI Waterfall:** Explicit tracking of Valuation Divergence (Nominal vs. Effective share).
- **Interface Games:** Dedicated sub-games for Aged Care and NDIS bottlenecks.
- **Structural Rules:** Swappable implementation of Funding Caps (Hard/Soft) and Audit Regimes.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [Poetry](https://python-poetry.org/)
- [Just](https://github.com/casey/just) (Command runner)

### Installation

```bash
git clone https://github.com/edithatogo/nhra_gt.git
cd nhra_gt
poetry install
```

### OneDrive / Cloud-Sync Folders (Important)

Git repositories are often unreliable inside cloud-synced folders (e.g. OneDrive) due to file-locking and partial sync.
If you see lock/reset/status issues, clone/move the repo to a normal local folder (e.g. `~/dev/...`) and work there.

### Streamlit Cloud

Streamlit Cloud installs dependencies from `requirements.txt` by default. This repo includes a minimal `requirements.txt`
for the dashboard runtime; optional features (e.g. some game-tree rendering) may require extra dependencies.

### Running the System

**1. Strategic Dashboard**
Launch the interactive "War Gaming" interface:
```bash
just dashboard
```

**2. Simulation Pipeline**
Run the core simulation, diagram rendering, and network generation:
```bash
just run
```

**3. Model Calibration**
Optimize parameters against multi-target historical data:
```bash
python scripts/optimize_calibration.py
```

**4. Full Quality Suite**
Execute formatting, linting, grounding checks, and tests:
```bash
just all
```

---

## 📂 Scenario Library

The `scenario_library/` contains standard YAML-based counterfactuals for policy exploration:
- `baseline.yaml`: Standard NHRA settings.
- `cap_removed.yaml`: Impact of removing the 6.5% growth cap.
- `audit_surge.yaml`: High-intensity compliance regime.
- `nep_freeze.yaml`: Stagnant efficiency pricing vs. rising costs.
- `crisis_start.yaml`: Stress-testing system recovery from an initial failure state.

---

## 🏗️ Architecture

The model is built on a modular four-layer architecture:
1.  **Macro-Fiscal:** NEP trajectory and input cost drift (NEP vs. WPI).
2.  **Strategic Layer:** Interacting games (Bargaining, Signalling, Definition, Coding).
3.  **Operational Layer:** M/M/s patient flow and capacity dynamics.
4.  **Political/Utility:** Non-linear loss functions driven by KPI threshold breaches.

---

## 👩‍💻 Development Standards

We adhere to high-integrity software engineering standards:
- **Linting/Formatting:** [Ruff](https://github.com/astral-sh/ruff)
- **Type Checking:** [Mypy](https://mypy-lang.org/) (Strict mode)
- **Testing:** [Pytest](https://docs.pytest.org/) (>95% coverage requirement)
- **Environment:** [Nox](https://nox.thea.codes/) for multi-version orchestration.

---

## 📚 Citation

If you use this model in your research, please cite:

> Mordaunt, D. A. (2025). *NHRA Game Theory: A Cognitive Digital Twin Framework for Mechanism Design*. https://github.com/edithatogo/nhra_gt
