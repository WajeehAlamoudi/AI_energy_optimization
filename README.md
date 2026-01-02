```bash
# AI Energy Optimization – Smart Home RL Controller

A simulation-based AI system that controls smart-home devices (HVAC, lighting, etc.) to **reduce energy consumption** while keeping **indoor comfort** inside a target range.  
The project combines **machine learning prediction**, **reinforcement learning control**, and a **web dashboard** to monitor devices, energy use, and model performance.

---

## 1. Project Overview

This project implements a complete pipeline for **AI-driven energy management** in a virtual smart home.

- It simulates one or more homes, each with **rooms**, **devices**, and a **comfort range**.
- A **device catalog** defines the base energy usage and control permissions for typical home appliances.
- A **calibration module** converts human-readable permissions (e.g. `set_low`, `eco_mode`) into numeric energy/temperature impacts.
- A **multi-output XGBoost model** predicts room temperature and energy consumption based on weather and indoor signals.
- A **DQN reinforcement learning agent** learns when and how to change device settings to reduce energy while keeping comfort.
- A **FastAPI backend with a static web UI** exposes endpoints and dashboards for monitoring logs and model behavior.

The system is designed as a **research / teaching platform** for AI-based energy optimization, with clear separation between data, simulation, learning, and presentation layers.

---

## 2. Features

- **Multi-home & multi-room configuration**
  - Define multiple homes, each with named rooms and assigned devices.
  - Set custom comfort temperature ranges per home.

- **Device catalog & impact map**
  - Central catalog of devices with:
    - Base energy consumption (kWh per step).
    - List of supported control permissions.
  - Automatic generation of an **impact map** that approximates how each permission affects energy and temperature.

- **Smart-home simulation (RL environment)**
  - Simulates indoor temperature, energy usage, and device actions in discrete time steps.
  - Includes natural thermal drift towards outdoor temperature.
  - Computes a reward that balances **comfort** and **energy savings**.

- **Machine-learning prediction**
  - Multi-output XGBoost regressor predicts:
    - Future room temperature.
    - Future energy consumption.
  - Uses time features, weather features, and lag / rolling statistics.

- **Reinforcement learning (DQN)**
  - RL agent with replay memory and epsilon-greedy exploration.
  - Periodic saving of model checkpoints.
  - Training KPIs logged as CSV and plots.

- **Web dashboard**
  - FastAPI backend + static HTML/JS/CSS.
  - Shows recent logs, cumulative KPIs, and basic home/room status.

- **Modular, extensible design**
  - Clear modules for management, simulation, ML, RL, logging, and web UI.
  - Easy to extend with new devices, homes, or models.

---

## 3. System Architecture

### 3.1 High-level layers

- **Management Layer**
  - Manages homes, rooms, and device assignments.
  - Stores:
    - Home comfort ranges.
    - Device catalog (name, base kWh, permissions).
  - All configuration is stored under the `data/` directory.

- **Simulation Layer**
  - Implemented in the RL environment.
  - State includes:
    - Indoor temperature and total energy used so far.
    - Outdoor temperature and time-of-day features (hour, weekend flag, etc.).
    - Device actions applied at each step.
  - Uses `devices_catalog.json` and `impact_map.json` to estimate:
    - Energy used by each action.
    - Temperature change from climate-related actions.
  - Provides a `reset()` and `step(action)` API compatible with RL training.

- **Learning Layer**
  - **XGBoost multi-output regression**:
    - Trained offline in notebooks.
    - Saved as `multioutput_xgb_model.pkl` and `feature_cols.pkl`.
  - **DQN RL agent**:
    - Learns control policies for turning devices on/off or changing levels.
    - Receives a reward equal to:
      - Negative energy usage (penalizes high consumption).
      - Additional penalty when temperature leaves the comfort range.
      - Small positive reward when comfort is maintained with low power.
  - Training procedure:
    - Runs for multiple episodes (simulated days).
    - Logs metrics (total reward, total energy, comfort violations).
    - Saves episodic and final checkpoints.

- **Presentation Layer (API + Web UI)**
  - **FastAPI app (`app.py`)**:
    - Initializes core components (device manager, home manager, calibrator).
    - Exposes API endpoints for:
      - System initialization.
      - Inspecting homes/devices.
      - Reading logs and KPIs.
    - Serves static frontend.
  - **Static dashboard (`static/`)**:
    - `index.html`, `styles.css` define layout and styling.
    - `script.js`, `data.js` fetch data from the API and render charts and tables.

### 3.2 Project Structure

```text
AI_energy_optimization/
├── data/
│   ├── devices_catalog.json
│   ├── devices_catalog_backup.json
│   ├── homes.json
│   └── impact_map.json
├── logs/
│   └── Default/
│       ├── training_kpis.csv
│       ├── default_kpi_*.png / .pdf
│       └── default_live_log.json
├── models/
│   ├── checkpoints/
│   │   ├── default_ep010.pth
│   │   ├── default_ep020.pth
│   │   ├── default_ep030.pth
│   │   └── default_final.pth
│   ├── feature_cols.pkl
│   └── multioutput_xgb_model.pkl
├── notebooks/
│   ├── build_device_catalog.ipynb
│   ├── training_module.ipynb
│   └── training_xgboost.ipynb
├── raw_data/
│   └── smart_home_energy_consumption_large.csv
├── rl/
│   ├── rl_agent.py
│   ├── rl_environment.py
│   ├── rl_utils.py
│   └── train_rl.py
├── static/
│   ├── index.html
│   ├── data.js
│   ├── script.js
│   └── styles.css
├── app.py
├── device_manager.py
├── home_manager.py
├── impact_calibrator.py
├── lstm_predictor.py
├── main.py
├── paths.py
├── test.py
└── README.md

