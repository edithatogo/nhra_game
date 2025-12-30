from __future__ import annotations

import sys
from pathlib import Path

# Add src
sys.path.append("src")

from nhra_gt.domain.registry import EvidenceRegistry
from nhra_gt.domain.state import BaselineProvider


def sync_all():
    """Main orchestration for the data spine."""
    print("🔄 Synchronizing Data Spine...")

    # 1. Load Registry
    reg_path = Path("data/registry/staging.csv")
    if reg_path.exists():
        print(f"  - Loading Evidence Registry from {reg_path}")
        registry = EvidenceRegistry.load_from_csv(reg_path)

        # 2. Promote to YAML Config
        config_path = Path("configs/defaults.yaml")
        print(f"  - Promoting evidence to {config_path}")
        registry.promote_all_to_yaml(config_path)
    else:
        print("  ! Staging registry not found. Skipping promotion.")

    # 3. Verify Baseline loading
    print("  - Verifying BaselineProvider initialization...")
    params, state = BaselineProvider.get_baseline()

    print("✅ Data Spine Synchronized.")
    print(f"  - Current Agreement Year: {state.year}")
    print(f"  - Active Cth Share Target: {params.nominal_cth_share_target * 100:.1f}%")


if __name__ == "__main__":
    sync_all()
