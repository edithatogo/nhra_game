# SOTA environment for NHRA mechanism models
FROM python:3.15.2-slim-bookworm

# System deps for graphviz + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    graphviz \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=rust:1.100.0-slim-bookworm /usr/local/cargo /usr/local/cargo
COPY --from=rust:1.100.0-slim-bookworm /usr/local/rustup /usr/local/rustup
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv
ENV CARGO_HOME=/usr/local/cargo RUSTUP_HOME=/usr/local/rustup
ENV PATH="/usr/local/cargo/bin:$PATH"

# Create non-root user
RUN useradd -m nhra_user
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy dependency files
COPY pyproject.toml uv.lock /app/

# Use the locked application environment and the image's Python.
RUN uv sync --locked --no-dev --no-install-project

# Copy source
COPY . /app

# Install the project itself
RUN uv sync --locked --no-dev

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
