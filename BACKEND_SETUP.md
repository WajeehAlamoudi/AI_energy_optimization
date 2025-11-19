# Backend Setup and Usage Guide

## Fixed Issues

### 1. Critical Syntax Error in `app.py`
**Location:** Line 205 in `/api/live_data` endpoint

**Issue:** Invalid Python syntax
```python
# BEFORE (BROKEN)
return json.load(f)["step"[-1]]
```

**Fix:** Proper array access and error handling
```python
# AFTER (WORKING)
data = json.load(f)
if "steps" in data and len(data["steps"]) > 0:
    return data["steps"][-1]
return data
```

### 2. Missing Dependencies
Created `requirements.txt` with all necessary Python packages.

### 3. Build Artifacts
Added `.gitignore` to exclude `__pycache__`, logs, and generated files.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Dependencies Installed
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pandas** - Data processing
- **numpy** - Numerical computing
- **torch** - Machine learning
- **requests** - HTTP client
- **tqdm** - Progress bars
- **matplotlib** - Plotting (optional)

## Running the Backend

### Start the Server

```bash
# Start the backend on default port 8000
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

# Or with auto-reload for development
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Test the Backend

```bash
# Run the automated test script
python3 test_backend.py
```

## API Endpoints

### Home Management
- `GET /api/homes` - List all homes
- `POST /api/homes/add` - Add a new home
- `POST /api/homes/delete` - Delete a home
- `POST /api/rooms/add` - Add a room to a home
- `POST /api/rooms/delete` - Delete a room
- `POST /api/rooms/assign_device` - Assign a device to a room

### Device Management
- `GET /api/devices` - List all devices
- `POST /api/devices/add` - Add a new device
- `POST /api/devices/permissions/add` - Add permission to a device

### Weather & System
- `GET /api/weather` - Get current weather data
- `GET /api/init` - Initialize the system

### Training & Simulation
- `POST /api/train` - Train RL agent for a home
- `POST /api/simulate/day` - Simulate a day for a home
- `POST /api/activate_optimizer` - Activate live optimizer
- `GET /api/live_data` - Get live optimization data

### KPIs & Monitoring
- `GET /api/kpis` - Get KPI summary
- `GET /api/kpis/full` - Get full KPI log

## Testing

The backend has been tested and verified to work correctly:

```
✅ GET /api/init - System initialization
✅ GET /api/homes - List homes
✅ GET /api/devices - List devices
✅ GET /api/weather - Get weather data
✅ GET /api/kpis - Get KPIs
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Module not found
```bash
# Make sure you're in the project directory
cd /path/to/AI_energy_optimization
python3 -m uvicorn app:app
```

## Project Structure

```
AI_energy_optimization/
├── app.py                  # Main FastAPI application (FIXED)
├── requirements.txt        # Python dependencies (NEW)
├── .gitignore             # Git ignore rules (NEW)
├── test_backend.py        # Backend test script (NEW)
├── home_manager.py        # Home management logic
├── device_manager.py      # Device catalog management
├── impact_calibrator.py   # Energy impact calibration
├── lstm_predictor.py      # LSTM prediction model
├── main.py                # Live agent runner
├── paths.py               # Path configuration
├── training_kpi_logger.py # KPI logging
├── data/                  # Data storage (gitignored)
├── logs/                  # Log files (gitignored)
├── models/                # Trained models
├── rl/                    # Reinforcement learning
│   ├── rl_agent.py        # RL agent implementation
│   ├── rl_environment.py  # Smart home environment
│   ├── rl_utils.py        # Utility functions
│   └── train_rl.py        # Training script
└── static/                # Frontend files
```

## Next Steps

1. **Frontend Integration**: Ensure frontend points to correct backend URL
2. **Model Training**: Train RL models for your homes using `/api/train`
3. **Live Optimization**: Activate optimizer with `/api/activate_optimizer`
4. **Monitoring**: Check KPIs and live data through the API

## Support

If you encounter any issues:
1. Check the console output for error messages
2. Run `python3 test_backend.py` to verify installation
3. Ensure all dependencies are installed correctly
4. Check that data files exist in the `data/` directory
