"""
COMPLETE FILE INDEX & MANIFEST
Aircraft Predictive Maintenance System v1.0.0
"""

FILE_MANIFEST = {
    "ROOT LEVEL": {
        "setup.bat": "Windows setup automation - creates venv and installs dependencies",
        "run_project.bat": "Interactive execution menu - setup, training, or dashboard",
        "requirements.txt": "Python dependencies list (16 packages)",
        "README.md": "Comprehensive documentation and user guide",
        "QUICKSTART.md": "5-minute setup guide for quick start",
        "PROJECT_MANIFEST.json": "System blueprint and configuration details",
        "PROJECT_SUMMARY.py": "Complete project statistics and summary",
        ".gitignore": "Git ignore file for version control",
        "__init__.py": "Package initialization"
    },

    "config/": {
        "__init__.py": "Configuration module initialization",
        "config.py": "Centralized configuration (200+ lines) - ALL paths and settings"
    },

    "preprocessing/": {
        "__init__.py": "Preprocessing module initialization",
        "engine_preprocessor.py": "Engine data preprocessing (250+ lines) - NASA C-MAPSS handling",
        "electrical_preprocessor.py": "Electrical data preprocessing (220+ lines) - auto feature detection",
        "hydraulic_preprocessor.py": "Hydraulic data preprocessing (220+ lines) - dynamic scaling"
    },

    "models/": {
        "model_architectures.py": "Model definitions (350+ lines) - Autoencoder, LSTM, RandomForest",
        "engine/": "Trained engine models directory",
        "electrical/": "Trained electrical models directory",
        "hydraulic/": "Trained hydraulic models directory"
    },

    "agents/": {
        "__init__.py": "Agents module initialization",
        "engine_agent.py": "Engine diagnostics agent (250+ lines) - health, fault, RUL",
        "electrical_agent.py": "Electrical diagnostics agent (230+ lines) - system monitoring",
        "hydraulic_agent.py": "Hydraulic diagnostics agent (230+ lines) - anomaly detection",
        "coordinator_agent.py": "Multi-agent coordinator (300+ lines) - aggregates results",
        "rag_agent.py": "RAG maintenance assistant (400+ lines) - knowledge base"
    },

    "training/": {
        "__init__.py": "Training module initialization",
        "train_engine.py": "Engine model training (220+ lines) - all 4 datasets",
        "train_electrical.py": "Electrical model training (180+ lines) - flexible data",
        "train_hydraulic.py": "Hydraulic model training (180+ lines) - dynamic features",
        "train_all.py": "Master training orchestrator (100+ lines) - trains all subsystems"
    },

    "inference/": {
        "__init__.py": "Inference module initialization",
        "inference.py": "Complete inference pipeline (200+ lines) - predictions + reports"
    },

    "rag/": {
        "maintenance_manuals/": "Knowledge base documents directory",
        "vector_db/": "FAISS vector database directory"
    },

    "dashboard/": {
        "app.py": "Streamlit dashboard (800+ lines) - premium aerospace UI"
    },

    "reports/": {
        "__init__.py": "Reports module initialization",
        "report_generator.py": "PDF report generation (350+ lines) - ReportLab powered"
    },

    "data/": {
        "engine/": "Engine datasets - place FD001-FD004 files here",
        "electrical/": "Electrical datasets - place CSV files here",
        "hydraulic/": "Hydraulic datasets - place CSV files here"
    }
}

FUNCTIONALITY_INDEX = {
    "DATA LOADING & PREPROCESSING": [
        "preprocessing/engine_preprocessor.py - EnginePreprocessor class",
        "preprocessing/electrical_preprocessor.py - ElectricalPreprocessor class",
        "preprocessing/hydraulic_preprocessor.py - HydraulicPreprocessor class"
    ],

    "MODEL ARCHITECTURES": [
        "models/model_architectures.py - AutoencoderAnomalyDetector",
        "models/model_architectures.py - LSTMHealthPredictor",
        "models/model_architectures.py - RandomForestFaultClassifier",
        "models/model_architectures.py - RandomForestRULRegressor"
    ],

    "TRAINING PIPELINES": [
        "training/train_engine.py - EngineTrainingPipeline",
        "training/train_electrical.py - ElectricalTrainingPipeline",
        "training/train_hydraulic.py - HydraulicTrainingPipeline",
        "training/train_all.py - Master training orchestration"
    ],

    "INFERENCE & DIAGNOSTICS": [
        "agents/engine_agent.py - EngineAgent",
        "agents/electrical_agent.py - ElectricalAgent",
        "agents/hydraulic_agent.py - HydraulicAgent",
        "agents/coordinator_agent.py - CoordinatorAgent",
        "agents/rag_agent.py - RAGMaintenanceAgent",
        "inference/inference.py - run_inference()"
    ],

    "WEB INTERFACE": [
        "dashboard/app.py - Streamlit dashboard (main, tabs, visualizations)"
    ],

    "REPORT GENERATION": [
        "reports/report_generator.py - ReportGenerator (PDF, TXT)"
    ],

    "CONFIGURATION": [
        "config/config.py - All settings, paths, constants"
    ]
}

