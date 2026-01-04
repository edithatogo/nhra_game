"""
JAX-compatible state definitions for the NHRA simulation.

This module defines the data structures used to represent the state of the system
at various levels of granularity (LHN, Jurisdiction, Global). It uses
`flax.struct.dataclass` to ensure compatibility with JAX transformations
like `jit`, `vmap`, and `grad`.
"""

from __future__ import annotations

import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

import jax.numpy as jnp
from flax import struct

from .params_generated import ParamsGenerated

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class SystemModeJax(IntEnum):
    """Enumeration of system-wide operational modes."""
    NORMAL = 0
    STRESS = 1
    CRISIS = 2
    RECOVERY = 3


@struct.dataclass
class EconomicSpineJax:
    """JAX-compatible container for economic indices."""

    years: jnp.ndarray  # int32[N]
    nep_per_nwau: jnp.ndarray  # float64[N]
    wpi_health_index: jnp.ndarray  # float64[N]


@struct.dataclass
class MetricsJax:
    """Accumulated metrics for policy optimization and objective functions."""

    cumulative_pressure: float = 0.0
    cumulative_budget_variance: float = 0.0
    max_occupancy: float = 0.0
    min_within4: float = 1.0

    # Leakage Metrics
    cumulative_indexation_loss: float = 0.0
    cumulative_cap_loss: float = 0.0
    cumulative_audit_loss: float = 0.0
    cumulative_adjustment_costs: float = 0.0

    # Stability Metrics
    max_solver_n_equilibria: int = 0
    mean_solver_residual: float = 0.0

    def replace(self, **kwargs: Any) -> MetricsJax:
        return self.replace(**kwargs)


