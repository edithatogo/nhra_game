from __future__ import annotations

import csv
from dataclasses import fields
from pathlib import Path
import pandas as pd
from nhra_game_theory.v9 import Params

def generate_full_registry(output_path: Path):
    """Generates the comprehensive parameter registry."""
    # (Simplified logic from v20 script, or just reusing it if I import it)
    # But for cleaner codebase, I'll reimplement the core logic here.
    
    p = Params()
    rows = []
    for f in fields(Params):
        name = f.name
        val = getattr(p, name)
        
        # Determine source type based on name (heuristic for now)
        source = "Model Assumption"
        if "growth" in name or "nep" in name:
            source = "IHACPA/ABS"
        elif "share" in name:
            source = "NHRA"
            
        rows.append({
            "parameter": name,
            "default_value": str(val),
            "evidence_source": source
        })
        
    pd.DataFrame(rows).to_csv(output_path, index=False)

def generate_manuscript_table(output_path: Path):
    """Generates a simplified table for the manuscript."""
    p = Params()
    rows = []
    
    # Select key parameters for the paper
    key_params = [
        "nominal_cth_share_target", "nep_annual_growth", "input_cost_annual_growth",
        "discharge_delay_base", "bed_capacity_index", "cost_shifting_intensity",
        "fragmentation_index", "political_salience"
    ]
    
    for f in fields(Params):
        if f.name in key_params:
            val = getattr(p, f.name)
            rows.append({
                "Parameter": f.name.replace("_", " ").title(),
                "Value": str(val),
                "Source": "Model Assumption" # Placeholder logic
            })
            
    # Update sources for key items
    for r in rows:
        if "Nep" in r["Parameter"]: r["Source"] = "IHACPA"
        if "Input Cost" in r["Parameter"]: r["Source"] = "ABS"
        if "Share" in r["Parameter"]: r["Source"] = "NHRA"
            
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Generated manuscript table at {output_path}")

if __name__ == "__main__":
    generate_manuscript_table(Path("reports/manuscript_parameter_table.csv"))
