import os

import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from paths import MODELS_DIR


class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.fc(x)


class RLAgent:
    def __init__(self, state_size, action_size):
        self.model = DQN(state_size, action_size)
        self.memory = deque(maxlen=2000)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.1

    def save_model(self, path=MODELS_DIR / "checkpoints/agent_model.pth"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"✅ Model saved to: {path}")

    def load_model(self, path):
        if not os.path.exists(path):
            print(f"⚠️ No model found for this home at: {path}")
            print("➡️ Starting training from scratch.")
            return

        try:
            state_dict = torch.load(path, weights_only=True)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            print(f"📦 Model loaded successfully from: {path}")
        except RuntimeError as e:
            print(f"⚠️ Model mismatch or outdated checkpoint: {e}")
            print("🔄 Resetting model weights for new architecture...")
            self.model.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.model.fc[-1].out_features)
        q_values = self.model(torch.FloatTensor(state))
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return 0.0  # no training yet

        batch = random.sample(self.memory, batch_size)
        total_loss = 0.0

        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                target += self.gamma * torch.max(self.model(torch.FloatTensor(next_state))).item()

            current = self.model(torch.FloatTensor(state))[action]
            loss = self.criterion(current, torch.tensor(target, dtype=torch.float32))
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # ✅ Return average loss for KPI tracking
        return total_loss / batch_size
