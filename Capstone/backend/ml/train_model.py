import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from ml.dataset_generator import generate_synthetic_dataset

FEATURE_COLUMNS = [
    'requests_per_min',
    'failed_logins',
    'endpoint_freq_score',
    'status_4xx_ratio',
    'status_5xx_ratio',
    'auth_failures'
]

def train_isolation_forest(dataset_path="backend/ml/api_traffic_dataset.csv", model_output_path="backend/ml/model.pkl"):
    if not os.path.exists(dataset_path):
        generate_synthetic_dataset(output_path=dataset_path)

    df = pd.read_csv(dataset_path)
    X = df[FEATURE_COLUMNS]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest (contamination=0.05 matches our dataset's 5% anomaly ratio)
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        max_samples='auto'
    )
    model.fit(X_scaled)

    payload = {
        'model': model,
        'scaler': scaler,
        'feature_columns': FEATURE_COLUMNS
    }

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(payload, model_output_path)
    print(f"Isolation Forest model trained & saved successfully to '{model_output_path}'")
    return model_output_path

if __name__ == '__main__':
    train_isolation_forest()
