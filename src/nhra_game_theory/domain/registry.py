from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List
import pandas as pd
from pathlib import Path

@dataclass(frozen=True)
class EvidenceEntry:
    parameter: str
    mean: float
    lower_ci: Optional[float] = None
    upper_ci: Optional[float] = None
    source_url: str = ""
    nhmrc_level: str = "IV"
    unit: str = "absolute"
    access_date: str = ""
    
    def __post_init__(self):
        if self.lower_ci is not None and self.lower_ci > self.mean:
            raise ValueError("lower_ci must be <= mean")
        if self.upper_ci is not None and self.upper_ci < self.mean:
            raise ValueError("upper_ci must be >= mean")

    def get_sigma(self) -> Optional[float]:
        """Calculates standard deviation from 95% CI (Normal approximation)."""
        if self.lower_ci is None or self.upper_ci is None:
            return None
        return (self.upper_ci - self.lower_ci) / 3.92

@dataclass
class EvidenceRegistry:
    # Key is parameter name, value is a list of entries
    entries: Dict[str, List[EvidenceEntry]] = field(default_factory=dict)
    
    def add_entry(self, entry: EvidenceEntry):
        if entry.parameter not in self.entries:
            self.entries[entry.parameter] = []
        self.entries[entry.parameter].append(entry)
        
    def get_all_entries(self, parameter: str) -> List[EvidenceEntry]:
        return self.entries.get(parameter, [])
        
    def get_entry(self, parameter: str) -> Optional[EvidenceEntry]:
        """Returns the best entry based on NHMRC grading."""
        return self.resolve_conflict(parameter, method="best_grade")
        
    def resolve_conflict(self, parameter: str, method: str = "best_grade") -> Optional[EvidenceEntry]:
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
            
        return all_entries[-1] # Default to latest

    def is_sane(self, entry: EvidenceEntry, baseline: Dict[str, float], threshold: float = 0.5) -> bool:
        """Check if an entry's mean deviates more than threshold fraction from a baseline."""
        if entry.parameter not in baseline:
            return True
        base_val = baseline[entry.parameter]
        if base_val == 0:
            return entry.mean == 0
        deviation = abs(entry.mean - base_val) / abs(base_val)
        return deviation <= threshold

    def save_to_csv(self, path: Path | str):
        flat_data = []
        for p_entries in self.entries.values():
            for e in p_entries:
                flat_data.append(asdict(e))
        df = pd.DataFrame(flat_data)
        df.to_csv(path, index=False)
        
    @classmethod
    def load_from_csv(cls, path: Path | str) -> EvidenceRegistry:
        df = pd.read_csv(path)
        registry = cls()
        df = df.where(pd.notnull(df), None)
        for _, row in df.iterrows():
            entry = EvidenceEntry(
                parameter=str(row["parameter"]),
                mean=float(row["mean"]),
                lower_ci=float(row["lower_ci"]) if row["lower_ci"] is not None else None,
                upper_ci=float(row["upper_ci"]) if row["upper_ci"] is not None else None,
                source_url=str(row["source_url"]) if row["source_url"] else "",
                nhmrc_level=str(row["nhmrc_level"]),
                unit=str(row["unit"]),
                access_date=str(row["access_date"])
            )
            registry.add_entry(entry)
        return registry