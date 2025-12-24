from __future__ import annotations

import pandas as pd
import pytest
from nhra_game_theory.domain.registry import EvidenceEntry, EvidenceRegistry
from nhra_game_theory.legacy_engine import Params


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
        access_date="2025-12-23",
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


def test_registry_conflict_logic():
    """Verify that multiple entries for the same parameter are tracked and resolved."""
    registry = EvidenceRegistry()
    e1 = EvidenceEntry(parameter="within4_base", mean=0.53, nhmrc_level="III-2")
    e2 = EvidenceEntry(parameter="within4_base", mean=0.55, nhmrc_level="I")

    registry.add_entry(e1)
    registry.add_entry(e2)

    assert len(registry.get_all_entries("within4_base")) == 2
    resolved = registry.resolve_conflict("within4_base", method="best_grade")
    assert resolved.nhmrc_level == "I"


def test_registry_resolve_conflict_none():
    """Verify conflict resolution for non-existent parameters."""
    registry = EvidenceRegistry()
    assert registry.resolve_conflict("missing") is None


def test_registry_resolve_conflict_single():
    """Verify conflict resolution for parameters with a single entry."""
    registry = EvidenceRegistry()
    e = EvidenceEntry(parameter="p1", mean=1.0)
    registry.add_entry(e)
    assert registry.resolve_conflict("p1") == e


def test_registry_resolve_conflict_default():
    """Verify default conflict resolution (latest)."""
    registry = EvidenceRegistry()
    e1 = EvidenceEntry(parameter="p1", mean=1.0)
    e2 = EvidenceEntry(parameter="p1", mean=2.0)
    registry.add_entry(e1)
    registry.add_entry(e2)
    assert registry.resolve_conflict("p1", method="latest") == e2


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


def test_registry_sanity_checks():
    """Verify sanity checks against various baseline scenarios."""
    registry = EvidenceRegistry()
    baseline = {"ok_param": 1.0, "bad_param": 1.0, "zero_param": 0.0}

    # 1. Parameter missing from baseline (hits line 94)
    assert registry.is_sane(EvidenceEntry(parameter="missing", mean=100), baseline)

    # 2. Base value is zero, entry is zero (hits line 97)
    assert registry.is_sane(EvidenceEntry(parameter="zero_param", mean=0.0), baseline)

    # 3. Base value is zero, entry is non-zero (hits line 97)
    assert not registry.is_sane(EvidenceEntry(parameter="zero_param", mean=1.0), baseline)

    # 4. Standard deviation check (hits lines 101-102)
    assert registry.is_sane(EvidenceEntry(parameter="ok_param", mean=1.1), baseline, threshold=0.5)
    assert not registry.is_sane(
        EvidenceEntry(parameter="bad_param", mean=2.0), baseline, threshold=0.5
    )


def test_evidence_to_noise_mapping():
    """Verify that we can map 95% CI to standard deviation."""
    entry = EvidenceEntry(parameter="test", mean=0.5, lower_ci=0.4, upper_ci=0.6)
    assert pytest.approx(entry.get_sigma(), rel=1e-2) == 0.051

    entry_none = EvidenceEntry(parameter="test", mean=0.5)
    assert entry_none.get_sigma() is None


def test_registry_grounding_report_generation(tmp_path):
    """Verify that the registry can generate a Markdown audit report."""
    registry = EvidenceRegistry()
    registry.add_entry(
        EvidenceEntry(parameter="p1", mean=1.0, nhmrc_level="I", source_url="Source A")
    )

    report_path = tmp_path / "grounding_report.md"
    registry.generate_grounding_report(report_path)

    assert report_path.exists()
    content = report_path.read_text()
    assert "# Evidence Grounding Report" in content
    assert "p1" in content


def test_registry_sync_to_params():
    """Verify that registry entries can update a Params object."""
    registry = EvidenceRegistry()
    registry.add_entry(EvidenceEntry(parameter="rurality_weight", mean=0.50))

    p_base = Params()
    p_new = registry.promote_to_params(p_base)
    assert p_new.rurality_weight == 0.50


def test_registry_sync_to_calibration_targets(tmp_path):
    """Verify that registry updates can be synced to the calibration targets file."""
    registry = EvidenceRegistry()
    registry.add_entry(EvidenceEntry(parameter="within4_base", mean=0.55))

    targets_path = tmp_path / "calibration_targets.csv"
    pd.DataFrame({"metric": ["within4_base"], "target": [0.53]}).to_csv(targets_path, index=False)

    registry.sync_to_targets(targets_path)
    updated = pd.read_csv(targets_path)
    assert updated.loc[updated["metric"] == "within4_base", "target"].iloc[0] == 0.55
