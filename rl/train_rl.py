import os
import random
import numpy as np
from pathlib import Path
from tqdm import tqdm

from rl.rl_agent import RLAgent
from rl.rl_environment import SmartHomeEnv
from training_kpi_logger import TrainingKPI
from lstm_predictor import LSTMPredictor
from paths import MODELS_DIR


# === CONFIGURATION ===
# NUM_EPISODES = 50 # simulate 50 days of RL training
# MAX_STEPS_PER_EPISODE = 24 # each = 24 hours
# SAVE_EVERY = 10 # save model every 10 episodes
#

def train_rl_agent(HOME_NAME="Default", NUM_EPISODES=50, MAX_STEPS_PER_EPISODE=24, SAVE_EVERY=10):
    print("=== 🏠 INITIALIZING ENVIRONMENT ===")
    env = SmartHomeEnv(home_name=HOME_NAME)
    action_size = len(env.action_space)

    lstm_path = MODELS_DIR / "lstm_model.pth"
    lstm = None
    if lstm_path.exists():
        print(f"✅ Found LSTM model at: {lstm_path}")
        lstm = LSTMPredictor(model_path=lstm_path)
        state_size = 4  # [current_temp, total_kWh, predicted_temp, predicted_kWh]
    else:
        print("⚠️ No LSTM model found. Using simulated state only.")
        state_size = env.state_size  # fallback: 2 features

    print(f"Environment ready → {action_size} actions, state size {state_size}")

    print("=== 🤖 INITIALIZING AGENT ===")
    agent = RLAgent(state_size=state_size, action_size=action_size)
    agent.load_model(MODELS_DIR / "checkpoints/final_agent_model.pth")

    tracker = TrainingKPI(home_name=HOME_NAME)
    print("📊 KPI Logger ready.\n")

    # === TRAINING LOOP ===
    for episode in tqdm(range(1, NUM_EPISODES + 1), desc="Training Progress", ncols=100):
        state = env.reset()
        total_reward = 0.0
        total_energy = 0.0
        total_loss = 0.0

        temps = []

        for step in range(MAX_STEPS_PER_EPISODE):
            if lstm:
                # 1️⃣ Prepare input for LSTM (features)
                lstm_input = []
                # LSTM predicts the next indoor temperature and kWh
                predicted_kWh, predicted_temp = lstm.predict(lstm_input)

                # Combine current & forecasted values
                state_input = np.array([
                    env.indoor_temp,  # current indoor temp
                    env.total_kWh,  # current energy used so far
                    predicted_temp,  # next predicted indoor temp
                    predicted_kWh  # next predicted kWh
                ], dtype=np.float32)
            else:
                # fallback if no LSTM
                state_input = state

            loss_value = agent.replay(batch_size=32)
            total_loss += float(loss_value)
            # Choose action
            action_idx = agent.act(state_input)
            next_state, reward, done, info = env.step(action_idx)

            # Store experience
            agent.remember(state, action_idx, reward, next_state, done)

            # Training step
            agent.replay(batch_size=32)

            # Accumulate metrics
            total_reward += reward
            total_energy += info["energy_used"]
            temps.append(info["indoor_temp"])

            state = next_state
            if done:
                break

        avg_temp = np.mean(temps)
        comfort_min, comfort_max = env.comfort_min, env.comfort_max
        comfort_violation = np.mean([
            abs(t - np.clip(t, comfort_min, comfort_max)) for t in temps
        ])

        # === LOG KPIs ===
        avg_loss = total_loss / MAX_STEPS_PER_EPISODE
        tracker.log(
            episode=int(episode),
            reward=float(total_reward),
            total_energy=float(total_energy),
            avg_temp=float(avg_temp),
            epsilon=float(agent.epsilon),
            comfort_violation=float(comfort_violation),
            loss=float(avg_loss)
        )

        print(f"\n📅 Episode {episode:03d} finished:")
        print(f"   Total Reward     : {total_reward:.3f}")
        print(f"   Total Energy (kWh): {total_energy:.3f}")
        print(f"   Avg Temp (°C)    : {avg_temp:.2f}")
        print(f"   Epsilon          : {agent.epsilon:.3f}")

        # === SAVE CHECKPOINT ===
        if episode % SAVE_EVERY == 0:
            save_path = MODELS_DIR / f"checkpoints/{HOME_NAME.lower().replace(' ', '_')}_ep{episode:03d}.pth"
            agent.save_model(save_path)

    # === FINALIZE ===
    final_path = MODELS_DIR / f"checkpoints/{HOME_NAME.lower().replace(' ', '_')}_final.pth"
    agent.save_model(final_path)
    tracker.plot(save=True, show=False)
    tracker.summary(last_n=10)

    print("\n=== ✅ TRAINING COMPLETE ===")
    print(f"Model saved → {MODELS_DIR / f'checkpoints/{HOME_NAME}_final_agent_model.pth'}")
    print(f"KPI log → {tracker.csv_path}")
    print(f"Plots → {tracker.plots_dir}")
