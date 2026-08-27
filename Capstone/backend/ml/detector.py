import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

_model_cache = None

def get_model_payload():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            from ml.train_model import train_isolation_forest
            train_isolation_forest(model_output_path=MODEL_PATH)
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def predict_anomaly(features_dict):
    """
    Input features_dict format:
    {
        'requests_per_min': int,
        'failed_logins': int,
        'endpoint_freq_score': float (0.0 - 1.0),
        'status_4xx_ratio': float (0.0 - 1.0),
        'status_5xx_ratio': float (0.0 - 1.0),
        'auth_failures': int
    }
    Returns: dict { 'is_anomaly': bool, 'anomaly_score': float (0.0-1.0), 'classification': str }
    """
    try:
        payload = get_model_payload()
        model = payload['model']
        scaler = payload['scaler']
        feature_cols = payload['feature_columns']

        df_input = pd.DataFrame([features_dict])[feature_cols]
        scaled_input = scaler.transform(df_input)

        # Isolation Forest prediction: 1 for inliers (normal), -1 for outliers (anomalous)
        prediction = model.predict(scaled_input)[0]
        # Decision function: lower values mean more anomalous (negative for anomalies)
        raw_score = model.decision_function(scaled_input)[0]

        # Convert raw decision score into normalized anomaly score (0.0 to 1.0)
        # Normal scores are around +0.1 to +0.3, anomaly scores are around -0.1 to -0.3
        anomaly_score = round(max(0.0, min(1.0, (0.2 - raw_score) * 2.0)), 2)
        is_anomaly = bool(prediction == -1 or anomaly_score > 0.45)

        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'classification': 'ANOMALOUS' if is_anomaly else 'NORMAL',
            'raw_score': round(float(raw_score), 4)
        }
    except Exception as e:
        print(f"ML Prediction fallback triggered: {e}")
        return {
            'is_anomaly': False,
            'anomaly_score': 0.0,
            'classification': 'NORMAL',
            'raw_score': 0.0
        }
