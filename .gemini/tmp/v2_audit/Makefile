PY=python

.PHONY: all mpe lint test

all:
	$(PY) scripts/run_all.py

mpe:
	$(PY) scripts/run_mpe.py --fast

lint:
	python -m pip install ruff
	ruff check .

test:
	python -m pip install pytest
	pytest -q