KEY_CLASSES = {
    "EnginePreprocessor": {
        "file": "preprocessing/engine_preprocessor.py",
        "methods": ["load_engine_data()", "preprocess_dataset()", "preprocess_all_datasets()"],
        "purpose": "NASA C-MAPSS data processing with RUL labels"
    },
    "ElectricalPreprocessor": {
        "file": "preprocessing/electrical_preprocessor.py",
        "methods": ["load_electrical_data()", "preprocess_data()", "create_health_labels()"],
        "purpose": "Electrical data with auto feature detection"
    },
    "HydraulicPreprocessor": {
        "file": "preprocessing/hydraulic_preprocessor.py",
        "methods": ["load_hydraulic_data()", "preprocess_data()", "detect_features()"],
        "purpose": "Hydraulic data with dynamic scaling"
    },
    "AutoencoderAnomalyDetector": {
        "file": "models/model_architectures.py",
        "methods": ["build_model()", "train()", "detect_anomalies()"],
        "purpose": "Anomaly detection via reconstruction error"
    },
    "LSTMHealthPredictor": {
        "file": "models/model_architectures.py",
        "methods": ["build_model()", "train()", "predict()"],
        "purpose": "Health score and RUL prediction"
    },
    "RandomForestFaultClassifier": {
        "file": "models/model_architectures.py",
        "methods": ["train()", "predict()", "predict_proba()"],
        "purpose": "Fault type classification"
    },
    "RandomForestRULRegressor": {
        "file": "models/model_architectures.py",
        "methods": ["train()", "predict()", "evaluate()"],
        "purpose": "RUL regression"
    },
    "EngineAgent": {
        "file": "agents/engine_agent.py",
        "methods": ["diagnose()", "detect_anomalies()", "predict_rul()"],
        "purpose": "Engine health monitoring"
    },
    "ElectricalAgent": {
        "file": "agents/electrical_agent.py",
        "methods": ["diagnose()", "detect_anomalies()", "predict_rul()"],
        "purpose": "Electrical system monitoring"
    },
    "HydraulicAgent": {
        "file": "agents/hydraulic_agent.py",
        "methods": ["diagnose()", "detect_anomalies()", "predict_rul()"],
        "purpose": "Hydraulic system monitoring"
    },
    "CoordinatorAgent": {
        "file": "agents/coordinator_agent.py",
        "methods": ["coordinate()", "calculate_weighted_health()", "generate_recommendations()"],
        "purpose": "Multi-agent orchestration"
    },
    "RAGMaintenanceAgent": {
        "file": "agents/rag_agent.py",
        "methods": ["search()", "generate_maintenance_report()"],
        "purpose": "Knowledge base retrieval"
    },
    "ReportGenerator": {
        "file": "reports/report_generator.py",
        "methods": ["generate_maintenance_report()", "generate_summary_report()"],
        "purpose": "PDF and text report generation"
    }
}

EXECUTION_ENTRY_POINTS = {
    "Setup": {
        "command": "setup.bat",
        "action": "Creates virtual environment and installs dependencies",
        "platform": "Windows"
    },
    "Interactive Run": {
        "command": "run_project.bat",
        "action": "Menu for training, dashboard, or both",
        "platform": "Windows"
    },
    "Train All Models": {
        "command": "python training/train_all.py",
        "action": "Trains all subsystem models (2-5 minutes)",
        "platform": "Any"
    },
    "Launch Dashboard": {
        "command": "streamlit run dashboard/app.py",
        "action": "Starts web interface at localhost:8501",
        "platform": "Any"
    },
    "Run Inference": {
        "command": "python inference/inference.py",
        "action": "Complete diagnostics pipeline",
        "platform": "Any"
    },
    "View Summary": {
        "command": "python PROJECT_SUMMARY.py",
        "action": "Displays comprehensive project summary",
        "platform": "Any"
    }
}

