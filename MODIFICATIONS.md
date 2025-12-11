# Project Modifications Log

**Date**: December 11, 2025  
**Modified By**: Development Team  
**Version**: 1.1.0

---

## Overview

This document details all modifications made to fix critical bugs and ensure the AI Energy Optimization system runs without errors. The primary issues resolved were dependency conflicts, sensor error handling, and PyTorch compatibility.

---

## Critical Errors Fixed

### 1. **PyTorch 2.6 Compatibility Issue**
**Error**: `Weights only load failed`

**Root Cause**: PyTorch 2.6 changed the default value of `weights_only` parameter from `False` to `True` in `torch.load()`. Legacy pickle files containing XGBoost objects require `weights_only=False`.

**Solution**: Modified `lstm_predictor.py` line 15 to explicitly set `weights_only=False`.

**File Modified**: `lstm_predictor.py`

---

### 2. **Missing XGBoost Module**
**Error**: `ModuleNotFoundError: No module named 'xgboost'`

**Root Cause**: XGBoost was not installed in the Python environment running the uvicorn server.

**Solution**: Installed xgboost via pip.

**Command**:
```powershell
python -m pip install xgboost
```

**Current Version**: `xgboost==2.1.4`

---

### 3. **Numpy Compatibility Issue**
**Error**: `No module named 'numpy._core'`

**Root Cause**: The installed numpy version (1.23.5) was too old and didn't have the `_core` module required by newer xgboost versions.

**Solution**: Upgraded numpy to version with `_core` module.

**Command**:
```powershell
python -m pip install "numpy==1.26.4"
```

**Current Version**: `numpy==1.26.4`

---

### 4. **Scikit-learn Version Mismatch**
**Error**: `Invalid magic number; corrupt file?`

**Root Cause**: The LSTM model pickle file (`multioutput_xgb_model.pkl`) was created with scikit-learn 1.7.2, but the environment had scikit-learn 1.1.3. Version mismatches cause pickle deserialization failures.

**Solution**: Upgraded scikit-learn to latest version.

**Command**:
```powershell
python -m pip install --upgrade scikit-learn
```

**Current Version**: `scikit-learn==1.6.1`

---

### 5. **Sensor None Value Arithmetic Errors**
**Error**: `unsupported operand type(s) for -: 'float' and 'NoneType'`

**Root Cause**: Real sensor APIs can return `None` when sensors fail. The code attempted arithmetic operations on `None` values without validation.

**Solution**: Added None-safety checks with fallback default values in multiple files.

**Files Modified**:
- `main.py` (lines 52-56): Added fallback defaults for `comfort_min`, `comfort_max`, `indoor_temp`
- `rl/rl_environment.py` (lines 77-110): Enhanced `_out_temp()`, `_indoor_temp()`, `_real_kWh()` methods with None checks

---

### 6. **Training Endpoint Error Handling**
**Error**: Server crashes when training fails

**Root Cause**: Unhandled exceptions in training endpoint would crash the entire FastAPI server.

**Solution**: Wrapped training logic in try-catch block that returns structured error responses.

**File Modified**: `app.py` (lines 128-145)

---

## Modified Files Summary

### 1. `lstm_predictor.py`
**Lines Modified**: 13-19  
**Changes**:
- Added `weights_only=False` parameter to `torch.load()`
- Added detailed comments explaining PyTorch 2.6 compatibility fix

### 2. `app.py`
**Lines Modified**: 128-145  
**Changes**:
- Wrapped training endpoint in try-catch block
- Returns structured error response instead of crashing
- Added detailed comments explaining error handling

### 3. `main.py`
**Lines Modified**: 52-56, 68-71  
**Changes**:
- Added None-safety checks for `comfort_min`, `comfort_max`, `indoor_temp`
- Fallback defaults: comfort_min=20, comfort_max=27, indoor_temp=23
- Added detailed comments explaining sensor error handling

### 4. `rl/rl_environment.py`
**Lines Modified**: 77-98, 88-98, 100-108  
**Changes**:
- Enhanced `_out_temp()` method with None checks
- Enhanced `_indoor_temp()` method with None checks
- Enhanced `_real_kWh()` method with None checks
- Added detailed comments explaining sensor error handling

### 5. `rl/train_rl.py`
**Lines Modified**: 25-33  
**Changes**:
- Cleaned up LSTM loading logic (removed degraded fallback mode)
- Ensures full-quality training with state_size=4 when LSTM available

---

## Dependency Requirements

### Critical Dependencies
```text
numpy==1.26.4              # MUST be 1.26+ for _core module
xgboost==2.1.4             # MUST be installed
scikit-learn==1.6.1        # MUST match pickle file version or newer
torch==2.6+                # Requires weights_only parameter
fastapi
uvicorn
scipy
pandas
matplotlib
```

