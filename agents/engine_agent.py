"""
Engine Agent - Engine Health Monitoring and Diagnostics
"""
import numpy as np
import pickle
import tensorflow as tf
from config.config import ENGINE_MODELS_DIR, HEALTH_CRITICAL, HEALTH_WARNING, HEALTH_GOOD
from config.config import RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_NORMAL
from models.hub_loader import ModelArtifactError, resolve_model_path

class EngineAgent:
    """Engine subsystem monitoring agent"""

    def __init__(self, dataset_name="FD001"):
        self.models_dir = ENGINE_MODELS_DIR
        self.dataset_name = dataset_name
        self.models = {}
        self.scaler = None
        self.load_models()

    def load_models(self):
        """Load trained models"""
        try:
            # Load autoencoder
            ae_path = resolve_model_path(self.models_dir, f"autoencoder_{self.dataset_name}.h5")
            self.models['autoencoder'] = tf.keras.models.load_model(str(ae_path), compile=False)

            # Load LSTM
            lstm_path = resolve_model_path(self.models_dir, f"lstm_{self.dataset_name}.h5")
            self.models['lstm'] = tf.keras.models.load_model(str(lstm_path), compile=False)

            # Load Random Forest classifier
            rf_clf_path = resolve_model_path(self.models_dir, f"rf_classifier_{self.dataset_name}.pkl")
            with open(rf_clf_path, 'rb') as f:
                self.models['rf_classifier'] = pickle.load(f)

            # Load Random Forest RUL regressor
            rf_rul_path = resolve_model_path(self.models_dir, f"rf_rul_{self.dataset_name}.pkl")
            with open(rf_rul_path, 'rb') as f:
                self.models['rf_rul'] = pickle.load(f)

            # Load scaler
            scaler_path = resolve_model_path(self.models_dir, f"scaler_{self.dataset_name}.pkl")
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            print(f"Engine models loaded from {self.dataset_name}")
        except ModelArtifactError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"Could not load engine model artifacts for {self.dataset_name}."
            ) from e

    def detect_anomalies(self, X):
        """Detect anomalies using autoencoder"""
        if 'autoencoder' not in self.models:
            raise RuntimeError("Engine autoencoder is not loaded.")

        try:
            X_pred = self.models['autoencoder'].predict(X, verbose=0)
            mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
            threshold = np.percentile(mse, 95)
            anomalies = mse > threshold
            return anomalies, mse
        except Exception as e:
            raise RuntimeError("Engine anomaly detection failed.") from e

    def predict_health(self, X):
        """Predict health score using LSTM"""
        if 'lstm' not in self.models:
            raise RuntimeError("Engine LSTM is not loaded.")

        try:
            health_scores = self.models['lstm'].predict(X, verbose=0)
            # Clip to 0-100 range
            health_scores = np.clip(health_scores, 0, 100)
            return health_scores.flatten()
        except Exception as e:
            raise RuntimeError("Engine LSTM prediction failed.") from e

    def classify_fault(self, X):
        """Classify fault type using Random Forest"""
        if 'rf_classifier' not in self.models:
            raise RuntimeError("Engine fault classifier is not loaded.")

        try:
            # Reshape if necessary
            if len(X.shape) == 3:
                X = X.reshape(X.shape[0], -1)

            predictions = self.models['rf_classifier'].predict(X)
            probabilities = self.models['rf_classifier'].predict_proba(X)
            return predictions, probabilities
        except Exception as e:
            raise RuntimeError("Engine fault classification failed.") from e

    def predict_rul(self, X):
        """Predict Remaining Useful Life"""
        if 'rf_rul' not in self.models:
            raise RuntimeError("Engine RUL model is not loaded.")

        try:
            # Reshape if necessary
            if len(X.shape) == 3:
                X = X.reshape(X.shape[0], -1)

            rul = self.models['rf_rul'].predict(X)
            # Ensure positive RUL
            rul = np.maximum(rul, 0)
            return rul
        except Exception as e:
            raise RuntimeError("Engine RUL prediction failed.") from e

    def assess_risk(self, health_score):
        """Assess risk level based on health score"""
        if health_score >= HEALTH_GOOD:
            return RISK_NORMAL
        elif health_score >= HEALTH_WARNING:
            return RISK_LOW
        elif health_score >= HEALTH_CRITICAL:
            return RISK_MEDIUM
        else:
            return RISK_HIGH

    def get_fault_name(self, fault_id):
        """Map fault ID to fault name"""
        fault_map = {
            0: "Normal Operation",
            1: "Compressor Degradation",
            2: "Fan Blade Erosion",
            3: "Bearing Wear",
            4: "Seal Leakage",
            5: "Turbine Blade Erosion"
        }
        return fault_map.get(int(fault_id), "Unknown Fault")

    def diagnose(self, X_sequence):
        """Complete diagnosis for engine"""
        results = {
            'subsystem': 'Engine',
            'health_score': None,
            'fault': 'Unknown',
            'confidence': None,
            'risk': 'Unknown',
            'rul': None,
            'anomaly': None,
            'anomaly_score': None,
            'status': 'Unknown'
        }

        anomalies, anomaly_scores = self.detect_anomalies(X_sequence)
        results['anomaly'] = bool(anomalies[-1])
        results['anomaly_score'] = float(anomaly_scores[-1])

        # The engine LSTM was trained on RUL targets, not health labels.
        fault_pred, fault_prob = self.classify_fault(X_sequence[-1:])
        results['fault'] = self.get_fault_name(fault_pred[-1])
        results['confidence'] = float(np.max(fault_prob[-1]) * 100)

        rul = self.predict_rul(X_sequence[-1:])
        results['rul'] = float(rul[-1])

        return results
