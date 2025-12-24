from __future__ import annotations

import pytest
from nhra_game_theory.domain.bibliography import Reference, parse_endnote_token


def test_reference_model():
    """Verify Reference Pydantic model validation."""
    ref = Reference(
        record_number=101,
        label="AIHW_MyHospitals",
        author="Australian Institute of Health and Welfare",
        year=2024,
        title="MyHospitals API",
        doi="10.1234/test",
        url="https://example.com",
    )
    assert ref.record_number == 101
    assert ref.year == 2024


def test_parse_endnote_token():
    """Verify parsing of {Author, YYYY @Label #RecordNumber}."""
    token = "{Australian Institute of Health and Welfare, 2024 @AIHW_MyHospitals #101}"

    # This should return a dict of extracted fields
    parsed = parse_endnote_token(token)

    assert parsed["author"] == "Australian Institute of Health and Welfare"
    assert parsed["year"] == 2024
    assert parsed["label"] == "AIHW_MyHospitals"
    assert parsed["record_number"] == 101


def test_invalid_token():
    """Verify that malformed tokens raise error or return None."""
    with pytest.raises(ValueError):
        parse_endnote_token("invalid { token")
