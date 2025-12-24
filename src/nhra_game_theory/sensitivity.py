from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from SALib.analyze import morris as morris_analyzer
from SALib.analyze import sobol as sobol_analyzer
from SALib.sample import morris as morris_sampler
from SALib.sample import saltelli as sobol_sampler

from nhra_game_theory.legacy_engine import Params


def generate_sensitivity_summary(morris_path: Path, sobol_path: Path, output_path: Path) -> None:
    """Synthesizes Morris and Sobol results into a Markdown report."""
    summary = "# Global Sensitivity Analysis Summary (v21)\n\n"
    summary += "This report summarizes the findings from the Morris screening and Sobol variance decomposition.\n\n"

    # Morris Section
    if morris_path.exists():
        df_m = pd.read_csv(morris_path, index_col=0)
        summary += "## 1. Morris Screening (Influence & Non-linearity)\n"
        summary += "The Morris method identifies parameters with the greatest overall influence (mu_star) and those with non-linear or interactive effects (sigma).\n\n"
        summary += df_m[["mu_star", "sigma"]].head(5).to_markdown()
        summary += "\n\n"

    # Sobol Section
    if sobol_path.exists():
        df_s = pd.read_csv(sobol_path)
        summary += "## 2. Sobol Analysis (Variance Decomposition)\n"
        summary += "The Sobol method quantifies the percentage of output variance attributable to each parameter (S1) and its total effect including interactions (ST).\n\n"
        summary += (
            df_s[["Parameter", "S1", "ST"]].sort_values("ST", ascending=False).head(5).to_markdown()
        )
        summary += "\n\n"

    summary += "## 3. Key Findings\n"
    # Logic to identify top driver
    if sobol_path.exists():
        top_param = df_s.sort_values("ST", ascending=False).iloc[0]["Parameter"]
        summary += f"- **Primary Driver:** The most influential parameter in the system is **{top_param}**.\n"

    summary += "- **Interactions:** High sigma values in Morris or gaps between ST and S1 in Sobol indicate strong parameter interactions.\n"

    output_path.write_text(summary)


def get_parameter_lineage() -> dict[str, str]:
    """Returns a mapping of model parameters to their evidence sources in the context pack."""
    return {
        "nominal_cth_share_target": "NHRA Section 127; Federal Financial Relations Agreement (2020-2025)",
        "nep_annual_growth": "IHACPA National Efficient Price Determination 2024-25 (Historical Indexation)",
        "bed_capacity_index": "AIHW Hospital Resources 2022-23 (Bed-to-Population Ratios)",
        "discharge_delay_base": "Medicare UCC Evaluation Report (2024); Aged Care/NDIS Interface Audit",
        "political_salience": "Model Assumption Log (05_assumptions_log.md) - Behavioural Weights",
        "audit_pressure": "NHRA Performance and Accountability Framework (Section 4.2)",
        "rurality_weight": "AIHW Hospital Activity Data (2024) - Regional/Remote peer group weights",
        "cost_shifting_intensity": "Productivity Commission (2023) - Report on Government Services (Health)",
    }


def plot_sobol_indices(si: dict[str, Any], output_path: Path) -> None:
    """Generates Sobol first-order and total sensitivity plots."""
    names = si["names"]
    s1 = si["S1"]
    st = si["ST"]
    s1_conf = si["S1_conf"]
    st_conf = si["ST_conf"]

    # First Order (S1)
    df_s1 = pd.DataFrame({"index": s1, "conf": s1_conf}, index=names).sort_values(
        "index", ascending=True
    )
    plt.figure(figsize=(10, 6))
    plt.barh(df_s1.index, df_s1["index"], xerr=df_s1["conf"], color="lightgreen", capsize=5)
    plt.xlabel("S1 (First-order sensitivity index)")
    plt.ylabel("Parameter")
    plt.title("Sobol Analysis: First-order Effects")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path.parent / (output_path.name + "_s1.png"), dpi=300)
    plt.savefig(output_path.parent / (output_path.name + "_s1.svg"))
    plt.savefig(output_path.parent / (output_path.name + "_s1.pdf"))
    plt.close()

    # Total Order (ST)
    df_st = pd.DataFrame({"index": st, "conf": st_conf}, index=names).sort_values(
        "index", ascending=True
    )
    plt.figure(figsize=(10, 6))
    plt.barh(df_st.index, df_st["index"], xerr=df_st["conf"], color="salmon", capsize=5)
    plt.xlabel("ST (Total-order sensitivity index)")
    plt.ylabel("Parameter")
    plt.title("Sobol Analysis: Total-order Effects")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path.parent / (output_path.name + "_st.png"), dpi=300)
    plt.savefig(output_path.parent / (output_path.name + "_st.svg"))
    plt.savefig(output_path.parent / (output_path.name + "_st.pdf"))
    plt.close()


