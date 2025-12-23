from __future__ import annotations

import pandas as pd
from pathlib import Path

def verify_alignment():
    spine_path = Path("data/calibration_v21/economic_spine.csv")
    activity_path = Path("data/calibration_v21/historical_normalized.csv")
    
    if not spine_path.exists() or not activity_path.exists():
        print(f"Error: Missing files. Spine: {spine_path.exists()}, Activity: {activity_path.exists()}")
        return False
        
    df_spine = pd.read_csv(spine_path)
    df_activity = pd.read_csv(activity_path)
    
    years_spine = set(df_spine["year"])
    years_activity = set(df_activity["year"])
    
    print(f"Spine years: {min(years_spine)} - {max(years_spine)} (Total: {len(years_spine)})")
    print(f"Activity years: {min(years_activity)} - {max(years_activity)} (Total: {len(years_activity)})")
    
    # 1. Temporal overlap check
    missing_in_spine = years_activity - years_spine
    missing_in_activity = years_spine - years_activity
    
    overlap_ok = True
    if missing_in_spine:
        print(f"WARNING: Activity years missing from Economic Spine: {sorted(list(missing_in_spine))}")
        # Not a hard error if we have fallback logic, but good to know
    
    if 2011 not in years_spine or 2024 not in years_spine:
        print("ERROR: Economic Spine must cover at least 2011-2024 for baseline grounding.")
        overlap_ok = False
        
    # 2. Continuity check
    def is_continuous(years):
        return all(y + 1 in years for y in range(min(years), max(years)))
        
    if not is_continuous(years_spine):
        print("ERROR: Economic Spine has gaps in the year series.")
        overlap_ok = False
        
    if overlap_ok:
        print("SUCCESS: Data alignment and consistency check passed.")
        return True
    else:
        print("FAILURE: Data alignment and consistency check failed.")
        return False

if __name__ == "__main__":
    import sys
    success = verify_alignment()
    if not success:
        sys.exit(1)
