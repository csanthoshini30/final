"""
Inference Pipeline - Make Predictions on New Data
"""
import sys
import pickle
from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reports.report_generator import ReportGenerator


def _read_dataset(source, filename, system_type):
    """Read an uploaded object or project file using its actual file format."""
    suffix = Path(filename).suffix.lower()
    if isinstance(source, pd.DataFrame):
        return source.copy()

    if isinstance(source, (str, Path)):
        path = Path(source)
        if suffix == ".txt" and system_type == "engine":
            return pd.read_csv(path, sep=r"\s+", header=None)
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path)
        return pd.read_csv(path)

    content = source.getvalue() if hasattr(source, "getvalue") else source.read()
    buffer = BytesIO(content)
    if suffix == ".txt" and system_type == "engine":
        return pd.read_csv(buffer, sep=r"\s+", header=None)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(buffer)
    return pd.read_csv(buffer)


def prepare_inference_sequences(system_type, source, filename, scaler, sequence_length=30, max_windows=256):
    """Apply the saved training scaler and sample real sliding windows for inference."""
    frame = _read_dataset(source, filename, system_type)
    if system_type == "engine":
        numeric_frame = frame.apply(pd.to_numeric, errors="coerce")
        if numeric_frame.shape[1] >= 23:
            features = numeric_frame.iloc[:, 2:23]
        else:
            features = numeric_frame.select_dtypes(include="number")
    else:
        features = frame.select_dtypes(include="number")

    expected_features = getattr(scaler, "n_features_in_", None)
    if expected_features is not None and features.shape[1] != expected_features:
        raise ValueError(
            f"{system_type.title()} data has {features.shape[1]} numeric features; "
            f"the trained scaler expects {expected_features}."
        )
    if features.empty:
        raise ValueError("The uploaded dataset contains no numeric sensor features.")

    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.ffill().bfill()
    if features.isna().any().any():
        fill_values = getattr(scaler, "mean_", np.zeros(features.shape[1]))
        features = features.fillna(pd.Series(fill_values, index=features.columns))

    scaled = scaler.transform(features.to_numpy(dtype=np.float64)).astype(np.float32)
    window_count = len(scaled) - sequence_length + 1
    if window_count <= 0:
        raise ValueError(
            f"At least {sequence_length} rows are required; received {len(scaled)}."
        )

    sample_count = min(window_count, max_windows)
    starts = np.linspace(0, window_count - 1, num=sample_count, dtype=int)
    sequences = np.stack([scaled[start:start + sequence_length] for start in starts])
    return frame, features.columns.tolist(), starts + sequence_length - 1, sequences


def run_subsystem_inference(system_type, source, filename, engine_dataset="FD003"):
    """Run the saved subsystem models on selected or uploaded sensor data."""
    from agents.electrical_agent import ElectricalAgent
    from agents.engine_agent import EngineAgent
    from agents.hydraulic_agent import HydraulicAgent

    agent_types = {
        "engine": EngineAgent,
        "electrical": ElectricalAgent,
        "hydraulic": HydraulicAgent,
    }
    if system_type not in agent_types:
        raise ValueError(f"Unsupported subsystem: {system_type}")

    dataset_name = engine_dataset if system_type == "engine" else None
    agent = agent_types[system_type](dataset_name) if dataset_name else agent_types[system_type]()
    try:
        frame, feature_names, row_positions, sequences = prepare_inference_sequences(
            system_type, source, filename, agent.scaler
        )
        required_models = {"autoencoder", "lstm", "rf_classifier", "rf_rul"}
        missing_models = required_models.difference(agent.models)
        if missing_models:
            raise RuntimeError(
                f"Required {system_type} models were not loaded: {', '.join(sorted(missing_models))}"
            )

        if system_type == "engine":
            lstm_values = np.asarray(
                agent.models["lstm"].predict(sequences, verbose=0)
            ).reshape(-1)
            health_values = None
        else:
            health_values = agent.predict_health(sequences)
            if health_values is None:
                raise RuntimeError(f"The {system_type} health model did not return predictions.")
            lstm_values = None

        rul_values = agent.predict_rul(sequences)
        anomaly_flags, anomaly_scores = agent.detect_anomalies(sequences)
        fault_ids, fault_probabilities = agent.classify_fault(sequences[-1:])
        if rul_values is None or anomaly_flags is None or fault_ids is None:
            raise RuntimeError(f"One or more {system_type} prediction models returned no result.")

        fault_id = int(fault_ids[-1])
        sampled_frame = frame.iloc[row_positions][feature_names]
        sampled_features = {
            str(name): pd.to_numeric(sampled_frame[name], errors="coerce").tolist()
            for name in feature_names
        }
        result = {
            "system": system_type,
            "dataset": filename,
            "rows": len(frame),
            "sampled_windows": len(sequences),
            "row_positions": row_positions.tolist(),
            "feature_names": feature_names,
            "feature_series": sampled_features,
            "latest_features": frame.iloc[int(row_positions[-1])].to_dict(),
            "health_score": float(health_values[-1]) if health_values is not None else None,
            "health_series": health_values.tolist() if health_values is not None else None,
            "lstm_rul_estimate": float(lstm_values[-1]) if lstm_values is not None else None,
            "lstm_rul_series": lstm_values.tolist() if lstm_values is not None else None,
            "rul": float(rul_values[-1]),
            "rul_series": np.asarray(rul_values).reshape(-1).tolist(),
            "anomaly": bool(anomaly_flags[-1]),
            "anomaly_flags": np.asarray(anomaly_flags).reshape(-1).tolist(),
            "anomaly_scores": np.asarray(anomaly_scores).reshape(-1).tolist(),
            "fault": agent.get_fault_name(fault_id),
            "fault_id": fault_id,
            "confidence": float(np.max(fault_probabilities[-1]) * 100),
            "models": sorted(agent.models),
            "model_variant": dataset_name,
        }
        return result
    finally:
        del agent
        import gc
        import tensorflow as tf

        tf.keras.backend.clear_session()
        gc.collect()

