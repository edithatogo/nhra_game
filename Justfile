set shell := ["bash", "-lc"]

# Install all dependencies including optional and accelerated groups
install:
  uv sync --all-groups

# Update dependencies locally (local equivalent of dependabot)
update:
  uv lock --upgrade
  uv sync --all-groups

# Quick pipeline run
run:
  uv run python scripts/run_baseline.py
  uv run python scripts/diagrams/render_all.py
  uv run python scripts/interactive/make_d3_network.py

# Build a shareable context pack
context:
  uv run python scripts/build_context_pack.py

# Validate public sourcing
grounded:
  uv run python scripts/check_parameters_grounded.py

# Format code
format:
  uv run ruff format src tests scripts
  uv run ruff check src tests scripts --fix

# Lint code
lint:
  uv run nox -s lint

# Type check
type:
  uv run nox -s type

# Run tests
test:
  uv run nox -s tests

# Build docs
docs:
  uv run nox -s docs

# Run mutation tests
mutate:
  uv run mutmut run

# Launch dashboard
dashboard:
  uv run streamlit run streamlit_app.py

# Validation
validate:
  uv run python scripts/validation/validate_mechanism.py

# Full check
all:
  just format
  just lint
  just type
  just test
  just run
  just docs
