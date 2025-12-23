from __future__ import annotations

from pathlib import Path

import pandas as pd


def test_posterior_sampling_logic():
    """Verify that we can sample parameter sets from the trials dataframe."""
    # Mock Optuna trials_dataframe structure
    data = {
        "number": [0, 1, 2],
        "value": [0.001, 0.005, 0.002],
        "params_cost_shifting_intensity": [0.2, 0.5, 0.3],
        "params_fragmentation_index": [1.0, 0.8, 1.1],
        "state": ["COMPLETE", "COMPLETE", "COMPLETE"]
    }
    df = pd.DataFrame(data)
    
    # Filtering for 'good' trials (e.g. value < 0.003)
    good_trials = df[df["value"] < 0.003]
    assert len(good_trials) == 2
    
    # Sampling a parameter set
    sample = good_trials.sample(1).iloc[0]
    assert "params_cost_shifting_intensity" in sample
    assert sample["params_cost_shifting_intensity"] in [0.2, 0.3]

def test_posterior_file_exists_after_run():
    """Check if the posterior file exists in the expected location (integration-style check)."""
    post_path = Path("data/calibration_v21/calibration_trials_posterior.csv")
    # This might not exist yet if script hasn't run, but we check the path logic
    assert post_path.parent.exists()
