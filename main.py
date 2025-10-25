"""
AI Energy Optimization — Full System Pipeline
Author: Abdulrahman Alamoudi
"""

import os
import time
from pathlib import Path
from impact_calibrator import ImpactCalibrator
from device_manager import DeviceManager
from home_manager import HomeManager
from lstm_predictor import LSTMPredictor
from rl.rl_environment import SmartHomeEnv
from rl.rl_agent import RLAgent
from training_kpi_logger import TrainingKPI
from rl.train_rl import train_rl_agent
from paths import DATA_DIR, MODELS_DIR, LOGS_DIR


def initialize_system():
    """Ensure directories, calibrations, and base setup."""
    print("=== ⚙️ INITIALIZING PROJECT STRUCTURE ===")

    for d in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"📂 Verified: {d}")

    device_manager = DeviceManager()
    home_manager = HomeManager()
    calibrator = ImpactCalibrator()

    # Run impact calibration once
    impact_path = DATA_DIR / "impact_map.json"
    if not impact_path.exists():
        print("⚙️ Generating new impact map...")
        calibrator.calibrate()
    else:
        print("✅ Existing impact map found.")

    return device_manager, home_manager, calibrator


def setup_home(home_manager: HomeManager):
    """Create default home if not exists."""
    home_name = "Villa 88"
    if home_name not in home_manager.homes:
        print(f"🏡 Creating new home '{home_name}'...")
        home_manager.add_home(home_name, comfort_range=(22, 26))
        home_manager.add_room(home_name, "Living Room")
        home_manager.add_room(home_name, "Kitchen")
        home_manager.assign_device(home_name, "Living Room", "Air Conditioning")
        home_manager.assign_device(home_name, "Living Room", "Tv")
        home_manager.assign_device(home_name, "Kitchen", "Fridge")
        home_manager.assign_device(home_name, "Kitchen", "Oven")
    else:
        print(f"✅ Home '{home_name}' already exists.")
    print(f"🏠 Home configuration:\n{home_manager.homes[home_name]}")
    return home_name


def evaluate_trained_agent(home_name):
    """Run a 24-hour simulation using trained model."""
    print("\n=== ☀️ 24-HOUR SIMULATION ===")
    env = SmartHomeEnv(home_name=home_name)
    agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))
    model_path = MODELS_DIR / "checkpoints/final_agent_model.pth"

    agent.load_model(model_path)
    agent.epsilon = 0.0  # deterministic actions
    state = env.reset()

    total_reward, total_energy = 0, 0
    temps = []

    for hour in range(24):
        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)
        total_reward += reward
        total_energy += info["energy_used"]
        temps.append(info["indoor_temp"])

        print(f"[Hour {hour + 1:02d}] {info['device']} → {info['action']} | "
              f"Energy: {info['energy_used']:.3f} kWh | Temp: {info['indoor_temp']:.2f}°C | Reward: {reward:.3f}")

        state = next_state
        if done:
            break

    print("\n=== 📊 SUMMARY ===")
    print(f"Total Reward: {total_reward:.3f}")
    print(f"Total Energy Used: {total_energy:.3f} kWh")
    print(f"Average Temperature: {sum(temps) / len(temps):.2f}°C")
    print(f"Comfort Range: {env.comfort_min}-{env.comfort_max}°C")


def run_live_agent(home_name):
    env = SmartHomeEnv(home_name)
    lstm = LSTMPredictor("models/lstm_model.pth")
    agent = RLAgent(state_size=4, action_size=len(env.action_space))
    agent.load_model("models/checkpoints/final_agent_model.pth")
    agent.epsilon = 0.0  # deterministic actions

    for hour in range(24):
        # Collect sensor data
        indoor_temp = env.indoor_temp
        outdoor_temp = ...  # from weather API
        total_kWh = env.total_kWh

        # Predict next state
        predicted_kWh, predicted_temp = lstm.predict([
            indoor_temp, total_kWh, outdoor_temp, hour
        ])

        state = [indoor_temp, total_kWh, predicted_temp, predicted_kWh]
        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)

        print(f"[{hour + 1:02d}] {info['device']} → {info['action']} | "
              f"Temp: {info['indoor_temp']:.2f}°C | kWh: {info['energy_used']:.2f} | Reward: {reward:.2f}")

        time.sleep(1)  # simulate 1-hour delay (real-time mode)


def main():
    # 1️⃣ Setup environment
    device_manager, home_manager, calibrator = initialize_system()

    # 2️⃣ Ensure at least one home exists
    home_name = setup_home(home_manager)

    # 3️⃣ Train RL Agent
    print("\n=== 🧠 TRAINING RL AGENT ===")
    train_rl_agent(HOME_NAME=home_name, NUM_EPISODES=50, MAX_STEPS_PER_EPISODE=24)

    # 4️⃣ Evaluate performance
    evaluate_trained_agent(home_name)


if __name__ == "__main__":
    main()
