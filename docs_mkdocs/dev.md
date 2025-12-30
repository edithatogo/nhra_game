# Development Guide

This guide covers development workflows, tooling, and advanced features for contributors.

---

## Quality Tooling Stack

| Tool | Purpose | Command |
|------|---------|---------|
| [Ruff](https://docs.astral.sh/ruff/) | Linting + formatting | `poetry run ruff check src tests` |
| [Mypy](https://mypy.readthedocs.io/) | Static type checking | `poetry run mypy --strict src/nhra_gt` |
| [Pytest](https://docs.pytest.org/) | Testing framework | `poetry run pytest` |
| [Hypothesis](https://hypothesis.readthedocs.io/) | Property-based testing | Integrated with pytest |
| [Pre-commit](https://pre-commit.com/) | Git hooks | `pre-commit run --all-files` |
| [Bandit](https://bandit.readthedocs.io/) | Security scanning | `poetry run bandit -r src` |
| [Deptry](https://deptry.com/) | Dependency hygiene | `poetry run deptry .` |

---

## Running Tests

### Basic Test Run

```bash
poetry run pytest
```

### With Coverage

```bash
poetry run pytest --cov=src/nhra_gt --cov-report=html
open htmlcov/index.html
```

### Specific Test Files

```bash
# Run only game tests
poetry run pytest tests/test_games.py

# Run with verbose output
poetry run pytest -v

# Stop on first failure
poetry run pytest -x
```

### Property-Based Tests

We use Hypothesis for property-based testing:

```bash
poetry run pytest tests/test_properties.py
```

---

## Performance Profiling

### Scalene (Recommended)

We use [Scalene](https://github.com/plasma-umass/scalene) for high-performance CPU, GPU, and memory profiling:

```bash
# Profile the backtest loop
LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src \
  scalene --cli --profile-all scripts/validation/recursive_backtest.py
```

### py-spy (Sampling Profiler)

For low-overhead production profiling:

```bash
py-spy record -o profile.svg -- python scripts/run_baseline.py
```

### memray (Memory Profiling)

```bash
memray run -o output.bin scripts/run_baseline.py
memray flamegraph output.bin
```

---

## JAX Acceleration & Functional Core

The project uses a high-performance JAX/XLA functional core for the simulation engine. This allows for 10-100x speedups via vectorization and hardware acceleration.

### Functional Programming Rules

To maintain JIT-compatibility, all code in `src/nhra_gt/engine.py` must be **purely functional**:
1.  **No Side Effects:** No `print()`, no global variable mutations, no in-place array updates.
2.  **No Python Control Flow:** Use `jax.lax.cond`, `jax.lax.switch`, and `jax.lax.scan` instead of `if`, `elif`, and `for`.
3.  **Statelessness:** Use `StateJax` Pytrees instead of objects with `self`.

### Pytree State Management

System state is managed using `flax.struct.dataclass`. This allows JAX to treat complex objects as unified blocks of memory:

```python
from nhra_gt.domain.state import StateJax

# Transformation (returns a new state)
new_state = state.replace(pressure=1.2)
```

### Vectorization (vmap)

Use `jax.vmap` to run thousands of Monte Carlo samples or all 8 Australian jurisdictions in parallel at near-zero extra cost:

```python
# Run 1000 rollouts in parallel
keys = jax.random.split(key, 1000)
parallel_results = jax.vmap(run_simulation)(keys)
```

### Performance & Caching

The engine automatically uses a persistent disk cache for compiled XLA kernels located at `~/.cache/jax_cache`. This minimizes "Time-to-First-Plot" in the dashboard.

To run performance benchmarks:
```bash
poetry run python scripts/benchmark_modernization.py
```

---

## Snakemake Pipelines

The project uses [Snakemake](https://snakemake.github.io/) for reproducible pipelines.

### Available Targets

```bash
# Run baseline simulation
poetry run snakemake --cores 4 run_baseline

# Build context pack
poetry run snakemake --cores 4 context_pack

# Run all experiments
poetry run snakemake --cores 4 all

# Dry run (show what would execute)
poetry run snakemake -n all
```

### Visualize DAG

```bash
poetry run snakemake --dag all | dot -Tpng > dag.png
```

---

## CI/CD Pipeline

The GitHub Actions CI runs on every push and PR:

1. **Lint** — Ruff check and format
2. **Type Check** — Mypy strict mode
3. **Security** — Bandit scan (Ubuntu/3.12 only)
4. **Dependency Hygiene** — Deptry (Ubuntu/3.12 only)
5. **Input Traceability** — Parameter grounding check
6. **Context Pack** — Build and verify
7. **Tests** — Full pytest suite
8. **Pipeline** — Snakemake verification
9. **Docs** — MkDocs build
10. **Link Check** — Lychee markdown link validation

### Matrix

Tests run across:
- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.10, 3.11, 3.12, 3.13

---

## Observability (Optional)

For production observability, we support [Logfire](https://logfire.pydantic.dev/):

```bash
# Install observability extras
poetry install --extras observability

# Enable Logfire
export LOGFIRE_SEND_TO_LOGFIRE=true
python scripts/run_baseline.py
```

---

## Debugging Tips

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Ensure `PYTHONPATH=src` is set |
| Type errors | Run `poetry run mypy --strict src/nhra_gt` |
| Test failures | Check `poetry run pytest -v` for details |
| Slow builds | Use `poetry run mkdocs serve` for live reload |

### Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment:

```bash
NHRA_DEBUG=true python scripts/run_baseline.py
```

---

## See Also

- [Contributing Guide](contributing.md) — How to contribute
- [Usage Guide](guides/usage.md) — Getting started
- [API Reference](reference/index.md) — Module documentation
