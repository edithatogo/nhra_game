from __future__ import annotations
import pytest
from pathlib import Path
import pandas as pd
import json
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
    
    # get_entry should return the 'best' or 'latest' if multiple exist
    retrieved = registry.get_entry("within4_base")
    assert retrieved.mean == 0.53

def test_registry_conflict_logic():
    """Verify that multiple entries for the same parameter are tracked."""
    registry = EvidenceRegistry()
    e1 = EvidenceEntry(parameter="within4_base", mean=0.53, nhmrc_level="III-2")
    e2 = EvidenceEntry(parameter="within4_base", mean=0.55, nhmrc_level="I")
    
    registry.add_entry(e1)
    registry.add_entry(e2)
    
    # We expect both to be stored
    assert len(registry.get_all_entries("within4_base")) == 2
    
    # We should be able to resolve to one
    resolved = registry.resolve_conflict("within4_base", method="best_grade")
    assert resolved.nhmrc_level == "I"

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

def test_registry_sanity_check():
    """Verify that the registry can flag entries that deviate significantly from a baseline."""
    registry = EvidenceRegistry()
    baseline = {"within4_base": 0.53, "zero_param": 0.0}
    
    # Base value is zero
    entry_zero = EvidenceEntry(parameter="zero_param", mean=0.0)
    assert registry.is_sane(entry_zero, baseline) == True
    
    entry_not_zero = EvidenceEntry(parameter="zero_param", mean=1.0)
    assert registry.is_sane(entry_not_zero, baseline) == False
    
    # 10% deviation
    entry_ok = EvidenceEntry(parameter="within4_base", mean=0.55)
    assert registry.is_sane(entry_ok, baseline, threshold=0.5) == True
    
    # 60% deviation
    entry_bad = EvidenceEntry(parameter="within4_base", mean=0.90)
    assert registry.is_sane(entry_bad, baseline, threshold=0.5) == False

def test_evidence_to_noise_mapping():
    """Verify that we can map 95% CI to standard deviation."""
    entry = EvidenceEntry(parameter="test", mean=0.5, lower_ci=0.4, upper_ci=0.6)
    sigma = entry.get_sigma()
    assert pytest.approx(sigma, rel=1e-2) == 0.051
    
    # Missing coverage: None CIs
    entry_none = EvidenceEntry(parameter="test", mean=0.5)
    assert entry_none.get_sigma() is None

def test_registry_resolve_conflict_edge_cases():
    """Verify conflict resolution edge cases."""
    registry = EvidenceRegistry()
    assert registry.resolve_conflict("non_existent") is None
    
    e1 = EvidenceEntry(parameter="p1", mean=1.0)
    e2 = EvidenceEntry(parameter="p1", mean=2.0)
    registry.add_entry(e1)
    registry.add_entry(e2)
    # Default method coverage (multiple entries)
    assert registry.resolve_conflict("p1", method="latest") == e2