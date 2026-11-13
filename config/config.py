"""
Aircraft Predictive Maintenance System - Configuration
"""
import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Data Configuration
DATA_DIR = PROJECT_ROOT / "data"
ENGINE_DATA_DIR = DATA_DIR / "engine"
ELECTRICAL_DATA_DIR = DATA_DIR / "electrical"
HYDRAULIC_DATA_DIR = DATA_DIR / "hydraulic"

# Engine Dataset Files
ENGINE_TRAIN_FILES = {
    "FD001": ENGINE_DATA_DIR / "FD001_train.txt",
    "FD002": ENGINE_DATA_DIR / "FD002_train.txt",
    "FD003": ENGINE_DATA_DIR / "FD003_train.txt",
    "FD004": ENGINE_DATA_DIR / "FD004_train.txt",
}

ENGINE_TEST_FILES = {
    "FD001": ENGINE_DATA_DIR / "FD001_test.txt",
    "FD002": ENGINE_DATA_DIR / "FD002_test.txt",
    "FD003": ENGINE_DATA_DIR / "FD003_test.txt",
    "FD004": ENGINE_DATA_DIR / "FD004_test.txt",
}

ENGINE_RUL_FILES = {
    "FD001": ENGINE_DATA_DIR / "RUL_FD001.txt",
    "FD002": ENGINE_DATA_DIR / "RUL_FD002.txt",
    "FD003": ENGINE_DATA_DIR / "RUL_FD003.txt",
    "FD004": ENGINE_DATA_DIR / "RUL_FD004.txt",
}

# Electrical Dataset Files
ELECTRICAL_FILES = {
    "data": ELECTRICAL_DATA_DIR / "electrical_data.csv",
    "train": ELECTRICAL_DATA_DIR / "electrical_train.csv",
    "test_1": ELECTRICAL_DATA_DIR / "electrical_test_1.csv",
    "test_2": ELECTRICAL_DATA_DIR / "electrical_test_2.csv",
}

# Hydraulic Dataset Files
HYDRAULIC_FILES = {
    "data": HYDRAULIC_DATA_DIR / "hydraulic_data.csv",
    "train": HYDRAULIC_DATA_DIR / "hydraulic_train.csv",
    "test_1": HYDRAULIC_DATA_DIR / "hydraulic_test_1.csv",
    "test_2": HYDRAULIC_DATA_DIR / "hydraulic_test_2.csv",
}

# Models Configuration
MODELS_DIR = PROJECT_ROOT / "models"
ENGINE_MODELS_DIR = MODELS_DIR / "engine"
ELECTRICAL_MODELS_DIR = MODELS_DIR / "electrical"
HYDRAULIC_MODELS_DIR = MODELS_DIR / "hydraulic"

# RAG Configuration
RAG_DIR = PROJECT_ROOT / "rag"
MAINTENANCE_MANUALS_DIR = RAG_DIR / "maintenance_manuals"
VECTOR_DB_DIR = RAG_DIR / "vector_db"
VECTOR_DB_INDEX = VECTOR_DB_DIR / "faiss_index"

# Reports Configuration
REPORTS_DIR = PROJECT_ROOT / "reports"

# Training Configuration
SEQUENCE_LENGTH = 30
TRAIN_TEST_SPLIT = 0.8
VALIDATION_SPLIT = 0.2
RANDOM_STATE = 42
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

# Model Architecture
AUTOENCODER_LATENT_DIM = 16
LSTM_HIDDEN_DIM = 64
AUTOENCODER_THRESHOLD = 0.95  # Percentile for anomaly detection

# Health Score Thresholds
HEALTH_CRITICAL = 50
HEALTH_WARNING = 70
HEALTH_GOOD = 100

# Risk Levels
RISK_CRITICAL = "Critical"
RISK_HIGH = "High"
RISK_MEDIUM = "Medium"
RISK_LOW = "Low"
RISK_NORMAL = "Normal"

# Engine-specific Configuration
ENGINE_SENSOR_COLUMNS = [
    "T2", "T24", "T30", "T50", "P2", "P15", "P30", "Nf", "Nc",
    "epr", "Ps30", "phi", "NRf", "NRc", "BPR", "farB", "htBleed",
    "Nf_dmd", "PCNfR_dmd", "W31", "W32"
]
ENGINE_FEATURE_COUNT = len(ENGINE_SENSOR_COLUMNS)

# Electrical-specific Configuration
ELECTRICAL_FEATURES = [
    "voltage", "current", "power", "frequency",
    "battery_soc", "battery_voltage", "temperature",
    "efficiency", "load_percentage", "harmonics"
]

# Hydraulic-specific Configuration
HYDRAULIC_FEATURES = [
    "pressure_main", "pressure_accumulator", "flow_rate",
    "pump_outlet_temp", "motor_current", "valve_position",
    "fluid_temp", "contamination_level", "viscosity", "leakage_rate"
]

# Visualization Configuration
PLOT_COLORS = {
    "engine": "#FF6B6B",
    "electrical": "#4ECDC4",
    "hydraulic": "#45B7D1",
}

# Create directories if they don't exist
def ensure_directories():
    """Ensure all required directories exist"""
    dirs = [
        DATA_DIR, ENGINE_DATA_DIR, ELECTRICAL_DATA_DIR, HYDRAULIC_DATA_DIR,
        MODELS_DIR, ENGINE_MODELS_DIR, ELECTRICAL_MODELS_DIR, HYDRAULIC_MODELS_DIR,
        RAG_DIR, MAINTENANCE_MANUALS_DIR, VECTOR_DB_DIR, REPORTS_DIR
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

ensure_directories()
