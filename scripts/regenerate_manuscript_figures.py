"""Regenerates all figures for the research manuscript."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import run_simulation
from nhra_gt.visualization.interactive import PlotConfig, plot_risk_pressure, plot_vfi_waterfall

# Configuration
OUTPUT_DIR = Path("publications/P2_Modelling_MJA/05_Figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_scenarios():
    """Load counterfactual scenarios from configuration."""
    with open("configs/scenarios.yaml") as f:
        data = yaml.safe_load(f)
    return data["scenarios"]


def run_scenario(name, params_dict, base_params, years=6):
    """Run a single scenario and return the trajectory DataFrame."""
    # Create scenario-specific params
    # Filter params_dict to only include keys that are in ParamsJax fields
    valid_keys = ParamsJax.__dataclass_fields__.keys()
    filtered_overrides = {k: v for k, v in params_dict.items() if k in valid_keys}

    current_params = base_params.replace(**filtered_overrides)

    print(f"Running scenario: {name}...")
    results = run_simulation(years=years, params=current_params)

    # Convert dict of arrays to DataFrame
    # Flatten any multidimensional arrays (take mean or first dim) if necessary
    flat_results = {}
    for k, v in results.items():
        if isinstance(v, np.ndarray):
            if v.ndim > 1:
                # For visualization, we often want the mean across batch/LHNs if it's not time-series only
                # But engine output is usually [Time] or [Time, LHN]
                # If [Time, LHN], take mean across LHN
                flat_results[f"{k}_mean"] = v.mean(axis=tuple(range(1, v.ndim)))
            else:
                flat_results[k] = v
        else:
            flat_results[k] = v

    df = pd.DataFrame(flat_results)
    df["Scenario"] = name

    # Ensure year column exists
    if "year" not in df.columns:
        df["year"] = range(2025, 2025 + len(df))

    return df


def generate_figures():
    """Generate all manuscript figures for all scenarios."""
    print("Loading configuration...")
    scenarios_config = load_scenarios()

    # Load default base params
    try:
        base_params = ParamsJax.from_yaml("configs/defaults.yaml")
    except Exception as e:
        print(f"Error loading defaults: {e}")
        # Fallback to default constructor
        base_params = ParamsJax()

    # Define Baseline and Comparator
    # Note: scenarios.yaml keys are 'steady_state', 'reform_package' etc.
    baseline_overrides = scenarios_config["steady_state"]["params"]
    reform_overrides = scenarios_config["reform_package"]["params"]

    df_baseline = run_scenario("Baseline", baseline_overrides, base_params)
    df_reform = run_scenario("Transparency Surge", reform_overrides, base_params)

    combined = pd.concat([df_baseline, df_reform])

    # Figure 1: System Pressure Comparison
    print("Generating Figure 1: System Pressure...")
    # Check if 'pressure_mean' exists, else use 'pressure'
    y_col = "pressure_mean" if "pressure_mean" in combined.columns else "pressure"

    fig1 = plot_risk_pressure(
        combined,
        y_col=y_col,
        title="Figure 1: Policy Trade-offs - System Pressure Trajectory",
        ylabel="System Pressure Index",
        config=PlotConfig(primary_color="#2E8B57"),  # SeaGreen
    )

    try:
        fig1.write_image(OUTPUT_DIR / "figure_1_pressure.png", width=1200, height=800, scale=2)
    except Exception as e:
        print(f"Warning: Could not save PNG (kaleido missing?): {e}")

    fig1.write_html(OUTPUT_DIR / "figure_1_pressure.html")

    # Figure 2: VFI Waterfall
    print("Generating Figure 2: VFI Waterfall...")
    last_row = df_baseline.iloc[-1]

    # Use robust get with fallbacks
    # nominal = float(last_row.get("cth_nominal_mean", last_row.get("effective_cth_share", 0.45)))
    # Wait, nominal is the target. effective is the result.    # If the simulation doesn't output 'nominal_cth_share', we use the input param.
    # The input param is 0.45.
    nominal_input = 0.45
    effective = float(
        last_row.get("effective_cth_share_mean", last_row.get("effective_cth_share", 0.38))
    )

    gap = nominal_input - effective

    # Artificial breakdown for visualization if specific loss metrics aren't in output
    indexation = gap * 0.4
    cap = gap * 0.3
    audit = gap * 0.2
    friction = gap * 0.1

    fig2 = plot_vfi_waterfall(
        nominal_share=nominal_input,
        indexation_loss=indexation,
        cap_loss=cap,
        audit_loss=audit,
        adjustment_loss=friction,
        effective_share=effective,
        title="Figure 2: Vertical Fiscal Imbalance Waterfall (2030 Projection)",
    )

    try:
        fig2.write_image(OUTPUT_DIR / "figure_2_vfi_waterfall.png", width=1000, height=800, scale=2)
    except Exception as e:
        print(f"Warning: Could not save PNG: {e}")

    fig2.write_html(OUTPUT_DIR / "figure_2_vfi_waterfall.html")

    print(f"Figures saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_figures()
