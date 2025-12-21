from pathlib import Path

# Notes:
# - Defines shared project directories (data, raw_data, models, logs)
# - Ensures each directory exists at import time

# Automatically detect the project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parents[0]

# Data directory (shared across all components)
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Models directory
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Logs directory
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
