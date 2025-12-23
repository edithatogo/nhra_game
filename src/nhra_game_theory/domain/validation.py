from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict
from nhra_game_theory.v9 import Params, run_hybrid

def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Root Mean Square Error."""
    return float(np.sqrt(np.mean((actual - predicted)**2)))

def calculate_mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Mean Absolute Percentage Error."""
    # Avoid division by zero
    actual_safe = np.where(actual == 0, 1e-9, actual)
    return float(np.mean(np.abs((actual - predicted) / actual_safe)))

def calculate_theil_u(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Theil's U1 inequality coefficient.
    
    U = 0: Perfect fit
    U = 1: Worst possible fit
    """
    numerator = np.sqrt(np.mean((actual - predicted)**2))
    denominator = np.sqrt(np.mean(actual**2)) + np.sqrt(np.mean(predicted**2))
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)

def calculate_hit_rate(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Directional Accuracy (Hit Rate).
    
    Percentage of steps where predicted change direction matches actual change direction.
    """
    if len(actual) < 2:
        return 1.0
    
    actual_diff = np.diff(actual)
    pred_diff = np.diff(predicted)
    
    # Check if signs match (include 0 as a distinct "no change" direction)
    hits = np.sign(actual_diff) == np.sign(pred_diff)
    return float(np.mean(hits))

class MechanismValidator:
    """Verifies that model sensitivity aligns with mechanistic/historical narratives."""
    
    def __init__(self, gsa_results: pd.DataFrame):
        self.results = gsa_results.set_index("parameter")

    def verify_rank(self, parameter: str, expected_rank: int) -> bool:
        """Check if parameter holds a specific rank."""
        if parameter not in self.results.index:
            return False
        return int(self.results.loc[parameter, "rank"]) == expected_rank

    def verify_top_n(self, parameter: str, n: int) -> bool:
        """Check if parameter is within the top N drivers."""
        if parameter not in self.results.index:
            return False
        return int(self.results.loc[parameter, "rank"]) <= n

    def verify_magnitude(self, parameter: str, threshold: float, comparison: str = ">") -> bool:
        """Check if parameter influence (mu_star) meets a threshold."""
        if parameter not in self.results.index:
            return False
        val = float(self.results.loc[parameter, "mu_star"])
        if comparison == ">":
            return val > threshold
        return val < threshold

    def verify_inequality(self, param_a: str, param_b: str) -> bool:
        """Check if param_a has greater influence than param_b."""
        if param_a not in self.results.index or param_b not in self.results.index:
            return False
        val_a = float(self.results.loc[param_a, "mu_star"])
        val_b = float(self.results.loc[param_b, "mu_star"])
        return val_a > val_b

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

def aggregate_metrics(results: list[RecursiveResult]) -> dict[str, dict[str, float]]:
    """Calculate summary statistics across all backtest steps."""
    if not results:
        return {}
        
    metrics_summary = {}
    # Get list of all metrics present in the first result
    metric_names = results[0].predicted.keys()
    
    for m in metric_names:
        preds = np.array([r.predicted[m] for r in results])
        actuals = np.array([r.actual[m] for r in results])
        
        metrics_summary[m] = {
            "rmse": calculate_rmse(actuals, preds),
            "mape": calculate_mape(actuals, preds),
            "theil_u": calculate_theil_u(actuals, preds),
            "hit_rate": calculate_hit_rate(actuals, preds)
        }
        
    return metrics_summary

class BlindReveal:
    """Performs blind holdout validation (e.g., train on <2024, test on 2024-2025)."""
    
    def __init__(self, historical_data: pd.DataFrame, holdout_years: list[int], seed: int = 42):
        self.historical_data = historical_data.sort_values("year")
        self.holdout_years = sorted(holdout_years)
        self.seed = seed
        
        # Split data
        self.holdout_df = self.historical_data[self.historical_data["year"].isin(self.holdout_years)]
        self.train_df = self.historical_data[~self.historical_data["year"].isin(self.holdout_years)]
        
    def run_prediction(self) -> list[RecursiveResult]:
        """Run the model for the holdout period using default (or calibrated) params."""
        # Note: In a real implementation, we would calibrate p using self.train_df first.
        # Here we use default params for the MVP.
        p = Params()
        
        # Run model for all holdout years in one go (assuming they are contiguous for now, or just the set)
        traj, _ = run_hybrid(years=self.holdout_years, p=p, n_mc=100, seed=self.seed)
        
        results = []
        for year in self.holdout_years:
            # Get prediction
            pred_row = traj[traj["year"] == year].iloc[0]
            
            # Get actual
            actual_row = self.holdout_df[self.holdout_df["year"] == year].iloc[0]
            
            results.append(RecursiveResult(
                test_year=year,
                predicted={
                    "within4": pred_row["within4_mean"],
                    "occupancy": pred_row["occupancy_mean"]
                },
                actual={
                    "within4": actual_row["within4"],
                    "occupancy": actual_row["occupancy"]
                },
                params=p
            ))
            
        return results