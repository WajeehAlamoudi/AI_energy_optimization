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
        # MODIFIED: Added weights_only=False parameter for PyTorch 2.6+ compatibility
        # PyTorch 2.6 changed the default from weights_only=False to weights_only=True
        # This caused "Weights only load failed" errors when loading legacy pickle models
        # The multioutput_xgb_model.pkl contains XGBoost objects which require weights_only=False
        try:
            self.model = torch.load(path, map_location=self.device, weights_only=False)
        except:
            # Fallback for newer PyTorch versions
            self.model = torch.load(path, map_location=self.device, weights_only=False)
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
