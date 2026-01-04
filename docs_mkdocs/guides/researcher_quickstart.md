# Researcher Quickstart (Zero-to-Hero)

This guide provides a step-by-step path for external researchers to clone, build, and run the NHRA Game model from scratch.

## 1. Prerequisites

- **Python 3.10+** (Recommend [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- **Docker** (Optional, for containerized runs)
- **Just** (Recommended command runner: `brew install just`)

## 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/nhra_gt.git
cd nhra_gt
pip install poetry
poetry install --with dev,accel,opt
```

## 3. Running the Simulation

The project uses `Justfile` to simplify complex commands.

### Run Baseline Trajectory

```bash
just baseline
```

### Start Interactive Dashboard

```bash
just dashboard
```

## 4. Reproducing Published Results

To reproduce the exact figures found in the MJA publication series:

1. Ensure the `data/raw` directory contains the AIHW/ABS snapshots (or run `just ingest`).
2. Run the Snakemake pipeline:

```bash
just all
```

1. Check the `outputs/` folder for generated figures and tables.

## 5. Troubleshooting

- **JAX Errors:** If you lack a GPU, JAX will fallback to CPU. Ensure `jaxlib` is correctly installed for your OS.
- **D3 Maps:** If the strategic map is empty, ensure you have run `python scripts/interactive/make_d3_network.py`.
