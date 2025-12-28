import pytest
from pathlib import Path
from nhra_gt.domain.state import ParamsJax, BaselineProvider
from nhra_gt.domain.registry import EvidenceRegistry, EvidenceEntry

def test_yaml_param_loading(tmp_path):
    """Verify that ParamsJax can load from a custom YAML."""
    config_content = """
funding:
  nominal_cth_share_target: 0.55
pricing:
  nep_annual_growth: 0.05
"""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)
    
    p = ParamsJax.from_yaml(config_path)
    assert p.nominal_cth_share_target == 0.55
    assert p.nep_annual_growth == 0.05

def test_registry_to_yaml_promotion(tmp_path):
    """Verify that the registry can overwrite YAML defaults."""
    # 1. Setup base config
    config_content = "funding:\n  nominal_cth_share_target: 0.45\n"
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)
    
    # 2. Setup Registry with better evidence
    registry = EvidenceRegistry()
    registry.add_entry(EvidenceEntry(
        parameter="nominal_cth_share_target",
        mean=0.50,
        source_url="New Deal 2025"
    ))
    
    # 3. Promote
    registry.promote_all_to_yaml(config_path)
    
    # 4. Verify
    p_updated = ParamsJax.from_yaml(config_path)
    assert p_updated.nominal_cth_share_target == 0.50

def test_baseline_provider_integration():
    """Verify high-level BaselineProvider integration."""
    params, state = BaselineProvider.get_baseline()
    
    assert isinstance(params, ParamsJax)
    assert state.year == 2025
    # Should have loaded from defaults.yaml
    assert params.nominal_cth_share_target == 0.45
