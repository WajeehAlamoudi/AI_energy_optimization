import os
import random
from collections import deque
from datetime import datetime
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim

from paths import MODELS_DIR


# Logging (consistent format)
LEVEL_WIDTH = 5  # INFO, ERROR, WARN, DEBUG


def log(level: str, msg: str) -> None:
    """
    Simple console logger with fixed format.
    Example:
      [2025-12-20 04:12:33] [INFO ] | Model saved to: ...
    """
    level = (level or "INFO").upper()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level:<{LEVEL_WIDTH}}] | {msg}")

# Deep Q-Network (DQN)
class DQN(nn.Module):
    """
    Simple fully-connected network that maps state -> Q-values over actions.
    """

    def __init__(self, state_size: int, action_size: int):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: returns Q-values for each action.
        """
        return self.fc(x)

# RL Agent (DQN-based)
class RLAgent:
    """
    DQN agent with experience replay and epsilon-greedy exploration.
    """

    def __init__(self, state_size: int, action_size: int):
        # Q-network
        self.model = DQN(state_size, action_size)

        # Replay buffer
        self.memory = deque(maxlen=2000)

        # Training components
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        # RL hyperparameters
        self.gamma = 0.95  # discount factor

        # Exploration schedule
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.1

        # Keep action_size for safe random action sampling
        self.action_size = action_size

    def save_model(self, path: Path = MODELS_DIR / "checkpoints/agent_model.pth") -> None:
        """
        Save model weights (state_dict) to disk.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
        log("INFO", f"Model saved to: {path}")

    def load_model(self, path: Path) -> None:
        """
        Load model weights from disk.
        - If file doesn't exist: training from scratch.
        - If architecture mismatch: re-init weights to avoid crashing.
        """
        path = Path(path)

        if not path.exists():
            log("WARN", f"No model found at: {path}")
            log("INFO", "Starting training from scratch.")
            return

        try:
            # weights_only=True requires newer PyTorch. If it fails, fallback to normal load.
            try:
                state_dict = torch.load(path, weights_only=True)
            except TypeError:
                state_dict = torch.load(path)

            self.model.load_state_dict(state_dict)
            self.model.eval()
            log("INFO", f"Model loaded successfully from: {path}")

        except RuntimeError as e:
            log("WARN", f"Checkpoint mismatch/outdated: {e}")
            log("INFO", "Resetting model weights for new architecture.")
            self.model.apply(self._init_weights)

    @staticmethod
    def _init_weights(m: nn.Module) -> None:
        """
        Initialize Linear layers with Xavier for stable training.
        """
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def act(self, state) -> int:
        """
        Choose action using epsilon-greedy:
        - With probability epsilon: random action.
        - Otherwise: argmax Q(state).
        """
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)

        with torch.no_grad():
            state_t = torch.as_tensor(state, dtype=torch.float32)
            q_values = self.model(state_t)
            return int(torch.argmax(q_values).item())

    def remember(self, state, action: int, reward: float, next_state, done: bool) -> None:
        """
        Store a transition in replay buffer.
        """
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size: int = 32) -> float:
        """
        Train on a random minibatch from replay buffer.
        Returns average loss for KPI tracking.
        """
        if len(self.memory) < batch_size:
            return 0.0  # not enough samples yet

        batch = random.sample(self.memory, batch_size)
        total_loss = 0.0

        for state, action, reward, next_state, done in batch:
            # Compute target: r + gamma*max(Q(next_state)) if not terminal
            target = float(reward)
            if not done:
                with torch.no_grad():
                    next_q = self.model(torch.as_tensor(next_state, dtype=torch.float32))
                    target += self.gamma * float(torch.max(next_q).item())

            # Predicted Q for the taken action
            q_values = self.model(torch.as_tensor(state, dtype=torch.float32))
            current = q_values[action]

            # MSE loss between predicted Q and target Q
            loss = self.criterion(current, torch.tensor(target, dtype=torch.float32))

            # Backprop step
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            total_loss += float(loss.item())

        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return total_loss / batch_size
