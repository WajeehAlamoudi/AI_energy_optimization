import json
import random
from datetime import datetime

import numpy as np

from paths import DATA_DIR
from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from rl.rl_utils import (
    get_user_location,
    get_real_outdoor_temp,
    get_real_indoor_temp,
    get_real_energy_usage,
    get_if_weekend,
)



# Logging (consistent format)
LEVEL_WIDTH = 5  # INFO, ERROR, WARN, DEBUG


def log(level: str, msg: str) -> None:
    """
    Simple console logger with fixed format.
    Example:
      [2025-12-20 04:12:33] [INFO ] | Resetting environment...
    """
    level = (level or "INFO").upper()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level:<{LEVEL_WIDTH}}] | {msg}")


class SmartHomeEnv:
    """
    Smart home environment for RL:
      - State: [indoor_temp, total_kWh]
      - Action: (device, permission) pairs from device catalog / home-specific devices
      - Dynamics: uses an impact_map (energy_factor, temp_change) per action keyword
    """

    def __init__(self, home_name=None, mode: str = "real", comfort_range=(20, 27)):
        # Environment observable variables
        self.outdoor_temp = None
        self.indoor_temp = None
        self.total_kWh = None
        self.is_weekend = None

        # User location (used for outdoor weather in real mode)
        loc = get_user_location() or {}
        self.city = loc.get("city", "UnknownCity")
        self.lat = loc.get("lat", 0.0)
        self.lon = loc.get("lon", 0.0)
        self.country = loc.get("country", "UnknownCountry")

        # Managers and mode
        self.home_name = home_name
        self.home_manager = HomeManager()
        self.manager = DeviceManager()
        self.mode = mode  # "real" or "sim"

        # Select device scope + comfort range
        if self.home_name and self.home_name in self.home_manager.homes:
            log("INFO", f"Loading environment for home: {self.home_name}")
            self.devices = {
                d: self.manager.get_all_devices()[d]
                for d in self.home_manager.get_home_devices(self.home_name)
            }
            self.comfort_min, self.comfort_max = self.home_manager.homes[self.home_name].get(
                "comfort_range", comfort_range
            )
        else:
            log("INFO", "No specific home provided. Using global device catalog.")
            self.devices = self.manager.get_all_devices()
            self.comfort_min, self.comfort_max = comfort_range

        # Initialize real/sim signals
        self._out_temp()
        self._indoor_temp()
        self._real_kWh()
        self._is_weekend()

        # Step counter (e.g., one day simulation = 24 steps)
        self.step_count = 0

        # Load or create impact map (rules for energy/temp effects)
        impact_path = DATA_DIR / "impact_map.json"
        impact_path.parent.mkdir(parents=True, exist_ok=True)

        if not impact_path.exists():
            log("WARN", "Impact map not found. Running calibration...")
            calibrator = ImpactCalibrator()
            calibrator.calibrate()

        with open(impact_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

        # Action space and state definition
        self.action_space = self._build_action_space()
        self.state_size = 2  # [indoor_temp, total_kWh]

    def _is_weekend(self) -> None:
        """
        Set weekend flag:
          - real mode: use actual weekday
          - sim mode : probability-based approximation
        """
        if self.mode == "real":
            self.is_weekend = bool(get_if_weekend())
        else:
            self.is_weekend = random.random() < (2 / 7)

    def _out_temp(self) -> None:
        """
        Update outdoor temperature:
          - real mode: weather API/sensor using user location
          - sim mode : random uniform range
        Includes fallback when sensor returns None or throws.
        """
        if self.mode == "real":
            try:
                self.outdoor_temp = get_real_outdoor_temp(self.lat, self.lon)
                if self.outdoor_temp is None:
                    raise ValueError("Outdoor temperature is None")

                log("INFO", f"Real outdoor temp for {self.city}, {self.country}: {self.outdoor_temp:.1f}°C")

            except Exception as e:
                log("WARN", f"Outdoor sensor/API error: {e}. Falling back to last known/random value.")
                if self.outdoor_temp is None:
                    self.outdoor_temp = random.uniform(10, 40)
        else:
            self.outdoor_temp = random.uniform(10, 40)

    def _indoor_temp(self) -> None:
        """
        Update indoor temperature:
          - real mode: indoor sensor
          - sim mode : random within comfort range
        Includes fallback to comfort mean if sensor fails.
        """
        if self.mode == "real":
            try:
                self.indoor_temp = get_real_indoor_temp()
                if self.indoor_temp is None:
                    raise ValueError("Indoor temperature is None")

                log("INFO", f"Real indoor temp: {self.indoor_temp:.1f}°C")

            except Exception as e:
                log("WARN", f"Indoor sensor error: {e}. Falling back to last known/comfort mean.")
                if self.indoor_temp is None:
                    self.indoor_temp = float(np.mean([self.comfort_min, self.comfort_max]))
        else:
            self.indoor_temp = random.uniform(self.comfort_min, self.comfort_max)

    def _real_kWh(self) -> None:
        """
        Update cumulative energy usage:
          - real mode: energy meter/sensor reading
          - sim mode : starts at 0.0
        Includes fallback to 0.0 if sensor fails.
        """
        if self.mode == "real":
            try:
                self.total_kWh = get_real_energy_usage()
                if self.total_kWh is None:
                    raise ValueError("Energy usage is None")

                log("INFO", f"Real energy usage: {self.total_kWh:.3f} kWh")

            except Exception as e:
                log("WARN", f"Energy sensor error: {e}. Falling back to last known/0.0.")
                if self.total_kWh is None:
                    self.total_kWh = 0.0
        else:
            self.total_kWh = 0.0

    def _build_action_space(self):
        """
        Action space = list of (device_name, permission_string) pairs.
        Example: ("AC", "Turn On"), ("Light", "Dim"), ...
        """
        actions = []
        for device, info in self.devices.items():
            for perm in info.get("permissions", []):
                actions.append((device, perm))
        return actions

    def reset(self):
        """
        Reset environment state for a new episode.
        Returns: state vector [indoor_temp, total_kWh]
        """
        log("INFO", "Resetting environment...")

        self._out_temp()
        self._indoor_temp()
        self._real_kWh()
        self._is_weekend()

        self.step_count = 0
        return np.array([self.indoor_temp, self.total_kWh], dtype=np.float32)

    def step(self, action_index: int):
        """
        Execute action by index:
          - Update indoor temperature (if HVAC/heater)
          - Update energy usage based on base_kWh * energy_factor
          - Apply drift toward outdoor temperature
          - Compute reward (comfort + energy)
        Returns: (next_state, reward, done, info)
        """
        if not (0 <= action_index < len(self.action_space)):
            raise IndexError(f"action_index out of range: {action_index}")

        device, action = self.action_space[action_index]
        base_kWh = float(self.devices[device]["base_kWh"])

        # Default dynamics
        action_lower = str(action).lower()
        energy_factor = 1.0
        temp_change = 0.0

        # Find first matching rule by keyword
        for keyword, rule in self.rules.items():
            if keyword in action_lower:
                energy_factor = float(rule.get("energy_factor", 1.0))
                temp_change = float(rule.get("temp_change", 0.0))
                break

        # Energy for this step
        energy_used = base_kWh * energy_factor

        # Apply temperature impact for HVAC-like devices
        if any(k in str(device).lower() for k in ["ac", "air", "heater"]):
            self.indoor_temp += temp_change

        # Natural drift toward outdoor temperature (simple thermal model)
        self.indoor_temp += 0.05 * (self.outdoor_temp - self.indoor_temp)

        # Update cumulative metrics
        self.total_kWh += energy_used
        self.step_count += 1

        # -----------------------------
        # Reward function
        # -----------------------------
        comfort_center = float(np.mean([self.comfort_min, self.comfort_max]))

        # Comfort penalty / reward
        if self.comfort_min <= self.indoor_temp <= self.comfort_max:
            comfort_penalty = 0.0
            comfort_reward = 1.5
        else:
            comfort_penalty = abs(self.indoor_temp - comfort_center)
            comfort_reward = 0.0

        # Energy weighting (optional dynamic scaling)
        energy_weight = 0.8 if energy_used < 3.0 else 1.0

        # Higher reward when energy is low and comfort is maintained
        reward = -(energy_used * energy_weight + comfort_penalty * 1.90) + comfort_reward

        # Episode termination condition: one simulated day (24 steps)
        done = self.step_count >= 24

        next_state = np.array([self.indoor_temp, self.total_kWh], dtype=np.float32)

        info = {
            "device": device,
            "action": action,
            "energy_used": energy_used,
            "indoor_temp": self.indoor_temp,
            "outdoor_temp": self.outdoor_temp,
        }

        return next_state, reward, done, info
