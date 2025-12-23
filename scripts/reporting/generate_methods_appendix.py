from __future__ import annotations

import pandas as pd
from pathlib import Path
from nhra_game_theory.v9 import Params

def generate_appendix(registry_path: Path, output_path: Path):
    """Generates a STRESS-compliant methods appendix."""
    
    content = ["# Methods Appendix: NHRA Game Theory Model (v21/22/23)\n"]
    content.append("## 1. Model Structure")
    content.append("The model is a **Hybrid Agent-Based / System Dynamics** simulation with the following components:")
    content.append("- **Strategic Layer:** 6 concurrent Nash Equilibrium games (Bargaining, Definition, Cost Shifting, Discharge, Governance, Compliance).")
    content.append("- **Operational Layer:** System Dynamics mapping pressure to occupancy, offload delay, and ED performance.")
    content.append("- **Economic Spine:** Calibrated against historical NEP (IHACPA) and WPI (ABS) series.")
    
    content.append("\n## 2. Parameter Registry")
    content.append("All parameters are grounded in public evidence where possible.\n")
    
    if registry_path.exists():
        df = pd.read_csv(registry_path)
        # Markdown table
        table = df[["parameter", "default", "evidence_source"]].to_markdown(index=False)
        content.append(table)
    else:
        content.append("*Parameter registry file not found.*")
        
    content.append("\n## 3. Equations")
    content.append("### Pressure Index")
    content.append("$$ P_t = 0.8 + 0.8 \times (0.55 \cdot \sigma(Occ_t) + 0.45 \cdot \sigma(Off_t)) \times D_t $$")
    content.append("Where $\sigma$ is a logistic sigmoid function, $Occ_t$ is occupancy, $Off_t$ is offload delay, and $D_t$ is discharge delay.")
    
    content.append("\n### Effective Share Drift")
    content.append("$$ Share_{eff} = Share_{nom} \times \frac{1}{1 + Gap_t} $")
    content.append("Where $Gap_t$ drifts based on the divergence between Input Cost Growth (WPI) and Efficient Price Indexation (NEP).")

    with open(output_path, "w") as f:
        f.write("\n".join(content))
        
    print(f"Generated methods appendix at {output_path}")

if __name__ == "__main__":
    reg_path = Path("docs/parameter_registry_v18_20251221.csv")
    out_path = Path("reports/methods_appendix.md")
    generate_appendix(reg_path, out_path)
