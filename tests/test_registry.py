from __future__ import annotations
import pytest
from pathlib import Path
import pandas as pd
from nhra_game_theory.domain.registry import EvidenceRegistry, EvidenceEntry

def test_evidence_entry_creation():
    """Verify that an EvidenceEntry can be created with full provenance and uncertainty."""
    entry = EvidenceEntry(
        parameter="within4_base",
        mean=0.53,
        lower_ci=0.51,
        upper_ci=0.55,
        source_url="https://example.com/aihw",
        nhmrc_level="III-2",
        unit="proportion",
        access_date="2025-12-23"
    )
    assert entry.parameter == "within4_base"
    assert entry.mean == 0.53
    assert entry.lower_ci == 0.51

def test_registry_add_and_get():
    """Verify entries can be added to and retrieved from the registry."""
    registry = EvidenceRegistry()
    entry = EvidenceEntry(parameter="within4_base", mean=0.53)
    registry.add_entry(entry)
    
    retrieved = registry.get_entry("within4_base")
    assert retrieved.mean == 0.53

def test_registry_persistence(tmp_path):
    """Verify the registry can save to and load from a CSV file."""
    csv_file = tmp_path / "registry.csv"
    registry = EvidenceRegistry()
    entry = EvidenceEntry(parameter="within4_base", mean=0.53, source_url="http://src")
    registry.add_entry(entry)
    
    registry.save_to_csv(csv_file)
    assert csv_file.exists()
    
    new_registry = EvidenceRegistry.load_from_csv(csv_file)
    assert new_registry.get_entry("within4_base").source_url == "http://src"

def test_registry_validation():
    """Verify that the registry validates CI bounds."""
    with pytest.raises(ValueError, match="lower_ci must be <= mean"):
        EvidenceEntry(parameter="test", mean=0.5, lower_ci=0.6)
    with pytest.raises(ValueError, match="upper_ci must be >= mean"):
        EvidenceEntry(parameter="test", mean=0.5, upper_ci=0.4)
