import json
import random
from pathlib import Path
from collections import deque

from paths import DATA_DIR
import numpy as np
from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from rl.rl_utils import get_user_location, get_real_outdoor_temp, get_real_indoor_temp, get_real_energy_usage, \
    get_if_weekend


class SmartHomeEnv:

    def __init__(self, home_name=None, mode="real", comfort_range=(20, 27)):

        # === ORIGINAL CORE VARS (kept for compatibility) ===
        self.outdoor_temp = None
        self.indoor_temp = None
        self.total_kWh = None
        self.is_weekend = None

        # === NEW FEATURE VARS (simulated if no sensors) ===
        self.outdoor_humidity = None   # relative_humidity_2m
        self.room_humidity = None      # room_humidity
        self.hvac_temperature = None   # HVAC_temperature
        self.hour = None               # hour (0-23)

        # History buffers for lag/rolling features
        self.energy_hist = deque(maxlen=3)     # store energy_used per step
        self.room_temp_hist = deque(maxlen=3)  # store indoor_temp per step

        # Feature order (exact)
        self.feature_names = [
            "temperature_2m",
            "relative_humidity_2m",
            "room_temperature",
            "room_humidity",
            "HVAC_temperature",
            "hour",
            "is_weekend",
            "energy_lag1",
            "energy_lag2",
            "energy_roll3",
            "room_temp_roll3",
        ]
        self.state_size = len(self.feature_names)

        # === LOCATION (already used for weather) ===
        loc = get_user_location()
        self.city = loc["city"]
        self.lat = loc["lat"]
        self.lon = loc["lon"]
        self.country = loc["country"]

        self.home_name = home_name
        self.home_manager = HomeManager()
        self.manager = DeviceManager()
        self.mode = mode

        # specific for new home or falls into default values min in-temp, max in-temp, set self.indoor_temp range
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

        # here can get any real data from sensors (but your indoor + energy intentionally fail)
        self._out_temp()
        self._indoor_temp()
        self._real_kWh()
        self._is_weekend()

        # init hour + simulated humidities/HVAC
        self._init_simulated_features()

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

    # -------------------------
    # NEW helpers (minimal)
    # -------------------------

    def _init_simulated_features(self):
        # hour: if not real sensor/time, tie it to step_count; reset() seeds it to 0.
        if self.hour is None:
            self.hour = 0

        # humidity: simulated (since you don't have sensors)
        if self.outdoor_humidity is None:
            self.outdoor_humidity = random.uniform(20, 90)
        if self.room_humidity is None:
            self.room_humidity = random.uniform(25, 65)

        # hvac temperature: simple proxy (close to indoor)
        if self.hvac_temperature is None:
            self.hvac_temperature = float(self.indoor_temp)

        # seed histories so lag/roll features are defined immediately
        self.energy_hist.clear()
        self.room_temp_hist.clear()
        for _ in range(3):
            self.energy_hist.append(0.0)
            self.room_temp_hist.append(float(self.indoor_temp))

    def _roll3(self, dq):
        return float(np.mean(dq)) if len(dq) > 0 else 0.0

    def _get_state(self):
        # lag features from energy_used history
        energy_lag1 = self.energy_hist[-2] if len(self.energy_hist) >= 2 else 0.0
        energy_lag2 = self.energy_hist[-3] if len(self.energy_hist) >= 3 else 0.0
        energy_roll3 = self._roll3(self.energy_hist)
        room_temp_roll3 = self._roll3(self.room_temp_hist)

        return np.array([
            float(self.outdoor_temp),                         # temperature_2m
            float(self.outdoor_humidity),                     # relative_humidity_2m
            float(self.indoor_temp),                          # room_temperature
            float(self.room_humidity),                        # room_humidity
            float(self.hvac_temperature),                     # HVAC_temperature
            float(self.hour),                                 # hour
            float(1.0 if self.is_weekend else 0.0),           # is_weekend
            float(energy_lag1),                               # energy_lag1
            float(energy_lag2),                               # energy_lag2
            float(energy_roll3),                              # energy_roll3
            float(room_temp_roll3),                           # room_temp_roll3
        ], dtype=np.float32)

    # -------------------------
    # ORIGINAL methods (kept)
    # -------------------------

    def _is_weekend(self):
        if self.mode == "real":
            self.is_weekend = get_if_weekend()
        else:
            self.is_weekend = random.random() < (2 / 7)

    def _out_temp(self):
        # keep your original weather logic
        if self.mode == "real":
            try:
                self.outdoor_temp = get_real_outdoor_temp(self.lat, self.lon)
                if self.outdoor_temp is None:
                    raise ValueError("Outdoor temp is None")
                print(f"🌍 Using real weather for {self.city}, {self.country}: {self.outdoor_temp:.1f}°C")
            except Exception as e:
                print(f"⚠️ Sensor error: {e}, fallback to last known value.")
                if self.outdoor_temp is None:
                    self.outdoor_temp = random.uniform(10, 40)
        else:
            self.outdoor_temp = random.uniform(10, 40)

        # simulate outdoor humidity since you don't have it
        if self.outdoor_humidity is None:
            self.outdoor_humidity = random.uniform(20, 90)

    def _indoor_temp(self):
        if self.mode == "real":
            try:
                self.indoor_temp = get_real_indoor_temp()
                # NOTE: your rl_utils raises ConnectionError here on purpose :contentReference[oaicite:3]{index=3}
                print(f"🏡 Real indoor temp: {self.indoor_temp:.1f}°C")
            except Exception as e:
                print(f"⚠️ Sensor error: {e}, fallback to last known value.")
                if self.indoor_temp is None:
                    self.indoor_temp = np.mean([self.comfort_min, self.comfort_max])
        else:
            self.indoor_temp = random.uniform(self.comfort_min, self.comfort_max)

        # simulate room humidity + hvac temp (simple proxy)
        if self.room_humidity is None:
            self.room_humidity = random.uniform(25, 65)
        if self.hvac_temperature is None:
            self.hvac_temperature = float(self.indoor_temp)

    def _real_kWh(self):
        if self.mode == "real":
            try:
                self.total_kWh = get_real_energy_usage()
                # NOTE: your rl_utils raises ConnectionError here on purpose :contentReference[oaicite:4]{index=4}
                print(f"⚡ Real energy usage: {self.total_kWh:.3f} kWh")
            except Exception as e:
                print(f"⚠️ Energy sensor error: {e}, fallback to last known value.")
                if self.total_kWh is None:
                    self.total_kWh = 0.0
        else:
            self.total_kWh = 0.0

    def _build_action_space(self):
        actions = []
        for device, info in self.devices.items():
            for perm in info.get("permissions", []):
                actions.append((device, perm))
        return actions

    def reset(self):
        print("🔄 Resetting environment...")
        self._out_temp()
        self._indoor_temp()
        self._real_kWh()
        self._is_weekend()

        self.step_count = 0
        self.hour = 0  # start of day

        # re-seed simulated features + histories
        self._init_simulated_features()

        # return FULL feature vector (11)
        return self._get_state()

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

        # Update hour (each step = 1 hour)
        self.hour = (self.hour + 1) % 24

        # Very light simulated drift for humidity + hvac temp (optional but stable)
        self.outdoor_humidity = float(np.clip(self.outdoor_humidity + random.uniform(-2, 2), 10, 100))
        self.room_humidity = float(np.clip(self.room_humidity + random.uniform(-1, 1), 10, 95))
        self.hvac_temperature = float(self.indoor_temp)  # keep proxy simple

        # Update histories for lags/rolls
        self.energy_hist.append(float(energy_used))
        self.room_temp_hist.append(float(self.indoor_temp))

        # === Reward Function (UNCHANGED) ===
        comfort_center = np.mean([self.comfort_min, self.comfort_max])
        if self.comfort_min <= self.indoor_temp <= self.comfort_max:
            comfort_penalty = 0.0
            comfort_reward = 1.5
        else:
            comfort_penalty = abs(self.indoor_temp - comfort_center)
            comfort_reward = 0.0

        energy_weight = 0.8 if energy_used < 3.0 else 1.0
        reward = -(energy_used * energy_weight + comfort_penalty * 1.90) + comfort_reward

        done = self.step_count >= 24  # one simulated day

        # return FULL feature vector (11)
        next_state = self._get_state()

        return next_state, reward, done, {
            "device": device,
            "action": action,
            "energy_used": energy_used,
            "indoor_temp": self.indoor_temp,
            "outdoor_temp": self.outdoor_temp,
        }
