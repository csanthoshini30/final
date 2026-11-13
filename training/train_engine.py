"""
Engine Model Training Pipeline
"""
import numpy as np
import pickle
import json
from pathlib import Path
from preprocessing.engine_preprocessor import EnginePreprocessor
from models.model_architectures import (
    AutoencoderAnomalyDetector, LSTMHealthPredictor, RandomForestFaultClassifier, RandomForestRULRegressor
)
from config.config import (
    ENGINE_MODELS_DIR, SEQUENCE_LENGTH, EPOCHS, BATCH_SIZE,
    LEARNING_RATE, AUTOENCODER_LATENT_DIM, LSTM_HIDDEN_DIM
)

class EngineTrainingPipeline:
    """Complete training pipeline for engine models"""

    def __init__(self):
        self.engine_models_dir = ENGINE_MODELS_DIR
        self.engine_models_dir.mkdir(parents=True, exist_ok=True)
        self.preprocessor = EnginePreprocessor()
        self.metrics = {}

    def train_autoencoder(self, X_train, dataset_name):
        """Train autoencoder for anomaly detection"""
        print(f"  Training Autoencoder for {dataset_name}...")

        input_shape = (X_train.shape[1], X_train.shape[2])
        autoencoder = AutoencoderAnomalyDetector(input_shape, latent_dim=AUTOENCODER_LATENT_DIM)
        autoencoder.compile(learning_rate=LEARNING_RATE)

        history = autoencoder.train(X_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

        # Save model
        model_path = self.engine_models_dir / f"autoencoder_{dataset_name}.h5"
        autoencoder.model.save(str(model_path))

        return autoencoder, history

    def train_lstm(self, X_train, y_train, dataset_name):
        """Train LSTM for health prediction"""
        print(f"  Training LSTM for {dataset_name}...")

        input_shape = (X_train.shape[1], X_train.shape[2])
        lstm = LSTMHealthPredictor(input_shape, hidden_dim=LSTM_HIDDEN_DIM)
        lstm.compile(learning_rate=LEARNING_RATE)

        history = lstm.train(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

        # Save model
        model_path = self.engine_models_dir / f"lstm_{dataset_name}.h5"
        lstm.model.save(str(model_path))

        return lstm, history

    def train_random_forest_classifier(self, X_train, y_labels, dataset_name):
        """Train Random Forest for fault classification"""
        print(f"  Training Random Forest Classifier for {dataset_name}...")

        rf_classifier = RandomForestFaultClassifier(n_estimators=100)
        rf_classifier.train(X_train, y_labels)

        # Save model
        model_path = self.engine_models_dir / f"rf_classifier_{dataset_name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_classifier, f)

        return rf_classifier

    def train_random_forest_rul(self, X_train, y_train, dataset_name):
        """Train Random Forest for RUL prediction"""
        print(f"  Training Random Forest RUL for {dataset_name}...")

        rf_rul = RandomForestRULRegressor(n_estimators=100)
        rf_rul.train(X_train, y_train)

        # Save model
        model_path = self.engine_models_dir / f"rf_rul_{dataset_name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_rul, f)

        return rf_rul

    def create_fault_labels(self, y_train):
        """Create fault labels from RUL"""
        # Label healthy vs degraded
        threshold = np.percentile(y_train, 25)
        labels = (y_train < threshold).astype(int)
        return labels

    def train_single_dataset(self, dataset_name):
        """Train models for single dataset"""
        print(f"\nTraining models for {dataset_name}...")

        # Preprocess data
        data = self.preprocessor.preprocess_dataset(dataset_name)
        X_train = data['X_train']
        y_train = data['y_train']
        X_test = data['X_test']
        y_test = data['y_test']

        print(f"  Data shapes - Train: {X_train.shape}, Test: {X_test.shape}")

        # Train models
        autoencoder, ae_history = self.train_autoencoder(X_train, dataset_name)
        lstm, lstm_history = self.train_lstm(X_train, y_train, dataset_name)

        # Create fault labels for classifier
        fault_labels = self.create_fault_labels(y_train)
        rf_classifier = self.train_random_forest_classifier(X_train, fault_labels, dataset_name)
        rf_rul = self.train_random_forest_rul(X_train, y_train, dataset_name)

        # Save scaler
        scaler_path = self.engine_models_dir / f"scaler_{dataset_name}.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(data['scaler'], f)

        # Store metrics
        self.metrics[dataset_name] = {
            'X_train_shape': X_train.shape,
            'X_test_shape': X_test.shape,
            'y_train_range': (float(y_train.min()), float(y_train.max())),
            'y_test_range': (float(y_test.min()), float(y_test.max())),
        }

        print(f"  ✓ Models trained and saved for {dataset_name}")

        return {
            'autoencoder': autoencoder,
            'lstm': lstm,
            'rf_classifier': rf_classifier,
            'rf_rul': rf_rul,
            'data': data
        }

    def train_all_datasets(self):
        """Train models for all engine datasets"""
        results = {}
        dataset_names = list(['FD001', 'FD002', 'FD003', 'FD004'])

        for dataset_name in dataset_names:
            try:
                results[dataset_name] = self.train_single_dataset(dataset_name)
            except Exception as e:
                print(f"  ✗ Error training {dataset_name}: {str(e)}")
                continue

        # Save metrics
        metrics_path = self.engine_models_dir / "training_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)

        print("\n✓ All engine datasets trained successfully!")
        return results


def run_engine_training():
    """Run full engine training pipeline"""
    print("=" * 60)
    print("ENGINE MODEL TRAINING PIPELINE")
    print("=" * 60)

    pipeline = EngineTrainingPipeline()
    results = pipeline.train_all_datasets()

    return results


if __name__ == "__main__":
    run_engine_training()
