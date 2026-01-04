from __future__ import annotations

import pandas as pd
from scripts.dashboard import rank_interventions

from nhra_gt.engine import Params


def test_rank_interventions():
    """Verify intervention ranking logic."""
    from unittest.mock import patch

    with patch("scripts.dashboard.run_hybrid") as mock_run:
        # Mock side effects for different interventions
        def side_effect(years, p, **kwargs):
            # Baseline (no intervention roughly)
            pressure = 1.0

            print(f"DEBUG: CSI={p.cost_shifting_intensity}, Frag={p.fragmentation_index}")

            # Identify intervention by param changes (heuristic)
            # Default CSI is 0.35. Pooled funding -> 0.2625 (< 0.34)
            # Default Frag is 1.0. UCC -> 0.8 (< 0.99)

            if p.cost_shifting_intensity < 0.34:  # Pooled funding
                pressure = 0.90
            elif p.fragmentation_index < 0.99:  # UCC
                pressure = 0.95

            # Return dummy trajectory
            df = pd.DataFrame(
                {
                    "year": years,
                    "pressure_mean": [pressure] * len(years),
                    "rr_mean": [pressure] * len(years),
                    "offload_mean": [20.0] * len(years),
                    "within4_mean": [0.50] * len(years),
                    "rr_p10": [pressure - 0.1] * len(years),
                    "rr_p90": [pressure + 0.1] * len(years),
                }
            )
            return df, None

        mock_run.side_effect = side_effect

        base_params = Params()
        interventions = ["Pooled Funding", "UCC Integration"]

        df = rank_interventions(base_params, interventions)

        assert len(df) == 2
        assert "Intervention" in df.columns
        assert "Pressure Impact" in df.columns

        pooled_row = df[df["Intervention"] == "Pooled Funding"].iloc[0]
        ucc_row = df[df["Intervention"] == "UCC Integration"].iloc[0]

        # Pooled (0.90) has greater impact (0.10) than UCC (0.95, impact 0.05)
        assert pooled_row["Pressure Impact"] > ucc_row["Pressure Impact"]
