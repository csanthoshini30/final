"""
Model Architectures for Aircraft Maintenance Prediction
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config.config import (
    AUTOENCODER_LATENT_DIM, LSTM_HIDDEN_DIM, AUTOENCODER_THRESHOLD
)

class AutoencoderAnomalyDetector:
    """Autoencoder for anomaly detection"""

    def __init__(self, input_shape, latent_dim=AUTOENCODER_LATENT_DIM):
        self.input_shape = input_shape
        self.latent_dim = latent_dim
        self.model = self.build_model()
        self.threshold = None

    def build_model(self):
        """Build autoencoder architecture"""
        # Encoder
        input_layer = layers.Input(shape=self.input_shape)

        if len(self.input_shape) == 2:
            # For 2D input (sequences)
            x = layers.Flatten()(input_layer)
            x = layers.Dense(128, activation='relu')(x)
            x = layers.Dense(64, activation='relu')(x)
            encoded = layers.Dense(self.latent_dim, activation='relu', name='encoding')(x)

            # Decoder
            x = layers.Dense(64, activation='relu')(encoded)
            x = layers.Dense(128, activation='relu')(x)
            decoded = layers.Dense(int(np.prod(self.input_shape)), activation='sigmoid')(x)
            decoded = layers.Reshape(self.input_shape)(decoded)
        else:
            # For 1D input
            x = layers.Dense(128, activation='relu')(input_layer)
            x = layers.Dense(64, activation='relu')(x)
            encoded = layers.Dense(self.latent_dim, activation='relu', name='encoding')(x)

            # Decoder
            x = layers.Dense(64, activation='relu')(encoded)
            x = layers.Dense(128, activation='relu')(x)
            decoded = layers.Dense(self.input_shape[0], activation='sigmoid')(x)

        autoencoder = Model(input_layer, decoded)
        return autoencoder

    def compile(self, learning_rate=0.001):
        """Compile model"""
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

    def train(self, X_train, epochs=50, batch_size=32, validation_split=0.2):
        """Train autoencoder"""
        history = self.model.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        return history

    def get_reconstruction_error(self, X):
        """Calculate reconstruction error"""
        X_pred = self.model.predict(X, verbose=0)
        mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2)) if len(X.shape) == 3 else np.mean(np.power(X - X_pred, 2), axis=1)
        return mse

    def detect_anomalies(self, X, percentile=AUTOENCODER_THRESHOLD):
        """Detect anomalies"""
        errors = self.get_reconstruction_error(X)
        self.threshold = np.percentile(errors, percentile * 100)
        anomalies = errors > self.threshold
        return anomalies, errors


class LSTMHealthPredictor:
    """LSTM for health score and RUL prediction"""

    def __init__(self, input_shape, hidden_dim=LSTM_HIDDEN_DIM):
        self.input_shape = input_shape
        self.hidden_dim = hidden_dim
        self.model = self.build_model()

    def build_model(self):
        """Build LSTM architecture"""
        model = keras.Sequential([
            layers.LSTM(self.hidden_dim, activation='relu', input_shape=self.input_shape, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(self.hidden_dim // 2, activation='relu', return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(1)
        ])
        return model

    def compile(self, learning_rate=0.001):
        """Compile model"""
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
        """Train LSTM"""
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        return history

    def predict(self, X):
        """Make predictions"""
        return self.model.predict(X, verbose=0)


class RandomForestFaultClassifier:
    """Random Forest for fault classification"""

    def __init__(self, n_estimators=100):
        self.n_estimators = n_estimators
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        self.feature_importance = None

    def prepare_features(self, X):
        """Prepare features for Random Forest"""
        if len(X.shape) == 3:
            # Reshape sequences to feature vectors
            return X.reshape(X.shape[0], -1)
        return X

    def train(self, X_train, y_train):
        """Train Random Forest"""
        X_prepared = self.prepare_features(X_train)
        self.model.fit(X_prepared, y_train)
        self.feature_importance = self.model.feature_importances_

    def predict(self, X):
        """Make predictions"""
        X_prepared = self.prepare_features(X)
        return self.model.predict(X_prepared)

    def predict_proba(self, X):
        """Predict probabilities"""
        X_prepared = self.prepare_features(X)
        return self.model.predict_proba(X_prepared)


class RandomForestRULRegressor:
    """Random Forest for RUL regression"""

    def __init__(self, n_estimators=100):
        self.n_estimators = n_estimators
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        self.feature_importance = None

    def prepare_features(self, X):
        """Prepare features for Random Forest"""
        if len(X.shape) == 3:
            # Reshape sequences to feature vectors
            return X.reshape(X.shape[0], -1)
        return X

    def train(self, X_train, y_train):
        """Train Random Forest"""
        X_prepared = self.prepare_features(X_train)
        self.model.fit(X_prepared, y_train)
        self.feature_importance = self.model.feature_importances_

    def predict(self, X):
        """Make predictions"""
        X_prepared = self.prepare_features(X)
        return self.model.predict(X_prepared)

    def evaluate(self, X, y):
        """Evaluate model"""
        predictions = self.predict(X)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mse)
        return {'mse': mse, 'rmse': rmse, 'mae': mae}
