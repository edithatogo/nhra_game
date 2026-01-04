# SOTA environment for NHRA mechanism models
FROM python:3.12-slim

# System deps for graphviz + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user
RUN useradd -m nhra_user
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy dependency files
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
# --system installs into the system python, avoiding venv complexity in docker
RUN uv sync --frozen --no-install-project

# Copy source
COPY . /app

# Install the project itself
RUN uv sync --frozen

# Cloud operationalization: ENV defaults
ENV NHRA_MC_SAMPLES=300
ENV NHRA_SEED=123
ENV NHRA_ORCHESTRATION=simultaneous
# Ensure the virtualenv is in the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER nhra_user

# Entrypoint allowing command override
ENTRYPOINT ["snakemake", "--cores", "1"]
CMD ["all"]