def run_inference(engine_data, electrical_data, hydraulic_data, generate_report=True):
    """
    Run complete inference pipeline

    Parameters:
    -----------
    engine_data : np.ndarray
        Engine sensor data (sequence_length, n_sensors)
    electrical_data : np.ndarray
        Electrical system data (sequence_length, n_features)
    hydraulic_data : np.ndarray
        Hydraulic system data (sequence_length, n_features)
    generate_report : bool
        Whether to generate PDF report

    Returns:
    --------
    dict : Complete assessment results
    """

    print("=" * 60)
    print("AIRCRAFT PREDICTIVE MAINTENANCE - INFERENCE")
    print("=" * 60)

    from agents.coordinator_agent import CoordinatorAgent
    from agents.electrical_agent import ElectricalAgent
    from agents.engine_agent import EngineAgent
    from agents.hydraulic_agent import HydraulicAgent
    from agents.rag_agent import RAGMaintenanceAgent

    # Initialize agents
    print("\n[1/4] Loading agents...")
    engine_agent = EngineAgent()
    electrical_agent = ElectricalAgent()
    hydraulic_agent = HydraulicAgent()
    coordinator_agent = CoordinatorAgent(engine_agent, electrical_agent, hydraulic_agent)
    rag_agent = RAGMaintenanceAgent()
    print("✓ Agents loaded")

    # Ensure data is 3D (batch_size, sequence_length, features)
    if len(engine_data.shape) == 2:
        engine_data = engine_data[np.newaxis, :, :]
    if len(electrical_data.shape) == 2:
        electrical_data = electrical_data[np.newaxis, :, :]
    if len(hydraulic_data.shape) == 2:
        hydraulic_data = hydraulic_data[np.newaxis, :, :]

    # Get individual diagnostics
    print("\n[2/4] Running subsystem diagnostics...")
    engine_result = engine_agent.diagnose(engine_data)
    electrical_result = electrical_agent.diagnose(electrical_data)
    hydraulic_result = hydraulic_agent.diagnose(hydraulic_data)
    print("✓ Subsystem diagnostics complete")

    # Get coordinator assessment
    print("\n[3/4] Coordinating multi-agent assessment...")
    coordinator_result = coordinator_agent.coordinate(
        engine_data, electrical_data, hydraulic_data
    )
    print("✓ Multi-agent coordination complete")

    # Print results
    print("\n" + "=" * 60)
    print("ASSESSMENT RESULTS")
    print("=" * 60)

    print(f"\nOverall Health Score: {coordinator_result['overall_health']}%")
    print(f"Overall Risk Level: {coordinator_result['overall_risk']}")
    print(f"Priority Subsystem: {coordinator_result['priority']}")

    print("\n--- ENGINE ---")
    print(f"  Health: {engine_result['health_score']}%")
    print(f"  Fault: {engine_result['fault']}")
    print(f"  Risk: {engine_result['risk']}")
    print(f"  RUL: {engine_result['rul']} hours")

    print("\n--- ELECTRICAL ---")
    print(f"  Health: {electrical_result['health_score']}%")
    print(f"  Fault: {electrical_result['fault']}")
    print(f"  Risk: {electrical_result['risk']}")
    print(f"  RUL: {electrical_result['rul']} hours")

    print("\n--- HYDRAULIC ---")
    print(f"  Health: {hydraulic_result['health_score']}%")
    print(f"  Fault: {hydraulic_result['fault']}")
    print(f"  Risk: {hydraulic_result['risk']}")
    print(f"  RUL: {hydraulic_result['rul']} hours")

    print("\n--- RECOMMENDATIONS ---")
    for rec in coordinator_result['recommendations'][:5]:
        print(f"  [{rec['priority']}] {rec['subsystem']}: {rec['action']}")

    # Generate report if requested
    if generate_report:
        print("\n[4/4] Generating maintenance report...")
        report_gen = ReportGenerator()
        pdf_file = report_gen.generate_maintenance_report(
            coordinator_result,
            coordinator_result['subsystem_results']
        )
        print(f"✓ Report saved: {pdf_file}")

    print("\n" + "=" * 60)
    print("INFERENCE COMPLETE")
    print("=" * 60 + "\n")

    return {
        'overall': coordinator_result,
        'engine': engine_result,
        'electrical': electrical_result,
        'hydraulic': hydraulic_result,
        'rag': rag_agent
    }


if __name__ == "__main__":
    # Generate dummy data for testing
    print("Generating test data...")
    np.random.seed(42)

    engine_test_data = np.random.randn(30, 21) * 10 + 50
    electrical_test_data = np.random.randn(30, 10) * 5 + 50
    hydraulic_test_data = np.random.randn(30, 10) * 8 + 50

    # Run inference
    results = run_inference(
        engine_test_data,
        electrical_test_data,
        hydraulic_test_data,
        generate_report=True
    )
