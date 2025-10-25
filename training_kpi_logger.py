import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from paths import LOGS_DIR


class TrainingKPI:
    def __init__(self, home_name):
        self.home_name = home_name.strip().title().replace(" ", "_")
        self.home_log_dir = LOGS_DIR / self.home_name
        self.home_log_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.home_log_dir / "training_kpis.csv"
        self.plots_dir = self.home_log_dir

        # Create header if not exist
        if not self.csv_path.exists():
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "episode", "reward", "total_energy_kWh",
                    "avg_temp", "epsilon", "comfort_violation", "loss"
                ])

    def log(
            self,
            episode: int,
            reward: float,
            total_energy: float,
            avg_temp: float,
            epsilon: float,
            comfort_violation: float = 0.0,
            loss: float = None,
    ):
        """Log one episode of training progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, episode, reward, total_energy,
                avg_temp, epsilon, comfort_violation, loss or 0.0
            ])

    def plot(self, save=True, show=True):
        """Visualize and optionally save the reward, epsilon, and energy trends"""
        df = pd.read_csv(self.csv_path)

        plt.figure(figsize=(10, 5))
        plt.plot(df["episode"], df["reward"], label="Reward", color="blue", linewidth=2)
        plt.plot(df["episode"], df["total_energy_kWh"], label="Energy (kWh)", color="orange", linewidth=1.5)
        plt.plot(df["episode"], df["epsilon"], label="Epsilon", color="green", linestyle="--")

        plt.title(f"Training KPIs - {self.home_name}")
        plt.xlabel("Episode")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_path = self.plots_dir / f"{self.home_name}_kpi_{timestamp}.png"
            pdf_path = self.plots_dir / f"{self.home_name}_kpi_{timestamp}.pdf"
            plt.savefig(png_path)
            plt.savefig(pdf_path)
            print(f"📊 KPI plot saved → {png_path.name}, {pdf_path.name}")

        if show:
            plt.show()
        else:
            plt.close()

    def summary(self, last_n=10):
        """Print recent episode stats"""
        df = pd.read_csv(self.csv_path)
        recent = df.tail(last_n)
        print(f"=== 📈 Last {last_n} Episodes Summary ===")
        print(recent[["episode", "reward", "total_energy_kWh", "avg_temp", "epsilon"]].to_string(index=False))