def plot_sobol_heatmap(si: dict[str, Any], output_path: Path) -> None:
    """Generates a heatmap of second-order interaction indices (S2)."""
    if "S2" not in si or si["S2"] is None:
        print("S2 indices not available for heatmap.")
        return

    names = si["names"]
    s2 = si["S2"]

    # s2 is a square matrix (num_vars, num_vars)
    # SALib returns a triangular matrix or flattened array depending on version
    # Let's ensure it's a square matrix for the heatmap
    n = len(names)
    s2_matrix = np.zeros((n, n))

    # SALib typically returns S2 as a 2D array where only the upper triangle is filled
    # or a 1D array of length n*(n-1)/2.
    # In recent versions, it's often a 2D array.
    if isinstance(s2, np.ndarray) and s2.ndim == 2:
        s2_matrix = s2
    else:
        # Handle flattened case if necessary (legacy SALib)
        print("Handling flattened S2 not yet implemented.")
        return

    plt.figure(figsize=(10, 8))
    sns.heatmap(s2_matrix, annot=True, xticklabels=names, yticklabels=names, cmap="YlGnBu")
    plt.title("Sobol Analysis: Second-order Interaction Indices (S2)")
    plt.tight_layout()
    plt.savefig(output_path.with_suffix(".png"), dpi=300)
    plt.savefig(output_path.with_suffix(".svg"))
    plt.savefig(output_path.with_suffix(".pdf"))
    plt.close()


