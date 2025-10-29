"""
Peak Time Prediction API Routes
Forecasting busy periods for better preparation using ML and time series analysis
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
from app.models.models import Service, QueueEntry
from sqlalchemy import func

router = APIRouter()

class PeakTimePredictionRequest(BaseModel):
    """Request model for peak time prediction"""
    department: Optional[str] = Field(None, example="Emergency")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, example=1, description="0=Monday, 6=Sunday")
    hours_ahead: Optional[int] = Field(24, ge=1, le=168, example=24, description="Hours to predict ahead")
    include_weekend: Optional[bool] = Field(True, example=True)

class PeakTimePredictionResponse(BaseModel):
    """Response model for peak time prediction"""
    department: str
    day_of_week: int
    is_weekend: bool
    hours_ahead: int
    peak_analysis: Dict
    hourly_predictions: List[Dict]
    recommendations: List[str]
    prediction_timestamp: str

class DepartmentAnalysisResponse(BaseModel):
    """Response model for department analysis"""
    department: str
    base_multiplier: float
    peak_hours: List[int]
    weekend_factor: float
    hourly_pattern: Dict[int, int]
    pattern_description: str

class AdvancedPeakTimePredictor:
    """Advanced peak time prediction system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.department_patterns = {}
        self.seasonal_patterns = {}
        self.holiday_patterns = {}
        self.peak_thresholds = {}
        self._load_models()
        self._initialize_parameters()
        
    def _initialize_parameters(self):
        """Initialize prediction parameters and thresholds"""
        
        # Peak time thresholds (percentiles)
        self.peak_thresholds = {
            'low': 0.25,      # Bottom 25% - off-peak
            'medium': 0.50,   # Middle 50% - normal
            'high': 0.75,    # Top 25% - peak
            'extreme': 0.90   # Top 10% - extreme peak
        }
        
        # Seasonal patterns
        self.seasonal_patterns = {
            'spring': {'multiplier': 1.0, 'peak_hours': [9, 14, 16]},
            'summer': {'multiplier': 0.9, 'peak_hours': [8, 13, 15]},
            'fall': {'multiplier': 1.1, 'peak_hours': [9, 14, 16]},
            'winter': {'multiplier': 1.2, 'peak_hours': [8, 12, 15]}
        }
        
        # Holiday patterns
        self.holiday_patterns = {
            'regular': {'multiplier': 1.0, 'pattern': 'normal'},
            'holiday': {'multiplier': 0.7, 'pattern': 'reduced'},
            'pre_holiday': {'multiplier': 1.3, 'pattern': 'increased'},
            'post_holiday': {'multiplier': 1.4, 'pattern': 'catch_up'}
        }
        
        # Department-specific patterns
        self.department_patterns = {
            'Emergency': {'base_multiplier': 1.0, 'peak_hours': [8, 14, 20], 'weekend_factor': 1.2, 'hourly_pattern': {}, 'pattern_description': 'Emergency shows peak activity during 8:00, 14:00, 20:00'},
            'Cardiology': {'base_multiplier': 0.9, 'peak_hours': [9, 15, 16], 'weekend_factor': 0.8, 'hourly_pattern': {}, 'pattern_description': 'Cardiology shows peak activity during 9:00, 15:00, 16:00'},
            'Neurology': {'base_multiplier': 0.9, 'peak_hours': [10, 14, 15], 'weekend_factor': 0.9, 'hourly_pattern': {}, 'pattern_description': 'Neurology shows peak activity during 10:00, 14:00, 15:00'},
            'Orthopedics': {'base_multiplier': 0.8, 'peak_hours': [9, 13, 16], 'weekend_factor': 1.1, 'hourly_pattern': {}, 'pattern_description': 'Orthopedics shows peak activity during 9:00, 13:00, 16:00'},
            'General Surgery': {'base_multiplier': 0.9, 'peak_hours': [8, 12, 15], 'weekend_factor': 0.7, 'hourly_pattern': {}, 'pattern_description': 'General Surgery shows peak activity during 8:00, 12:00, 15:00'},
            'Internal Medicine': {'base_multiplier': 0.6, 'peak_hours': [9, 14, 16], 'weekend_factor': 0.8, 'hourly_pattern': {}, 'pattern_description': 'Internal Medicine shows peak activity during 9:00, 14:00, 16:00'},
            'Pediatrics': {'base_multiplier': 0.8, 'peak_hours': [10, 15, 17], 'weekend_factor': 1.0, 'hourly_pattern': {}, 'pattern_description': 'Pediatrics shows peak activity during 10:00, 15:00, 17:00'},
            'Obstetrics': {'base_multiplier': 0.9, 'peak_hours': [8, 14, 20], 'weekend_factor': 1.1, 'hourly_pattern': {}, 'pattern_description': 'Obstetrics shows peak activity during 8:00, 14:00, 20:00'},
            'Radiology': {'base_multiplier': 0.7, 'peak_hours': [9, 13, 15], 'weekend_factor': 0.6, 'hourly_pattern': {}, 'pattern_description': 'Radiology shows peak activity during 9:00, 13:00, 15:00'},
            'Oncology': {'base_multiplier': 0.9, 'peak_hours': [9, 14, 16], 'weekend_factor': 0.8, 'hourly_pattern': {}, 'pattern_description': 'Oncology shows peak activity during 9:00, 14:00, 16:00'}
        }
    
    def _load_models(self):
        """Load trained models and components"""
        try:
            # Load models
            model_files = {
                'random_forest': 'models/peak_time_random_forest.pkl',
                'gradient_boosting': 'models/peak_time_gradient_boosting.pkl'
            }
            
            for name, file_path in model_files.items():
                if os.path.exists(file_path):
                    self.models[name] = joblib.load(file_path)
            
            # Load scaler
            scaler_path = 'models/peak_time_scaler.pkl'
            if os.path.exists(scaler_path):
                self.scalers['standard'] = joblib.load(scaler_path)
            
            # Load metadata
            metadata_path = 'models/peak_time_prediction_metadata.pkl'
            if os.path.exists(metadata_path):
                metadata = joblib.load(metadata_path)
                self.feature_importance = metadata.get('feature_importance', {})
                self.department_patterns = metadata.get('department_patterns', {})
                self.seasonal_patterns = metadata.get('seasonal_patterns', {})
                self.holiday_patterns = metadata.get('holiday_patterns', {})
                self.peak_thresholds = metadata.get('peak_thresholds', {})
            
            print("[SUCCESS] Advanced peak time prediction models loaded successfully")
            
        except Exception as e:
            print(f"[ERROR] Error loading peak time prediction models: {e}")
            self.models = {}
            self.scalers = {}
    
    def predict_peak_times(self, 
                          department: str = None,
                          day_of_week: int = None,
                          hours_ahead: int = 24,
                          include_weekend: bool = True) -> Dict:
        """Predict peak times for a department or overall"""
        
        # Use current day if not provided
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        
        is_weekend = day_of_week >= 5
        
        # Get predictions for all hours
        hours = np.arange(24)
        predictions = []
        
        for hour in hours:
            # Prepare features for this hour
            features = self._prepare_prediction_features(
                hour, day_of_week, is_weekend, department
            )
            
            # Scale features
            features_scaled = self.scalers['standard'].transform([features])
            
            # Get prediction from ensemble
            rf_pred = self.models['random_forest'].predict(features_scaled)[0]
            gb_pred = self.models['gradient_boosting'].predict(features_scaled)[0]
            
            # Ensemble prediction (weighted average)
            ensemble_pred = 0.6 * rf_pred + 0.4 * gb_pred
            
            # Apply department-specific adjustments
            if department and department in self.department_patterns:
                dept_multiplier = self.department_patterns[department]['base_multiplier']
                ensemble_pred *= dept_multiplier
                
                # Weekend adjustment
                if is_weekend:
                    weekend_factor = self.department_patterns[department]['weekend_factor']
                    ensemble_pred *= weekend_factor
            
            predictions.append({
                'hour': int(hour),
                'predicted_volume': round(ensemble_pred, 2),
                'random_forest_pred': round(rf_pred, 2),
                'gradient_boosting_pred': round(gb_pred, 2),
                'ensemble_pred': round(ensemble_pred, 2)
            })
        
        # Identify peak times
        volumes = [p['predicted_volume'] for p in predictions]
        peak_analysis = self._analyze_peak_times(volumes)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            peak_analysis, department, day_of_week
        )
        
        return {
            'department': department or 'Overall',
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'hours_ahead': hours_ahead,
            'peak_analysis': peak_analysis,
            'hourly_predictions': predictions,
            'recommendations': recommendations,
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _prepare_prediction_features(self, hour: int, day_of_week: int, is_weekend: bool, department: str = None) -> List[float]:
        """Prepare features for ML prediction"""
        
        # Base features
        features = [
            hour,  # Hour
            day_of_week,  # DayOfWeek
            int(is_weekend),  # IsWeekend
            np.sin(2 * np.pi * hour / 24),  # HourSin
            np.cos(2 * np.pi * hour / 24),  # HourCos
            hour ** 2,  # HourSquared
            np.sin(2 * np.pi * day_of_week / 7),  # DaySin
            np.cos(2 * np.pi * day_of_week / 7),  # DayCos
        ]
        
        # Department-specific features
        if department and department in self.department_patterns:
            dept_pattern = self.department_patterns[department]
            features.extend([
                dept_pattern.get('DeptPatientCount', 100),  # DeptPatientCount
                dept_pattern.get('DeptMeanWait', 45),  # DeptMeanWait
                dept_pattern.get('DeptStdWait', 15),  # DeptStdWait
            ])
        else:
            features.extend([100, 45, 15])  # Default values
        
        # Hourly features
        hourly_pattern = 50  # Default hourly pattern
        features.extend([
            hourly_pattern,  # HourlyPatientCount
            hourly_pattern * 0.8,  # HourlyMeanWait
            hourly_pattern * 0.2,  # HourlyStdWait
            hourly_pattern,  # HourlyVolumeMA3
            hourly_pattern,  # HourlyVolumeMA7
        ])
        
        return features
    
    def _analyze_peak_times(self, volumes: List[float]) -> Dict:
        """Analyze predicted volumes to identify peak times"""
        
        volumes_array = np.array(volumes)
        
        # Calculate thresholds
        low_threshold = np.percentile(volumes_array, self.peak_thresholds['low'] * 100)
        medium_threshold = np.percentile(volumes_array, self.peak_thresholds['medium'] * 100)
        high_threshold = np.percentile(volumes_array, self.peak_thresholds['high'] * 100)
        extreme_threshold = np.percentile(volumes_array, self.peak_thresholds['extreme'] * 100)
        
        # Categorize hours
        low_hours = [i for i, vol in enumerate(volumes) if vol <= low_threshold]
        medium_hours = [i for i, vol in enumerate(volumes) if low_threshold < vol <= medium_threshold]
        high_hours = [i for i, vol in enumerate(volumes) if medium_threshold < vol <= high_threshold]
        extreme_hours = [i for i, vol in enumerate(volumes) if vol > extreme_threshold]
        
        # Peak hours (high + extreme)
        peak_hours = high_hours + extreme_hours
        
        return {
            'thresholds': {
                'low': round(low_threshold, 2),
                'medium': round(medium_threshold, 2),
                'high': round(high_threshold, 2),
                'extreme': round(extreme_threshold, 2)
            },
            'hour_categories': {
                'low': low_hours,
                'medium': medium_hours,
                'high': high_hours,
                'extreme': extreme_hours
            },
            'peak_hours': sorted(peak_hours),
            'extreme_peak_hours': sorted(extreme_hours),
            'total_predicted_volume': round(sum(volumes), 2),
            'average_volume': round(np.mean(volumes), 2),
            'peak_volume': round(max(volumes), 2),
            'peak_hour': int(np.argmax(volumes))
        }
    
    def _generate_recommendations(self, peak_analysis: Dict, department: str, day_of_week: int) -> List[str]:
        """Generate recommendations based on peak time predictions"""
        
        recommendations = []
        
        peak_hours = peak_analysis['peak_hours']
        extreme_hours = peak_analysis['extreme_peak_hours']
        
        if len(peak_hours) > 0:
            peak_hours_str = ', '.join([f"{h}:00" for h in peak_hours])
            recommendations.append(f"📈 Peak hours predicted: {peak_hours_str}")
            
            if len(extreme_hours) > 0:
                extreme_hours_str = ', '.join([f"{h}:00" for h in extreme_hours])
                recommendations.append(f"🚨 Extreme peak hours: {extreme_hours_str} - consider additional staff")
        
        # Department-specific recommendations
        if department and department in self.department_patterns:
            dept_pattern = self.department_patterns[department]
            if department == 'Emergency':
                recommendations.append("🚨 Emergency department - ensure 24/7 coverage")
            elif department == 'Pediatrics':
                recommendations.append("👶 Pediatrics - consider family-friendly scheduling")
            elif department == 'Oncology':
                recommendations.append("🎗️ Oncology - plan for longer consultation times")
        
        # Day-specific recommendations
        if day_of_week == 0:  # Monday
            recommendations.append("📅 Monday - expect higher volume after weekend")
        elif day_of_week == 4:  # Friday
            recommendations.append("📅 Friday - consider pre-weekend rush")
        elif day_of_week >= 5:  # Weekend
            recommendations.append("📅 Weekend - reduced staffing may be appropriate")
        
        # Volume-based recommendations
        total_volume = peak_analysis['total_predicted_volume']
        if total_volume > 1000:
            recommendations.append("📊 High predicted volume - consider opening additional service counters")
        elif total_volume < 500:
            recommendations.append("📊 Low predicted volume - opportunity for staff training or maintenance")
        
        return recommendations
    
    def get_department_analysis(self, department: str) -> Dict:
        """Get detailed analysis for a department"""
        
        dept_pattern = self.department_patterns.get(department, {})
        
        return {
            'department': department,
            'base_multiplier': dept_pattern.get('base_multiplier', 1.0),
            'peak_hours': dept_pattern.get('peak_hours', [9, 14, 16]),
            'weekend_factor': dept_pattern.get('weekend_factor', 1.0),
            'hourly_pattern': dept_pattern.get('hourly_pattern', {}),
            'pattern_description': dept_pattern.get('pattern_description', f"{department} shows peak activity during 9:00, 14:00, 16:00")
        }
    
    def get_prediction_summary(self) -> Dict:
        """Get summary of peak time prediction system"""
        return {
            'models_available': list(self.models.keys()),
            'departments_analyzed': len(self.department_patterns),
            'feature_count': len(self.feature_importance),
            'peak_thresholds': self.peak_thresholds,
            'seasonal_patterns': list(self.seasonal_patterns.keys()),
            'holiday_patterns': list(self.holiday_patterns.keys()),
            'top_features': dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        }

# Initialize predictor
predictor = AdvancedPeakTimePredictor()

@router.post("/predict", response_model=PeakTimePredictionResponse)
async def predict_peak_times(
    request: PeakTimePredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict peak times for better preparation using ML and time series analysis
    
    - **department**: Department name (optional, defaults to overall)
    - **day_of_week**: Day of week (0=Monday, 6=Sunday, optional)
    - **hours_ahead**: Hours to predict ahead (1-168, default 24)
    - **include_weekend**: Include weekend patterns (default true)
    """
    try:
        prediction = predictor.predict_peak_times(
            department=request.department,
            day_of_week=request.day_of_week,
            hours_ahead=request.hours_ahead,
            include_weekend=request.include_weekend
        )
        return PeakTimePredictionResponse(**prediction)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Peak time prediction failed: {str(e)}")

@router.get("/departments/{department}", response_model=DepartmentAnalysisResponse)
async def get_department_analysis(department: str):
    """
    Get detailed analysis for a specific department
    """
    try:
        analysis = predictor.get_department_analysis(department)
        return DepartmentAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get department analysis: {str(e)}")

@router.get("/departments", response_model=List[Dict])
async def get_all_departments():
    """
    Get information about all departments
    """
    try:
        departments = []
        for dept_name, dept_info in predictor.department_patterns.items():
            departments.append({
                'name': dept_name,
                'base_multiplier': dept_info['base_multiplier'],
                'peak_hours': dept_info['peak_hours'],
                'weekend_factor': dept_info['weekend_factor'],
                'pattern_description': dept_info['pattern_description']
            })
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get departments: {str(e)}")

@router.get("/summary")
async def get_prediction_summary():
    """
    Get summary of the peak time prediction system
    """
    try:
        summary = predictor.get_prediction_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prediction summary: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """
    Get the status of peak time prediction models
    """
    try:
        model_files = {
            'random_forest': 'models/peak_time_random_forest.pkl',
            'gradient_boosting': 'models/peak_time_gradient_boosting.pkl',
            'scaler': 'models/peak_time_scaler.pkl',
            'metadata': 'models/peak_time_prediction_metadata.pkl'
        }
        
        status = {
            "models_loaded": len(predictor.models),
            "scalers_loaded": len(predictor.scalers),
            "departments_analyzed": len(predictor.department_patterns),
            "feature_count": len(predictor.feature_importance),
            "files_status": {},
            "last_checked": datetime.now().isoformat()
        }
        
        for name, file_path in model_files.items():
            status["files_status"][name] = os.path.exists(file_path)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.get("/patterns")
async def get_patterns():
    """
    Get seasonal and holiday patterns
    """
    try:
        return {
            "seasonal_patterns": predictor.seasonal_patterns,
            "holiday_patterns": predictor.holiday_patterns,
            "peak_thresholds": predictor.peak_thresholds,
            "department_patterns": predictor.department_patterns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.post("/train-models")
async def train_peak_time_models():
    """
    Train peak time prediction models (admin endpoint)
    """
    try:
        return {
            "message": "Model training should be performed using the advanced_peak_time_predictor.py script",
            "command": "python advanced_peak_time_predictor.py",
            "status": "training_required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/thresholds")
async def get_peak_thresholds():
    """
    Get peak time thresholds
    """
    try:
        return {
            "thresholds": predictor.peak_thresholds,
            "description": {
                "low": "Bottom 25% - off-peak hours",
                "medium": "Middle 50% - normal hours", 
                "high": "Top 25% - peak hours",
                "extreme": "Top 10% - extreme peak hours"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thresholds: {str(e)}")

@router.get("/current-peak")
async def get_current_peak_status():
    """
    Get current peak status for all departments
    """
    try:
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        current_predictions = {}
        for dept_name in predictor.department_patterns.keys():
            prediction = predictor.predict_peak_times(
                department=dept_name,
                day_of_week=current_day
            )
            
            current_volume = next(
                (p['predicted_volume'] for p in prediction['hourly_predictions'] if p['hour'] == current_hour),
                0
            )
            
            is_peak = current_hour in prediction['peak_analysis']['peak_hours']
            is_extreme = current_hour in prediction['peak_analysis']['extreme_peak_hours']
            
            current_predictions[dept_name] = {
                'current_hour': current_hour,
                'predicted_volume': current_volume,
                'is_peak': is_peak,
                'is_extreme': is_extreme,
                'peak_level': 'extreme' if is_extreme else 'peak' if is_peak else 'normal'
            }
        
        return {
            'current_hour': current_hour,
            'current_day': current_day,
            'department_status': current_predictions,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current peak status: {str(e)}")