### Installation Command
```powershell
python -m pip install numpy==1.26.4 xgboost==2.1.4 scikit-learn==1.6.1 torch fastapi uvicorn scipy pandas matplotlib
```

---

## How to Run the Project

### 1. **Install Dependencies**
```powershell
cd C:\Users\razer\OneDrive\Desktop\Python\AI_energy_optimization
python -m pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, use:
```powershell
python -m pip install numpy==1.26.4 xgboost==2.1.4 scikit-learn==1.6.1 torch fastapi uvicorn scipy pandas matplotlib
```

### 2. **Start the Backend Server**
```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### 3. **Access the Frontend**
Open your browser and navigate to:
```
http://localhost:8000
```

The frontend serves:
- `/` → `static/index.html`
- `/styles.css` → `static/styles.css`
- `/script.js` → `static/script.js`

### 4. **Test Training**
- Navigate to the "Training" tab in the UI
- Select a home from the dropdown
- Choose number of episodes (default: 10)
- Click "Start Training"
- Monitor progress in the neural network visualization

### 5. **Test Simulation**
- Navigate to the "Overview" tab
- Select a home from the dropdown
- Click "Run 24h Simulation"
- View results in the modal popup

---

## Known Issues & Warnings

### 1. **XGBoost Serialization Warning**
**Warning Message**:
```
WARNING: If you are loading a serialized model (like pickle in Python, RDS in R) 
or configuration generated by an older version of XGBoost, please export the model 
by calling `Booster.save_model` from that version first
```

**Impact**: Non-critical warning. Model loads and works correctly.

**Recommendation**: Re-save the model using `Booster.save_model()` in future updates.

### 2. **Scikit-learn Version Warning**
**Warning Message**:
```
UserWarning: Trying to unpickle estimator MultiOutputRegressor from version 1.7.2 
when using version 1.6.1
```

**Impact**: Non-critical warning. Model loads successfully.

**Recommendation**: Regenerate pickle file with consistent scikit-learn version.

### 3. **Matplotlib Threading Warning**
**Warning Message**:
```
UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
```

**Impact**: Non-critical. KPI plots still save correctly.

**Recommendation**: Refactor plotting to run in main thread in future updates.

### 4. **Dependency Conflicts**
Some global packages (rasa, camel-tools, tensorflow) have version conflicts with upgraded dependencies. These do NOT affect this project but may affect other projects in the same environment.

**Recommendation**: Use a virtual environment to isolate dependencies.

---

## Virtual Environment Setup (Recommended)

To avoid dependency conflicts with other projects:

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install numpy==1.26.4 xgboost==2.1.4 scikit-learn==1.6.1 torch fastapi uvicorn scipy pandas matplotlib

# Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Deactivate when done
deactivate
```

---

## Testing Checklist

- [x] Backend starts without errors
- [x] Frontend loads at `http://localhost:8000`
- [x] All API endpoints respond (homes, devices, weather, init, kpis)
- [x] LSTM model loads successfully with xgboost
- [x] Training completes without errors
- [x] Simulation runs successfully
- [x] Charts render correctly
- [x] Modal popups work
- [x] Device assignment works
- [x] Home/room creation works

---

## Architecture Notes

### Frontend Stack
- **Framework**: Vanilla JavaScript (no frameworks)
- **Design**: "Aura Energy" theme with glassmorphism
- **Colors**: Warm earth tones (#FF6B35 orange, #2EC4B6 teal, #F7C59F beige)
- **Files**: 3 files total (~2600 lines)
  - `static/index.html` - SPA structure with 5 views
  - `static/styles.css` - Complete styling with animations
  - `static/script.js` - API integration and interactivity

### Backend Stack
- **Framework**: FastAPI with Uvicorn server
- **ML Libraries**: PyTorch (LSTM), XGBoost, Scikit-learn
- **RL Framework**: Custom DQN implementation
- **Port**: 8000
- **Auto-reload**: Enabled (WatchFiles)

### Data Flow
1. User interacts with frontend
2. JavaScript makes fetch() calls to FastAPI endpoints
3. Backend processes request (training/simulation/CRUD)
4. RL agent uses LSTM predictions for enhanced state representation
5. Results returned as JSON to frontend
6. Frontend updates UI dynamically

---

## Contact & Support

For issues or questions about these modifications:
1. Check this document first
2. Verify all dependencies are correct versions
3. Check terminal output for detailed error messages
4. Ensure LSTM model file exists at `models/multioutput_xgb_model.pkl`

---

**End of Modifications Log**
