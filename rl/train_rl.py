from rl_environment import SmartHomeEnv
from rl_agent import RLAgent
import numpy as np

env = SmartHomeEnv()
agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))

EPISODES = 200

for e in range(EPISODES):
    state = env.reset()
    total_reward = 0

    while True:
        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)
        agent.remember(state, action_idx, reward, next_state, done)
        agent.replay()
        state = next_state
        total_reward += reward
        if done:
            print(f"Episode {e+1}/{EPISODES}, Total Reward: {round(total_reward, 3)}")
            break
