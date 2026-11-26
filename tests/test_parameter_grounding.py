"""Controls for the parameter traceability gate."""

import pytest
from scripts.check_parameters_grounded import _row_failures, scalar_defaults

from nhra_gt.domain.params import Params


def test_grounding_includes_inherited_jax_scalars():
    """Check the JAX defaults that remain outside the public configuration."""
    defaults = scalar_defaults(Params)

    assert defaults["demand_base"] == Params().demand_base
    assert defaults["nep_per_nwau_start"] == Params().to_params_jax().nep_per_nwau_start
    assert defaults["use_sequential_bargaining"] is False
    assert {"ops", "behavior", "policy", "spine", "cap_rule"}.isdisjoint(defaults)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"value": "0.92"}, "differs from runtime default"),
        ({"range_low": "nan"}, "must be finite"),
        ({"range_low": "0.80", "range_high": "0.87"}, "must include the runtime default"),
        ({"source_type": "unknown"}, "unknown source_type"),
        ({"source_type": "calculated", "citation_or_file": "historical"}, "requires public URL"),
        (
            {"source_type": "assumed", "justification": "Stylised"},
            "requires detailed justification",
        ),
    ],
)
def test_grounding_rejects_stale_or_untraceable_rows(change, message):
    """Reject invalid documentation while accepting a fixed reference value."""
    row = {
        "parameter": "occupancy_base",
        "description": "Model starting occupancy",
        "value": "0.88",
        "units": "occupancy fraction",
        "source_type": "assumed",
        "citation_or_file": "https://example.org/model/parameters",
        "locator": "Baseline scenario",
        "range_low": "0.88",
        "range_high": "0.88",
        "justification": (
            "The synthetic starting occupancy seeds the first state and observation buffer. "
            "The paired runtime checks hold it fixed at the active scenario setting when "
            "comparing the two implementations of equilibrium selection."
        ),
    }
    defaults = {"occupancy_base": 0.88}

    assert _row_failures([row], defaults) == []
    failures = _row_failures([row | change], defaults)
    assert any(message in failure for failure in failures)
