from __future__ import annotations

import pytest
from nhra_game_theory.domain.bibliography import Reference, BibliographyManager

@pytest.fixture
def manager():
    mgr = BibliographyManager()
    ref = Reference(
        record_number=101,
        label="AIHW_MyHospitals",
        author="AIHW",
        year=2024,
        title="MyHospitals API",
        doi="10.1234/test",
        url="https://example.com"
    )
    mgr.add_reference(ref)
    return mgr

def test_ris_export(manager):
    ris = manager.to_ris()
    assert "TY  - JOUR" in ris
    assert "ID  - AIHW_MyHospitals" in ris
    assert "DO  - 10.1234/test" in ris

def test_enw_export(manager):
    enw = manager.to_enw()
    assert "%0 Journal Article" in enw
    assert "%A AIHW" in enw
    assert "%M 101" in enw

def test_bibtex_export(manager):
    bib = manager.to_bibtex()
    assert "@article{AIHW_MyHospitals" in bib
    assert "author = {AIHW}" in bib
    assert "doi = {10.1234/test}" in bib
