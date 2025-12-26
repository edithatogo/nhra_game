from __future__ import annotations

import pytest
from pydantic import ValidationError

from nhra_gt.domain.registry import EvidenceEntry, EvidenceRegistry
from nhra_gt.legacy_engine import Params


def test_params_pydantic_validation():
    """Verify that Params enforces type safety and bounds via Pydantic."""
    # Rurality weight must be between 0 and 1
    with pytest.raises(ValidationError):
        Params(rurality_weight=1.5)

    # Check valid creation
    p = Params(rurality_weight=0.5)
    assert p.rurality_weight == 0.5


def test_evidence_entry_pydantic_validation():
    """Verify that EvidenceEntry enforces CI logic via Pydantic validators."""
    # lower_ci cannot be greater than mean
    with pytest.raises(ValidationError):
        EvidenceEntry(parameter="test", mean=0.5, lower_ci=0.6)

    # Valid entry
    entry = EvidenceEntry(parameter="test", mean=0.5, lower_ci=0.4, upper_ci=0.6)
    assert entry.mean == 0.5


def test_registry_pydantic_serialization(tmp_path):
    """Verify that EvidenceRegistry uses Pydantic for robust serialization."""
    registry = EvidenceRegistry()
    registry.add_entry(EvidenceEntry(parameter="test", mean=0.5))

    json_path = tmp_path / "registry.json"
    # Pydantic makes JSON export trivial and safe
    json_path.write_text(registry.model_dump_json())

    new_registry = EvidenceRegistry.model_validate_json(json_path.read_text())
    assert new_registry.get_entry("test").mean == 0.5
