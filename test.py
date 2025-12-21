import json
from threading import Thread

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

from starlette.staticfiles import StaticFiles

# Project modules
from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from main import run_live_agent
from rl.train_rl import train_rl_agent
from rl.rl_environment import SmartHomeEnv
from rl.rl_agent import RLAgent
from rl.rl_utils import get_user_location, get_real_outdoor_temp
from training_kpi_logger import TrainingKPI
from lstm_predictor import LSTMPredictor
from paths import DATA_DIR, LOGS_DIR, MODELS_DIR


def init_system():
    # Notes:
    # - Runs impact calibration (rebuild impact_map.json)
    # - Loads device + home managers to ensure files are ready
    calibrator = ImpactCalibrator()
    calibrator.calibrate()
    devices = DeviceManager()
    homes = HomeManager()

    return {
        "message": "System initialized successfully",
        "devices_count": len(devices.get_all_devices()),
        "homes_count": len(homes.homes)
    }


# Simple local test call (prints init result)
gg = init_system()
print(f"[INFO] | {gg}")
