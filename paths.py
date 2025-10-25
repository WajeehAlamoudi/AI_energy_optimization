# core/paths.py
from pathlib import Path

# Automatically detect the project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parents[0]
# Data directory (shared across all components)
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Models directory
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
