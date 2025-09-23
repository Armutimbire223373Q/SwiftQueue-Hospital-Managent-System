"""
Staff Optimization API Routes
AI recommendations for optimal staffing levels using ML and operational research
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

class StaffOptimizationRequest(BaseModel):
    """Request model for staff optimization"""
    department: str = Field(..., example="Emergency")
    current_metrics: Dict[str, float] = Field(..., example={
        "providers_on_shift": 3,
        "nurses_on_shift": 6,
        "patient_count": 15,
        "facility_occupancy": 0.8,
        "hour": 14,
        "day_of_week": 1,
        "is_weekend": 0,
        "is_peak_hour": 1
    })
    optimization_horizon: Optional[int] = Field(4, example=4)

class StaffOptimizationResponse(BaseModel):
    """Response model for staff optimization"""
    department: str
    current_staffing: Dict[str, int]
    optimized_staffing: Dict[str, int]
    staff_adjustments: Dict[str, int]
    performance_prediction: Dict[str, float]
    optimization_score: float
    recommendations: List[str]
    cost_analysis: Dict[str, float]
    optimization_timestamp: str

class DepartmentAnalysisResponse(BaseModel):
    """Response model for department analysis"""
    department: str
    baseline_staffing: Dict[str, int]
    complexity_score: float
    average_wait_time: float
    patient_volume: int
    peak_hours: List[int]
    staff_efficiency: float
    optimization_constraints: Dict[str, float]

class AdvancedStaffOptimizer:
    """Advanced staff optimization system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.department_baselines = {}
        self.optimization_constraints = {}
        self.cost_parameters = {}
        self._load_models()
        self._initialize_parameters()
        
    def _initialize_parameters(self):
        """Initialize optimization parameters and constraints"""
        
        # Cost parameters (per hour)
        self.cost_parameters = {
            'provider_hourly_cost': 75.0,  # $75/hour for providers
            'nurse_hourly_cost': 45.0,     # $45/hour for nurses
            'overtime_multiplier': 1.5,    # 1.5x for overtime
            'understaffing_cost': 200.0,   # Cost of patient dissatisfaction
            'overstaffing_cost': 50.0      # Cost of idle staff
        }
        
        # Optimization constraints
        self.optimization_constraints = {
            'min_providers': 1,             # Minimum providers per department
            'max_providers': 10,            # Maximum providers per department
            'min_nurses': 1,                # Minimum nurses per department
            'max_nurses': 20,               # Maximum nurses per department
            'provider_nurse_ratio_min': 0.2, # Minimum provider:nurse ratio
            'provider_nurse_ratio_max': 2.0, # Maximum provider:nurse ratio
            'max_staff_to_patient_ratio': 0.8, # Maximum staff:patient ratio
            'min_staff_to_patient_ratio': 0.1  # Minimum staff:patient ratio
        }
        
        # Department-specific parameters
        self.department_baselines = {
            'Emergency': {'base_providers': 3, 'base_nurses': 6, 'complexity': 1.0, 'avg_wait_time': 45.0, 'patient_volume': 486, 'peak_hours': [8, 14, 20], 'staff_efficiency': 0.7},
            'Cardiology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9, 'avg_wait_time': 40.0, 'patient_volume': 485, 'peak_hours': [9, 15, 16], 'staff_efficiency': 0.8},
            'Neurology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9, 'avg_wait_time': 42.0, 'patient_volume': 499, 'peak_hours': [10, 14, 15], 'staff_efficiency': 0.75},
            'Orthopedics': {'base_providers': 2, 'base_nurses': 3, 'complexity': 0.8, 'avg_wait_time': 38.0, 'patient_volume': 492, 'peak_hours': [9, 13, 16], 'staff_efficiency': 0.8},
            'General Surgery': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9, 'avg_wait_time': 44.0, 'patient_volume': 506, 'peak_hours': [8, 12, 15], 'staff_efficiency': 0.7},
            'Internal Medicine': {'base_providers': 1, 'base_nurses': 2, 'complexity': 0.6, 'avg_wait_time': 35.0, 'patient_volume': 505, 'peak_hours': [9, 14, 16], 'staff_efficiency': 0.85},
            'Pediatrics': {'base_providers': 2, 'base_nurses': 3, 'complexity': 0.8, 'avg_wait_time': 36.0, 'patient_volume': 527, 'peak_hours': [10, 15, 17], 'staff_efficiency': 0.8},
            'Obstetrics': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9, 'avg_wait_time': 43.0, 'patient_volume': 481, 'peak_hours': [8, 14, 20], 'staff_efficiency': 0.75},
            'Radiology': {'base_providers': 1, 'base_nurses': 2, 'complexity': 0.7, 'avg_wait_time': 32.0, 'patient_volume': 489, 'peak_hours': [9, 13, 15], 'staff_efficiency': 0.9},
            'Oncology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9, 'avg_wait_time': 48.0, 'patient_volume': 530, 'peak_hours': [9, 14, 16], 'staff_efficiency': 0.7}
        }
    
    def _load_models(self):
        """Load trained models and components"""
        try:
            # Load models
            model_files = {
                'wait_time_predictor': 'models/staff_optimizer_wait_time_predictor.pkl',
                'efficiency_predictor': 'models/staff_optimizer_efficiency_predictor.pkl'
            }
            
            for name, file_path in model_files.items():
                if os.path.exists(file_path):
                    self.models[name] = joblib.load(file_path)
            
            # Load scaler
            scaler_path = 'models/staff_optimizer_scaler.pkl'
            if os.path.exists(scaler_path):
                self.scalers['standard'] = joblib.load(scaler_path)
            
            # Load metadata
            metadata_path = 'models/staff_optimization_metadata.pkl'
            if os.path.exists(metadata_path):
                metadata = joblib.load(metadata_path)
                self.feature_importance = metadata.get('feature_importance', {})
                self.department_baselines = metadata.get('department_baselines', {})
            
            print("✅ Advanced staff optimization models loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading staff optimization models: {e}")
            self.models = {}
            self.scalers = {}
    
    def optimize_staffing(self, 
                         department: str,
                         current_metrics: Dict,
                         optimization_horizon: int = 4) -> Dict:
        """Optimize staffing levels for a department"""
        
        # Get department baseline
        dept_baseline = self.department_baselines.get(department, self.department_baselines['Internal Medicine'])
        
        # Current staffing
        current_providers = current_metrics.get('providers_on_shift', dept_baseline['base_providers'])
        current_nurses = current_metrics.get('nurses_on_shift', dept_baseline['base_nurses'])
        
        # Try different staffing combinations
        best_config = None
        best_score = float('inf')
        
        for providers in range(
            max(self.optimization_constraints['min_providers'], current_providers - 2),
            min(self.optimization_constraints['max_providers'], current_providers + 3)
        ):
            for nurses in range(
                max(self.optimization_constraints['min_nurses'], current_nurses - 3),
                min(self.optimization_constraints['max_nurses'], current_nurses + 5)
            ):
                # Check constraints
                if not self._check_constraints(providers, nurses, current_metrics):
                    continue
                
                # Predict performance with this staffing
                performance = self._predict_performance(
                    department, providers, nurses, current_metrics
                )
                
                # Calculate optimization score
                score = self._calculate_optimization_score(
                    providers, nurses, performance, current_metrics
                )
                
                if score < best_score:
                    best_score = score
                    best_config = {
                        'providers': providers,
                        'nurses': nurses,
                        'total_staff': providers + nurses,
                        'performance': performance,
                        'score': score
                    }
        
        if best_config is None:
            # Fallback to current staffing
            best_config = {
                'providers': current_providers,
                'nurses': current_nurses,
                'total_staff': current_providers + current_nurses,
                'performance': self._predict_performance(department, current_providers, current_nurses, current_metrics),
                'score': 0
            }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            department, current_providers, current_nurses, best_config, current_metrics
        )
        
        return {
            'department': department,
            'current_staffing': {
                'providers': current_providers,
                'nurses': current_nurses,
                'total_staff': current_providers + current_nurses
            },
            'optimized_staffing': {
                'providers': best_config['providers'],
                'nurses': best_config['nurses'],
                'total_staff': best_config['total_staff']
            },
            'staff_adjustments': {
                'provider_change': best_config['providers'] - current_providers,
                'nurse_change': best_config['nurses'] - current_nurses,
                'total_change': best_config['total_staff'] - (current_providers + current_nurses)
            },
            'performance_prediction': best_config['performance'],
            'optimization_score': best_config['score'],
            'recommendations': recommendations,
            'cost_analysis': self._calculate_cost_analysis(current_providers, current_nurses, best_config),
            'optimization_timestamp': datetime.now().isoformat()
        }
    
    def _check_constraints(self, providers: int, nurses: int, current_metrics: Dict) -> bool:
        """Check if staffing configuration meets constraints"""
        
        # Provider:nurse ratio constraint
        provider_nurse_ratio = providers / (nurses + 0.1)
        if not (self.optimization_constraints['provider_nurse_ratio_min'] <= 
                provider_nurse_ratio <= self.optimization_constraints['provider_nurse_ratio_max']):
            return False
        
        # Staff:patient ratio constraint
        total_staff = providers + nurses
        patient_count = current_metrics.get('patient_count', 10)
        staff_patient_ratio = total_staff / (patient_count + 0.1)
        
        if not (self.optimization_constraints['min_staff_to_patient_ratio'] <= 
                staff_patient_ratio <= self.optimization_constraints['max_staff_to_patient_ratio']):
            return False
        
        return True
    
    def _predict_performance(self, department: str, providers: int, nurses: int, current_metrics: Dict) -> Dict:
        """Predict performance with given staffing"""
        
        if not self.models:
            return self._fallback_performance_prediction(providers, nurses, current_metrics)
        
        # Prepare features for prediction
        features = self._prepare_prediction_features(department, providers, nurses, current_metrics)
        
        # Scale features
        features_scaled = self.scalers['standard'].transform([features])
        
        # Predict wait time and efficiency
        predicted_wait_time = self.models['wait_time_predictor'].predict(features_scaled)[0]
        predicted_efficiency = self.models['efficiency_predictor'].predict(features_scaled)[0]
        
        # Calculate additional metrics
        total_staff = providers + nurses
        staff_patient_ratio = total_staff / (current_metrics.get('patient_count', 10) + 0.1)
        
        return {
            'predicted_wait_time': float(predicted_wait_time),
            'predicted_efficiency': float(predicted_efficiency),
            'staff_utilization': float(min(1.0, staff_patient_ratio * 0.5)),
            'throughput': float(total_staff * predicted_efficiency * 2),  # patients per hour
            'capacity_utilization': float(min(1.0, current_metrics.get('facility_occupancy', 0.7)))
        }
    
    def _prepare_prediction_features(self, department: str, providers: int, nurses: int, current_metrics: Dict) -> List[float]:
        """Prepare features for ML prediction"""
        
        # Get department baseline
        dept_baseline = self.department_baselines.get(department, self.department_baselines['Internal Medicine'])
        
        # Calculate features
        total_staff = providers + nurses
        provider_nurse_ratio = providers / (nurses + 0.1)
        staff_efficiency = 1 / (total_staff / (current_metrics.get('patient_count', 10) + 0.1) + 0.1)
        staff_workload = (total_staff / (current_metrics.get('patient_count', 10) + 0.1)) * current_metrics.get('facility_occupancy', 0.7)
        
        # Prepare feature vector (must match training features exactly)
        features = [
            dept_baseline['avg_wait_time'],  # TotalTimeInHospital (baseline)
            current_metrics.get('day_of_week', 1),  # DayOfWeekNumeric
            current_metrics.get('is_weekend', 0),  # IsWeekend
            providers,  # ProvidersOnShift
            nurses,  # NursesOnShift
            total_staff,  # TotalStaff
            provider_nurse_ratio,  # ProviderNurseRatio
            staff_efficiency,  # StaffEfficiency
            staff_workload,  # StaffWorkload
            dept_baseline['avg_wait_time'],  # DeptMeanWait
            dept_baseline['avg_wait_time'] * 0.2,  # DeptStdWait
            0.0,  # WaitTimeZScore
            dept_baseline['patient_volume'] / 1000,  # PatientFlowRate
            current_metrics.get('facility_occupancy', 0.7),  # CapacityUtilization
            current_metrics.get('facility_occupancy', 0.7) ** 2  # CapacitySquared
        ]
        
        return features
    
    def _fallback_performance_prediction(self, providers: int, nurses: int, current_metrics: Dict) -> Dict:
        """Fallback performance prediction when ML models unavailable"""
        
        total_staff = providers + nurses
        patient_count = current_metrics.get('patient_count', 10)
        
        # Simple heuristic-based prediction
        base_wait_time = 60  # Base wait time
        staff_factor = max(0.1, 1.0 / (total_staff / patient_count + 0.1))
        predicted_wait_time = base_wait_time * staff_factor
        
        efficiency = min(1.0, total_staff / (patient_count * 0.3))
        
        return {
            'predicted_wait_time': predicted_wait_time,
            'predicted_efficiency': efficiency,
            'staff_utilization': min(1.0, total_staff / patient_count),
            'throughput': total_staff * efficiency * 1.5,
            'capacity_utilization': current_metrics.get('facility_occupancy', 0.7)
        }
    
    def _calculate_optimization_score(self, providers: int, nurses: int, performance: Dict, current_metrics: Dict) -> float:
        """Calculate optimization score (lower is better)"""
        
        # Wait time component (higher weight for longer wait times)
        wait_time_score = performance['predicted_wait_time'] * 0.4
        
        # Efficiency component
        efficiency_score = (1.0 - performance['predicted_efficiency']) * 100 * 0.3
        
        # Cost component
        hourly_cost = (providers * self.cost_parameters['provider_hourly_cost'] + 
                      nurses * self.cost_parameters['nurse_hourly_cost']) * 0.2
        
        # Utilization component (penalize over/under utilization)
        utilization = performance['staff_utilization']
        utilization_score = abs(utilization - 0.8) * 50 * 0.1
        
        total_score = wait_time_score + efficiency_score + hourly_cost + utilization_score
        
        return total_score
    
    def _generate_recommendations(self, department: str, current_providers: int, current_nurses: int, 
                                 best_config: Dict, current_metrics: Dict) -> List[str]:
        """Generate staffing recommendations"""
        
        recommendations = []
        
        provider_change = best_config['providers'] - current_providers
        nurse_change = best_config['nurses'] - current_nurses
        
        if provider_change > 0:
            recommendations.append(f"➕ Add {provider_change} provider(s) to improve wait times")
        elif provider_change < 0:
            recommendations.append(f"➖ Reduce {abs(provider_change)} provider(s) to optimize costs")
        
        if nurse_change > 0:
            recommendations.append(f"➕ Add {nurse_change} nurse(s) for better patient care")
        elif nurse_change < 0:
            recommendations.append(f"➖ Reduce {abs(nurse_change)} nurse(s) to optimize staffing")
        
        # Performance-based recommendations
        predicted_wait = best_config['performance']['predicted_wait_time']
        if predicted_wait > 45:
            recommendations.append("⚠️ Predicted wait time is high - consider additional staff")
        elif predicted_wait < 20:
            recommendations.append("✅ Excellent predicted wait time - current staffing is optimal")
        
        # Efficiency recommendations
        efficiency = best_config['performance']['predicted_efficiency']
        if efficiency < 0.6:
            recommendations.append("📈 Staff efficiency could be improved with better scheduling")
        elif efficiency > 0.9:
            recommendations.append("🎯 High staff efficiency - consider maintaining current levels")
        
        # Cost recommendations
        cost_analysis = self._calculate_cost_analysis(current_providers, current_nurses, best_config)
        if cost_analysis['cost_change'] > 0:
            recommendations.append(f"💰 Additional cost: ${cost_analysis['cost_change']:.2f}/hour")
        elif cost_analysis['cost_change'] < 0:
            recommendations.append(f"💵 Cost savings: ${abs(cost_analysis['cost_change']):.2f}/hour")
        
        return recommendations
    
    def _calculate_cost_analysis(self, current_providers: int, current_nurses: int, best_config: Dict) -> Dict:
        """Calculate cost analysis for staffing changes"""
        
        current_hourly_cost = (current_providers * self.cost_parameters['provider_hourly_cost'] + 
                             current_nurses * self.cost_parameters['nurse_hourly_cost'])
        
        optimized_hourly_cost = (best_config['providers'] * self.cost_parameters['provider_hourly_cost'] + 
                               best_config['nurses'] * self.cost_parameters['nurse_hourly_cost'])
        
        cost_change = optimized_hourly_cost - current_hourly_cost
        
        return {
            'current_hourly_cost': current_hourly_cost,
            'optimized_hourly_cost': optimized_hourly_cost,
            'cost_change': cost_change,
            'daily_cost_change': cost_change * 8,  # Assuming 8-hour shifts
            'monthly_cost_change': cost_change * 8 * 22  # Assuming 22 working days
        }
    
    def get_department_analysis(self, department: str) -> Dict:
        """Get detailed analysis for a department"""
        
        dept_baseline = self.department_baselines.get(department, {})
        
        return {
            'department': department,
            'baseline_staffing': {
                'providers': dept_baseline.get('base_providers', 2),
                'nurses': dept_baseline.get('base_nurses', 3)
            },
            'complexity_score': dept_baseline.get('complexity', 1.0),
            'average_wait_time': dept_baseline.get('avg_wait_time', 60.0),
            'patient_volume': dept_baseline.get('patient_volume', 0),
            'peak_hours': dept_baseline.get('peak_hours', [9, 14, 16]),
            'staff_efficiency': dept_baseline.get('staff_efficiency', 0.5),
            'optimization_constraints': self.optimization_constraints
        }
    
    def get_optimization_summary(self) -> Dict:
        """Get summary of staff optimization system"""
        return {
            'models_available': list(self.models.keys()),
            'departments_analyzed': len(self.department_baselines),
            'feature_count': len(self.feature_importance),
            'optimization_constraints': self.optimization_constraints,
            'cost_parameters': self.cost_parameters,
            'top_features': dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        }

