import json
import random
from pathlib import Path
from paths import DATA_DIR
import numpy as np
from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from rl.weather import get_user_location, get_real_outdoor_temp


class SmartHomeEnv:
    # to be set by the user comfort_range
    # given indoor_temp
    # given outdoor_temp
    def __init__(self, home_name=None, mode="real", comfort_range=(21, 25)):
        """
        Smart Home Environment
        If home_name is provided, it will load devices and comfort range
        from HomeManager (per-home configuration).
        Otherwise, it uses the global device catalog.
        """
        loc = get_user_location()
        self.city = loc["city"]
        self.lat = loc["lat"]
        self.lon = loc["lon"]
        self.country = loc["country"]

        self.home_name = home_name
        self.home_manager = HomeManager()
        self.manager = DeviceManager()
        self.mode = mode

        # --- Load device context ---
        if self.home_name and self.home_name in self.home_manager.homes:
            print(f"🏠 Loading environment for home: {self.home_name}")
            self.devices = {
                d: self.manager.get_all_devices()[d]
                for d in self.home_manager.get_home_devices(self.home_name)
            }
            self.comfort_min, self.comfort_max = self.home_manager.homes[self.home_name].get(
                "comfort_range", comfort_range
            )
        else:
            print("⚙️ No specific home provided. Using global device catalog.")
            self.devices = self.manager.get_all_devices()
            self.comfort_min, self.comfort_max = comfort_range

        # --- Initialize dynamic variables ---
        self.indoor_temp = random.uniform(20, 26)

        if self.mode == "real":
            self.outdoor_temp = get_real_outdoor_temp(self.lat, self.lon)
            print(f"🌍 Using real weather for {self.city}, {self.country}: {self.outdoor_temp:.1f}°C")
        else:
            self.outdoor_temp = random.uniform(10, 40)
            print(f"🌡️ Using simulated outdoor temp: {self.outdoor_temp:.1f}°C")

        self.total_kWh = 0.0
        self.step_count = 0

        # --- Load or create impact map ---
        impact_path = DATA_DIR / "impact_map.json"
        impact_path.parent.mkdir(parents=True, exist_ok=True)
        if not impact_path.exists():
            print("⚠️ Impact map not found. Running calibration...")
            calibrator = ImpactCalibrator()
            calibrator.calibrate()

        with open(impact_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

        self.action_space = self._build_action_space()
        self.state_size = 2  # indoor_temp, total_kWh

    def _build_action_space(self):
        actions = []
        for device, info in self.devices.items():
            for perm in info.get("permissions", []):
                actions.append((device, perm))
        return actions

    def reset(self):
        """Reset environment to new random state"""
        self.indoor_temp = random.uniform(20, 26)
        self.outdoor_temp = random.uniform(10, 40)
        self.total_kWh = 0.0
        self.step_count = 0
        return np.array([self.indoor_temp, self.total_kWh], dtype=np.float32)

    def step(self, action_index):
        device, action = self.action_space[action_index]
        base_kWh = self.devices[device]["base_kWh"]

        # === Simplified dynamics (driven by impact map) ===
        action_lower = action.lower()
        energy_factor = 1.0
        temp_change = 0.0

        # Look up the closest matching rule
        for keyword, rule in self.rules.items():
            if keyword in action_lower:
                energy_factor = rule.get("energy_factor", 1.0)
                temp_change = rule.get("temp_change", 0.0)
                break

        # Apply energy use
        energy_used = base_kWh * energy_factor

        # Apply temperature impact (only for climate-related devices)
        if any(k in device.lower() for k in ["ac", "air", "heater"]):
            self.indoor_temp += temp_change

        # Natural drift toward outdoor temp
        self.indoor_temp += 0.05 * (self.outdoor_temp - self.indoor_temp)

        # Update cumulative metrics
        self.total_kWh += energy_used
        self.step_count += 1

        # === Reward Function ===
        comfort_center = np.mean([self.comfort_min, self.comfort_max])
        # Compute comfort penalty (absolute deviation from comfort center)
        if self.comfort_min <= self.indoor_temp <= self.comfort_max:
            comfort_penalty = 0.0
            comfort_reward = 1.5  # small positive boost for staying comfortable
        else:
            comfort_penalty = abs(self.indoor_temp - comfort_center)
            comfort_reward = 0.0
        # Dynamic weighting (optional — scales penalty by energy intensity)
        energy_weight = 0.8 if energy_used < 3.0 else 1.0
        # Final reward: lower energy and closer-to-comfort → higher reward
        reward = -(energy_used * energy_weight + comfort_penalty * 1.8) + comfort_reward

        done = self.step_count >= 24  # one simulated day
        next_state = np.array([self.indoor_temp, self.total_kWh], dtype=np.float32)

        return next_state, reward, done, {
            "device": device,
            "action": action,
            "energy_used": energy_used,
            "indoor_temp": self.indoor_temp,
            "outdoor_temp": self.outdoor_temp
        }
