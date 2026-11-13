# QUICK START GUIDE

## Aircraft Predictive Maintenance System - 5-Minute Setup

### Prerequisites
- Windows OS (for batch scripts) or Linux/Mac (run commands manually)
- Python 3.10 or higher
- Minimum 4GB RAM (8GB recommended for training)
- Your aircraft maintenance datasets

### Step 1: Initial Setup (1 minute)

```bash
# Extract the project
cd AircraftPredictiveMaintenance

# Run setup
setup.bat
```

The setup script will:
- ✓ Create Python virtual environment
- ✓ Install all dependencies
- ✓ Prepare the system

### Step 2: Add Your Datasets (1 minute)

Copy your dataset files to:

```
AircraftPredictiveMaintenance/data/
├── engine/
│   ├── FD001_train.txt
│   ├── FD001_test.txt
│   ├── RUL_FD001.txt
│   └── ... (FD002-FD004)
├── electrical/
│   ├── electrical_train.csv
│   └── ...
└── hydraulic/
    ├── hydraulic_train.csv
    └── ...
```

### Step 3: Train Models (2-3 minutes)

```bash
# Option A: Run everything with interactive menu
run_project.bat
# Then select: [3] Both - Train then Run Dashboard

# Option B: Just train
python training/train_all.py
```

The training will:
- ✓ Load all datasets
- ✓ Preprocess data
- ✓ Train Autoencoder, LSTM, Random Forest for each subsystem
- ✓ Save trained models

**Note**: First run takes 2-5 minutes depending on dataset size

### Step 4: Launch Dashboard (30 seconds)

```bash
# Activate virtual environment
call venv\Scripts\activate.bat

# Start dashboard
streamlit run dashboard/app.py
```

The dashboard will automatically open at:
```
http://localhost:8501
```

### Dashboard Features

Once running, you'll see:

1. **Aircraft Overview** - Overall health, risk, recommendations
2. **Engine Diagnostics** - Engine health, faults, RUL
3. **Electrical Diagnostics** - Battery, voltage, generator status
4. **Hydraulic Diagnostics** - Pressure, flow, pump health
5. **Maintenance Guidance** - RAG-powered maintenance instructions

### Troubleshooting

**Problem**: "Python not found"
- **Solution**: Install Python 3.10+ from python.org

**Problem**: "Virtual environment failed"
- **Solution**: Delete `venv` folder and rerun `setup.bat`

**Problem**: "Models not found"
- **Solution**: Run `python training/train_all.py` first

**Problem**: "Dashboard won't load"
- **Solution**: Ensure you're in virtual environment: `call venv\Scripts\activate.bat`

### File Locations

- **Models**: `models/engine/`, `models/electrical/`, `models/hydraulic/`
- **Datasets**: `data/engine/`, `data/electrical/`, `data/hydraulic/`
- **Reports**: `reports/` (auto-generated PDF)
- **Config**: `config/config.py` (customize settings)

### Next Steps

1. **Customize Configuration**
   - Edit `config/config.py`
   - Adjust thresholds, model parameters

2. **Add New Datasets**
   - Place files in `data/` subdirectories
   - Retrain models with `python training/train_all.py`

3. **Generate Reports**
   - Use inference pipeline: `python inference/inference.py`
   - PDF reports auto-save to `reports/`

4. **Integrate with Your Systems**
   - Use agents in your own scripts
   - Call inference pipeline programmatically

### Command Reference

```bash
# Setup
setup.bat                           # Initial setup

# Training
python training/train_all.py        # Train all subsystems
python training/train_engine.py     # Train engine only
python training/train_electrical.py # Train electrical only
python training/train_hydraulic.py  # Train hydraulic only

# Dashboard
streamlit run dashboard/app.py      # Launch dashboard

# Inference
python inference/inference.py       # Run inference and generate report

# Utilities
python config/config.py             # View configuration
```

### Performance Tips

**Faster Training**:
- Reduce EPOCHS in config.py (default: 50, try: 20)
- Use GPU (TensorFlow/CUDA compatible)
- Pre-filter dataset size

**Better Predictions**:
- Ensure quality datasets
- Use complete training set
- Retrain regularly with new data

**Lower Memory Usage**:
- Reduce BATCH_SIZE in config.py
- Use smaller sequence lengths
- Process data in batches

### Security Notes

- Store sensitive maintenance data securely
- Use VPN for cloud deployments
- Regularly backup trained models
- Audit report access

### Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review config.py for available settings
3. Check model-specific docstrings
4. Verify dataset format matches requirements

---

## You're All Set! 🎉

Your Aircraft Predictive Maintenance System is ready to use.

**Dashboard running at**: http://localhost:8501

Enjoy real-time aircraft health monitoring! ✈️
