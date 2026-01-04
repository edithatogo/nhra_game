# Frequently Asked Questions

Common questions about the NHRA Game Theory toolkit.

---

## General

### What is this project?

The NHRA Game Theory toolkit is a **stylised mechanism model** for analysing healthcare funding negotiations under the National Health Reform Agreement (NHRA). It uses game theory to model strategic interactions between Commonwealth and State governments.

!!! warning "Not a Forecast"
    This is a policy reasoning tool, not a predictive model. It helps understand incentive structures and compare policy directions.

### Who is this for?

- Health policy researchers
- Healthcare economists
- Policy analysts
- Academic researchers studying mechanism design

### What programming language is used?

Python 3.10+ with NumPy, Pandas, and optional JAX acceleration.

---

## Technical Questions

### How do I install the toolkit?

```bash
# Using Poetry (recommended)
git clone https://github.com/edithatogo/nhra_game.git
cd nhra_game
poetry install
poetry shell
```

See the [Usage Guide](guides/usage.md) for more details.

### What are the system requirements?

- Python 3.10, 3.11, 3.12, or 3.13
- ~500MB disk space
- 4GB RAM recommended for Monte Carlo simulations

### How do I run a simulation?

```python
from nhra_gt.engine import Params, run_simulation

results = run_simulation(years=10, n_samples=100, params=Params())
```

### What does "strict mypy mode" mean?

The codebase uses mypy in strict mode, requiring:

- Type hints on all functions
- No implicit `Any` types
- Explicit return types

This ensures type safety and catches bugs early.

---

## Game Theory Questions

### What is a Nash equilibrium?

A Nash equilibrium is a strategy profile where no player can improve their payoff by unilaterally changing their strategy. It represents a stable outcome where each player's strategy is a best response to others.

### Why use game theory for healthcare policy?

Healthcare funding involves strategic interactions between multiple parties (Commonwealth, States, hospitals) with different objectives. Game theory provides a rigorous framework to analyse these interactions and predict equilibrium outcomes.

### How are payoff matrices constructed?

Payoff matrices are parameterised by state variables (pressure, efficiency gap, etc.). The formulas are stylised representations based on:

- Economic incentives (funding share, cost shifting)
- Political factors (salience, electoral cycles)
- Operational constraints (discharge delays, capacity)

See [Game Theory Models](guides/models.md) for detailed payoff formulas.

### What is a "stage game"?

Each year of the simulation, players engage in multiple stage games representing different decision points:

- Definition (what counts as efficient?)
- Bargaining (converge or defer?)
- Cost shifting (invest or shift?)
- etc.

The outcomes of these games affect state variables that carry forward to the next year.

---

## Validation Questions

### How is the model validated?

The validation suite includes:

1. **Sensitivity Analysis**: Sobol global sensitivity to identify key parameters
2. **Recursive Backtesting**: Rolling horizon validation against historical patterns
3. **Mechanism Validation**: Verify game-theoretic properties hold
4. **Unit Tests**: Comprehensive pytest suite with property-based testing

See [Validation Documentation](validation.md) for details.

### What are the model's limitations?

Key limitations include:

- Stylised payoffs (not empirically estimated)
- Two-player simplification of multi-stakeholder dynamics
- No geographic heterogeneity
- Static games (no repeated game dynamics)

See [Requirements & Scope](project/requirements.md) for full discussion.

### How do I report a bug?

Open an issue on [GitHub](https://github.com/edithatogo/nhra_game/issues) with:

- Description of the issue
- Steps to reproduce
- Expected vs actual behaviour
- Python version and OS

---

## Data & Parameters

### Where do the parameters come from?

All parameters must be grounded in publicly accessible sources. The parameter registry (`context/04_parameter_registry.csv`) tracks:

- Value and units
- Source type (primary, secondary, calibrated, assumed)
- Public URL for traceability
- Plausible range for sensitivity analysis

### Can I use my own parameters?

Yes! Create a custom `Params` object:

```python
from nhra_gt.engine import Params

custom = Params(
    cost_shifting_intensity=0.3,
    political_salience=0.6,
    # ... other parameters
)
```

### How do I add new data sources?

1. Add the parameter to `context/04_parameter_registry.csv`
2. Include the public URL and source details
3. Run `python scripts/check_parameters_grounded.py` to validate

---

## Contributing

### How can I contribute?

See the [Contributing Guide](contributing.md) for:

- Development setup
- Code style requirements
- Pull request process

### Is the code open source?

Yes, licensed under Apache 2.0. See [LICENSE](https://github.com/edithatogo/nhra_game/blob/main/LICENSE).

---

## Still have questions?

Open an issue on [GitHub](https://github.com/edithatogo/nhra_game/issues) or check the [full documentation](https://edithatogo.github.io/nhra_game/).
