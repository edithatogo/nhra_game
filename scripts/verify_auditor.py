"""Verification script for Auditor Agent integration.

Ensures the AuditorValidator can process simulation traces.
"""

from nhra_gt.agents.base import AuditorValidator
from nhra_gt.engine import run_simulation


def verify_auditor_logic():
    """Ensures the AuditorValidator can process simulation traces."""
    # Run a short simulation
    results = run_simulation(years=2, n_samples=1)

    # Convert results to a simple trace format
    trace = []
    for i in range(len(results["year"])):
        trace.append(
            {
                "pressure": float(results["pressure"][i]),
                "occupancy": float(results["occupancy"][i]),
            }
        )

    validator = AuditorValidator()
    report = validator.validate(trace)

    print("Auditor Report:", report)
    assert report["realism_score"] > 0.0
    assert len(report["findings"]) > 0


if __name__ == "__main__":
    verify_auditor_logic()
