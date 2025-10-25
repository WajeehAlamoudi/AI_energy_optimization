import time
import numpy as np

from paths import MODELS_DIR
from rl.rl_agent import RLAgent
from datetime import datetime

from rl.rl_environment import SmartHomeEnv


def run_live_agent(home_name="Default", interval_sec=60, continuous=True):
    """
    Run the RL agent in real time (continuous loop).
    interval_sec = how long to wait between actions (e.g. 3600 for 1h, or 10 for quick test)
    continuous = True keeps looping forever, False stops after 24 steps
    """
    print(f"\n=== 🏡 STARTING LIVE AGENT FOR: {home_name} ===")
    env = SmartHomeEnv(home_name=home_name)

    model_path = MODELS_DIR / f"checkpoints/{home_name.lower().replace(' ', '_')}_final.pth"
    agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))

    if model_path.exists():
        agent.load_model(model_path)
        print(f"✅ Loaded trained model for {home_name}")
    else:
        print(f"⚠️ No trained model found → starting with random policy")

    agent.epsilon = 0.0  # deterministic actions
    state = env.reset()

    step = 0
    total_reward = 0
    total_energy = 0

    while True:
        step += 1
        print(f"\n⏱️ [{datetime.now().strftime('%H:%M:%S')}] STEP {step}")

        # 1️⃣ Get current sensor readings
        current_temp = env.indoor_temp
        outdoor_temp = env.outdoor_temp

        # 2️⃣ Agent decides the best action
        action_idx = agent.act(state)

        # 3️⃣ Apply action in environment
        next_state, reward, done, info = env.step(action_idx)

        # 4️⃣ Log results
        total_reward += reward
        total_energy += info["energy_used"]
        print(f" → Action: {info['device']} / {info['action']}")
        print(f" → Indoor: {info['indoor_temp']:.2f}°C | Outdoor: {outdoor_temp:.2f}°C")
        print(f" → Energy: {info['energy_used']:.3f} kWh | Reward: {reward:.3f}")
        print(f" → Total Energy Used: {total_energy:.3f} kWh")

        # 5️⃣ Wait for next control interval
        time.sleep(interval_sec)

        # 6️⃣ Update state
        state = next_state

        # Stop after 24 steps unless continuous mode
        if not continuous and step >= 24:
            break

