from __future__ import annotations

from pathlib import Path
from typing import Any, cast

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvidenceEntry(BaseModel):
    parameter: str
    mean: float
    lower_ci: float | None = None
    upper_ci: float | None = None
    source_url: str = ""
    nhmrc_level: str = "IV"
    unit: str = "absolute"
    access_date: str = ""

    @model_validator(mode="after")
    def validate_ci_bounds(self) -> EvidenceEntry:
        if self.lower_ci is not None and self.lower_ci > self.mean:
            raise ValueError("lower_ci must be <= mean")
        if self.upper_ci is not None and self.upper_ci < self.mean:
            raise ValueError("upper_ci must be >= mean")
        return self

    def get_sigma(self) -> float | None:
        """Calculates standard deviation from 95% CI (Normal approximation)."""
        if self.lower_ci is None or self.upper_ci is None:
            return None
        return (self.upper_ci - self.lower_ci) / 3.92


class EvidenceRegistry(BaseModel):
    # Key is parameter name, value is a list of entries
    entries: dict[str, list[EvidenceEntry]] = Field(default_factory=dict)

    model_config = ConfigDict(validate_assignment=True)

    def add_entry(self, entry: EvidenceEntry) -> None:
        if entry.parameter not in self.entries:
            self.entries[entry.parameter] = []
        self.entries[entry.parameter].append(entry)

    def get_all_entries(self, parameter: str) -> list[EvidenceEntry]:
        return self.entries.get(parameter, [])

    def get_entry(self, parameter: str) -> EvidenceEntry | None:
        """Returns the best entry based on NHMRC grading."""
        return self.resolve_conflict(parameter, method="best_grade")

    def resolve_conflict(self, parameter: str, method: str = "best_grade") -> EvidenceEntry | None:
        """Resolves multiple evidence sources into a single entry."""
        all_entries = self.get_all_entries(parameter)
        if not all_entries:
            return None
        if len(all_entries) == 1:
            return all_entries[0]

        if method == "best_grade":
            # Level I > II > III > IV
            grade_map = {"I": 1, "II": 2, "III-1": 3, "III-2": 4, "III-3": 5, "IV": 6}
            return min(all_entries, key=lambda e: grade_map.get(e.nhmrc_level, 99))

        return all_entries[-1]  # Default to latest

    def generate_grounding_report(self, path: Path | str) -> None:
        """Generates a Markdown report summarizing the evidence grounding."""
        report = "# Evidence Grounding Report\n\n"
        report += "| Parameter | Mean | 95% CI | NHMRC Grade | Source |\n"
        report += "|-----------|------|--------|-------------|--------|\n"

        for param in sorted(self.entries):
            e = self.get_entry(param)
            if e is None:
                continue
            ci_str = f"[{e.lower_ci}, {e.upper_ci}]" if e.lower_ci is not None else "N/A"
            report += (
                f"| {e.parameter} | {e.mean} | {ci_str} | {e.nhmrc_level} | {e.source_url} |\n"
            )

        Path(path).write_text(report)

    def sync_to_targets(self, targets_path: Path | str) -> None:
        """Updates the calibration targets CSV with promoted evidence."""
        if pl is None:
            import pandas as pd

            df = pd.read_csv(targets_path)

            best_entries: list[dict[str, Any]] = []
            for param in self.entries:
                entry = self.get_entry(param)
                if entry:
                    best_entries.append({"metric": param, "target_new": entry.mean})

            if best_entries:
                updates = pd.DataFrame(best_entries)
                df = df.merge(updates, on="metric", how="left")
                df["target"] = df["target_new"].combine_first(df["target"])
                df = df.drop(columns=["target_new"])
                df.to_csv(targets_path, index=False)
            return

        df_pl: Any = pl.read_csv(targets_path)

        # Update targets by joining with a temporary dataframe of best entries
        best_entries = []
        for param in self.entries:
            e = self.get_entry(param)
            if e:
                best_entries.append({"metric": param, "target_new": e.mean})

        if best_entries:
            updates = pl.DataFrame(best_entries)
            df_pl = df_pl.join(updates, on="metric", how="left")
            df_pl = (
                cast(Any, df_pl)
                .with_columns(
                    pl.when(pl.col("target_new").is_not_null())
                    .then(pl.col("target_new"))
                    .otherwise(pl.col("target"))
                    .alias("target")
                )
                .drop("target_new")
            )

            cast(Any, df_pl).write_csv(targets_path)

    def promote_to_params(self, base_params: Any) -> Any:
        """Returns a new Params object with all promoted registry values applied."""
        p_dict = {}
        for param in self.entries:
            if hasattr(base_params, param):
                e = self.get_entry(param)
                if e:
                    p_dict[param] = e.mean
        return base_params.model_copy(update=p_dict)

    def promote_all_to_yaml(self, config_path: Path | str) -> None:
        """Overwrites the YAML config defaults with the latest 'best' evidence from the registry."""
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Update each group if parameter matches
        for group_name, group_dict in config.items():
            if not isinstance(group_dict, dict):
                continue
            for param in group_dict:
                e = self.get_entry(param)
                if e:
                    config[group_name][param] = e.mean

        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    def is_sane(
        self,
        entry: EvidenceEntry,
        baseline: dict[str, float],
        threshold: float = 0.5,
    ) -> bool:
        """Check if an entry's mean deviates more than threshold fraction from a baseline."""
        if entry.parameter not in baseline:
            return True
        base_val = baseline[entry.parameter]
        if base_val == 0:
            return entry.mean == 0
        deviation = abs(entry.mean - base_val) / abs(base_val)
        return deviation <= threshold

    def save_to_csv(self, path: Path | str) -> None:
        flat_data = []
        for p_entries in self.entries.values():
            for e in p_entries:
                flat_data.append(e.model_dump())
        if pl is None:
            import pandas as pd

            pd.DataFrame(flat_data).to_csv(path, index=False)
            return

        pl.DataFrame(flat_data).write_csv(path)

    @classmethod
    def load_from_csv(cls, path: Path | str) -> EvidenceRegistry:
        registry = cls()
        if pl is None:
            import math

            import pandas as pd

            df_pd = pd.read_csv(path)
            for row in df_pd.to_dict(orient="records"):
                lower_ci = row.get("lower_ci")
                upper_ci = row.get("upper_ci")
                entry = EvidenceEntry(
                    parameter=str(row["parameter"]),
                    mean=float(row["mean"]),
                    lower_ci=None
                    if lower_ci is None or (isinstance(lower_ci, float) and math.isnan(lower_ci))
                    else float(lower_ci),
                    upper_ci=None
                    if upper_ci is None or (isinstance(upper_ci, float) and math.isnan(upper_ci))
                    else float(upper_ci),
                    source_url=str(row.get("source_url") or ""),
                    nhmrc_level=str(row["nhmrc_level"]),
                    unit=str(row["unit"]),
                    access_date=str(row.get("access_date") or ""),
                )
                registry.add_entry(entry)
            return registry

        df = pl.read_csv(path)
        for row in df.to_dicts():
            entry = EvidenceEntry(
                parameter=str(row["parameter"]),
                mean=float(row["mean"]),
                lower_ci=float(row["lower_ci"]) if row["lower_ci"] is not None else None,
                upper_ci=float(row["upper_ci"]) if row["upper_ci"] is not None else None,
                source_url=str(row["source_url"]) if row["source_url"] else "",
                nhmrc_level=str(row["nhmrc_level"]),
                unit=str(row["unit"]),
                access_date=str(row["access_date"]),
            )
            registry.add_entry(entry)
        return registry
