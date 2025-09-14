from sklearn.ensemble import RandomForestRegressor, IsolationForest
import numpy as np
import pandas as pd
from typing import List, Dict
import joblib
import os

class QueuePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.features = ['hour_of_day', 'day_of_week', 'queue_length', 'staff_count', 'service_id']
        self.model_path = "ai_models/queue_predictor.joblib"

    def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model with historical data"""
        self.model.fit(X[self.features], y)
        # Save the model
        os.makedirs("ai_models", exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def predict_wait_time(self, current_state: List[float]) -> float:
        """Predict wait time based on current state"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        return self.model.predict([current_state])[0]

    def get_feature_importance(self) -> Dict[str, float]:
        """Get the importance of each feature in making predictions"""
        return dict(zip(self.features, self.model.feature_importances_))

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.features = ['queue_length', 'wait_time', 'staff_count', 'service_rate']
        self.model_path = "ai_models/anomaly_detector.joblib"

    def train(self, data: pd.DataFrame):
        """Train the anomaly detection model"""
        self.model.fit(data[self.features])
        os.makedirs("ai_models", exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def detect_anomalies(self, current_metrics: pd.DataFrame) -> List[int]:
        """Detect anomalies in current system metrics"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        predictions = self.model.predict(current_metrics[self.features])
        return [1 if p == -1 else 0 for p in predictions]  # -1 indicates anomaly
