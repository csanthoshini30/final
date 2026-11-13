"""
Engine Data Preprocessing
NASA C-MAPSS Dataset Processing
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from config.config import (
    ENGINE_TRAIN_FILES, ENGINE_TEST_FILES, ENGINE_RUL_FILES,
    ENGINE_SENSOR_COLUMNS, SEQUENCE_LENGTH
)

class EnginePreprocessor:
    """Preprocess NASA C-MAPSS engine data"""

    def __init__(self, sequence_length=SEQUENCE_LENGTH):
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.train_data = {}
        self.test_data = {}
        self.rul_data = {}

    def load_engine_data(self, dataset_name):
        """Load engine training data from text file"""
        train_file = ENGINE_TRAIN_FILES.get(dataset_name)
        test_file = ENGINE_TEST_FILES.get(dataset_name)
        rul_file = ENGINE_RUL_FILES.get(dataset_name)

        if not train_file.exists():
            raise FileNotFoundError(f"Training file not found: {train_file}")
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")
        if not rul_file.exists():
            raise FileNotFoundError(f"RUL file not found: {rul_file}")

        # Load training data
        train_df = pd.read_csv(train_file, sep=" ", header=None)
        # Take only first 23 columns (engine_id, cycles, 21 sensors)
        train_df = train_df.iloc[:, :23]

        # Load test data
        test_df = pd.read_csv(test_file, sep=" ", header=None)
        test_df = test_df.iloc[:, :23]

        # Load RUL data
        rul_df = pd.read_csv(rul_file, header=None)

        # Set column names
        columns = ["engine_id", "cycles"] + ENGINE_SENSOR_COLUMNS
        train_df.columns = columns
        test_df.columns = columns

        self.train_data[dataset_name] = train_df
        self.test_data[dataset_name] = test_df
        self.rul_data[dataset_name] = rul_df

        return train_df, test_df, rul_df

    def create_rul_labels(self, train_df):
        """Create RUL labels from training data"""
        # Group by engine_id and get max cycles
        engine_cycles = train_df.groupby('engine_id')['cycles'].max().reset_index()
        engine_cycles.columns = ['engine_id', 'max_cycles']

        # Merge with original data
        rul_labels = train_df.merge(engine_cycles, on='engine_id')
        rul_labels['RUL'] = rul_labels['max_cycles'] - rul_labels['cycles']

        return rul_labels[['engine_id', 'cycles', 'RUL']]

    def normalize_sensors(self, data, fit=False):
        """Normalize sensor data - use actual columns from data"""
        # Get sensor columns (all except engine_id and cycles)
        sensor_cols = [col for col in data.columns if col not in ['engine_id', 'cycles']]
        sensor_data = data[sensor_cols].values

        if fit:
            normalized = self.scaler.fit_transform(sensor_data)
        else:
            normalized = self.scaler.transform(sensor_data)

        return normalized

    def create_sequences(self, data, labels=None):
        """Create sequences for LSTM"""
        X = []
        y = []

        for i in range(len(data) - self.sequence_length + 1):
            X.append(data[i:i + self.sequence_length])
            if labels is not None:
                y.append(labels[i + self.sequence_length - 1])

        return np.array(X), np.array(y) if labels is not None else None

    def preprocess_dataset(self, dataset_name):
        """Complete preprocessing pipeline for one dataset"""
        print(f"Processing {dataset_name}...")

        # Load data
        train_df, test_df, rul_df = self.load_engine_data(dataset_name)

        # Create RUL labels
        train_rul = self.create_rul_labels(train_df)

        # Normalize training sensors
        train_normalized = self.normalize_sensors(train_df, fit=True)

        # Normalize test sensors
        test_normalized = self.normalize_sensors(test_df, fit=False)

        # Create sequences for training
        X_train, y_train = self.create_sequences(
            train_normalized,
            train_rul['RUL'].values
        )

        # Create sequences for testing
        X_test, _ = self.create_sequences(test_normalized)

        # Get test RULs
        y_test = rul_df.values.flatten()

        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test,
            'y_test': y_test,
            'scaler': self.scaler,
            'train_df': train_df,
            'test_df': test_df,
            'train_rul': train_rul
        }

    def preprocess_all_datasets(self):
        """Preprocess all engine datasets"""
        datasets = {}
        for dataset_name in ENGINE_TRAIN_FILES.keys():
            datasets[dataset_name] = self.preprocess_dataset(dataset_name)
        return datasets


def combine_all_engine_data(preprocessor):
    """Combine all engine datasets"""
    all_X_train = []
    all_y_train = []

    for dataset_name in ENGINE_TRAIN_FILES.keys():
        data = preprocessor.preprocess_dataset(dataset_name)
        all_X_train.append(data['X_train'])
        all_y_train.append(data['y_train'])

    X_train_combined = np.concatenate(all_X_train, axis=0)
    y_train_combined = np.concatenate(all_y_train, axis=0)

    return X_train_combined, y_train_combined
