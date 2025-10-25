from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

# === Import project modules ===
from device_manager import DeviceManager
from home_manager import HomeManager
from impact_calibrator import ImpactCalibrator
from rl.train_rl import train_rl_agent
from rl.rl_environment import SmartHomeEnv
from rl.rl_agent import RLAgent
from rl.weather import get_user_location, get_real_outdoor_temp
from training_kpi_logger import TrainingKPI
from lstm_predictor import LSTMPredictor
from paths import DATA_DIR, LOGS_DIR, MODELS_DIR

# === Initialize FastAPI app ===
app = FastAPI(title="AI Energy Optimization API")

# Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 🌍 SYSTEM INITIALIZATION ===
@app.get("/api/init")
def init_system():
    calibrator = ImpactCalibrator()
    calibrator.calibrate()
    devices = DeviceManager()
    homes = HomeManager()

    return {
        "message": "System initialized successfully",
        "devices_count": len(devices.get_all_devices()),
        "homes": homes.homes
    }


# === 🏠 HOME MANAGEMENT ===
@app.get("/api/homes")
def list_homes():
    manager = HomeManager()
    return manager.homes


@app.post("/api/homes/add")
def add_home(home_name: str = Body(...), comfort_range: tuple = Body((21, 25))):
    manager = HomeManager()
    return manager.add_home(home_name, comfort_range)


@app.post("/api/homes/delete")
def delete_home(home_name: str = Body(...)):
    manager = HomeManager()
    return manager.delete_home(home_name)


@app.post("/api/rooms/add")
def add_room(home_name: str = Body(...), room_name: str = Body(...)):
    manager = HomeManager()
    return manager.add_room(home_name, room_name)


@app.post("/api/rooms/rename")
def rename_room(home_name: str = Body(...), old_name: str = Body(...), new_name: str = Body(...)):
    manager = HomeManager()
    return manager.rename_room(home_name, old_name, new_name)


@app.post("/api/rooms/delete")
def delete_room(home_name: str = Body(...), room_name: str = Body(...)):
    manager = HomeManager()
    return manager.delete_room(home_name, room_name)


@app.post("/api/rooms/assign_device")
def assign_device(home_name: str = Body(...), room_name: str = Body(...), device_name: str = Body(...)):
    manager = HomeManager()
    return manager.assign_device(home_name, room_name, device_name)


# === ⚙️ DEVICE MANAGEMENT ===
@app.get("/api/devices")
def list_devices():
    manager = DeviceManager()
    return manager.get_all_devices()


@app.post("/api/devices/add")
def add_device(name: str = Body(...), base_kWh: float = Body(...), permissions: list = Body([])):
    manager = DeviceManager()
    return manager.add_device(name, base_kWh, permissions)


@app.post("/api/devices/permissions/add")
def add_permission(name: str = Body(...), permission: str = Body(...)):
    manager = DeviceManager()
    return manager.add_permission(name, permission)


# === 🌤️ WEATHER ===
@app.get("/api/weather")
def get_weather():
    loc = get_user_location()
    temp = get_real_outdoor_temp(loc["lat"], loc["lon"])
    return {
        "city": loc["city"],
        "country": loc["country"],
        "temperature": temp,
        "latitude": loc["lat"],
        "longitude": loc["lon"]
    }


# === 🤖 TRAINING ===
@app.post("/api/train")
def train_agent(home: str = Body(...), episodes: int = Body(50)):
    model_path = MODELS_DIR / f"checkpoints/{home.lower().replace(' ', '_')}_final.pth"
    result = train_rl_agent(HOME_NAME=home, NUM_EPISODES=episodes)
    return {
        "message": f"Training complete for home '{home}'",
        "model_path": str(model_path)
    }


# === ☀️ SIMULATION ===
@app.post("/api/simulate/day")
def simulate_day(home: str = Body(...)):
    env = SmartHomeEnv(home_name=home)
    model_path = MODELS_DIR / f"checkpoints/{home.lower().replace(' ', '_')}_final.pth"
    agent = RLAgent(state_size=env.state_size, action_size=len(env.action_space))

    agent.load_model(model_path)
    agent.epsilon = 0.0

    total_reward, total_energy, temps = 0, 0, []
    state = env.reset()
    for hour in range(24):
        action_idx = agent.act(state)
        next_state, reward, done, info = env.step(action_idx)
        total_reward += reward
        total_energy += info["energy_used"]
        temps.append(info["indoor_temp"])
        state = next_state
        if done:
            break

    return {
        "total_reward": total_reward,
        "total_energy_kWh": total_energy,
        "avg_temp": sum(temps) / len(temps),
        "comfort_range": [env.comfort_min, env.comfort_max]
    }


# === 📊 KPIS ===
@app.get("/api/kpis")
def get_kpi_summary():
    kpi_path = LOGS_DIR / "training_kpis.csv"
    if not kpi_path.exists():
        return {"error": "No KPI data found."}

    df = pd.read_csv(kpi_path)
    summary = {
        "episodes": len(df),
        "avg_reward": float(df["reward"].mean()),
        "avg_energy_kWh": float(df["total_energy_kWh"].mean()),
        "avg_temp": float(df["avg_temp"].mean()),
        "final_epsilon": float(df["epsilon"].iloc[-1]),
    }
    return summary


@app.get("/api/kpis/full")
def get_full_kpi_log():
    kpi_path = LOGS_DIR / "training_kpis.csv"
    if not kpi_path.exists():
        return {"error": "No KPI file found."}
    return pd.read_csv(kpi_path).to_dict(orient="records")
