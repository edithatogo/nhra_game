# Streamlit Dashboard Guide

This page covers running, customizing, and deploying the NHRA Strategic Scenario Dashboard.

---

## Quick Start

### Running Locally

```bash
# Activate environment
poetry shell

# Run the dashboard
streamlit run scripts/dashboard.py
```

The dashboard will open at `http://localhost:8501`.

---

## Dashboard Features

### Tab Overview

| Tab | Purpose |
|-----|---------|
| 📈 **Scenario Analysis** | Trajectory plots, executive summary, intervention ranking |
| 🕸️ **Strategic Map** | D3 interactive network of game relationships |
| 🌲 **Game Tree Explorer** | Extensive form decision trees for each subgame |
| 🏥 **LHN Variance** | Intra-state local hospital network distribution |
| 🧬 **Data Lineage** | Parameter evidence traceability |
| ⚖️ **Validation Scorecard** | Backtest performance metrics and ghost overlays |
| 🔬 **Technical Analytics** | Stability regions and global sensitivity analysis |
| 🛡️ **Evidence Manager** | Evidence registry and conflict resolution |
| 🔍 **Forensic Audit** | Raw state inspection and parity checking |

### Sidebar Controls

| Category | Parameters |
|----------|------------|
| **Funding & Valuation** | Nominal Cth Share, NEP Growth |
| **Operational Capacity** | Bed Capacity Index, Discharge Delay |
| **Policy & Behaviour** | Political Salience, Audit Pressure |
| **Clinical & Workforce** | Rurality Weight, Cost-Shifting Intensity |
| **Patient Choice** | GP Out-of-Pocket, Time Value |

### Expert Mode

Toggle "🧠 Expert Strategic Mode" to manually override game equilibria:
- Definition: R (Realism) / E (Strict)
- Bargaining: A (Agree) / D (Defer)
- Cost-Shifting: I (Invest) / S (Shift)
- Discharge: C (Coordinate) / F (Fragment)
- Governance: I (Integrate) / S (Separate)
- Compliance: T (Tight) / L (Light)

---

## Deploying to Streamlit Cloud

### Prerequisites

1. **GitHub Repository**: The app must be in a public GitHub repo (or private with Streamlit Cloud Pro)
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

### Step 1: Create `requirements.txt`

Streamlit Cloud uses pip, not Poetry. Create a requirements file:

```bash
poetry export -f requirements.txt --without-hashes > requirements.txt
```

### Step 2: Create `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#008080"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

### Step 3: Create `streamlit_app.py`

Streamlit Cloud looks for `streamlit_app.py` by default. Create a symlink or entrypoint:

```python
# streamlit_app.py
import subprocess
import sys

# Ensure src is in path
sys.path.insert(0, "src")

# Import and run the main dashboard
from scripts.dashboard import main

if __name__ == "__main__":
    main()
```

### Step 4: Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `edithatogo/nhra_game`
4. Set branch: `main`
5. Set main file path: `streamlit_app.py`
6. Click "Deploy"

### Step 5: Configure Secrets (Optional)

For API keys or sensitive config:

1. Go to app settings → Secrets
2. Add secrets in TOML format:

```toml
[api_keys]
logfire = "your-api-key"
```

Access in code:
```python
import streamlit as st
api_key = st.secrets["api_keys"]["logfire"]
```

---

## Performance Optimization

### JAX Caching

The dashboard uses JAX with persistent disk caching:

```python
# Automatic XLA compilation cache
# Located at ~/.cache/jax_cache
```

### Streamlit Caching

Key functions use `@st.cache_data` for responsiveness:

```python
@st.cache_data
def cached_run_model(p: Params, years: list[int], n_mc: int = 50):
    return run_hybrid(years, p, seed=42, n_mc=n_mc)
```

### Monte Carlo Samples

- **Lite Mode** (default): 50 samples — fast, lower confidence
- **SOTA Mode**: 1000 samples — slower, high confidence

Toggle via sidebar "🚀 Boost to SOTA Accuracy" button.

---

## Customization

### Theming

Modify `apply_custom_theme()` in `scripts/dashboard.py`:

```python
def apply_custom_theme():
    st.markdown("""
        <style>
        :root {
            --primary-color: #008080;  /* Teal */
        }
        .stMetric {
            border-left: 5px solid #008080;
        }
        </style>
    """, unsafe_allow_html=True)
```

### Adding New Tabs

1. Add to the tabs list:
```python
tab1, tab2, ..., new_tab = st.tabs([..., "🆕 New Tab"])
```

2. Implement tab content:
```python
with new_tab:
    st.markdown("### New Feature")
    # Your content here
```

### Adding New Interventions

Update the `rank_interventions` function's intervention list:

```python
interventions = [
    "Pooled Funding",
    "UCC Integration",
    "New Intervention",  # Add here
    ...
]
```

And update `apply_intervention()` in `src/nhra_gt/engine.py` to handle the new option.

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Add `PYTHONPATH=src` before running |
| D3 network missing | Run `python scripts/interactive/make_d3_network_v26.py` |
| Validation data missing | Run `python scripts/validation/recursive_backtest.py` |
| GSA data missing | Run `python scripts/run_gsa.py` |
| Slow startup | First run compiles JAX kernels; subsequent runs are cached |

### Debug Mode

```bash
NHRA_DEBUG=true streamlit run scripts/dashboard.py
```

---

## See Also

- [Usage Guide](guides/usage.md) — General toolkit usage
- [Policy Scenarios](scenarios.md) — Pre-defined scenarios
- [Validation](validation.md) — Model validation details
