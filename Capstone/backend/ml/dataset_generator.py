import numpy as np
import pandas as pd
import os

def generate_synthetic_dataset(output_path="backend/ml/api_traffic_dataset.csv", n_samples=3000):
    np.random.seed(42)
    
    # 95% Normal traffic samples
    n_normal = int(n_samples * 0.95)
    normal_data = {
        'requests_per_min': np.random.poisson(lam=5, size=n_normal),
        'failed_logins': np.random.choice([0, 1], size=n_normal, p=[0.92, 0.08]),
        'endpoint_freq_score': np.random.uniform(0.7, 1.0, size=n_normal),
        'status_4xx_ratio': np.random.uniform(0.0, 0.1, size=n_normal),
        'status_5xx_ratio': np.random.uniform(0.0, 0.02, size=n_normal),
        'auth_failures': np.random.choice([0, 1], size=n_normal, p=[0.95, 0.05]),
        'label': 1 # 1 for Normal in Isolation Forest / binary label
    }
    df_normal = pd.DataFrame(normal_data)

    # 5% Anomalous traffic samples (Attack bursts, scanning, brute force)
    n_anomalous = n_samples - n_normal
    anomalous_data = {
        'requests_per_min': np.random.randint(25, 120, size=n_anomalous),
        'failed_logins': np.random.randint(4, 18, size=n_anomalous),
        'endpoint_freq_score': np.random.uniform(0.05, 0.4, size=n_anomalous),
        'status_4xx_ratio': np.random.uniform(0.4, 0.95, size=n_anomalous),
        'status_5xx_ratio': np.random.uniform(0.2, 0.8, size=n_anomalous),
        'auth_failures': np.random.randint(3, 12, size=n_anomalous),
        'label': -1 # -1 for Anomaly
    }
    df_anomalous = pd.DataFrame(anomalous_data)

    df_combined = pd.concat([df_normal, df_anomalous], ignore_index=True)
    df_combined = df_combined.sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_combined.to_csv(output_path, index=False)
    print(f"Generated synthetic API traffic dataset at '{output_path}' with {len(df_combined)} samples.")
    return output_path

if __name__ == '__main__':
    generate_synthetic_dataset()
