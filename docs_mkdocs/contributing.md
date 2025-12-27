# Contributing

Thank you for your interest in contributing to the NHRA Game Theory toolkit! This guide will help you get started.

---

## Development Setup

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- [Poetry](https://python-poetry.org/) for dependency management
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/edithatogo/nhra_game.git
cd nhra_game

# Install dependencies (including dev tools)
poetry install --with dev

# Activate the virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install
```

---

## Code Quality

We enforce strict code quality standards. All contributions must pass:

### Linting & Formatting

```bash
# Run ruff linter
poetry run ruff check src tests

# Run ruff formatter
poetry run ruff format src tests

# Auto-fix issues
poetry run ruff check src tests --fix
```

### Type Checking

```bash
# Run mypy in strict mode
poetry run mypy --strict src/nhra_gt
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/nhra_gt --cov-report=html
```

### Pre-commit

All checks run automatically on commit:

```bash
# Run all pre-commit hooks manually
pre-commit run --all-files
```

---

## Pull Request Process

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make changes** following code quality standards
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Commit** with [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code refactoring
   - `test:` for test additions/changes
   - `ci:` for CI/CD changes
7. **Push** and create a Pull Request

---

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints everywhere
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed, explaining the purpose
    and any important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.
    """
    pass
```

---

## Adding New Games

To add a new stage game:

1. **Define the game** in `src/nhra_gt/subgames/games.py`:

```python
def new_game(gp: GameParams) -> TwoPlayerGame:
    """Description of the new game."""
    # Build payoff matrices
    u_row = np.array([[...], [...]])
    u_col = np.array([[...], [...]])
    return TwoPlayerGame(
        u_row=u_row, 
        u_col=u_col, 
        row_actions=("A", "B"), 
        col_actions=("A", "B")
    )
```

2. **Add to agents** in `src/nhra_gt/agents/base.py` if the game should be played in simulation

3. **Document** the game in `docs_mkdocs/guides/models.md`

4. **Add tests** in `tests/`

---

## Questions?

Open an issue on GitHub or check the [documentation](https://edithatogo.github.io/nhra_game/).
