"""
Hydraulic System Data Preprocessing
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from config.config import (
    HYDRAULIC_FILES, SEQUENCE_LENGTH, HYDRAULIC_FEATURES
)

class HydraulicPreprocessor:
    """Preprocess hydraulic system data"""

    def __init__(self, sequence_length=SEQUENCE_LENGTH):
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.data = {}

    def load_hydraulic_data(self):
        """Load hydraulic datasets"""
        # Load main data
        if HYDRAULIC_FILES['data'].exists():
            data_df = pd.read_csv(HYDRAULIC_FILES['data'])
        else:
            raise FileNotFoundError(f"Hydraulic data file not found: {HYDRAULIC_FILES['data']}")

        # Load train data
        if HYDRAULIC_FILES['train'].exists():
            train_df = pd.read_csv(HYDRAULIC_FILES['train'])
        else:
            raise FileNotFoundError(f"Hydraulic train file not found: {HYDRAULIC_FILES['train']}")

        # Load test data
        test_data = {}
        for key in ['test_1', 'test_2']:
            if HYDRAULIC_FILES[key].exists():
                test_data[key] = pd.read_csv(HYDRAULIC_FILES[key])
            else:
                raise FileNotFoundError(f"Hydraulic test file not found: {HYDRAULIC_FILES[key]}")

        self.data['full'] = data_df
        self.data['train'] = train_df
        self.data['test'] = test_data

        return data_df, train_df, test_data

    def handle_missing_values(self, df):
        """Handle missing values"""
        # Fill forward then backward
        df = df.ffill().bfill()
        # Fill remaining with mean (numeric columns only)
        numeric_df = df.select_dtypes(include=[np.number])
        df[numeric_df.columns] = numeric_df.fillna(numeric_df.mean())
        return df

    def detect_features(self, df):
        """Automatically detect numerical features"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        return numerical_cols

    def normalize_data(self, data, fit=False, feature_cols=None):
        """Normalize numerical features"""
        if feature_cols is None:
            feature_cols = self.detect_features(data)

        data_copy = data.copy()
        numerical_data = data[feature_cols].values

        if fit:
            normalized = self.scaler.fit_transform(numerical_data)
        else:
            normalized = self.scaler.transform(numerical_data)

        data_copy[feature_cols] = normalized
        return data_copy, feature_cols

    def create_sequences(self, data, labels=None):
        """Create sequences for LSTM"""
        X = []
        y = []

        for i in range(len(data) - self.sequence_length + 1):
            X.append(data[i:i + self.sequence_length])
            if labels is not None:
                y.append(labels[i + self.sequence_length - 1])

        return np.array(X), np.array(y) if labels is not None else None

    def create_health_labels(self, df, window=50):
        """Create synthetic health labels based on pressure and flow stability"""
        if 'pressure_main' in df.columns:
            pressure_stability = df['pressure_main'].rolling(window=window).std()
            health = 100 - (pressure_stability / pressure_stability.max() * 100)
        else:
            # Generic health based on first column
            first_col = df.iloc[:, 0]
            col_std = first_col.rolling(window=window).std()
            health = 100 - (col_std / col_std.max() * 100)

        # Clip to 0-100 range
        health = health.fillna(100).clip(0, 100)
        return health.values

    def preprocess_data(self):
        """Complete preprocessing pipeline"""
        print("Processing hydraulic data...")

        # Load data
        data_df, train_df, test_data = self.load_hydraulic_data()

        # Handle missing values
        train_df = self.handle_missing_values(train_df)
        test_data = {k: self.handle_missing_values(v) for k, v in test_data.items()}

        # Detect features
        feature_cols = self.detect_features(train_df)

        # Normalize training data
        train_normalized, _ = self.normalize_data(train_df, fit=True, feature_cols=feature_cols)

        # Normalize test data
        test_normalized = {}
        for key, df in test_data.items():
            test_norm, _ = self.normalize_data(df, fit=False, feature_cols=feature_cols)
            test_normalized[key] = test_norm

        # Create health labels
        train_health = self.create_health_labels(train_df)

        # Create sequences for training
        X_train, y_train = self.create_sequences(
            train_normalized[feature_cols].values,
            train_health
        )

        # Create sequences for testing
        X_test_1, _ = self.create_sequences(test_normalized['test_1'][feature_cols].values)
        X_test_2, _ = self.create_sequences(test_normalized['test_2'][feature_cols].values)

        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_test_1': X_test_1,
            'X_test_2': X_test_2,
            'scaler': self.scaler,
            'feature_cols': feature_cols,
            'train_df': train_df,
            'test_df_1': test_data['test_1'],
            'test_df_2': test_data['test_2']
        }


def get_hydraulic_preprocessor():
    """Factory function for hydraulic preprocessor"""
    return HydraulicPreprocessor()
