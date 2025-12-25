# NHRA Game Theory

[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Stylised game-theory mechanism models for National Health Reform Agreement (NHRA) negotiations.**

This project simulates the strategic interactions between Commonwealth and State health actors, modelling the downstream consequences on hospital system pressure (e.g., exit block, ED crowding, ambulance offload delays).

> **Disclaimer:** These models are illustrative and intended for policy reasoning and sensitivity exploration. They are not a forecast of real-world mortality or budget impact.

---

## 🎯 Key Features

- **Predictive Game Theory:** Models strategic tension (Invest vs. Cost-Shift) under fiscal constraints.
- **Empirical Grounding:** Calibrated against AIHW and ABS time-series data (2011–2024).
- **Interactive Scenarios:** "War Gaming" dashboard to test policy interventions.
- **Global Sensitivity Analysis:** Morris/Sobol methods to identify high-impact parameters.
- **Publication-Ready:** Automated report generation compliant with academic standards.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/) (Recommended)

### Installation

```bash
git clone https://github.com/your-org/nhra-game-theory.git
cd nhra-game-theory
poetry install
```

### Running the Simulation

**1. Interactive Dashboard (Recommended)**
Launch the "War Gaming" interface to explore scenarios and policy levers:

```bash
just dashboard
```

**2. Full Validation Pipeline**
Run the model validation suite against historical data:

```bash
just validate
```

**3. Run Everything**
Execute the full build, test, and documentation pipeline:

```bash
just all
```

## 🏗️ Architecture

The model integrates three core domains:
1.  **Macro-Fiscal:** NEP trajectory, WPI inflation, and Funding Caps.
2.  **Strategic Game:** Commonwealth vs. State payoff matrices (Political Capital vs. Budget).
3.  **Hospital Operations:** System dynamics model of patient flow (ED -> Ward -> Discharge).

See [context/02_system_map.md](context/02_system_map.md) for a conceptual overview.

## 👩‍💻 Development

We follow [pyOpenSci](https://www.pyopensci.org/) standards.

- **Testing:** `just test` (runs pytest)
- **Linting:** `just lint` (runs ruff, mypy)
- **Docs:** `just docs` (serves mkdocs)

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use this model in your research, please cite:
> Mordaunt, D. A. (2025). *NHRA Game Theory: A Mechanism Design Framework*. [Repository URL]
