"""
Verification script for Auditor Agent integration.
Ensures the AuditorValidator can process simulation traces.
"""

from nhra_gt.agents.base import AuditorValidator
from nhra_gt.engine import run_simulation


def verify_auditor_logic():
    # Run a short simulation
    results = run_simulation(years=2, n_samples=1)

    # Construct a mock trace from results
    trace = []
    n_steps = len(results["year"])
    for i in range(n_steps):
        step_data = {
            "pressure": results["pressure"][i],
            "coding_intensity": 1.0,  # Placeholder as it's not fully exposed in all outputs
            "strategy": {"CODING": "U" if i % 2 == 0 else "H"},
        }
        trace.append(step_data)

    validator = AuditorValidator()
    report = validator.validate(trace)

    print("Auditor Report:", report)
    assert report["realism_score"] > 0.0
    assert len(report["findings"]) > 0


if __name__ == "__main__":
    verify_auditor_logic()
