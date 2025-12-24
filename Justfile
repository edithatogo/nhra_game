set shell := ["bash", "-lc"]

# quick pipeline
run:
  PYTHONPATH=src python scripts/run_v8_all.py
  PYTHONPATH=src python scripts/diagrams/render_all.py
  PYTHONPATH=src python scripts/interactive/make_d3_network_v9.py

# build a shareable context pack
context:
  python scripts/build_context_pack.py

# validate public sourcing / justification for every model input
grounded:
  python scripts/check_parameters_grounded.py

format:
  ruff format src tests
  ruff check src tests --fix

lint:
  ruff check src tests
  mypy --strict src/nhra_game_theory

test:
  pytest -q

docs:
  mkdocs build -q

# run mutation tests to verify test suite quality
mutate:
  mutmut run

all:
  just format
  just lint
  just grounded
  just test
  just run
  just context
  just docs
