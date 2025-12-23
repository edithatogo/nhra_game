from __future__ import annotations

from typing import Any
import pandas as pd
from pydantic import BaseModel, ConfigDict
from nhra_game_theory.v9 import Params, run_hybrid

class RecursiveResult(BaseModel):
    """Container for the results of a single backtest step."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    test_year: int
    predicted: dict[str, float]
    actual: dict[str, float]
    params: Any  # Params object

class RecursiveBacktest:
    """Engine for running recursive rolling horizon validation."""
    
    def __init__(
        self, 
        historical_data: pd.DataFrame, 
        train_window: int = 5, 
        test_window: int = 1,
        seed: int = 42
    ):
        self.historical_data = historical_data.sort_values("year")
        self.train_window = train_window
        self.test_window = test_window
        self.seed = seed

    def generate_windows(self):
        """Generator for (train_df, test_df) pairs."""
        n = len(self.historical_data)
        for i in range(n - self.train_window - self.test_window + 1):
            train_start = i
            train_end = i + self.train_window
            test_start = train_end
            test_end = test_start + self.test_window
            
            train_df = self.historical_data.iloc[train_start:train_end]
            test_df = self.historical_data.iloc[test_start:test_end]
            yield train_df, test_df

    def run_step(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> RecursiveResult:
        """Run a single validation step.
        
        In a real scenario, this would involve:
        1. Calibrating parameters to train_df.
        2. Running the model for test_df years.
        3. Comparing results.
        """
        # For now, we use default params (calibration integration is a separate task)
        p = Params()
        
        test_years = test_df["year"].tolist()
        traj, _ = run_hybrid(years=test_years, p=p, n_mc=100, seed=self.seed)
        
        # Aggregate predicted vs actual for the test years (simple mean for now)
        # Assuming we just take the first year in the test window for simplicity in this MVP
        target_year = test_years[0]
        pred_row = traj[traj["year"] == target_year].iloc[0]
        actual_row = test_df[test_df["year"] == target_year].iloc[0]
        
        return RecursiveResult(
            test_year=target_year,
            predicted={
                "within4": pred_row["within4_mean"],
                "occupancy": pred_row["occupancy_mean"]
            },
            actual={
                "within4": actual_row["within4"],
                "occupancy": actual_row["occupancy"]
            },
            params=p
        )

    def run_all(self) -> list[RecursiveResult]:
        """Execute the full backtest loop."""
        results = []
        for train_df, test_df in self.generate_windows():
            results.append(self.run_step(train_df, test_df))
        return results
