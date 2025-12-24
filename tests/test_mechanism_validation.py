from __future__ import annotations

import pandas as pd
import pytest

# To be implemented
from nhra_game_theory.domain.validation import MechanismValidator


@pytest.fixture
def mock_gsa_results():
    """Mock GSA dataframe structure."""
    return pd.DataFrame(
        {
            "parameter": [
                "discharge_delay_base",
                "fragmentation_index",
                "political_salience",
                "rurality_weight",
            ],
            "mu_star": [0.85, 0.45, 0.20, 0.05],
            "sigma": [0.10, 0.05, 0.02, 0.01],
            "rank": [1, 2, 3, 4],
        }
    )


def test_mechanism_validator_ranking(mock_gsa_results):
    """Verify that validator correctly checks parameter rankings."""
    validator = MechanismValidator(mock_gsa_results)

    # Assert that discharge_delay is the #1 driver
    assert validator.verify_rank("discharge_delay_base", expected_rank=1)

    # Assert that fragmentation is within top 3
    assert validator.verify_top_n("fragmentation_index", n=3)

    # Assert failure for incorrect rank
    assert not validator.verify_rank("political_salience", expected_rank=1)


def test_mechanism_validator_magnitude(mock_gsa_results):
    """Verify that validator checks magnitude thresholds."""
    validator = MechanismValidator(mock_gsa_results)

    # Assert discharge_delay has mu_star > 0.5
    assert validator.verify_magnitude("discharge_delay_base", threshold=0.5)

    # Assert rurality has low influence
    assert validator.verify_magnitude("rurality_weight", threshold=0.1, comparison="<")


def test_mechanism_validator_consistency():
    """Verify validator against historical narrative rules."""
    # Create a scenario where the mechanism is BROKEN (e.g., rurality is dominant driver of pressure, which contradicts history)
    broken_results = pd.DataFrame(
        {
            "parameter": ["rurality_weight", "discharge_delay_base"],
            "mu_star": [0.99, 0.01],
            "rank": [1, 2],
        }
    )

    validator = MechanismValidator(broken_results)

    # Define a narrative rule: "discharge_delay should > rurality" for pressure
    rule_passed = validator.verify_inequality("discharge_delay_base", "rurality_weight")
    assert not rule_passed, "Broken mechanism should fail validation"
