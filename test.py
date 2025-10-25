"""
Test the full AI-Driven Energy Optimization backend pipeline.
Covers:
1. Device catalog management
2. Home & room setup
3. Room renaming
4. Impact calibration
5. RL environment setup and one interaction step
"""

from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from rl.rl_environment import SmartHomeEnv
from rl.rl_agent import RLAgent
import random

print("\n=== 🔧 STEP 1: DEVICE CATALOG TEST ===")
device_manager = DeviceManager()
all_devices = device_manager.get_all_devices()
print(f"Loaded {len(all_devices)} devices.")

# Add new permission test
device_manager.add_permission("Air Conditioning", "night_mode")

print("\n=== 🏠 STEP 2: HOME & ROOM MANAGEMENT TEST ===")
home_manager = HomeManager()

# Add new home
print(home_manager.add_home("Villa 12"))

# Add rooms
print(home_manager.add_room("Villa 12", "Living Room"))
print(home_manager.add_room("Villa 12", "Bedroom"))

# Rename room
print(home_manager.rename_room("Villa 12", "Living Room", "Main Hall"))

# Assign devices
print(home_manager.assign_device("Villa 12", "Main Hall", "Air Conditioning"))
print(home_manager.assign_device("Villa 12", "Bedroom", "Heater"))

# Check devices in the home
print("Home devices:", home_manager.get_home_devices("Villa 12"))

print("\n=== ⚙️ STEP 3: IMPACT CALIBRATION TEST ===")
calibrator = ImpactCalibrator()
impact_map = calibrator.calibrate()
print(f"Generated {len(impact_map)} impact keywords.")
print("Sample:", list(impact_map.items())[:5])

print("\n=== 🤖 STEP 4: SMART HOME ENVIRONMENT TEST ===")
env = SmartHomeEnv(home_name="Villa 12")
print(f"Environment initialized for 'Villa 12' with {len(env.action_space)} possible actions.")

state = env.reset()
action_idx = random.randint(0, len(env.action_space) - 1)
next_state, reward, done, info = env.step(action_idx)
print("Action executed:", info)
print("Next state:", next_state, "Reward:", reward)

print("\n=== 🧠 STEP 5: RL AGENT TEST ===")
agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))
action = agent.act(state)
print(f"Agent chose action index {action} — ({env.action_space[action]})")

print("\n✅ All components executed successfully.")
