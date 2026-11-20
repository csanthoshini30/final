"""
Hydraulic Agent - Hydraulic System Health Monitoring
"""
import numpy as np
import pickle
from config.config import HYDRAULIC_MODELS_DIR, HEALTH_CRITICAL, HEALTH_WARNING, HEALTH_GOOD
from config.config import RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_NORMAL
from models.hub_loader import (
    ModelArtifactError,
    load_compatible_keras_model,
    resolve_model_path,
)


class HydraulicAgent:
    """Hydraulic subsystem monitoring agent"""

    def __init__(self):
        self.models_dir = HYDRAULIC_MODELS_DIR
        self.models = {}
        self.scaler = None
        self.load_models()

    def load_models(self):
        """Load trained models, failing clearly if any required artifact is invalid."""
        try:
            ae_path = resolve_model_path(self.models_dir, "autoencoder_hydraulic.h5")
            self.models['autoencoder'] = load_compatible_keras_model(ae_path)

            lstm_path = resolve_model_path(self.models_dir, "lstm_hydraulic.h5")
            self.models['lstm'] = load_compatible_keras_model(lstm_path)

            rf_clf_path = resolve_model_path(self.models_dir, "rf_classifier_hydraulic.pkl")
            with open(rf_clf_path, 'rb') as f:
                self.models['rf_classifier'] = pickle.load(f)

            rf_rul_path = resolve_model_path(self.models_dir, "rf_rul_hydraulic.pkl")
            with open(rf_rul_path, 'rb') as f:
                self.models['rf_rul'] = pickle.load(f)

            scaler_path = resolve_model_path(self.models_dir, "scaler_hydraulic.pkl")
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            print("Hydraulic models loaded")
        except Exception as exc:
            raise ModelArtifactError(
                f"Could not load the complete hydraulic model set: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

    def detect_anomalies(self, X):
        """Detect anomalies using autoencoder"""
        if 'autoencoder' not in self.models:
            return None, None
        try:
            X_pred = self.models['autoencoder'].predict(X, verbose=0)
            mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
            threshold = np.percentile(mse, 95)
            anomalies = mse > threshold
            return anomalies, mse
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return None, None

    def predict_health(self, X):
        """Predict health score using LSTM"""
        if 'lstm' not in self.models:
            return None
        try:
            health_scores = self.models['lstm'].predict(X, verbose=0)
            return np.clip(health_scores, 0, 100).flatten()
        except Exception as e:
            print(f"Error in health prediction: {e}")
            return None

    def classify_fault(self, X):
        """Classify fault type"""
        if 'rf_classifier' not in self.models:
            return None, None
        try:
            if len(X.shape) == 3:
                X = X.reshape(X.shape[0], -1)
            predictions = self.models['rf_classifier'].predict(X)
            probabilities = self.models['rf_classifier'].predict_proba(X)
            return predictions, probabilities
        except Exception as e:
            print(f"Error in fault classification: {e}")
            return None, None

    def predict_rul(self, X):
        """Predict Remaining Useful Life"""
        if 'rf_rul' not in self.models:
            return None
        try:
            if len(X.shape) == 3:
                X = X.reshape(X.shape[0], -1)
            return np.maximum(self.models['rf_rul'].predict(X), 0)
        except Exception as e:
            print(f"Error in RUL prediction: {e}")
            return None

    def assess_risk(self, health_score):
        """Assess risk level"""
        if health_score >= HEALTH_GOOD:
            return RISK_NORMAL
        elif health_score >= HEALTH_WARNING:
            return RISK_LOW
        elif health_score >= HEALTH_CRITICAL:
            return RISK_MEDIUM
        return RISK_HIGH

    def get_fault_name(self, fault_id):
        """Map fault ID to fault name"""
        fault_map = {
            0: "Normal Operation",
            1: "Pump Efficiency Degradation",
            2: "Pressure Regulation Fault",
            3: "Flow Rate Anomaly",
            4: "Fluid Temperature High",
            5: "Contamination Detected",
            6: "Leak Detected",
            7: "Valve Malfunction"
        }
        return fault_map.get(int(fault_id), "Unknown Fault")

    def diagnose(self, X_sequence):
        """Complete diagnosis for hydraulic system"""
        results = {
            'subsystem': 'Hydraulic', 'health_score': None, 'fault': 'Normal',
            'risk': RISK_NORMAL, 'rul': None, 'anomaly': False,
            'anomaly_score': None, 'status': 'Unknown'
        }
        try:
            anomalies, anomaly_scores = self.detect_anomalies(X_sequence)
            if anomalies is not None:
                results['anomaly'] = bool(anomalies[-1])
                results['anomaly_score'] = float(anomaly_scores[-1])
            health = self.predict_health(X_sequence)
            if health is not None:
                results['health_score'] = int(health[-1])
                results['risk'] = self.assess_risk(health[-1])
            fault_pred, _ = self.classify_fault(X_sequence[-1:])
            if fault_pred is not None:
                results['fault'] = self.get_fault_name(fault_pred[0])
            rul = self.predict_rul(X_sequence[-1:])
            if rul is not None:
                results['rul'] = int(max(0, rul[0]))
            if results['health_score'] is not None:
                if results['health_score'] >= 80:
                    results['status'] = 'Healthy'
                elif results['health_score'] >= 60:
                    results['status'] = 'Degraded'
                else:
                    results['status'] = 'Faulty'
        except Exception as e:
            print(f"Error in hydraulic diagnosis: {e}")
        return results
