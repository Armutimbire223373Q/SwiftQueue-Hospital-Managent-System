from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from .models import QueuePredictor, AnomalyDetector
from sqlalchemy.orm import Session
from app.models.models import QueueEntry, Service, ServiceCounter, Analytics
from sqlalchemy import func

class QueueAnalyzer:
    def __init__(self):
        self.queue_predictor = QueuePredictor()
        self.anomaly_detector = AnomalyDetector()

    def prepare_historical_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare historical data for model training"""
        # Get historical queue entries with wait times
        entries = db.query(
            QueueEntry.service_id,
            QueueEntry.created_at,
            QueueEntry.completed_at,
            QueueEntry.ai_predicted_wait,
            Service.staff_count
        ).join(Service).filter(
            QueueEntry.status == "completed"
        ).all()

        # Convert to DataFrame
        df = pd.DataFrame(entries)
        df['hour_of_day'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        df['actual_wait'] = (df['completed_at'] - df['created_at']).dt.total_seconds() / 60

        X = df[['hour_of_day', 'day_of_week', 'service_id', 'staff_count']]
        y = df['actual_wait']

        return X, y

    def train_models(self, db: Session):
        """Train both queue prediction and anomaly detection models"""
        # Train queue predictor
        X, y = self.prepare_historical_data(db)
        self.queue_predictor.train(X, y)

        # Prepare data for anomaly detection
        analytics = db.query(Analytics).all()
        analytics_df = pd.DataFrame([vars(a) for a in analytics])
        if not analytics_df.empty:
            self.anomaly_detector.train(analytics_df)

    def predict_service_wait(self, service_id: int, db: Session) -> float:
        """Predict wait time for a specific service"""
        service = db.query(Service).filter(Service.id == service_id).first()
        current_time = datetime.utcnow()
        
        current_state = [
            current_time.hour,
            current_time.weekday(),
            service_id,
            service.staff_count if service else 1,
        ]
        
        return self.queue_predictor.predict_wait_time(current_state)

    def detect_system_anomalies(self, db: Session) -> List[Dict]:
        """Detect anomalies in current system state"""
        current_metrics = self.get_current_metrics(db)
        anomalies = self.anomaly_detector.detect_anomalies(current_metrics)
        
        anomaly_descriptions = []
        for i, is_anomaly in enumerate(anomalies):
            if is_anomaly:
                metrics = current_metrics.iloc[i]
                anomaly_descriptions.append({
                    "service_id": int(metrics["service_id"]),
                    "metrics": metrics[self.anomaly_detector.features].to_dict(),
                    "severity": "high" if metrics["wait_time"] > 45 else "medium"
                })
        
        return anomaly_descriptions

    def get_current_metrics(self, db: Session) -> pd.DataFrame:
        """Get current system metrics for all services"""
        services = db.query(Service).all()
        metrics_list = []
        
        for service in services:
            queue_length = db.query(func.count(QueueEntry.id)).filter(
                QueueEntry.service_id == service.id,
                QueueEntry.status == "waiting"
            ).scalar()
            
            avg_wait = db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
                QueueEntry.service_id == service.id,
                QueueEntry.status == "waiting"
            ).scalar() or 0
            
            metrics_list.append({
                "service_id": service.id,
                "queue_length": queue_length,
                "wait_time": avg_wait,
                "staff_count": service.staff_count,
                "service_rate": service.service_rate or 1.0
            })
        
        return pd.DataFrame(metrics_list)
