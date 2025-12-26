# NHRA Game Theory: Cognitive Digital Twin

![Social Preview](og-image.png)

[![CI](https://github.com/edithatogo/nhra_game/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/nhra_game)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-008080.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-%3E95%25-green.svg)](https://github.com/edithatogo/nhra_game)

**State-of-the-Art (SOTA) decision-grade game-theory mechanism models for National Health Reform Agreement (NHRA) negotiations.**

This project implements a **Cognitive Digital Twin** of the Australian health funding system. It simulates strategic interactions between Commonwealth and State actors, mapping high-level negotiation choices to monthly operational states (access block, ED crowding, ambulance offload).

📖 **Live Documentation:** [https://edithatogo.github.io/nhra_game/](https://edithatogo.github.io/nhra_game/)

---

## 🏛️ System Architecture (C4 Model)

### Level 1: System Context
The model serves as a methodological bridge between empirical data (AIHW/ABS) and policy decision-making.

```mermaid
C4Context
    title System Context Diagram for NHRA Game Theory Model
    
    Person(user, "Policy Researcher / Analyst", "Uses the model to run scenarios and generate reports.")
    System(model, "NHRA Game Theory Model", "Predictive forecasting engine for hospital system pressure and risk.")
    
    System_Ext(aihw, "AIHW / ABS Data", "Provides historical health system metrics (NEP, ED performance).")
    System_Ext(mja, "Academic Community (MJA)", "Peer review and reproducibility target.")
    
    Rel(user, model, "Configures parameters and runs simulations")
    Rel(aihw, model, "Feeds historical data for calibration")
    Rel(model, mja, "Provides reproducible methodology and figures")
    Rel(model, user, "Delivers interactive dashboard and PDF reports")
```

### Level 3: Internal Components
Modular design separating strategic intent from operational execution.

```mermaid
C4Component
    title Component Diagram for NHRA Game Theory Model
    
    Component(engine, "Engine", "Python/NumPy", "Core transition functions and Monte Carlo logic.")
    Component(subgames, "Strategic Layer", "Python/NetworkX", "Game theory logic and Nash solvers.")
    Component(viz, "Visualization API", "Python/Matplotlib/Plotly", "Unified plotting infrastructure.")
    
    Rel(engine, subgames, "Calls strategic decisions")
    Rel(engine, viz, "Feeds data for plotting")
```

---

## 🎯 Evidence-Linked Capabilities

| Feature | Maturity | Verification | Evidence Source |
|---|---|---|---|
| **Stochastic Simulation** | **STABLE** | `tests/test_engine_smoke.py` | [Assumptions Log](context/05_assumptions_log.md) |
| **Multi-Game Equilibria** | **STABLE** | `tests/test_subgames_nash.py` | [Game Theory Spec](context/03_model_overview.md) |
| **45% Cth Share Logic** | **STABLE** | `context/grounding.ok` | [NHRA Agreement](https://www.publichospitalfunding.gov.au/) |
| **Cognitive DT Engine** | **ALPHA** | `tests/test_engine_smoke.py` | [Strategic Map](context/02_system_map.md) |

[Full Feature Matrix & Maturity Grades →](docs/feature_matrix.md)

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/edithatogo/nhra_game.git
cd nhra_game
poetry install
```

### 2. Launch War Room (Dashboard)
```bash
just dashboard
```

### 3. Run Pipeline
```bash
just run
```

---

## 📂 Logic & Workflows (ODD Protocol)

### Strategic Chain of Influence
How negotiation choices propagate through the system.

```mermaid
graph TD
    BARG[Bargaining] -- "funding levels" --> DEF[Definition]
    DEF -- "payment scope" --> SHIFT[Cost-shifting]
    SHIFT -- "community access" --> DISC[Discharge]
    DISC -- "throughput" --> COMP[Compliance]
    COMP -- "audit risk" --> SIGNAL[Signalling]
    SIGNAL -- "transparency" --> BARG
```

---

## 👩‍💻 High-Integrity Development

We adhere to the **Conductor** spec-driven development framework:
- **TDD:** >95% code coverage required for all core modules.
- **Safety:** Automated security scanning via `bandit` and `safety`.
- **Integrity:** Pydantic V2 runtime validation for all simulation parameters.

---

## 📚 Citation & Metadata

If you use this model in your research, please cite:

```bibtex
@software{Mordaunt_NHRA_Game_Theory_2025,
  author = {Mordaunt, Dylan},
  title = {NHRA Game Theory Model: A Cognitive Digital Twin for Public Hospital Funding},
  version = {26.0.0},
  year = {2025},
  url = {https://github.com/edithatogo/nhra_game}
}
```

[CITATION.cff](CITATION.cff) | [zenodo.json](zenodo.json)