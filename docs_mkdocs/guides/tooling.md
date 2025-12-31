# Tooling & Pipeline

This project has three main “ways in”:

- The `nhra_gt` Python package (library + simulation engine)
- A reproducible Snakemake pipeline (`Snakefile`)
- Utility scripts under `scripts/`

## Common tasks

### Run the baseline pipeline

The CI workflow runs the baseline and context pack targets via Snakemake:

```bash
poetry run snakemake --cores 1 run_baseline context_pack --forceall
```

### Build the context pack

```bash
poetry run python scripts/build_context_pack.py
```

### Check parameter traceability

```bash
poetry run python scripts/check_parameters_grounded.py
```

### Build the docs locally

```bash
poetry run mkdocs build
```

### Run the Streamlit app

```bash
poetry run streamlit run streamlit_app.py
```

## Where things live

- Pipeline entrypoint: `Snakefile`
- Scripts: `scripts/`
- Package source: `src/nhra_gt/`
- Documentation source: `docs_mkdocs/`