## 4. Data and Models

## 4.1 Datasets
Raw data (raw_data/)

smart_home_energy_consumption_large.csv
Time series including:

Indoor temperature and humidity.

Basic energy consumption signals.

Time information and other auxiliary features.

Configuration data (data/)

devices_catalog.json

Defines all controllable devices (e.g. Air Conditioning, Heater, Lights, TV, etc.).

For each device: base_kWh and a list of control permissions.

homes.json

Defines homes, their rooms, and which devices belong to each room.

Stores comfort ranges (min/max indoor temperature).

impact_map.json

Maps permission keywords (e.g. low, high, eco, cool, heat) to:

energy_factor – how that mode scales base energy.

temp_change – approximate temperature effect per step.

## 4.2 Machine Learning Models

Multi-output XGBoost regressor

Inputs (examples):

temperature_2m, relative_humidity_2m (weather).

room_temperature, room_humidity, HVAC_temperature (indoor).

Time features: hour, day_of_week, is_weekend.

Lag/rolling stats: energy_lag1, energy_lag2, energy_roll3, room_temp_roll3.

Outputs:

room_temperature

synthetic_energy

Trained in notebooks/training_xgboost.ipynb and saved as:

models/multioutput_xgb_model.pkl

models/feature_cols.pkl

DQN Reinforcement Learning agent

Implemented in rl_agent.py, trained in train_rl.py.

Uses a simple feed-forward neural network (Deep Q-Network).

Stores:

Replay memory.

Exploration parameters (epsilon, decay, etc.).

Model weights and checkpoints under models/checkpoints/.## Installation
```bash
## Clone the repository
git clone https://github.com/<your-username>/AI_energy_optimization.git
cd AI_energy_optimization
## Create and activate a virtual environment (recommended)
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
## Otherwise, at minimum install:
pip install fastapi uvicorn numpy pandas torch xgboost scikit-learn matplotlib

Tested with Python 3.10

```md
## How to Run

1. **Prepare data and impact files (already provided)**
   - `raw_data/smart_home_energy_consumption_large.csv`
   - `data/devices_catalog.json`
   - `data/homes.json`
   - `data/impact_map.json` (auto-generated by the calibrator)

2. **Train the XGBoost prediction model (optional)**
   - Open `notebooks/training_xgboost.ipynb` in Jupyter and run all cells, **or**
   - Use the provided trained model: `models/multioutput_xgb_model.pkl`.

3. **Train the RL agent**
   ```bash
   python -m rl.train_rl

## Web Dashboard
The web dashboard (files in static/) provides a simple front-end on top of the API.

## Main elements:

#Home & room listing

Shows available homes and rooms loaded from homes.json.

Includes comfort ranges and assigned devices per room.

# Energy & temperature visualization

Reads recent logs from logs/Default/default_live_log.json.

Plots indoor temperature and energy usage over time.

Shows actions chosen by the RL agent at each step.

# Training KPIs

Can load PNG/PDF plots stored under logs/Default/.

Helps evaluate learning progress: total reward, energy savings, comfort violations.

The UI is intentionally simple and can be upgraded later with richer charts and configuration panels.
## Limitations and Future Work
The simulation is simplified and does not capture full building physics or detailed occupant behavior.

Device impact factors in impact_map.json are heuristic and not yet calibrated on real meters.

The RL agent is currently tuned for a default home configuration; new homes may require retraining.

The dashboard focuses mainly on monitoring; it does not yet expose advanced configuration flows for non-technical users.
## Team
AI & RL: design and training of the DQN agent, XGBoost model, and evaluation pipelines.

Data & Simulation: dataset cleaning, feature engineering, and smart-home environment design.

Web & API: FastAPI backend, front-end dashboard (HTML/JS/CSS), and system integration.