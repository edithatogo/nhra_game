"""Tests for config."""

from nhra_gt.config import Settings, settings

_DEFAULT_SAMPLES = 100
_OVERRIDDEN_SAMPLES = 50


def test_settings_load_defaults():
    """Verify that settings load with correct defaults."""
    assert settings.DEFAULT_MC_SAMPLES == _DEFAULT_SAMPLES
    assert settings.DEBUG_MODE is False
    assert str(settings.DATA_DIR) == "data"


def test_settings_instantiation():
    """Verify we can instantiate Settings explicitly."""
    s = Settings(DEFAULT_MC_SAMPLES=50)
    assert s.DEFAULT_MC_SAMPLES == _OVERRIDDEN_SAMPLES
