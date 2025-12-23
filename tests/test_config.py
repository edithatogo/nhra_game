from nhra_game_theory.config import Settings, settings

def test_settings_load_defaults():
    """Verify that settings load with correct defaults."""
    assert settings.DEFAULT_MC_SAMPLES == 100
    assert settings.DEBUG_MODE is False
    assert str(settings.DATA_DIR) == "data"

def test_settings_instantiation():
    """Verify we can instantiate Settings explicitly."""
    s = Settings(DEFAULT_MC_SAMPLES=50)
    assert s.DEFAULT_MC_SAMPLES == 50
