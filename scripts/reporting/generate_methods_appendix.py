from __future__ import annotations

import pandas as pd
import json
from pathlib import Path
from nhra_game_theory.engine import Params
from nhra_game_theory.domain.bibliography import Reference, BibliographyManager

def generate_appendix(registry_path: Path, output_path: Path, references_path: Path):
    """Generates a STRESS-compliant methods appendix with bibliography."""
    
    # Initialize Bibliography
    bib_mgr = BibliographyManager()
    if references_path.exists():
        with open(references_path) as f:
            ref_data = json.load(f)
            for r in ref_data:
                bib_mgr.add_reference(Reference(**r))
    
    content = ["# Methods Appendix: NHRA Game Theory Model (v24)\n"]
    content.append("## 1. Model Structure")
    content.append("The model is a **Hybrid Agent-Based / System Dynamics** simulation with the following components:")
    content.append("- **Strategic Layer:** 6 concurrent Nash Equilibrium games (Bargaining, Definition, Cost Shifting, Discharge, Governance, Compliance).")
    content.append("- **Operational Layer:** System Dynamics mapping pressure to occupancy, offload delay, and ED performance.")
    
    cite_101 = "{Australian Institute of Health and Welfare, 2024 @AIHW_MyHospitals #101}" if 101 in bib_mgr.references else ""
    content.append(f"- **Economic Spine:** Calibrated against historical NEP (IHACPA) and WPI (ABS) series {cite_101}.")
    
    content.append("\n## 2. Parameter Registry")
    content.append("All parameters are grounded in public evidence where possible.\n")
    
    if registry_path.exists():
        df = pd.read_csv(registry_path)
        # Keep relevant columns for the appendix
        cols = ["parameter", "default", "evidence_source"] if "evidence_source" in df.columns else df.columns
        table = df[cols].to_markdown(index=False)
        content.append(table)
    
    content.append("\n## 3. Reporting Standards")
    cite_103 = "{Monks et al., 2019 @STRESS_Guidelines #103}" if 103 in bib_mgr.references else ""
    content.append(f"This study adheres to the STRESS guidelines for reporting simulation studies {cite_103}.")

    content.append("\n## 4. Bibliography")
    # Sort by record number for a consistent numbered list
    sorted_refs = sorted(bib_mgr.references.values(), key=lambda x: x.record_number)
    for i, ref in enumerate(sorted_refs, 1):
        content.append(f"{i}. {ref.author}. ({ref.year}). *{ref.title}*. {ref.journal or ref.publisher or ''}. {ref.url or ref.doi or ''}")

    with open(output_path, "w") as f:
        f.write("\n".join(content))
        
    # Export academic formats
    bib_dir = output_path.parent / "bibliography"
    bib_dir.mkdir(parents=True, exist_ok=True)
    (bib_dir / "references.ris").write_text(bib_mgr.to_ris())
    (bib_dir / "references.enw").write_text(bib_mgr.to_enw())
    (bib_dir / "references.bib").write_text(bib_mgr.to_bibtex())
    
    print(f"Generated methods appendix and academic reference files in {bib_dir}")

if __name__ == "__main__":
    # Point to the registry file that passed grounding (v24 standard)
    reg_path = Path("context/04_parameter_registry.csv")
    out_path = Path("reports/methods_appendix.md")
    refs_path = Path("data/bibliography/master_references.json")
    generate_appendix(reg_path, out_path, refs_path)