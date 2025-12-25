from __future__ import annotations

import json
from pathlib import Path


def identify_orphans() -> None:
    """Identify logic present in archives but missing in current engine."""
    fingerprints_path = Path("data/audit/zip_fingerprints.json")
    if not fingerprints_path.exists():
        print("Fingerprints not found. Run Task 2.1 first.")
        return

    all_fingerprints = json.loads(fingerprints_path.read_text())
    
    # Define "core" logic in current engine
    current_engine_path = Path("src/nhra_game_theory/engine.py")
    # Simple check for now: what subgames are mentioned?
    current_logic = {
        "BARG", "DEF", "SHIFT", "DISC", "GOV", "COMP", "SIGNAL"
    }
    
    orphans = []
    
    print("Scanning archives for orphaned logic...")
    for zip_name, files in all_fingerprints.items():
        for py_file, data in files.items():
            # Look at functions and classes
            for func in data["functions"]:
                # If it looks like a game or key mechanism but not in current
                if any(x in func.upper() for x in ["GAME", "SOLVE", "EQUILIBRIUM", "NASH"]):
                    if func.upper() not in current_logic:
                         orphans.append({
                             "source": f"{zip_name}::{py_file}",
                             "type": "Function",
                             "name": func,
                             "note": "Potentially orphaned subgame or solver logic"
                         })
            
            for cls in data["classes"]:
                if any(x in cls.upper() for x in ["GAME", "ENGINE", "SIMULATOR"]):
                    orphans.append({
                        "source": f"{zip_name}::{py_file}",
                        "type": "Class",
                        "name": cls,
                        "note": "Legacy engine or game class"
                    })

    output_file = Path("reports/orphaned_logic.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(orphans, f, indent=2)
        
    print(f"Identified {len(orphans)} potential orphans. Results saved to {output_file}")


if __name__ == "__main__":
    identify_orphans()
