from __future__ import annotations
from pydantic import Field, ConfigDict
from goodconf import GoodConf
from pathlib import Path

class Settings(GoodConf):
    """Environment-agnostic configuration for the NHRA model."""
    
    # Path settings
    DATA_DIR: Path = Field(default=Path("data"), description="Directory for data storage")
    OUTPUT_DIR: Path = Field(default=Path("outputs"), description="Directory for simulation outputs")
    CONTEXT_DIR: Path = Field(default=Path("context"), description="Directory for context pack evidence")
    
    # Execution settings
    DEFAULT_MC_SAMPLES: int = Field(default=100, ge=1, description="Default number of Monte Carlo rollouts")
    DEBUG_MODE: bool = Field(default=False, description="Enable verbose logging and debug features")
    
    # Calibration settings
    CALIBRATION_TARGETS_FILE: Path = Field(default=Path("data/raw/calibration_targets.csv"))
    
    model_config = ConfigDict(frozen=True)
    
    class Config:
        default_files = ["config.yaml", "config.json"]

# Global settings instance
settings = Settings()