@struct.dataclass
class ParamsJax(ParamsGenerated):
    """JAX-compatible simulation parameters.

    This class extends the auto-generated scalar parameters with runtime
    objects and JAX-native rules.
    """

    # Modular Rules (JAX-compatible PyTrees)
    cap_rule: Any = struct.field(default_factory=lambda: None)
    audit_rule: Any = struct.field(default_factory=lambda: None)
    eligibility_rule: Any = struct.field(default_factory=lambda: None)
    reconciliation_rule: Any = struct.field(default_factory=lambda: None)

    # Economic Spine (optional JAX arrays)
    spine: EconomicSpineJax | None = None
    economic_spine: str | None = struct.field(default=None, pytree_node=False)  # alias/placeholder

    def replace(self, **kwargs: Any) -> ParamsJax:
        return self.replace(**kwargs)

    @classmethod
    def from_yaml(cls, path: Path | str) -> ParamsJax:
        """Loads parameters from a YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        # Flatten the nested YAML groups
        flat_data = {}
        for group in data.values():
            if isinstance(group, dict):
                flat_data.update(group)

        # Filter only fields that exist in the dataclass
        # We handle default type conversion if needed (e.g. bools to ints for JAX)
        return cls(**{k: v for k, v in flat_data.items() if k in cls.__dataclass_fields__})


# Backwards-compatible alias (many callers/tests still import `Params` from this module).
Params = ParamsJax


class BaselineProvider:
    """
    Manages loading of the automated data spine and baseline parameters.

    Provides a centralized interface for synchronizing empirical data into
    the JAX simulation environment.
    """

    @staticmethod
    def load_spine(
        path: Path | str = "data/calibration/historical_normalized.csv",
    ) -> EconomicSpineJax:
        """
        Loads the economic spine (NEP, WPI) from a CSV file.

        Uses Polars if available, otherwise falls back to Pandas.
        """
        required = {"year", "nep_per_nwau", "wpi_health_index"}
        if pl is None:
            import pandas as pd

            df_pd = pd.read_csv(path)
            missing = required - set(df_pd.columns)
            if missing:
                raise ValueError(f"Spine missing required columns: {sorted(missing)}")
            return EconomicSpineJax(
                years=jnp.array(df_pd["year"].to_numpy().astype(jnp.int32)),
                nep_per_nwau=jnp.array(df_pd["nep_per_nwau"].to_numpy()),
                wpi_health_index=jnp.array(df_pd["wpi_health_index"].to_numpy()),
            )

        df = pl.read_csv(path)
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Spine missing required columns: {sorted(missing)}")
        return EconomicSpineJax(
            years=jnp.array(df["year"].to_numpy().astype(jnp.int32)),
            nep_per_nwau=jnp.array(df["nep_per_nwau"].to_numpy()),
            wpi_health_index=jnp.array(df["wpi_health_index"].to_numpy()),
        )

    @classmethod
    def get_baseline(cls, config_path: str = "configs/defaults.yaml") -> tuple[ParamsJax, StateJax]:
        """
        Retrieves baseline parameters and state for a new simulation run.
        """
        from nhra_gt.engine_jax import baseline_state_jax

        params = ParamsJax.from_yaml(config_path)
        # Check if spine exists
        spine_path = Path("data/calibration/historical_normalized.csv")
        if spine_path.exists():
            try:
                spine = cls.load_spine(spine_path)
            except ValueError as exc:
                logger.warning("Skipping spine load: %s", exc)
            else:
                params = params.replace(spine=spine)

        state = baseline_state_jax(2025, params)
        return params, state


@struct.dataclass
class LhnState:
    """
    Granular state for a single Local Hospital Network (LHN).

    Represents the operational and strategic status of a hospital cluster,
    including its pressure, occupancy, and internal choices.
    """

    id: int
    pressure: float = 1.0
    occupancy: float = 0.88
    within4: float = 0.53
    offload_min: float = 18.0
    nwau_actual: float = 100.0
    nwau_reported: float = 100.0
    coding_intensity: float = 1.0
    target_capacity: float = 1.0
    current_capacity: float = 1.0
    discharge_delay: float = 1.0
    adjustment_costs: float = 0.0

    def replace(self, **kwargs: Any) -> LhnState:
        """Flax-compatible field replacement."""
        return self.replace(**kwargs)


@struct.dataclass
class JurisdictionState:
    """
    Granular state for a single Jurisdiction (State/Territory).

    Aggregates LHNs and manages jurisdictional-level fiscal and political state.
    """

    id: int
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    political_capital: float = 1.0
    effective_cth_share: float = 0.38
    efficiency_gap: float = 0.10
    equity_index: float = 1.0
    total_block_revenue: float = 0.0
    lhn_states: LhnState = struct.field(
        default_factory=lambda: LhnState(0)
    )  # Vectorized in practice

    def replace(self, **kwargs: Any) -> JurisdictionState:
        """Flax-compatible field replacement."""
        return self.replace(**kwargs)


@struct.dataclass
class StateJax:
    """
    JAX-compatible simulation state (Global Orchestrator).

    The root PyTree for the entire simulation state. It contains both global
    aggregates and hierarchical jurisdictional/LHN states.
    """

    year: Any
    month: Any
    pressure: Any
    occupancy: Any
    offload_min: Any
    within4: Any

    # Fiscal / bargaining state
    effective_cth_share: Any = 0.38
    efficiency_gap: Any = 0.10
    discharge_delay: Any = 1.0
    political_capital: Any = 1.0
    equity_index: Any = 1.0
    reconciliation_balance: Any = 0.0
    bailout_expectation: Any = 0.0
    total_block_revenue: Any = 0.0

    # Orchestrator state
    system_mode: Any = 0  # Mapped from SystemModeJax
    agreement_clock: Any = 5
    workforce_pool: Any = 1.0
    target_capacity: Any = 1.0
    current_capacity: Any = 1.0
    coding_intensity: Any = 1.0
    reputation_score: Any = 1.0
    jurisdiction_id: Any = 0

    # Per-LHN (flat) state used by tests + simple vmaps
    lhn_pressure: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(5))
    lhn_nwau: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(5))

    # Hierarchical Entities (optional richer representation)
    jurisdictions: JurisdictionState | None = None

    # Auditor Agent state
    auditor_suspicion: float = 0.0
    audit_pressure_active: float = 0.0
    adjustment_costs: float = 0.0

    # Lags & Measurement
    # Buffers store up to 12 months of history
    lag_buffer_pressure: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_occupancy: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_within4: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_nwau: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_efficiency_gap: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_coding: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))

    # Reported values (lagged) available to agents
    reported_pressure: float = 1.0
    reported_occupancy: float = 0.88
    reported_within4: float = 0.53
    reported_nwau: float = 0.0
    reported_efficiency_gap: float = 0.10
    reported_coding_intensity: float = 1.0

    # Stability Telemetry
    solver_n_equilibria: int = 1
    solver_residual: float = 0.0

    # Patient Choice
    prob_ed: float = 0.5

    metrics: MetricsJax = MetricsJax()

    def replace(self, **kwargs: Any) -> StateJax:
        return self.replace(**kwargs)
