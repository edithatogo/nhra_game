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

# Cloud operationalization: ENV defaults
ENV NHRA_MC_SAMPLES=300
ENV NHRA_SEED=123
ENV NHRA_ORCHESTRATION=simultaneous

# Switch to non-root user
USER nhra_user

# Entrypoint allowing command override
ENTRYPOINT ["snakemake", "--cores", "1"]
CMD ["all"]