def export_sensitivity_indices(si: dict[str, Any], output_path: Path) -> None:
    """Exports all sensitivity indices to a CSV file."""
    names = si["names"]
    data = {
        "Parameter": names,
        "S1": si["S1"],
        "S1_conf": si["S1_conf"],
        "ST": si["ST"],
        "ST_conf": si["ST_conf"],
    }
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def plot_morris_tornado(df: pd.DataFrame, output_path: Path) -> None:
    """Generates a Morris Tornado plot (mu_star ranking)."""
    # Filter non-zero influence if needed, but here we show all
    df = df.sort_values("mu_star", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(df.index, df["mu_star"], xerr=df["mu_star_conf"], color="skyblue", capsize=5)
    plt.xlabel("mu_star (Absolute mean elementary effect)")
    plt.ylabel("Parameter")
    plt.title("Morris Screening: Parameter Influence")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save in multiple formats as per spec
    plt.savefig(output_path.with_suffix(".png"), dpi=300)
    plt.savefig(output_path.with_suffix(".svg"))
    plt.savefig(output_path.with_suffix(".pdf"))
    plt.close()


def get_salib_problem(
    param_names: list[str],
    bounds_override: dict[str, list[float]] | None = None,
    default_variation: float = 0.20,
) -> dict[str, Any]:
    """Generates a SALib-compatible problem dictionary from the Params dataclass.

    Args:
        param_names: List of parameter names to include in the GSA.
        bounds_override: Optional dictionary mapping parameter names to [min, max] bounds.
        default_variation: If no override, bounds are set to [default * (1-var), default * (1+var)].

    Returns:
        A dictionary with 'num_vars', 'names', and 'bounds'.
    """
    bounds_override = bounds_override or {}
    defaults = Params().__dict__

    problem_names = []
    problem_bounds = []

    for name in param_names:
        if name not in defaults:
            raise ValueError(f"Parameter '{name}' not found in Params dataclass.")

        problem_names.append(name)

        if name in bounds_override:
            problem_bounds.append(bounds_override[name])
        else:
            val = float(defaults[name])
            # Handle boolean or binary-like flags if they exist (Params v8 is mostly floats)
            problem_bounds.append(
                [val * (1.0 - default_variation), val * (1.0 + default_variation)]
            )

    return {"num_vars": len(problem_names), "names": problem_names, "bounds": problem_bounds}


def evaluate_parallel(
    model_func: Callable[[np.ndarray[Any, Any]], float], param_values: np.ndarray[Any, Any], n_procs: int = 4
) -> np.ndarray[Any, Any]:
    """Evaluates the model function in parallel across multiple processes.

    Args:
        model_func: Function that takes a parameter array and returns a scalar result.
        param_values: 2D array of shape (n_samples, n_vars).
        n_procs: Number of worker processes to use.

    Returns:
        A 1D array of results.
    """
    with ProcessPoolExecutor(max_workers=n_procs) as executor:
        # map preserves order
        results = list(executor.map(model_func, param_values))

    return np.array(results)


def run_morris_analysis(
    problem: dict[str, Any],
    model_func: Callable[[np.ndarray[Any, Any]], float],
    n_trajectories: int = 10,
    n_procs: int = 4,
    seed: int = 42,
) -> pd.DataFrame:
    """Performs Morris analysis (Elementary Effects screening).

    Returns:
        A pandas DataFrame with mu_star and sigma indices.
    """
    param_values = morris_sampler.sample(problem, N=n_trajectories, seed=seed)

    # Run the model
    results = evaluate_parallel(model_func, param_values, n_procs=n_procs)

    # Perform analysis
    si = morris_analyzer.analyze(problem, param_values, results, conf_level=0.95, seed=seed)

    # Convert to DataFrame
    df = pd.DataFrame(
        {
            "mu": si["mu"],
            "mu_star": si["mu_star"],
            "sigma": si["sigma"],
            "mu_star_conf": si["mu_star_conf"],
        },
        index=problem["names"],
    )

    return df.sort_values("mu_star", ascending=False)


def run_sobol_analysis(
    problem: dict[str, Any],
    model_func: Callable[[np.ndarray[Any, Any]], float],
    n_samples: int = 128,
    n_procs: int = 4,
    seed: int = 42,
) -> dict[str, Any]:
    """Performs Sobol variance-based sensitivity analysis.

    Args:
        n_samples: The number of samples to generate (must be a power of 2).

    Returns:
        A dictionary containing S1, ST, and S2 indices.
    """
    param_values = sobol_sampler.sample(problem, N=n_samples, calc_second_order=True)

    # Run the model
    results = evaluate_parallel(model_func, param_values, n_procs=n_procs)

    # Perform analysis
    si = sobol_analyzer.analyze(
        problem, results, calc_second_order=True, conf_level=0.95, seed=seed
    )

    # SALib dict doesn't always have names, so we add them for our utilities
    if "names" not in si:
        si["names"] = problem["names"]

    return si


def run_psa(
    distributions: dict[str, Callable[[int], np.ndarray[Any, Any]]],
    model_func: Callable[[np.ndarray[Any, Any]], float],
    n_samples: int = 1000,
    n_procs: int = 4,
) -> pd.DataFrame:
    """Performs Probabilistic Sensitivity Analysis (PSA).

    Args:
        distributions: Dict mapping param name to a sampler function (takes N, returns array).
        model_func: Function taking param array (in order of dict keys) -> scalar result.
        n_samples: Number of MC samples.

    Returns:
        DataFrame with parameters and outcome.
    """
    param_names = list(distributions.keys())

    # Generate samples
    samples = {}
    for name, sampler in distributions.items():
        samples[name] = sampler(n_samples)

    # Create param array for model_func
    # shape: (n_samples, n_vars)
    param_matrix = np.column_stack([samples[name] for name in param_names])

    # Evaluate
    outcomes = evaluate_parallel(model_func, param_matrix, n_procs=n_procs)

    # Build result DF
    df = pd.DataFrame(samples)
    df["outcome"] = outcomes
    return df
