import torch
import numpy as np


class LSTMPredictor:
    def __init__(self, model_path=None, device="cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        if model_path:
            self.load_model(model_path)

    def load_model(self, path):
        self.model = torch.load(path, map_location=self.device)
        self.model.eval()
        print(f"✅ LSTM model loaded from: {path}")

    def predict(self, features):
        """
        features: list or np.array → [outdoor_temp, hour, season, device_usage...]
        returns (predicted_kWh, predicted_indoor_temp)
        """
        if self.model is None:
            raise RuntimeError("⚠️ LSTM model not loaded yet.")

        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            y = self.model(x).cpu().numpy().flatten()

        predicted_kWh, predicted_temp = y[0], y[1]
        return float(predicted_kWh), float(predicted_temp)
