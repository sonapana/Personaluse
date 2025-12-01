import pandas as pd
from sklearn.ensemble import IsolationForest

def profile_data(df: pd.DataFrame) -> ProfilingReport:
    """Calculates statistics and runs anomaly detection."""
    profiles = []
    
    # Simple Profiling
    for col in ['Monthly Income', 'Customer ID']:
        # Note: Drift detection is simplified here; in production, use a dedicated library.
        profiles.append(ColumnProfile(
            name=col,
            mean=df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else 0,
            stdev=df[col].std() if pd.api.types.is_numeric_dtype(df[col]) else 0,
            missing_count=df[col].isnull().sum(),
            is_drift_detected=(df[col].mean() > 7000) # Example drift flag
        ))

    # Anomaly Detection (ML)
    if 'Monthly Income' in df.columns and pd.api.types.is_numeric_dtype(df['Monthly Income']):
        iso_forest = IsolationForest(contamination=0.01, random_state=42)
        df['anomaly'] = iso_forest.fit_predict(df[['Monthly Income']])
        anomalies = df[df['anomaly'] == -1]
        anomalies_detected = len(anomalies)
    else:
        anomalies_detected = 0

    return ProfilingReport(
        data_id="Customer_Feed_1201",
        timestamp=pd.Timestamp.now().isoformat(),
        column_profiles=profiles,
        anomalies_detected=anomalies_detected
    )