# Initialize optimizer
optimizer = AdvancedStaffOptimizer()

@router.post("/optimize", response_model=StaffOptimizationResponse)
async def optimize_staffing(
    request: StaffOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize staffing levels for a department using AI and operational research
    
    - **department**: Department name
    - **current_metrics**: Current system metrics
    - **optimization_horizon**: Optimization time horizon in hours
    """
    try:
        optimization = optimizer.optimize_staffing(
            request.department, 
            request.current_metrics, 
            request.optimization_horizon
        )
        return StaffOptimizationResponse(**optimization)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Staff optimization failed: {str(e)}")

@router.get("/departments/{department}", response_model=DepartmentAnalysisResponse)
async def get_department_analysis(department: str):
    """
    Get detailed analysis for a specific department
    """
    try:
        analysis = optimizer.get_department_analysis(department)
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
        for dept_name, dept_info in optimizer.department_baselines.items():
            departments.append({
                'name': dept_name,
                'baseline_staffing': {
                    'providers': dept_info['base_providers'],
                    'nurses': dept_info['base_nurses']
                },
                'complexity_score': dept_info['complexity'],
                'average_wait_time': dept_info['avg_wait_time'],
                'patient_volume': dept_info['patient_volume'],
                'peak_hours': dept_info['peak_hours'],
                'staff_efficiency': dept_info['staff_efficiency']
            })
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get departments: {str(e)}")

@router.get("/summary")
async def get_optimization_summary():
    """
    Get summary of the staff optimization system
    """
    try:
        summary = optimizer.get_optimization_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization summary: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """
    Get the status of staff optimization models
    """
    try:
        model_files = {
            'wait_time_predictor': 'models/staff_optimizer_wait_time_predictor.pkl',
            'efficiency_predictor': 'models/staff_optimizer_efficiency_predictor.pkl',
            'scaler': 'models/staff_optimizer_scaler.pkl',
            'metadata': 'models/staff_optimization_metadata.pkl'
        }
        
        status = {
            "models_loaded": len(optimizer.models),
            "scalers_loaded": len(optimizer.scalers),
            "departments_analyzed": len(optimizer.department_baselines),
            "feature_count": len(optimizer.feature_importance),
            "files_status": {},
            "last_checked": datetime.now().isoformat()
        }
        
        for name, file_path in model_files.items():
            status["files_status"][name] = os.path.exists(file_path)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.get("/constraints")
async def get_optimization_constraints():
    """
    Get optimization constraints and parameters
    """
    try:
        return {
            "optimization_constraints": optimizer.optimization_constraints,
            "cost_parameters": optimizer.cost_parameters,
            "department_baselines": optimizer.department_baselines
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get constraints: {str(e)}")

@router.post("/train-models")
async def train_staff_optimization_models():
    """
    Train staff optimization models (admin endpoint)
    """
    try:
        return {
            "message": "Model training should be performed using the advanced_staff_optimizer.py script",
            "command": "python advanced_staff_optimizer.py",
            "status": "training_required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/validate-metrics")
async def validate_metrics(metrics: Dict[str, float]):
    """
    Validate metrics format for staff optimization
    """
    try:
        required_fields = ['providers_on_shift', 'nurses_on_shift', 'patient_count', 'facility_occupancy']
        missing_fields = [field for field in required_fields if field not in metrics]
        
        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "provided_fields": list(metrics.keys()),
            "required_fields": required_fields,
            "validation_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/cost-analysis")
async def get_cost_analysis_template():
    """
    Get cost analysis template and parameters
    """
    try:
        return {
            "cost_parameters": optimizer.cost_parameters,
            "cost_calculation_example": {
                "current_staffing": {"providers": 3, "nurses": 6},
                "optimized_staffing": {"providers": 4, "nurses": 7},
                "hourly_cost_change": 75.0,  # Additional provider cost
                "daily_cost_change": 600.0,  # 8 hours * hourly change
                "monthly_cost_change": 13200.0  # 22 days * daily change
            },
            "cost_factors": {
                "provider_hourly_cost": "Base cost per provider per hour",
                "nurse_hourly_cost": "Base cost per nurse per hour",
                "overtime_multiplier": "Multiplier for overtime hours",
                "understaffing_cost": "Cost of patient dissatisfaction",
                "overstaffing_cost": "Cost of idle staff"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost analysis: {str(e)}")
