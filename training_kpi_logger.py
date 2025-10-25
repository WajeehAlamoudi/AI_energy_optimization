import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from paths import LOGS_DIR


class TrainingKPI:
    def __init__(self, csv_path: Path = LOGS_DIR / "training_kpis.csv"):

        self.csv_path = Path(csv_path)
        self.plots_dir = Path(LOGS_DIR)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

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

        plt.title("Training KPIs Over Episodes")
        plt.xlabel("Episode")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # === Save ===
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_path = self.plots_dir / f"kpi_plot_{timestamp}.png"
            pdf_path = self.plots_dir / f"kpi_plot_{timestamp}.pdf"
            plt.savefig(png_path)
            plt.savefig(pdf_path)
            print(f"📊 KPI plot saved → {png_path.name} and {pdf_path.name}")

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