DATASET_FILES = {
    "Engine (NASA C-MAPSS)": [
        "data/engine/FD001_train.txt",
        "data/engine/FD001_test.txt",
        "data/engine/RUL_FD001.txt",
        "data/engine/FD002_train.txt",
        "data/engine/FD002_test.txt",
        "data/engine/RUL_FD002.txt",
        "data/engine/FD003_train.txt",
        "data/engine/FD003_test.txt",
        "data/engine/RUL_FD003.txt",
        "data/engine/FD004_train.txt",
        "data/engine/FD004_test.txt",
        "data/engine/RUL_FD004.txt"
    ],
    "Electrical": [
        "data/electrical/electrical_data.csv",
        "data/electrical/electrical_train.csv",
        "data/electrical/electrical_test_1.csv",
        "data/electrical/electrical_test_2.csv"
    ],
    "Hydraulic": [
        "data/hydraulic/hydraulic_data.csv",
        "data/hydraulic/hydraulic_train.csv",
        "data/hydraulic/hydraulic_test_1.csv",
        "data/hydraulic/hydraulic_test_2.csv"
    ]
}

OUTPUT_LOCATIONS = {
    "Trained Models": "models/{subsystem}/*.h5 and *.pkl",
    "Training Metrics": "models/{subsystem}/training_metrics.json",
    "PDF Reports": "reports/*.pdf",
    "Text Reports": "reports/*.txt",
    "Log Files": "logs/ (when configured)",
    "Vector Database": "rag/vector_db/ (when built)"
}

CONFIGURATION_OPTIONS = {
    "Sequence Length": "config.py - SEQUENCE_LENGTH = 30",
    "Batch Size": "config.py - BATCH_SIZE = 32",
    "Epochs": "config.py - EPOCHS = 50",
    "Learning Rate": "config.py - LEARNING_RATE = 0.001",
    "Autoencoder Latent Dim": "config.py - AUTOENCODER_LATENT_DIM = 16",
    "LSTM Hidden Dim": "config.py - LSTM_HIDDEN_DIM = 64",
    "Health Thresholds": "config.py - HEALTH_CRITICAL/WARNING/GOOD",
    "Anomaly Threshold": "config.py - AUTOENCODER_THRESHOLD = 0.95"
}

def print_complete_index():
    """Print complete file index"""
    print("\n" + "="*70)
    print("COMPLETE FILE INDEX - AIRCRAFT PREDICTIVE MAINTENANCE SYSTEM")
    print("="*70 + "\n")

    print("FILE STRUCTURE:")
    print("-" * 70)
    for category, files in FILE_MANIFEST.items():
        print(f"\n{category}")
        for filename, description in files.items():
            print(f"  • {filename}: {description}")

    print("\n" + "="*70)
    print("FUNCTIONALITY INDEX:")
    print("-" * 70)
    for category, items in FUNCTIONALITY_INDEX.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

    print("\n" + "="*70)
    print("KEY CLASSES & METHODS:")
    print("-" * 70)
    for classname, info in KEY_CLASSES.items():
        print(f"\n{classname}:")
        print(f"  Location: {info['file']}")
        print(f"  Purpose: {info['purpose']}")
        print(f"  Methods: {', '.join(info['methods'])}")

    print("\n" + "="*70)
    print("EXECUTION ENTRY POINTS:")
    print("-" * 70)
    for name, info in EXECUTION_ENTRY_POINTS.items():
        print(f"\n{name}:")
        print(f"  Command: {info['command']}")
        print(f"  Action: {info['action']}")
        print(f"  Platform: {info['platform']}")

    print("\n" + "="*70)
    print("EXPECTED DATASET FILES:")
    print("-" * 70)
    for category, files in DATASET_FILES.items():
        print(f"\n{category}:")
        for file in files:
            print(f"  • {file}")

    print("\n" + "="*70)
    print("OUTPUT LOCATIONS:")
    print("-" * 70)
    for location, path in OUTPUT_LOCATIONS.items():
        print(f"  • {location}: {path}")

    print("\n" + "="*70)
    print("KEY CONFIGURATION OPTIONS:")
    print("-" * 70)
    for option, setting in CONFIGURATION_OPTIONS.items():
        print(f"  • {option}: {setting}")

    print("\n" + "="*70)
    print("✅ INDEX COMPLETE - All files documented and organized")
    print("="*70 + "\n")

if __name__ == "__main__":
    print_complete_index()
