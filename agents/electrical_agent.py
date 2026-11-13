"""
Electrical Agent - Electrical System Health Monitoring
"""
import numpy as np
import pickle
import tensorflow as tf
from pathlib import Path
from config.config import ELECTRICAL_MODELS_DIR, HEALTH_CRITICAL, HEALTH_WARNING, HEALTH_GOOD
from config.config import RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_NORMAL
from models.hub_loader import ModelArtifactError, resolve_model_path

class ElectricalAgent:
    """Electrical subsystem monitoring agent"""

    def __init__(self):
        self.models_dir = ELECTRICAL_MODELS_DIR
        self.models = {}
        self.scaler = None
        self.load_models()

    def load_models(self):
        """Load trained models"""
        try:
            # Load autoencoder
            ae_path = resolve_model_path(self.models_dir, "autoencoder_electrical.h5")
            self.models['autoencoder'] = tf.keras.models.load_model(str(ae_path), compile=False)

            # Load LSTM
            lstm_path = resolve_model_path(self.models_dir, "lstm_electrical.h5")
            self.models['lstm'] = tf.keras.models.load_model(str(lstm_path), compile=False)

            # Load Random Forest classifier
            rf_clf_path = resolve_model_path(self.models_dir, "rf_classifier_electrical.pkl")
            with open(rf_clf_path, 'rb') as f:
                self.models['rf_classifier'] = pickle.load(f)

            # Load Random Forest RUL regressor
            rf_rul_path = resolve_model_path(self.models_dir, "rf_rul_electrical.pkl")
            with open(rf_rul_path, 'rb') as f:
                self.models['rf_rul'] = pickle.load(f)

            # Load scaler
            scaler_path = resolve_model_path(self.models_dir, "scaler_electrical.pkl")
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            print("Electrical models loaded")
        except ModelArtifactError:
            raise
        except Exception as e:
            print(f"Warning: Could not load all electrical models: {e}")

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
            health_scores = np.clip(health_scores, 0, 100)
            return health_scores.flatten()
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

            rul = self.models['rf_rul'].predict(X)
            rul = np.maximum(rul, 0)
            return rul
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
        else:
            return RISK_HIGH

    def get_fault_name(self, fault_id):
        """Map fault ID to fault name"""
        fault_map = {
            0: "Normal Operation",
            1: "Battery Capacity Loss",
            2: "Voltage Regulation Fault",
            3: "Current Overload",
            4: "Generator Degradation",
            5: "Connection Fault",
            6: "Thermal Overload"
        }
        return fault_map.get(int(fault_id), "Unknown Fault")

    def diagnose(self, X_sequence):
        """Complete diagnosis for electrical system"""
        results = {
            'subsystem': 'Electrical',
            'health_score': None,
            'fault': 'Normal',
            'risk': RISK_NORMAL,
            'rul': None,
            'anomaly': False,
            'anomaly_score': None,
            'status': 'Unknown'
        }

        try:
            # Detect anomalies
            anomalies, anomaly_scores = self.detect_anomalies(X_sequence)
            if anomalies is not None:
                results['anomaly'] = bool(anomalies[-1])
                results['anomaly_score'] = float(anomaly_scores[-1])

            # Predict health
            health = self.predict_health(X_sequence)
            if health is not None:
                results['health_score'] = int(health[-1])
                results['risk'] = self.assess_risk(health[-1])

            # Classify fault
            fault_pred, fault_prob = self.classify_fault(X_sequence[-1:])
            if fault_pred is not None:
                results['fault'] = self.get_fault_name(fault_pred[0])

            # Predict RUL
            rul = self.predict_rul(X_sequence[-1:])
            if rul is not None:
                results['rul'] = int(max(0, rul[0]))

            # Determine status
            if results['health_score'] is not None:
                if results['health_score'] >= 80:
                    results['status'] = 'Healthy'
                elif results['health_score'] >= 60:
                    results['status'] = 'Degraded'
                else:
                    results['status'] = 'Faulty'

        except Exception as e:
            print(f"Error in electrical diagnosis: {e}")

        return results
