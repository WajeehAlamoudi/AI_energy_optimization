"""
====================================================
🏠 AI Energy Optimization - End-to-End Simulator
====================================================
Simulates a full user experience:
1️⃣ Setup (homes, rooms, devices)
2️⃣ Weather + Environment auto-init
3️⃣ Train RL Agent (short demo)
4️⃣ Run live 24-hour simulation
====================================================
"""

import time
from home_manager import HomeManager
from paths import MODELS_DIR
from rl.rl_environment import SmartHomeEnv
from rl.rl_agent import RLAgent
from pathlib import Path

from training_kpi_logger import TrainingKPI

# =====================================================
# STEP 1️⃣: SETUP HOMES / ROOMS / DEVICES
# =====================================================
print("\n=== 🏗️ INITIAL SETUP ===")
home_manager = HomeManager()

home_name = "Villa 12"
home_manager.add_home(home_name)
home_manager.add_room(home_name, "Living Room")
home_manager.add_room(home_name, "Kitchen")

# Assign example devices (from catalog)
home_manager.assign_device(home_name, "Living Room", "Air Conditioning")
home_manager.assign_device(home_name, "Living Room", "TV")
home_manager.assign_device(home_name, "Kitchen", "Fridge")
home_manager.assign_device(home_name, "Kitchen", "Oven")

print("\n✅ Home setup completed.")
print(home_manager.homes)

# =====================================================
# STEP 2️⃣: AUTO LOCATION + ENVIRONMENT
# =====================================================
print("\n=== 🌍 INITIALIZING ENVIRONMENT ===")
env = SmartHomeEnv(home_name=home_name, mode="real")
print(f"📍 City: {env.city}, Country: {env.country}")
print(f"🌡️ Outdoor Temperature: {env.outdoor_temp:.2f}°C")

# =====================================================
# STEP 3️⃣: TRAIN RL AGENT (SHORT TEST)
# =====================================================
print("\n=== 🧠 TRAINING RL AGENT (DEMO MODE) ===")
agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))
tracker = TrainingKPI()

NUM_EPISODES = 5
MAX_STEPS_PER_EPISODE = 24

for episode in range(1, NUM_EPISODES + 1):
    state = env.reset()
    total_reward, total_energy = 0, 0
    temps = []

    for step in range(MAX_STEPS_PER_EPISODE):
        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)
        agent.remember(state, action_idx, reward, next_state, done)
        agent.replay(batch_size=16)
        total_reward += reward
        total_energy += info["energy_used"]
        temps.append(info["indoor_temp"])
        state = next_state
        if done:
            break

    tracker.log(
        episode=episode,
        reward=float(total_reward),
        total_energy=float(total_energy),
        avg_temp=float(sum(temps)/len(temps)),
        epsilon=float(agent.epsilon)
    )

    print(f"Episode {episode}: Reward={total_reward:.2f}, Energy={total_energy:.2f} kWh")

# Save trained model
save_path = MODELS_DIR / "checkpoints/final_agent_model.pth"
agent.save_model(save_path)

print("\n✅ RL Training Completed.")

# =====================================================
# STEP 4️⃣: LIVE 24-HOUR SIMULATION
# =====================================================
print("\n=== ☀️ LIVE 24-HOUR SIMULATION ===")
agent.epsilon = 0.0
state = env.reset()
total_reward, total_energy = 0, 0
temps = []

for hour in range(24):
    action_idx = agent.act(state)
    next_state, reward, done, info = env.step(action_idx)
    total_reward += reward
    total_energy += info["energy_used"]
    temps.append(info["indoor_temp"])
    print(f"[Hour {hour+1:02d}] {info['device']} → {info['action']} | "
          f"Energy: {info['energy_used']:.3f} kWh | Temp: {info['indoor_temp']:.2f}°C | Reward: {reward:.3f}")
    state = next_state
    if done:
        break

print("\n=== 📊 FINAL SUMMARY ===")
print(f"Total Reward: {total_reward:.2f}")
print(f"Total Energy: {total_energy:.2f} kWh")
print(f"Average Temp: {sum(temps)/len(temps):.2f}°C")
print(f"Comfort Range: {env.comfort_min}-{env.comfort_max}°C")

print("\n✅ Simulation Completed Successfully.")
