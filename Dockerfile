# SOTA environment for NHRA mechanism models
FROM python:3.13-slim

# System deps for graphviz + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m nhra_user
WORKDIR /app

# Pin dependencies first for caching
COPY requirements.lock /app/
RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -r requirements.lock

# Copy source
COPY . /app
RUN pip install --no-cache-dir -e "."

# Switch to non-root user
USER nhra_user

# Default: run full Snakemake pipeline (v25)
CMD ["snakemake", "--cores", "1", "all"]
