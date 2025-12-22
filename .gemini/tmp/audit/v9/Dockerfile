# Minimal reproducible environment for NHRA mechanism models
FROM python:3.10-slim

# System deps for graphviz + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install package + optional dev deps (ruff/mypy/pytest)
RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -e ".[dev]"

# Default: run v8 pipeline (fast)
CMD ["bash", "-lc", "PYTHONPATH=src python scripts/run_v8_all.py && PYTHONPATH=src python scripts/diagrams/render_all.py && PYTHONPATH=src python scripts/interactive/make_d3_network_v9.py"]
