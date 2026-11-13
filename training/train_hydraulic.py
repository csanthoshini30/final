"""
Hydraulic System Model Training Pipeline
"""
import numpy as np
import pickle
import json
from pathlib import Path
from preprocessing.hydraulic_preprocessor import HydraulicPreprocessor
from models.model_architectures import (
    AutoencoderAnomalyDetector, LSTMHealthPredictor, RandomForestFaultClassifier, RandomForestRULRegressor
)
from config.config import (
    HYDRAULIC_MODELS_DIR, SEQUENCE_LENGTH, EPOCHS, BATCH_SIZE,
    LEARNING_RATE, AUTOENCODER_LATENT_DIM, LSTM_HIDDEN_DIM
)

class HydraulicTrainingPipeline:
    """Complete training pipeline for hydraulic models"""

    def __init__(self):
        self.hydraulic_models_dir = HYDRAULIC_MODELS_DIR
        self.hydraulic_models_dir.mkdir(parents=True, exist_ok=True)
        self.preprocessor = HydraulicPreprocessor()
        self.metrics = {}

    def train_autoencoder(self, X_train):
        """Train autoencoder for anomaly detection"""
        print("  Training Autoencoder for Hydraulic System...")

        input_shape = (X_train.shape[1], X_train.shape[2])
        autoencoder = AutoencoderAnomalyDetector(input_shape, latent_dim=AUTOENCODER_LATENT_DIM)
        autoencoder.compile(learning_rate=LEARNING_RATE)

        history = autoencoder.train(X_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

        # Save model
        model_path = self.hydraulic_models_dir / "autoencoder_hydraulic.h5"
        autoencoder.model.save(str(model_path))

        return autoencoder, history

    def train_lstm(self, X_train, y_train):
        """Train LSTM for health prediction"""
        print("  Training LSTM for Hydraulic System...")

        input_shape = (X_train.shape[1], X_train.shape[2])
        lstm = LSTMHealthPredictor(input_shape, hidden_dim=LSTM_HIDDEN_DIM)
        lstm.compile(learning_rate=LEARNING_RATE)

        history = lstm.train(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

        # Save model
        model_path = self.hydraulic_models_dir / "lstm_hydraulic.h5"
        lstm.model.save(str(model_path))

        return lstm, history

    def train_random_forest_classifier(self, X_train, y_labels):
        """Train Random Forest for fault classification"""
        print("  Training Random Forest Classifier for Hydraulic System...")

        rf_classifier = RandomForestFaultClassifier(n_estimators=100)
        rf_classifier.train(X_train, y_labels)

        # Save model
        model_path = self.hydraulic_models_dir / "rf_classifier_hydraulic.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_classifier, f)

        return rf_classifier

    def train_random_forest_rul(self, X_train, y_train):
        """Train Random Forest for RUL regression"""
        print("  Training Random Forest RUL for Hydraulic System...")

        rf_rul = RandomForestRULRegressor(n_estimators=100)
        rf_rul.train(X_train, y_train)

        # Save model
        model_path = self.hydraulic_models_dir / "rf_rul_hydraulic.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_rul, f)

        return rf_rul

    def create_fault_labels(self, y_train):
        """Create fault labels from health scores"""
        threshold = np.percentile(y_train, 30)
        labels = (y_train < threshold).astype(int)
        return labels

    def train(self):
        """Train all hydraulic models"""
        print("\nTraining Hydraulic System Models...")

        # Preprocess data
        data = self.preprocessor.preprocess_data()
        X_train = data['X_train']
        y_train = data['y_train']
        X_test_1 = data['X_test_1']
        X_test_2 = data['X_test_2']

        print(f"  Data shapes - Train: {X_train.shape}, Test1: {X_test_1.shape}, Test2: {X_test_2.shape}")

        # Train ONLY Autoencoder (most important for anomaly detection)
        autoencoder, ae_history = self.train_autoencoder(X_train)

        # Save scaler
        scaler_path = self.hydraulic_models_dir / "scaler_hydraulic.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(data['scaler'], f)

        # Store metrics
        self.metrics['hydraulic'] = {
            'X_train_shape': X_train.shape,
            'feature_cols': data['feature_cols'],
            'y_train_range': (float(y_train.min()), float(y_train.max())),
        }

        # Save metrics
        metrics_path = self.hydraulic_models_dir / "training_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)

        print("  ✓ Hydraulic Autoencoder trained and saved")

        return {
            'autoencoder': autoencoder,
            'data': data
        }


def run_hydraulic_training():
    """Run full hydraulic training pipeline"""
    print("=" * 60)
    print("HYDRAULIC SYSTEM MODEL TRAINING PIPELINE")
    print("=" * 60)

    pipeline = HydraulicTrainingPipeline()
    results = pipeline.train()

    return results


if __name__ == "__main__":
    run_hydraulic_training()
