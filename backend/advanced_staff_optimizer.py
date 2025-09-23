"""
Advanced Staff Optimization System
AI recommendations for optimal staffing levels using ML and operational research
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedStaffOptimizer:
    """Advanced staff optimization system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.department_baselines = {}
        self.optimization_constraints = {}
        self.cost_parameters = {}
        
        # Initialize optimization parameters
        self._initialize_parameters()
        
    def _initialize_parameters(self):
        """Initialize optimization parameters and constraints"""
        print("⚙️ Initializing staff optimization parameters...")
        
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
            'Emergency': {'base_providers': 3, 'base_nurses': 6, 'complexity': 1.0},
            'Cardiology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9},
            'Neurology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9},
            'Orthopedics': {'base_providers': 2, 'base_nurses': 3, 'complexity': 0.8},
            'General Surgery': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9},
            'Internal Medicine': {'base_providers': 1, 'base_nurses': 2, 'complexity': 0.6},
            'Pediatrics': {'base_providers': 2, 'base_nurses': 3, 'complexity': 0.8},
            'Obstetrics': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9},
            'Radiology': {'base_providers': 1, 'base_nurses': 2, 'complexity': 0.7},
            'Oncology': {'base_providers': 2, 'base_nurses': 4, 'complexity': 0.9}
        }
        
        print(f"   ✅ Initialized parameters for {len(self.department_baselines)} departments")
    
    def load_and_preprocess_data(self):
        """Load and preprocess hospital data for staff optimization"""
        print("📊 Loading hospital data for staff optimization...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_features()
        self._calculate_department_baselines()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean and validate the dataset"""
        print("🧹 Cleaning staff optimization dataset...")
        
        self.processed_df = self.df.copy()
        
        # Handle missing values
        numeric_columns = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_columns] = self.processed_df[numeric_columns].fillna(
            self.processed_df[numeric_columns].median()
        )
        
        # Remove extreme outliers (keep 95th percentile)
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            percentile_95 = self.processed_df[wait_time_col].quantile(0.95)
            before_count = len(self.processed_df)
            self.processed_df = self.processed_df[self.processed_df[wait_time_col] <= percentile_95]
            after_count = len(self.processed_df)
            
            if before_count != after_count:
                print(f"   Removed {before_count - after_count} extreme outliers (95th percentile: {percentile_95:.1f} min)")
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_features(self):
        """Engineer features for staff optimization"""
        print("⚙️ Engineering features for staff optimization...")
        
        # Time-based features
        if 'ArrivalTime' in self.processed_df.columns:
            self.processed_df['ArrivalTime'] = pd.to_datetime(self.processed_df['ArrivalTime'])
            self.processed_df['Hour'] = self.processed_df['ArrivalTime'].dt.hour
            self.processed_df['DayOfWeek'] = self.processed_df['ArrivalTime'].dt.dayofweek
            self.processed_df['IsWeekend'] = self.processed_df['DayOfWeek'].isin([5, 6]).astype(int)
            self.processed_df['IsPeakHour'] = self.processed_df['Hour'].isin([8, 9, 10, 14, 15, 16]).astype(int)
        elif 'DayOfWeek' in self.processed_df.columns:
            # Handle string day names
            day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
            self.processed_df['DayOfWeekNumeric'] = self.processed_df['DayOfWeek'].map(day_mapping)
            self.processed_df['IsWeekend'] = self.processed_df['DayOfWeekNumeric'].isin([5, 6]).astype(int)
        
        # Staff efficiency features
        if 'ProvidersOnShift' in self.processed_df.columns and 'NursesOnShift' in self.processed_df.columns:
            self.processed_df['TotalStaff'] = self.processed_df['ProvidersOnShift'] + self.processed_df['NursesOnShift']
            self.processed_df['ProviderNurseRatio'] = self.processed_df['ProvidersOnShift'] / (self.processed_df['NursesOnShift'] + 0.1)
            self.processed_df['StaffEfficiency'] = 1 / (self.processed_df['StaffToPatientRatio'] + 0.1)
            self.processed_df['StaffWorkload'] = self.processed_df['StaffToPatientRatio'] * self.processed_df['FacilityOccupancyRate']
        
        # Wait time features
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            self.processed_df['WaitTimeLog'] = np.log1p(self.processed_df[wait_time_col])
            self.processed_df['WaitTimeSqrt'] = np.sqrt(self.processed_df[wait_time_col])
            
            # Department-specific wait times
            self.processed_df['DeptMeanWait'] = self.processed_df.groupby('Department')[wait_time_col].transform('mean')
            self.processed_df['DeptStdWait'] = self.processed_df.groupby('Department')[wait_time_col].transform('std')
            self.processed_df['WaitTimeZScore'] = (self.processed_df[wait_time_col] - self.processed_df['DeptMeanWait']) / (self.processed_df['DeptStdWait'] + 0.1)
        
        # Patient flow features
        self.processed_df['PatientFlowRate'] = self.processed_df.groupby('Department').size() / self.processed_df.groupby('Department').size().sum()
        
        # Capacity utilization
        if 'FacilityOccupancyRate' in self.processed_df.columns:
            self.processed_df['CapacityUtilization'] = self.processed_df['FacilityOccupancyRate']
            self.processed_df['CapacitySquared'] = self.processed_df['FacilityOccupancyRate'] ** 2
        
        print(f"   ✅ Feature engineering completed: {len(self.processed_df.columns)} features")
    
    def _calculate_department_baselines(self):
        """Calculate department-specific baseline metrics"""
        print("📏 Calculating department baselines...")
        
        wait_time_col = 'TotalTimeInHospital'
        
        for dept in self.processed_df['Department'].unique():
            dept_data = self.processed_df[self.processed_df['Department'] == dept]
            
            self.department_baselines[dept] = {
                'base_providers': int(dept_data['ProvidersOnShift'].median()) if 'ProvidersOnShift' in dept_data.columns else 2,
                'base_nurses': int(dept_data['NursesOnShift'].median()) if 'NursesOnShift' in dept_data.columns else 3,
                'complexity': float(dept_data[wait_time_col].mean() / self.processed_df[wait_time_col].mean()) if wait_time_col in dept_data.columns else 1.0,
                'avg_wait_time': float(dept_data[wait_time_col].mean()) if wait_time_col in dept_data.columns else 60.0,
                'patient_volume': len(dept_data),
                'peak_hours': self._get_peak_hours(dept_data),
                'staff_efficiency': float(dept_data['StaffEfficiency'].mean()) if 'StaffEfficiency' in dept_data.columns else 0.5
            }
        
        print(f"   ✅ Department baselines calculated for {len(self.department_baselines)} departments")
    
    def _get_peak_hours(self, dept_data: pd.DataFrame) -> List[int]:
        """Get peak hours for a department"""
        if 'Hour' in dept_data.columns:
            hourly_counts = dept_data['Hour'].value_counts()
            return hourly_counts.head(3).index.tolist()
        return [9, 14, 16]  # Default peak hours
    
    def train_staff_optimization_models(self):
        """Train ML models for staff optimization"""
        print("🤖 Training staff optimization models...")
        
        # Prepare features for training
        feature_columns = [
            'TotalTimeInHospital', 'Hour', 'DayOfWeekNumeric', 'IsWeekend', 'IsPeakHour',
            'ProvidersOnShift', 'NursesOnShift', 'TotalStaff', 'ProviderNurseRatio',
            'StaffEfficiency', 'StaffWorkload', 'DeptMeanWait', 'DeptStdWait',
            'WaitTimeZScore', 'PatientFlowRate', 'CapacityUtilization', 'CapacitySquared'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in self.processed_df.columns]
        X = self.processed_df[available_features].fillna(0)
        
        print(f"   Training with {len(available_features)} features: {available_features}")
        
        # Scale features
        self.scalers['standard'] = StandardScaler()
        X_scaled = self.scalers['standard'].fit_transform(X)
        
        # Train wait time prediction model (to optimize staff based on wait times)
        y_wait_time = self.processed_df['TotalTimeInHospital']
        
        self.models['wait_time_predictor'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        
        self.models['wait_time_predictor'].fit(X_scaled, y_wait_time)
        
        # Train efficiency prediction model
        y_efficiency = self.processed_df['StaffEfficiency'] if 'StaffEfficiency' in self.processed_df.columns else np.ones(len(X))
        
        self.models['efficiency_predictor'] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
        
        self.models['efficiency_predictor'].fit(X_scaled, y_efficiency)
        
        # Calculate feature importance
        self.feature_importance = dict(zip(available_features, self.models['wait_time_predictor'].feature_importances_))
        
        # Evaluate models
        y_pred_wait = self.models['wait_time_predictor'].predict(X_scaled)
        y_pred_efficiency = self.models['efficiency_predictor'].predict(X_scaled)
        
        wait_mse = mean_squared_error(y_wait_time, y_pred_wait)
        wait_r2 = r2_score(y_wait_time, y_pred_wait)
        efficiency_mse = mean_squared_error(y_efficiency, y_pred_efficiency)
        efficiency_r2 = r2_score(y_efficiency, y_pred_efficiency)
        
        print(f"   ✅ Wait Time Model - MSE: {wait_mse:.2f}, R²: {wait_r2:.4f}")
        print(f"   ✅ Efficiency Model - MSE: {efficiency_mse:.4f}, R²: {efficiency_r2:.4f}")
        
        # Save models
        self._save_models()
        
        return len(available_features)
    
    def _save_models(self):
        """Save trained models and components"""
        os.makedirs('models', exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'models/staff_optimizer_{name}.pkl')
        
        # Save scaler
        joblib.dump(self.scalers['standard'], 'models/staff_optimizer_scaler.pkl')
        
        # Save metadata
        metadata = {
            'feature_importance': self.feature_importance,
            'department_baselines': self.department_baselines,
            'optimization_constraints': self.optimization_constraints,
            'cost_parameters': self.cost_parameters,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(metadata, 'models/staff_optimization_metadata.pkl')
        print("   ✅ Models and metadata saved")
    
    def optimize_staffing(self, 
                         department: str,
                         current_metrics: Dict,
                         optimization_horizon: int = 4) -> Dict:
        """Optimize staffing levels for a department"""
        
        # Load models if not already loaded
        if not self.models:
            self._load_models()
        
        # Get department baseline
        dept_baseline = self.department_baselines.get(department, self.department_baselines['Internal Medicine'])
        
        # Current staffing
        current_providers = current_metrics.get('providers_on_shift', dept_baseline['base_providers'])
        current_nurses = current_metrics.get('nurses_on_shift', dept_baseline['base_nurses'])
        
        # Optimization parameters
        target_wait_time = 30  # Target wait time in minutes
        max_iterations = 20
        
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
    
    def _load_models(self):
        """Load trained models and components"""
        try:
            # Load models
            self.models['wait_time_predictor'] = joblib.load('models/staff_optimizer_wait_time_predictor.pkl')
            self.models['efficiency_predictor'] = joblib.load('models/staff_optimizer_efficiency_predictor.pkl')
            
            # Load scaler
            self.scalers['standard'] = joblib.load('models/staff_optimizer_scaler.pkl')
            
            # Load metadata
            metadata = joblib.load('models/staff_optimization_metadata.pkl')
            self.feature_importance = metadata.get('feature_importance', {})
            self.department_baselines = metadata.get('department_baselines', {})
            
        except Exception as e:
            print(f"❌ Error loading staff optimization models: {e}")
            self.models = {}
            self.scalers = {}
    
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

if __name__ == "__main__":
    optimizer = AdvancedStaffOptimizer()
    
    # Load and preprocess data
    optimizer.load_and_preprocess_data()
    
    # Train models
    feature_count = optimizer.train_staff_optimization_models()
    
    # Example optimizations
    print("\n🎯 Example Staff Optimizations:")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            'department': 'Emergency',
            'current_metrics': {
                'providers_on_shift': 3,
                'nurses_on_shift': 6,
                'patient_count': 15,
                'facility_occupancy': 0.8,
                'hour': 14,
                'day_of_week': 1,
                'is_weekend': 0,
                'is_peak_hour': 1
            }
        },
        {
            'department': 'Internal Medicine',
            'current_metrics': {
                'providers_on_shift': 1,
                'nurses_on_shift': 2,
                'patient_count': 8,
                'facility_occupancy': 0.6,
                'hour': 10,
                'day_of_week': 2,
                'is_weekend': 0,
                'is_peak_hour': 1
            }
        },
        {
            'department': 'Cardiology',
            'current_metrics': {
                'providers_on_shift': 2,
                'nurses_on_shift': 4,
                'patient_count': 12,
                'facility_occupancy': 0.9,
                'hour': 16,
                'day_of_week': 3,
                'is_weekend': 0,
                'is_peak_hour': 1
            }
        }
    ]
    
    for test_case in test_cases:
        optimization = optimizer.optimize_staffing(
            test_case['department'], 
            test_case['current_metrics']
        )
        
        print(f"\n🏥 Department: {optimization['department']}")
        print(f"   Current: {optimization['current_staffing']['providers']}P + {optimization['current_staffing']['nurses']}N")
        print(f"   Optimized: {optimization['optimized_staffing']['providers']}P + {optimization['optimized_staffing']['nurses']}N")
        print(f"   Changes: {optimization['staff_adjustments']['provider_change']:+d}P, {optimization['staff_adjustments']['nurse_change']:+d}N")
        print(f"   Predicted wait: {optimization['performance_prediction']['predicted_wait_time']:.1f} min")
        print(f"   Predicted efficiency: {optimization['performance_prediction']['predicted_efficiency']:.2f}")
        
        if optimization['recommendations']:
            print(f"   Recommendations:")
            for rec in optimization['recommendations'][:3]:  # Show first 3
                print(f"     • {rec}")
    
    # Get system summary
    summary = optimizer.get_optimization_summary()
    print(f"\n📋 System Summary:")
    print(f"   Models: {len(summary['models_available'])}")
    print(f"   Departments: {summary['departments_analyzed']}")
    print(f"   Features: {summary['feature_count']}")
    print(f"   Top features: {list(summary['top_features'].keys())}")
    
    print("\n✅ Advanced Staff Optimization System Ready!")
