import json
import time
import numpy as np

from paths import MODELS_DIR, LOGS_DIR
from rl.rl_agent import RLAgent
from datetime import datetime

from rl.rl_environment import SmartHomeEnv


def run_live_agent(home_name="Default", interval_sec=60, continuous=True):
    """
    Run the RL agent in real time (continuous loop) and log each step for dashboard display.
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

    agent.epsilon = 0.0
    state = env.reset()

    step = 0
    total_reward = 0
    total_energy = 0
    history = []

    log_path = LOGS_DIR / home_name / f"{home_name.lower().replace(' ', '_')}_live_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    while True:
        step += 1
        now = datetime.now()
        print(f"\n⏱️ [{now.strftime('%H:%M:%S')}] STEP {step}")

        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)

        total_reward += reward
        total_energy += info["energy_used"]

        # === Calculate comfort violation ===
        comfort_violation = 0.0
        # MODIFIED: Added None-safety checks for sensor values
        # Prevents "unsupported operand type(s) for -: 'float' and 'NoneType'" errors
        # Sensor failures can return None values, so we provide safe fallback defaults
        comfort_min = env.comfort_min if env.comfort_min is not None else 20
        comfort_max = env.comfort_max if env.comfort_max is not None else 27
        indoor_temp = info["indoor_temp"] if info["indoor_temp"] is not None else 23
        
        if not (comfort_min <= indoor_temp <= comfort_max):
            comfort_violation = abs(indoor_temp - np.mean([comfort_min, comfort_max]))

        # === Structure full record ===
        record = {
            "timestamp": now.isoformat(),
            "home": home_name,
            "step": step,
            "device": info["device"],
            "action": info["action"],
            "indoor_temp": round(indoor_temp, 2),
            "outdoor_temp": round(env.outdoor_temp if env.outdoor_temp else 20, 2),
            "energy_used": round(info["energy_used"], 3),
            "total_energy": round(total_energy, 3),
            "reward": round(reward, 3),
            "total_reward": round(total_reward, 3),
            "comfort_range": [comfort_min, comfort_max],
            "comfort_violation": round(comfort_violation, 3),
            "model": model_path.name if model_path.exists() else "untrained"
        }

        history.append(record)

        # === Print nicely ===
        print(f" → Action: {info['device']} / {info['action']}")
        outer_temp = env.outdoor_temp if env.outdoor_temp else 20
        print(f" → Indoor: {indoor_temp:.2f}°C | Outdoor: {outer_temp:.2f}°C")
        print(f" → Energy: {info['energy_used']:.3f} kWh | Reward: {reward:.3f}")
        print(f" → Total Energy Used: {total_energy:.3f} kWh")

        # === Save JSON snapshot for dashboard ===
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump({
                "home": home_name,
                "last_update": now.isoformat(),
                "total_reward": total_reward,
                "total_energy": total_energy,
                "steps": history[-50:]  # keep last 50 steps
            }, f, indent=2)

        # Wait and update state
        time.sleep(interval_sec)
        state = next_state

        if not continuous and step >= 24:
            break
