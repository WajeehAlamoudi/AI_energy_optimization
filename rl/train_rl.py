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


# Notes (high level):
# - Each episode = one simulated day (MAX_STEPS_PER_EPISODE hours)
# - State is either:
#   * 2 features: [indoor_temp, total_kWh]  (no predictor)
#   * 4 features: [indoor_temp, total_kWh, predicted_temp, predicted_kWh] (with predictor)
# - KPIs are logged each episode, and model checkpoints saved every SAVE_EVERY episodes

def train_rl_agent(HOME_NAME="Default", NUM_EPISODES=50, MAX_STEPS_PER_EPISODE=24, SAVE_EVERY=10):
    # ---------- Environment ----------
    print(f"[INFO] | === INITIALIZING ENVIRONMENT ===")
    env = SmartHomeEnv(home_name=HOME_NAME)
    action_size = len(env.action_space)

    #  Optional Predictor
    # If model file exists, we extend the state with predicted values (kept exactly as your code).
    lstm_path = MODELS_DIR / "multioutput_xgb_model.pkl"
    if lstm_path.exists():
        print(f"[INFO] | Found LSTM model at: {lstm_path}")
        lstm = LSTMPredictor(model_path=lstm_path)
        state_size = 4
    else:
        print(f"[WARN] | No LSTM model found. Using simulated state only.")
        lstm = None
        state_size = env.state_size

    print(f"[INFO] | Environment ready -> {action_size} actions, state size {state_size}")

    #  Agent + KPI Logger
    print(f"[INFO] | === INITIALIZING AGENT ===")
    agent = RLAgent(state_size=state_size, action_size=action_size)
    agent.load_model(MODELS_DIR / f"checkpoints/{HOME_NAME.lower()}_final.pth")

    tracker = TrainingKPI(home_name=HOME_NAME)
    print(f"[INFO] | KPI Logger ready.\n")

    #  Training Loop
    for episode in tqdm(range(1, NUM_EPISODES + 1), desc="Training Progress", ncols=100):
        # Reset for new episode/day
        state = env.reset()

        # Episode accumulators
        total_reward = 0.0
        total_energy = 0.0
        total_loss = 0.0
        temps = []  # for comfort metrics

        for step in range(MAX_STEPS_PER_EPISODE):
            # Build input state for the agent
            if lstm:
                # lstm_input is intentionally left as-is (you define it in your pipeline)
                predicted_kWh, predicted_temp = lstm.predict(lstm_input)
                state_input = np.array([
                    env.indoor_temp,
                    env.total_kWh,
                    predicted_temp,
                    predicted_kWh
                ], dtype=np.float32)
            else:
                state_input = state

            # Track loss (if replay returns 0.0 early, that's fine)
            loss_value = agent.replay(batch_size=32)
            total_loss += float(loss_value)

            # Act -> Step -> Store -> Train
            action_idx = agent.act(state_input)
            next_state, reward, done, info = env.step(action_idx)

            agent.remember(state, action_idx, reward, next_state, done)
            agent.replay(batch_size=32)

            # Collect metrics
            total_reward += reward
            total_energy += info["energy_used"]
            temps.append(info["indoor_temp"])

            state = next_state
            if done:
                break

        # Episode Metrics
        avg_temp = np.mean(temps)
        comfort_min, comfort_max = env.comfort_min, env.comfort_max
        comfort_violation = np.mean([
            abs(t - np.clip(t, comfort_min, comfort_max)) for t in temps
        ])

        #  KPI Logging
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

        #  Console Summary
        print(f"\n[INFO] | Episode {episode:03d} finished:")
        print(f"[INFO] | Total Reward      : {total_reward:.3f}")
        print(f"[INFO] | Total Energy (kWh): {total_energy:.3f}")
        print(f"[INFO] | Avg Temp (°C)     : {avg_temp:.2f}")
        print(f"[INFO] | Epsilon           : {agent.epsilon:.3f}")

        #  Checkpointing
        if episode % SAVE_EVERY == 0:
            save_path = MODELS_DIR / f"checkpoints/{HOME_NAME.lower().replace(' ', '_')}_ep{episode:03d}.pth"
            agent.save_model(save_path)

    #  Finalize
    final_path = MODELS_DIR / f"checkpoints/{HOME_NAME.lower().replace(' ', '_')}_final.pth"
    agent.save_model(final_path)

    tracker.plot(save=True, show=False)
    tracker.summary(last_n=10)

    print(f"\n[INFO] | === TRAINING COMPLETE ===")
    print(f"[INFO] | Model saved -> {MODELS_DIR / f'checkpoints/{HOME_NAME}_final_agent_model.pth'}")
    print(f"[INFO] | KPI log -> {tracker.csv_path}")
    print(f"[INFO] | Plots -> {tracker.plots_dir}")
