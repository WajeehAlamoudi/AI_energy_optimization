# AI Energy Optimization (Smart Home RL Controller)

A smart-home energy optimization system that learns how to control devices (AC/heater/lights/etc.) to reduce energy usage while keeping indoor temperature within a comfort range.

---

## 1) Features
- Home/room/device management (add, delete, rename, assign devices)
- Automatic impact calibration (builds impact map from permission keywords)
- Smart home simulation environment (safe training/testing)
- Optional real-mode hooks (weather/location APIs + sensor placeholders)
- RL training (DQN) with checkpoints
- KPI logging (CSV + plots)
- Live optimizer loop that writes JSON snapshots for dashboards
- FastAPI endpoints for managing and running the system

---

## 2) Project Structure
AI_energy_optimization/
├─ raw_data/
│ └─ rl/
│ ├─ rl_agent.py
│ ├─ rl_environment.py
│ ├─ rl_utils.py
│ └─ train_rl.py
├─ static/
├─ app.py
├─ device_manager.py
├─ home_manager.py
├─ impact_calibrator.py
├─ lstm_predictor.py
├─ main.py
├─ paths.py
├─ training_kpi_logger.py
├─ test.py
└─ README.md

---

## Main Components
- **FastAPI Server (`app.py`)**: API endpoints for initialization, home/device management, training, simulation, KPIs, and live optimizer control.
- **Device Manager (`device_manager.py`)**: Loads/saves `devices_catalog.json`, manages devices/permissions, triggers recalibration.
- **Home Manager (`home_manager.py`)**: Loads/saves `homes.json`, manages homes/rooms/device assignment.
- **Impact Calibrator (`impact_calibrator.py`)**: Generates `impact_map.json` from permission keywords (energy_factor + temp_change).
- **Environment (`raw_data/rl/rl_environment.py`)**: SmartHomeEnv simulation with reward function combining energy + comfort.
- **RL Agent (`raw_data/rl/rl_agent.py`)**: DQN agent with replay buffer, epsilon-greedy, save/load checkpoints.
- **Training (`raw_data/rl/train_rl.py`)**: Episodic training loop (24 steps = 1 simulated day), checkpointing, KPI logging.
- **KPI Logger (`training_kpi_logger.py`)**: Writes training KPIs to CSV and generates plots.
- **Live Agent (`main.py`)**: Runs the trained policy in a loop and writes a rolling JSON log for dashboards.

---

## Data & Outputs
### Data files (created/used)
- `data/devices_catalog.json` — device catalog with `base_kWh` and `permissions`
- `data/homes.json` — home structure with comfort range, rooms, and devices
- `data/impact_map.json` — auto-generated impact map (keyword → energy_factor/temp_change)

### Outputs
- `models/checkpoints/` — saved models: `<home>_ep###.pth` and `<home>_final.pth`
- `logs/<HOME_NAME>/training_kpis.csv` — KPI history
- `logs/<HOME_NAME>/*.png` — KPI plots
- `logs/<HOME_NAME>/<home>_live_log.json` — live optimizer log (rolling window)

---

## Requirements
- Python 3.9+ recommended
- Packages:
  - `fastapi`, `uvicorn`
  - `torch`
  - `numpy`, `pandas`, `matplotlib`
  - `requests`, `tqdm`

---

## Installation (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi uvicorn torch numpy pandas matplotlib requests tqdm
