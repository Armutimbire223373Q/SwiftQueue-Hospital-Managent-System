"""
AI Prediction Service for Queue Management
Provides wait time and peak time predictions using trained ML models.
"""

import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for making AI predictions using trained models."""
    
    def __init__(self):
        self.wait_time_model = None
        self.peak_time_model = None
        self.models_loaded = False
        
    def load_models(self) -> bool:
        """Load the trained models from disk."""
        try:
            # Load wait time prediction model
            wait_model_data = joblib.load('backend/models/wait_time_model.pkl')
            self.wait_time_model = wait_model_data['model']
            self.wait_time_scaler = wait_model_data['scaler']
            self.wait_time_features = wait_model_data['feature_columns']
            self.wait_time_encoders = wait_model_data.get('encoders', {})
            
            # Load peak time prediction model
            peak_model_data = joblib.load('backend/models/peak_time_model.pkl')
            self.peak_time_model = peak_model_data['model']
            self.peak_time_scaler = peak_model_data['scaler']
            self.peak_time_features = peak_model_data['feature_columns']
            self.peak_time_encoders = peak_model_data.get('encoders', {})
            
            # Load department efficiency model if available
            try:
                dept_model_data = joblib.load('backend/models/department_efficiency_model.pkl')
                self.dept_efficiency_model = dept_model_data['model']
                self.dept_efficiency_scaler = dept_model_data['scaler']
                self.dept_efficiency_features = dept_model_data['feature_columns']
                self.dept_efficiency_encoders = dept_model_data.get('encoders', {})
            except FileNotFoundError:
                logger.info("Department efficiency model not found, skipping...")
            
            self.models_loaded = True
            logger.info("Enhanced AI models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            return False
    
    def predict_wait_time(self, 
                         current_queue_length: int,
                         hour: Optional[int] = None,
                         day_of_week: Optional[int] = None,
                         is_weekend: Optional[bool] = None) -> Dict:
        """
        Predict wait time for a customer joining the queue.
        
        Args:
            current_queue_length: Current number of people in queue
            hour: Hour of day (0-23), defaults to current hour
            day_of_week: Day of week (0=Monday, 6=Sunday), defaults to current day
            is_weekend: Whether it's weekend, defaults to calculated from day_of_week
            
        Returns:
            Dict with prediction and confidence metrics
        """
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        try:
            # Use current time if not provided
            now = datetime.now()
            hour = hour if hour is not None else now.hour
            day_of_week = day_of_week if day_of_week is not None else now.weekday()
            is_weekend = is_weekend if is_weekend is not None else (day_of_week >= 5)
            
            # Determine if it's peak hour
            is_peak_hour = (
                (8 <= hour <= 10) or  # Morning peak
                (12 <= hour <= 14) or  # Lunch peak
                (17 <= hour <= 19)    # Evening peak
            )
            
            # Prepare features
            features = pd.DataFrame({
                'hour': [hour],
                'day_of_week': [day_of_week],
                'day_of_month': [now.day],
                'month': [now.month],
                'queue_length': [current_queue_length],
                'is_peak_hour': [int(is_peak_hour)],
                'is_weekend': [int(is_weekend)]
            })
            
            # Ensure all required features are present
            for feature in self.wait_time_features:
                if feature not in features.columns:
                    features[feature] = 0
            
            # Reorder columns to match training data
            features = features[self.wait_time_features]
            
            # Make prediction
            features_scaled = self.wait_time_scaler.transform(features)
            predicted_wait = self.wait_time_model.predict(features_scaled)[0]
            
            # Calculate confidence based on model performance
            confidence = min(0.95, max(0.6, 1.0 - abs(predicted_wait - 15) / 30))
            
            return {
                "predicted_wait_time_minutes": round(predicted_wait, 2),
                "confidence": round(confidence, 2),
                "peak_hour": is_peak_hour,
                "weekend": is_weekend,
                "model_info": {
                    "features_used": self.wait_time_features,
                    "queue_length": current_queue_length,
                    "hour": hour,
                    "day_of_week": day_of_week
                }
            }
            
        except Exception as e:
            logger.error(f"Error in wait time prediction: {e}")
            return {"error": str(e)}
    
    def predict_peak_times(self, 
                          day_of_week: Optional[int] = None,
                          hours_ahead: int = 24) -> Dict:
        """
        Predict peak times for the next hours.
        
        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday), defaults to current day
            hours_ahead: Number of hours to predict ahead
            
        Returns:
            Dict with peak time predictions
        """
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        try:
            # Use current day if not provided
            if day_of_week is None:
                day_of_week = datetime.now().weekday()
            
            is_weekend = day_of_week >= 5
            
            # Get predictions for all hours
            hours = np.arange(24)
            features = pd.DataFrame({
                'hour': hours,
                'day_of_week': [day_of_week] * 24,
                'hour_squared': hours ** 2,
                'hour_sin': np.sin(2 * np.pi * hours / 24),
                'hour_cos': np.cos(2 * np.pi * hours / 24),
                'is_weekend': [int(is_weekend)] * 24
            })
            
            # Ensure all required features are present
            for feature in self.peak_time_features:
                if feature not in features.columns:
                    features[feature] = 0
            
            # Reorder columns to match training data
            features = features[self.peak_time_features]
            
            # Make predictions
            features_scaled = self.peak_time_scaler.transform(features)
            predictions = self.peak_time_model.predict(features_scaled)
            
            # Identify peak times (top 25% of predictions)
            threshold = np.percentile(predictions, 75)
            peak_hours = hours[predictions >= threshold].tolist()
            
            # Create hourly predictions
            hourly_predictions = []
            for hour, pred in zip(hours, predictions):
                hourly_predictions.append({
                    "hour": int(hour),
                    "predicted_queue_length": round(pred, 2),
                    "is_peak": hour in peak_hours
                })
            
            return {
                "day_of_week": day_of_week,
                "peak_hours": peak_hours,
                "hourly_predictions": hourly_predictions,
                "recommendations": self._generate_recommendations(peak_hours, predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in peak time prediction: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, peak_hours: List[int], predictions: np.ndarray) -> List[str]:
        """Generate recommendations based on peak time predictions."""
        recommendations = []
        
        if len(peak_hours) > 0:
            # Find the busiest hour
            busiest_hour = peak_hours[np.argmax(predictions[peak_hours])]
            
            recommendations.append(f"Peak hours today: {', '.join(map(str, peak_hours))}")
            recommendations.append(f"Busiest hour: {busiest_hour}:00")
            
            # Suggest off-peak times
            off_peak_hours = [h for h in range(24) if h not in peak_hours]
            if off_peak_hours:
                recommendations.append(f"Consider visiting during off-peak hours: {', '.join(map(str, off_peak_hours[:3]))}")
        
        return recommendations
    
    def get_queue_analytics(self, queue_data: List[Dict]) -> Dict:
        """
        Analyze queue data and provide insights.
        
        Args:
            queue_data: List of queue entries with timestamps and wait times
            
        Returns:
            Dict with analytics insights
        """
        if not queue_data:
            return {"error": "No queue data provided"}
        
        try:
            df = pd.DataFrame(queue_data)
            
            # Convert timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Calculate metrics
            avg_wait_time = df['wait_time'].mean()
            max_wait_time = df['wait_time'].max()
            avg_queue_length = df['queue_length'].mean()
            
            # Peak hour analysis
            hourly_stats = df.groupby('hour').agg({
                'wait_time': 'mean',
                'queue_length': 'mean'
            }).reset_index()
            
            busiest_hour = hourly_stats.loc[hourly_stats['queue_length'].idxmax(), 'hour']
            
            return {
                "average_wait_time": round(avg_wait_time, 2),
                "max_wait_time": round(max_wait_time, 2),
                "average_queue_length": round(avg_queue_length, 2),
                "busiest_hour": int(busiest_hour),
                "hourly_statistics": hourly_stats.to_dict('records'),
                "insights": [
                    f"Average wait time: {avg_wait_time:.1f} minutes",
                    f"Busiest hour: {busiest_hour}:00",
                    f"Peak queue length: {df['queue_length'].max()} people"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in queue analytics: {e}")
            return {"error": str(e)}

# Global instance
prediction_service = PredictionService()
