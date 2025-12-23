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

@dataclass
class EvidenceRegistry:
    entries: Dict[str, EvidenceEntry] = field(default_factory=dict)
    
    def add_entry(self, entry: EvidenceEntry):
        self.entries[entry.parameter] = entry
        
    def get_entry(self, parameter: str) -> Optional[EvidenceEntry]:
        return self.entries.get(parameter)
        
    def save_to_csv(self, path: Path | str):
        data = [asdict(e) for e in self.entries.values()]
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        
    @classmethod
    def load_from_csv(cls, path: Path | str) -> EvidenceRegistry:
        df = pd.read_csv(path)
        registry = cls()
        # Handle cases where columns might be missing or NaN
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
