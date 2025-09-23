"""
Wait Time Prediction API Routes
Intelligent ML-based wait time estimation using historical patterns
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import joblib
import os
from app.database import get_db
from app.models.models import QueueEntry, Service

router = APIRouter()

class WaitTimePredictionRequest(BaseModel):
    """Request model for wait time prediction"""
    arrival_hour: int
    arrival_day: int  # 0=Monday, 6=Sunday
    department: str
    age_group: str
    insurance_type: str
    appointment_type: str
    facility_occupancy: Optional[float] = 0.5
    staff_count: Optional[int] = 3

class WaitTimePredictionResponse(BaseModel):
    """Response model for wait time prediction"""
    predicted_wait_time: float
    confidence_interval: float
    min_wait_time: float
    max_wait_time: float
    model_used: str
    features_considered: int
    top_factors: List[str]
    prediction_timestamp: str
    department: str
    arrival_time: str
    day_of_week: str

class HistoricalInsightsResponse(BaseModel):
    """Response model for historical insights"""
    hourly_patterns: List[Dict]
    department_patterns: List[Dict]
    daily_patterns: List[Dict]
    average_wait_time: float
    median_wait_time: float
    peak_hours: List[int]
    busiest_departments: List[tuple]

class PracticalWaitTimePredictor:
    """Practical ML-based wait time prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = {}
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and components"""
        try:
            model_path = 'models/practical_wait_time_model.pkl'
            scaler_path = 'models/practical_wait_time_scaler.pkl'
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                
                # Load encoders
                encoder_paths = {
                    'department': 'models/practical_department_encoder.pkl',
                    'age': 'models/practical_age_encoder.pkl',
                    'insurance': 'models/practical_insurance_encoder.pkl'
                }
                
                for name, path in encoder_paths.items():
                    if os.path.exists(path):
                        self.encoders[name] = joblib.load(path)
                
                print("✅ Wait time prediction model loaded successfully")
            else:
                print("⚠️ Wait time prediction model not found. Please train the model first.")
        except Exception as e:
            print(f"❌ Error loading wait time prediction model: {e}")
    
    def predict_wait_time(self, request: WaitTimePredictionRequest) -> WaitTimePredictionResponse:
        """Predict wait time for a new patient"""
        
        if self.model is None or self.scaler is None:
            raise HTTPException(
                status_code=503, 
                detail="Wait time prediction model not available. Please train the model first."
            )
        
        # Prepare features
        features = {
            'ArrivalHour': request.arrival_hour,
            'ArrivalDayOfWeek': request.arrival_day,
            'ArrivalMonth': datetime.now().month,
            'is_peak_hour': 1 if request.arrival_hour in [8, 9, 10, 14, 15, 16] else 0,
            'is_weekend': 1 if request.arrival_day in [6, 7] else 0,
            'FacilityOccupancyRate': request.facility_occupancy,
            'ProvidersOnShift': request.staff_count,
            'NursesOnShift': request.staff_count,
            'StaffToPatientRatio': 1.0 / (request.staff_count + 0.1),
            'staff_efficiency': 1 / (1.0 / (request.staff_count + 0.1) + 0.1)
        }
        
        # Add department-specific features
        dept_avg_wait = {
            'Emergency': 45.0, 'Cardiology': 35.0, 'Neurology': 40.0,
            'General Surgery': 30.0, 'Orthopedics': 25.0, 'Internal Medicine': 20.0,
            'Pediatrics': 20.0, 'Obstetrics': 30.0, 'Radiology': 15.0
        }
        features['dept_avg_wait'] = dept_avg_wait.get(request.department, 25.0)
        
        dept_complexity = {
            'Emergency': 1.5, 'Cardiology': 1.3, 'Neurology': 1.3,
            'General Surgery': 1.2, 'Orthopedics': 1.1, 'Internal Medicine': 1.0,
            'Pediatrics': 1.0, 'Obstetrics': 1.1, 'Radiology': 0.9
        }
        features['dept_complexity'] = dept_complexity.get(request.department, 1.0)
        
        # Add patient-specific features
        age_complexity = {
            'Young Adult (18-35)': 1.0,
            'Adult (36-60)': 1.1,
            'Senior (61+)': 1.3
        }
        features['age_complexity'] = age_complexity.get(request.age_group, 1.0)
        
        insurance_complexity = {
            'Private': 1.0, 'Medicare': 1.1, 'Medicaid': 1.2,
            'Self-pay': 1.3, 'None': 1.4
        }
        features['insurance_complexity'] = insurance_complexity.get(request.insurance_type, 1.0)
        
        appointment_complexity = {
            'New Patient': 1.3, 'Specialist Referral': 1.2, 'Urgent Care': 1.1,
            'Routine checkup': 1.0, 'Follow-up procedure': 1.1
        }
        features['appointment_complexity'] = appointment_complexity.get(request.appointment_type, 1.0)
        
        # Encode categorical variables
        try:
            features['Department_encoded'] = self.encoders['department'].transform([request.department])[0]
        except:
            features['Department_encoded'] = 0
        
        try:
            features['AgeGroup_encoded'] = self.encoders['age'].transform([request.age_group])[0]
        except:
            features['AgeGroup_encoded'] = 0
        
        try:
            features['InsuranceType_encoded'] = self.encoders['insurance'].transform([request.insurance_type])[0]
        except:
            features['InsuranceType_encoded'] = 0
        
        # Convert to array and predict
        import numpy as np
        feature_array = np.array([list(features.values())]).reshape(1, -1)
        feature_array_scaled = self.scaler.transform(feature_array)
        
        predicted_wait = self.model.predict(feature_array_scaled)[0]
        
        # Ensure positive prediction
        predicted_wait = max(5.0, predicted_wait)  # Minimum 5 minutes
        
        # Add confidence interval
        confidence_interval = predicted_wait * 0.25  # ±25% confidence
        
        # Get feature importance for explanation
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'is_peak_hour', 'is_weekend',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_wait', 'dept_complexity', 'staff_efficiency',
            'age_complexity', 'insurance_complexity', 'appointment_complexity',
            'Department_encoded', 'AgeGroup_encoded', 'InsuranceType_encoded'
        ]
        
        feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return WaitTimePredictionResponse(
            predicted_wait_time=round(predicted_wait, 1),
            confidence_interval=round(confidence_interval, 1),
            min_wait_time=round(max(5.0, predicted_wait - confidence_interval), 1),
            max_wait_time=round(predicted_wait + confidence_interval, 1),
            model_used='Practical ML Predictor',
            features_considered=len(features),
            top_factors=[f"{factor}: {importance:.3f}" for factor, importance in top_factors],
            prediction_timestamp=datetime.now().isoformat(),
            department=request.department,
            arrival_time=f"{request.arrival_hour:02d}:00",
            day_of_week=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][request.arrival_day]
        )

# Initialize predictor
predictor = PracticalWaitTimePredictor()

@router.post("/predict", response_model=WaitTimePredictionResponse)
async def predict_wait_time(
    request: WaitTimePredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict wait time for a patient using ML-based historical pattern analysis
    
    - **arrival_hour**: Hour of arrival (0-23)
    - **arrival_day**: Day of week (0=Monday, 6=Sunday)
    - **department**: Hospital department
    - **age_group**: Patient age group
    - **insurance_type**: Insurance type
    - **appointment_type**: Type of appointment
    - **facility_occupancy**: Current facility occupancy (0.0-1.0)
    - **staff_count**: Number of staff on duty
    """
    try:
        prediction = predictor.predict_wait_time(request)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/insights", response_model=HistoricalInsightsResponse)
