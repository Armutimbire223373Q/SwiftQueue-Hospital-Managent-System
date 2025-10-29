"""
Anomaly Detection API Routes
Automatic identification of system irregularities using multiple ML algorithms
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import joblib
import os
import pandas as pd
import numpy as np
from app.database import get_db
from app.models.models import QueueEntry, Service, Analytics

router = APIRouter()

class AnomalyDetectionRequest(BaseModel):
    """Request model for anomaly detection"""
    metrics: Dict[str, float] = Field(..., example={
        "TotalTimeInHospital": 120.0,
        "Hour": 14,
        "DayOfWeekNumeric": 1,
        "IsWeekend": 0,
        "IsPeakHour": 1,
        "WaitTimeLog": 4.8,
        "WaitTimeSqrt": 10.95,
        "WaitTimeZScore": 2.5,
        "DeptMeanWait": 60.0,
        "DeptStdWait": 20.0,
        "DeptCount": 100,
        "PatientFlowRate": 0.1
    })
    department: Optional[str] = None
    service_id: Optional[int] = None

class AnomalyDetectionResponse(BaseModel):
    """Response model for anomaly detection"""
    anomaly_count: int
    anomaly_rate: float
    anomalies: List[bool]
    analysis: Dict
    model_predictions: Dict
    detection_timestamp: str
    real_time: bool
    alert_level: Optional[str] = None
    recommended_actions: Optional[List[str]] = None

class AnomalySummaryResponse(BaseModel):
    """Response model for anomaly summary"""
    models_available: List[str]
    scalers_available: List[str]
    feature_count: int
    baseline_categories: int
    anomaly_thresholds: Dict[str, float]
    top_features: Dict[str, float]

class AdvancedAnomalyDetector:
    """Advanced anomaly detection system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.anomaly_thresholds = {}
        self.baseline_metrics = {}
        self._load_models()
        
    def _load_models(self):
        """Load trained models and components"""
        try:
            # Load models
            model_files = {
                'isolation_forest': 'models/anomaly_isolation_forest.pkl',
                'one_class_svm': 'models/anomaly_one_class_svm.pkl',
                'dbscan': 'models/anomaly_dbscan.pkl'
            }
            
            for name, file_path in model_files.items():
                if os.path.exists(file_path):
                    self.models[name] = joblib.load(file_path)
            
            # Load scalers
            scaler_files = {
                'standard': 'models/anomaly_scaler_standard.pkl',
                'robust': 'models/anomaly_scaler_robust.pkl'
            }
            
            for name, file_path in scaler_files.items():
                if os.path.exists(file_path):
                    self.scalers[name] = joblib.load(file_path)
            
            # Load metadata
            metadata_path = 'models/anomaly_detection_metadata.pkl'
            if os.path.exists(metadata_path):
                metadata = joblib.load(metadata_path)
                self.feature_importance = metadata.get('feature_importance', {})
                self.anomaly_thresholds = metadata.get('anomaly_thresholds', {})
                self.baseline_metrics = metadata.get('baseline_metrics', {})
            
            print("[SUCCESS] Advanced anomaly detection models loaded successfully")
            
        except Exception as e:
            print(f"[ERROR] Error loading anomaly detection models: {e}")
            self.models = {}
            self.scalers = {}
    
    def detect_anomalies(self, 
                        data: pd.DataFrame = None, 
                        real_time: bool = False) -> Dict:
        """Detect anomalies in the data"""
        
        if not self.models or not self.scalers:
            return self._fallback_anomaly_detection(data)
        
        # Prepare features
        feature_columns = list(self.feature_importance.keys())
        if data is None:
            return self._fallback_anomaly_detection(data)
        
        available_features = [col for col in feature_columns if col in data.columns]
        if not available_features:
            return self._fallback_anomaly_detection(data)
        
        X = data[available_features].fillna(0)
        
        # Scale features
        X_scaled_standard = self.scalers['standard'].transform(X)
        X_scaled_robust = self.scalers['robust'].transform(X)
        
        # Get predictions from all models
        predictions = {}
        
        # Isolation Forest
        iso_predictions = self.models['isolation_forest'].predict(X_scaled_standard)
        iso_scores = self.models['isolation_forest'].decision_function(X_scaled_standard)
        predictions['isolation_forest'] = {
            'predictions': iso_predictions,
            'scores': iso_scores.tolist(),
            'anomalies': (iso_predictions == -1).tolist()
        }
        
        # One-Class SVM
        svm_predictions = self.models['one_class_svm'].predict(X_scaled_robust)
        svm_scores = self.models['one_class_svm'].decision_function(X_scaled_robust)
        predictions['one_class_svm'] = {
            'predictions': svm_predictions,
            'scores': svm_scores.tolist(),
            'anomalies': (svm_predictions == -1).tolist()
        }
        
        # DBSCAN
        dbscan_labels = self.models['dbscan'].fit_predict(X_scaled_standard)
        predictions['dbscan'] = {
            'labels': dbscan_labels.tolist(),
            'anomalies': (dbscan_labels == -1).tolist()
        }
        
        # Combine results
        combined_results = self._combine_predictions(predictions, X_scaled_standard)
        
        # Analyze anomalies
        anomaly_analysis = self._analyze_anomalies(data, combined_results)
        
        return {
            'anomaly_count': combined_results['anomaly_count'],
            'anomaly_rate': combined_results['anomaly_rate'],
            'anomalies': combined_results['anomalies'].tolist(),
            'analysis': anomaly_analysis,
            'model_predictions': predictions,
            'detection_timestamp': datetime.now().isoformat(),
            'real_time': real_time
        }
    
    def _combine_predictions(self, predictions: Dict, X_scaled: np.ndarray) -> Dict:
        """Combine predictions from multiple models"""
        
        n_samples = len(X_scaled)
        anomaly_votes = np.zeros(n_samples)
        
        # Weighted voting based on model performance
        model_weights = {
            'isolation_forest': 0.4,
            'one_class_svm': 0.3,
            'dbscan': 0.3
        }
        
        for model_name, pred_data in predictions.items():
            if 'anomalies' in pred_data:
                anomalies = np.array(pred_data['anomalies'], dtype=float)
                anomaly_votes += anomalies * model_weights.get(model_name, 0.33)
        
        # Determine final anomalies (threshold: 0.5)
        final_anomalies = anomaly_votes >= 0.5
        
        return {
            'anomaly_count': int(np.sum(final_anomalies)),
            'anomaly_rate': float(np.mean(final_anomalies)),
            'anomalies': final_anomalies,
            'anomaly_scores': anomaly_votes.tolist(),
            'model_agreement': anomaly_votes.tolist()
        }
    
    def _analyze_anomalies(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Analyze detected anomalies for insights"""
        
        anomalies = results['anomalies']
        if len(anomalies) == 0 or not np.any(anomalies):
            return {'message': 'No anomalies detected', 'insights': []}
        
        anomaly_data = data[anomalies]
        
        analysis = {
            'total_anomalies': len(anomaly_data),
            'anomaly_rate': results['anomaly_rate'],
            'insights': []
        }
        
        # Analyze by department
        if 'Department' in anomaly_data.columns:
            dept_anomalies = anomaly_data['Department'].value_counts()
            analysis['department_anomalies'] = dept_anomalies.to_dict()
            
            # Find departments with highest anomaly rates
            dept_rates = {}
            for dept in data['Department'].unique():
                dept_total = len(data[data['Department'] == dept])
                dept_anomaly_count = len(anomaly_data[anomaly_data['Department'] == dept])
                dept_rates[dept] = dept_anomaly_count / dept_total if dept_total > 0 else 0
            
            if dept_rates:
                top_anomaly_dept = max(dept_rates, key=dept_rates.get)
                analysis['insights'].append(f"Department with highest anomaly rate: {top_anomaly_dept} ({dept_rates[top_anomaly_dept]:.1%})")
        
        # Analyze wait times
        if 'TotalTimeInHospital' in anomaly_data.columns:
            anomaly_wait_times = anomaly_data['TotalTimeInHospital']
            baseline_wait = self.baseline_metrics.get('overall', {}).get('mean_wait_time', 60)
            
            analysis['wait_time_analysis'] = {
                'anomaly_mean_wait': float(anomaly_wait_times.mean()),
                'baseline_mean_wait': float(baseline_wait),
                'wait_time_ratio': float(anomaly_wait_times.mean() / baseline_wait)
            }
            
            if anomaly_wait_times.mean() > baseline_wait * 1.5:
                analysis['insights'].append(f"Anomalies show significantly longer wait times ({anomaly_wait_times.mean():.1f} vs {baseline_wait:.1f} min)")
        
        return analysis
    
    def _fallback_anomaly_detection(self, data: pd.DataFrame) -> Dict:
        """Fallback anomaly detection using simple statistical methods"""
        
        if data is None or data.empty:
            return {
                'anomaly_count': 0,
                'anomaly_rate': 0.0,
                'anomalies': [],
                'analysis': {'message': 'No data provided', 'insights': []},
                'model_predictions': {},
                'detection_timestamp': datetime.now().isoformat(),
                'real_time': False
            }
        
        # Simple statistical anomaly detection
        anomalies = []
        if 'TotalTimeInHospital' in data.columns:
            wait_times = data['TotalTimeInHospital']
            mean_wait = wait_times.mean()
            std_wait = wait_times.std()
            
            # Anomalies are values > 2 standard deviations from mean
            threshold = mean_wait + 2 * std_wait
            anomalies = (wait_times > threshold).tolist()
        else:
            anomalies = [False] * len(data)
        
        return {
            'anomaly_count': sum(anomalies),
            'anomaly_rate': sum(anomalies) / len(anomalies) if anomalies else 0.0,
            'anomalies': anomalies,
            'analysis': {
                'message': 'Using statistical fallback detection',
                'insights': ['Fallback method: 2-sigma rule']
            },
            'model_predictions': {'fallback': 'statistical'},
            'detection_timestamp': datetime.now().isoformat(),
            'real_time': False
        }
    
    def get_real_time_anomaly(self, current_metrics: Dict) -> Dict:
        """Detect anomalies in real-time metrics"""
        
        # Convert to DataFrame and ensure all required features are present
        current_df = pd.DataFrame([current_metrics])
        
        # Add missing features with default values
        required_features = list(self.feature_importance.keys())
        for feature in required_features:
            if feature not in current_df.columns:
                if feature == 'DayOfWeekNumeric':
                    current_df[feature] = 1  # Default to Tuesday
                elif feature == 'Hour':
                    current_df[feature] = 12  # Default to noon
                elif feature == 'IsWeekend':
                    current_df[feature] = 0  # Default to weekday
                elif feature == 'IsPeakHour':
                    current_df[feature] = 0  # Default to non-peak
                else:
                    current_df[feature] = 0  # Default to 0
        
        # Detect anomalies
        result = self.detect_anomalies(current_df, real_time=True)
        
        # Add real-time specific analysis
        if result['anomaly_count'] > 0:
            result['alert_level'] = 'HIGH' if result['anomaly_rate'] > 0.8 else 'MEDIUM'
            result['recommended_actions'] = self._get_recommended_actions(current_metrics)
        else:
            result['alert_level'] = 'LOW'
            result['recommended_actions'] = ['Continue monitoring']
        
        return result
    
    def _get_recommended_actions(self, metrics: Dict) -> List[str]:
        """Get recommended actions based on detected anomalies"""
        actions = []
        
        baseline_wait = self.baseline_metrics.get('overall', {}).get('q95_wait_time', 120)
        
        if 'TotalTimeInHospital' in metrics and metrics['TotalTimeInHospital'] > baseline_wait:
            actions.append("Consider adding more staff or opening additional service counters")
        
        if 'queue_length' in metrics and metrics.get('queue_length', 0) > 20:
            actions.append("Implement queue management strategies or patient flow optimization")
        
        if 'service_rate' in metrics and metrics.get('service_rate', 1.0) < 0.5:
            actions.append("Review service processes for efficiency improvements")
        
        if not actions:
            actions.append("Monitor system closely and investigate root causes")
        
        return actions
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of anomaly detection system"""
        return {
            'models_available': list(self.models.keys()),
            'scalers_available': list(self.scalers.keys()),
            'feature_count': len(self.feature_importance),
            'baseline_categories': len(self.baseline_metrics),
            'anomaly_thresholds': self.anomaly_thresholds,
            'top_features': dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        }

# Initialize detector
detector = AdvancedAnomalyDetector()

@router.post("/detect", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in system metrics using advanced ML algorithms
    
    - **metrics**: Current system metrics to analyze
    - **department**: Department name (optional)
    - **service_id**: Service ID (optional)
    """
    try:
        # Convert metrics to DataFrame
        metrics_df = pd.DataFrame([request.metrics])
        
        # Detect anomalies
        result = detector.detect_anomalies(metrics_df, real_time=True)
        
        # Add alert level and recommendations
        if result['anomaly_count'] > 0:
            result['alert_level'] = 'HIGH' if result['anomaly_rate'] > 0.8 else 'MEDIUM'
            result['recommended_actions'] = detector._get_recommended_actions(request.metrics)
        else:
            result['alert_level'] = 'LOW'
            result['recommended_actions'] = ['Continue monitoring']
        
        return AnomalyDetectionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.post("/real-time", response_model=AnomalyDetectionResponse)
async def detect_real_time_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in real-time system metrics
    """
    try:
        result = detector.get_real_time_anomaly(request.metrics)
        return AnomalyDetectionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time anomaly detection failed: {str(e)}")

@router.get("/summary", response_model=AnomalySummaryResponse)
async def get_anomaly_summary():
    """
    Get summary of the anomaly detection system
    """
    try:
        summary = detector.get_anomaly_summary()
        return AnomalySummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get anomaly summary: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """
    Get the status of anomaly detection models
    """
    try:
        model_files = {
            'isolation_forest': 'models/anomaly_isolation_forest.pkl',
            'one_class_svm': 'models/anomaly_one_class_svm.pkl',
            'dbscan': 'models/anomaly_dbscan.pkl',
            'standard_scaler': 'models/anomaly_scaler_standard.pkl',
            'robust_scaler': 'models/anomaly_scaler_robust.pkl',
            'metadata': 'models/anomaly_detection_metadata.pkl'
        }
        
        status = {
            "models_loaded": len(detector.models),
            "scalers_loaded": len(detector.scalers),
            "feature_count": len(detector.feature_importance),
            "baseline_categories": len(detector.baseline_metrics),
            "files_status": {},
            "last_checked": datetime.now().isoformat()
        }
        
        for name, file_path in model_files.items():
            status["files_status"][name] = os.path.exists(file_path)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.get("/baseline-metrics")
async def get_baseline_metrics():
    """
    Get baseline metrics used for anomaly detection
    """
    try:
        return {
            "baseline_metrics": detector.baseline_metrics,
            "anomaly_thresholds": detector.anomaly_thresholds,
            "feature_importance": detector.feature_importance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get baseline metrics: {str(e)}")

@router.post("/train-models")
async def train_anomaly_models():
    """
    Train anomaly detection models (admin endpoint)
    """
    try:
        return {
            "message": "Model training should be performed using the advanced_anomaly_detector.py script",
            "command": "python advanced_anomaly_detector.py",
            "status": "training_required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/thresholds")
async def get_anomaly_thresholds():
    """
    Get anomaly detection thresholds
    """
    try:
        return {
            "thresholds": detector.anomaly_thresholds,
            "description": {
                "low": "Bottom 10% - likely anomalies",
                "medium": "Bottom 25% - potential anomalies", 
                "high": "Bottom 5% - definite anomalies",
                "extreme": "Bottom 1% - extreme anomalies"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thresholds: {str(e)}")

@router.post("/validate-metrics")
async def validate_metrics(metrics: Dict[str, float]):
    """
    Validate metrics format for anomaly detection
    """
    try:
        required_features = list(detector.feature_importance.keys())
        missing_features = [f for f in required_features if f not in metrics]
        
        return {
            "valid": len(missing_features) == 0,
            "missing_features": missing_features,
            "provided_features": list(metrics.keys()),
            "required_features": required_features,
            "validation_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
