import re
from pathlib import Path
import json

def check_orphans():
    dash_path = Path("scripts/dashboard_v21.py")
    content = dash_path.read_text()
    
    # Check for legacy versions
    legacy_refs = re.findall(r"v[0-9]+", content)
    
    # Check for missing games
    games = ["bargaining_game", "compliance_game", "cost_shifting_game", 
             "definition_game", "discharge_coordination_game", "governance_integration_game"]
    
    missing_games = [g for g in games if g not in content]
    
    results = {
        "legacy_references": list(set(legacy_refs)),
        "missing_game_imports": missing_games
    }
    
    with open("reports/orphaned_logic.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Audit complete. Missing game imports: {missing_games}")

if __name__ == "__main__":
    check_orphans()