async def get_historical_insights(db: Session = Depends(get_db)):
    """
    Get historical wait time insights and patterns
    """
    try:
        # Load historical insights from saved results
        results_path = 'models/practical_wait_time_results.pkl'
        if os.path.exists(results_path):
            results = joblib.load(results_path)
            historical_patterns = results.get('historical_patterns', {})
            
            return HistoricalInsightsResponse(
                hourly_patterns=historical_patterns.get('hourly', []),
                department_patterns=historical_patterns.get('department', []),
                daily_patterns=historical_patterns.get('daily', []),
                average_wait_time=results.get('dataset_stats', {}).get('average_wait_time', 154.9),
                median_wait_time=results.get('dataset_stats', {}).get('median_wait_time', 152.3),
                peak_hours=[8, 9, 10, 14, 15, 16],
                busiest_departments=[('Emergency', 45.0), ('Cardiology', 35.0), ('Neurology', 40.0)]
            )
        else:
            # Return default insights if model not trained
            return HistoricalInsightsResponse(
                hourly_patterns=[],
                department_patterns=[],
                daily_patterns=[],
                average_wait_time=154.9,
                median_wait_time=152.3,
                peak_hours=[8, 9, 10, 14, 15, 16],
                busiest_departments=[('Emergency', 45.0), ('Cardiology', 35.0), ('Neurology', 40.0)]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """
    Get the status of the wait time prediction model
    """
    try:
        model_path = 'models/practical_wait_time_model.pkl'
        scaler_path = 'models/practical_wait_time_scaler.pkl'
        
        model_exists = os.path.exists(model_path)
        scaler_exists = os.path.exists(scaler_path)
        
        status = {
            "model_available": model_exists and scaler_exists,
            "model_path": model_path,
            "scaler_path": scaler_path,
            "model_loaded": predictor.model is not None,
            "scaler_loaded": predictor.scaler is not None,
            "encoders_loaded": len(predictor.encoders),
            "last_checked": datetime.now().isoformat()
        }
        
        if model_exists and scaler_exists:
            # Get model performance metrics
            results_path = 'models/practical_wait_time_results.pkl'
            if os.path.exists(results_path):
                results = joblib.load(results_path)
                performance = results.get('model_performance', {})
                status.update({
                    "r2_score": performance.get('r2_score', 'N/A'),
                    "mae": performance.get('mae', 'N/A'),
                    "rmse": performance.get('rmse', 'N/A'),
                    "training_date": results.get('training_date', 'N/A'),
                    "dataset_size": results.get('dataset_size', 'N/A')
                })
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.post("/train-model")
async def train_wait_time_model():
    """
    Train the wait time prediction model (admin endpoint)
    """
    try:
        # This would trigger the training process
        # For now, return a message indicating training should be done via script
        return {
            "message": "Model training should be performed using the practical_wait_time_predictor.py script",
            "command": "python practical_wait_time_predictor.py",
            "status": "training_required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/departments")
async def get_available_departments():
    """
    Get list of available departments for prediction
    """
    departments = [
        "Emergency", "Cardiology", "Neurology", "General Surgery",
        "Orthopedics", "Internal Medicine", "Pediatrics", "Obstetrics", "Radiology"
    ]
    
    return {
        "departments": departments,
        "count": len(departments)
    }

@router.get("/age-groups")
async def get_available_age_groups():
    """
    Get list of available age groups for prediction
    """
    age_groups = [
        "Young Adult (18-35)",
        "Adult (36-60)",
        "Senior (61+)"
    ]
    
    return {
        "age_groups": age_groups,
        "count": len(age_groups)
    }

@router.get("/insurance-types")
async def get_available_insurance_types():
    """
    Get list of available insurance types for prediction
    """
    insurance_types = [
        "Private", "Medicare", "Medicaid", "Self-pay", "None"
    ]
    
    return {
        "insurance_types": insurance_types,
        "count": len(insurance_types)
    }

@router.get("/appointment-types")
async def get_available_appointment_types():
    """
    Get list of available appointment types for prediction
    """
    appointment_types = [
        "New Patient", "Specialist Referral", "Urgent Care",
        "Routine checkup", "Follow-up procedure"
    ]
    
    return {
        "appointment_types": appointment_types,
        "count": len(appointment_types)
    }
