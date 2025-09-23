"""
Advanced Intelligent Wait Time Prediction System
ML-based estimation using comprehensive historical patterns and real-time data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedWaitTimePredictor:
    """Advanced ML-based wait time prediction using historical patterns"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.performance_metrics = {}
        self.historical_patterns = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess hospital wait time data"""
        print("📊 Loading hospital wait time dataset...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_wait_time_features()
        self._analyze_historical_patterns()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean and validate the dataset"""
        print("🧹 Cleaning wait time dataset...")
        
        self.processed_df = self.df.copy()
        
        # Handle missing values
        numeric_columns = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_columns] = self.processed_df[numeric_columns].fillna(
            self.processed_df[numeric_columns].median()
        )
        
        categorical_columns = self.processed_df.select_dtypes(include=['object']).columns
        self.processed_df[categorical_columns] = self.processed_df[categorical_columns].fillna('Unknown')
        
        # Remove outliers (wait times > 3 standard deviations)
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            mean_wait = self.processed_df[wait_time_col].mean()
            std_wait = self.processed_df[wait_time_col].std()
            outlier_threshold = mean_wait + 3 * std_wait
            
            before_count = len(self.processed_df)
            self.processed_df = self.processed_df[self.processed_df[wait_time_col] <= outlier_threshold]
            after_count = len(self.processed_df)
            
            print(f"   Removed {before_count - after_count} outliers")
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_wait_time_features(self):
        """Engineer features specifically for wait time prediction"""
        print("🔧 Engineering wait time prediction features...")
        
        # Time-based features
        if 'ArrivalHour' in self.processed_df.columns:
            self.processed_df['is_peak_hour'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if x in [8, 9, 10, 14, 15, 16] else 0
            )
            self.processed_df['is_weekend'] = self.processed_df['ArrivalDayOfWeek'].apply(
                lambda x: 1 if x in [6, 7] else 0
            )
            self.processed_df['is_morning'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if 6 <= x <= 12 else 0
            )
            self.processed_df['is_afternoon'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if 13 <= x <= 18 else 0
            )
            self.processed_df['is_evening'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if 19 <= x <= 23 else 0
            )
            
            # Cyclical time features
            self.processed_df['hour_sin'] = np.sin(2 * np.pi * self.processed_df['ArrivalHour'] / 24)
            self.processed_df['hour_cos'] = np.cos(2 * np.pi * self.processed_df['ArrivalHour'] / 24)
            self.processed_df['day_sin'] = np.sin(2 * np.pi * self.processed_df['ArrivalDayOfWeek'] / 7)
            self.processed_df['day_cos'] = np.cos(2 * np.pi * self.processed_df['ArrivalDayOfWeek'] / 7)
        
        # Department-specific features
        if 'Department' in self.processed_df.columns:
            # Department average wait times
            dept_stats = self.processed_df.groupby('Department')['TotalTimeInHospital'].agg([
                'mean', 'std', 'median', 'count'
            ]).reset_index()
            dept_stats.columns = ['Department', 'dept_avg_wait', 'dept_wait_std', 'dept_median_wait', 'dept_count']
            self.processed_df = self.processed_df.merge(dept_stats, on='Department', how='left')
            
            # Department efficiency (patients per hour)
            self.processed_df['dept_efficiency'] = self.processed_df['dept_count'] / 24  # Simplified efficiency metric
        
        # Staff and resource features
        if 'StaffToPatientRatio' in self.processed_df.columns:
            self.processed_df['staff_efficiency'] = 1 / (self.processed_df['StaffToPatientRatio'] + 0.001)
            self.processed_df['staff_workload'] = self.processed_df['StaffToPatientRatio'] * self.processed_df['FacilityOccupancyRate']
        
        if 'ProvidersOnShift' in self.processed_df.columns and 'NursesOnShift' in self.processed_df.columns:
            self.processed_df['total_staff'] = self.processed_df['ProvidersOnShift'] + self.processed_df['NursesOnShift']
            self.processed_df['provider_nurse_ratio'] = self.processed_df['ProvidersOnShift'] / (self.processed_df['NursesOnShift'] + 0.001)
        
        # Facility occupancy features
        if 'FacilityOccupancyRate' in self.processed_df.columns:
            self.processed_df['occupancy_level'] = pd.cut(
                self.processed_df['FacilityOccupancyRate'], 
                bins=[0, 0.3, 0.6, 0.8, 1.0], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            self.processed_df['occupancy_squared'] = self.processed_df['FacilityOccupancyRate'] ** 2
        
        # Patient-specific features
        if 'AgeGroup' in self.processed_df.columns:
            # Age group complexity (older patients typically take longer)
            age_complexity = {
                'Young Adult (18-35)': 1.0,
                'Adult (36-60)': 1.2,
                'Senior (61+)': 1.5
            }
            self.processed_df['age_complexity'] = self.processed_df['AgeGroup'].map(age_complexity).fillna(1.0)
        
        if 'InsuranceType' in self.processed_df.columns:
            # Insurance type processing time
            insurance_processing = {
                'Private': 1.0,
                'Medicare': 1.1,
                'Medicaid': 1.2,
                'Self-pay': 1.3,
                'None': 1.4
            }
            self.processed_df['insurance_processing_time'] = self.processed_df['InsuranceType'].map(insurance_processing).fillna(1.0)
        
        # Appointment type features
        if 'AppointmentType' in self.processed_df.columns:
            appointment_complexity = {
                'New Patient': 1.3,
                'Specialist Referral': 1.2,
                'Urgent Care': 1.1,
                'Routine checkup': 1.0,
                'Follow-up procedure': 1.1
            }
            self.processed_df['appointment_complexity'] = self.processed_df['AppointmentType'].map(appointment_complexity).fillna(1.0)
        
        print("   ✅ Advanced features engineered for wait time prediction")
    
    def _analyze_historical_patterns(self):
        """Analyze historical patterns in wait times"""
        print("📈 Analyzing historical wait time patterns...")
        
        # Peak hours analysis
        if 'ArrivalHour' in self.processed_df.columns:
            hourly_patterns = self.processed_df.groupby('ArrivalHour')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['hourly'] = hourly_patterns.to_dict('records')
        
        # Day of week patterns
        if 'ArrivalDayOfWeek' in self.processed_df.columns:
            daily_patterns = self.processed_df.groupby('ArrivalDayOfWeek')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['daily'] = daily_patterns.to_dict('records')
        
        # Department patterns
        if 'Department' in self.processed_df.columns:
            dept_patterns = self.processed_df.groupby('Department')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['department'] = dept_patterns.to_dict('records')
        
        # Seasonal patterns
        if 'ArrivalMonth' in self.processed_df.columns:
            monthly_patterns = self.processed_df.groupby('ArrivalMonth')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['monthly'] = monthly_patterns.to_dict('records')
        
        print("   ✅ Historical patterns analyzed")
    
    def train_wait_time_models(self):
        """Train multiple models for wait time prediction"""
        print("🤖 Training wait time prediction models...")
        
        # Prepare features for wait time prediction
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'is_peak_hour', 'is_weekend', 'is_morning', 'is_afternoon', 'is_evening',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_wait', 'dept_wait_std', 'dept_efficiency',
            'staff_efficiency', 'staff_workload', 'total_staff', 'provider_nurse_ratio',
            'occupancy_squared', 'age_complexity', 'insurance_processing_time', 'appointment_complexity'
        ]
        
        # Encode categorical variables
        le_department = LabelEncoder()
        self.processed_df['Department_encoded'] = le_department.fit_transform(self.processed_df['Department'])
        feature_columns.append('Department_encoded')
        
        le_age = LabelEncoder()
        self.processed_df['AgeGroup_encoded'] = le_age.fit_transform(self.processed_df['AgeGroup'])
        feature_columns.append('AgeGroup_encoded')
        
        le_insurance = LabelEncoder()
        self.processed_df['InsuranceType_encoded'] = le_insurance.fit_transform(self.processed_df['InsuranceType'])
        feature_columns.append('InsuranceType_encoded')
        
        # Prepare data
        X = self.processed_df[feature_columns].fillna(0)
        y = self.processed_df['TotalTimeInHospital'].fillna(0)
        
        # Remove any infinite values
        X = X.replace([np.inf, -np.inf], 0)
        y = y.replace([np.inf, -np.inf], 0)
        
        print(f"   Features: {len(feature_columns)}")
        print(f"   Samples: {len(X):,}")
        print(f"   Target range: {y.min():.1f} - {y.max():.1f} minutes")
        
        # Split data with time series consideration
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models to train
        models_to_train = {
            'RandomForest': RandomForestRegressor(
                n_estimators=200, 
                max_depth=20, 
                min_samples_split=5, 
                min_samples_leaf=2,
                random_state=42
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=150, 
                learning_rate=0.1, 
                max_depth=7, 
                min_samples_split=5,
                random_state=42
            ),
            'ExtraTrees': ExtraTreesRegressor(
                n_estimators=200, 
                max_depth=20, 
                min_samples_split=5, 
                min_samples_leaf=2,
                random_state=42
            ),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1),
            'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5)
        }
        
        # Train and evaluate models
        results = {}
        
        for name, model in models_to_train.items():
            print(f"   🔍 Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            print(f"      R² Score: {r2:.4f}")
            print(f"      MAE: {mae:.2f} minutes")
            print(f"      RMSE: {rmse:.2f} minutes")
            print(f"      CV R²: {cv_mean:.4f} (±{cv_std:.4f})")
            
            results[name] = {
                'model': model,
                'r2': r2,
                'mae': mae,
                'rmse': rmse,
                'cv_mean': cv_mean,
                'cv_std': cv_std
            }
            
            # Save feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(feature_columns, model.feature_importances_))
                self.feature_importance[name] = importance_dict
        
        # Choose best model based on R² score
        best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
        best_model = results[best_model_name]['model']
        
        print(f"   ✅ Best model: {best_model_name} with R² = {results[best_model_name]['r2']:.4f}")
        
        # Save models and components
        os.makedirs('models', exist_ok=True)
        joblib.dump(best_model, 'models/advanced_wait_time_model.pkl')
        joblib.dump(scaler, 'models/wait_time_scaler.pkl')
        joblib.dump(le_department, 'models/department_encoder.pkl')
        joblib.dump(le_age, 'models/age_encoder.pkl')
        joblib.dump(le_insurance, 'models/insurance_encoder.pkl')
        
        # Save all results
        self.models = results
        self.scalers['wait_time'] = scaler
        self.encoders['department'] = le_department
        self.encoders['age'] = le_age
        self.encoders['insurance'] = le_insurance
        self.performance_metrics = results
        
        # Save comprehensive results
        comprehensive_results = {
            'best_model': best_model_name,
            'performance_metrics': results,
            'feature_importance': self.feature_importance,
            'historical_patterns': self.historical_patterns,
            'feature_columns': feature_columns,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(comprehensive_results, 'models/wait_time_comprehensive_results.pkl')
        
        return best_model, results[best_model_name]
    
    def predict_wait_time(self, 
                         arrival_hour: int,
                         arrival_day: int,
                         department: str,
                         age_group: str,
                         insurance_type: str,
                         appointment_type: str,
                         facility_occupancy: float,
                         staff_count: int) -> Dict:
        """Predict wait time for a new patient"""
        
        # Load the best model and components
        model = joblib.load('models/advanced_wait_time_model.pkl')
        scaler = joblib.load('models/wait_time_scaler.pkl')
        dept_encoder = joblib.load('models/department_encoder.pkl')
        age_encoder = joblib.load('models/age_encoder.pkl')
        insurance_encoder = joblib.load('models/insurance_encoder.pkl')
        
        # Prepare features
        features = {
            'ArrivalHour': arrival_hour,
            'ArrivalDayOfWeek': arrival_day,
            'ArrivalMonth': datetime.now().month,
            'is_peak_hour': 1 if arrival_hour in [8, 9, 10, 14, 15, 16] else 0,
            'is_weekend': 1 if arrival_day in [6, 7] else 0,
            'is_morning': 1 if 6 <= arrival_hour <= 12 else 0,
            'is_afternoon': 1 if 13 <= arrival_hour <= 18 else 0,
            'is_evening': 1 if 19 <= arrival_hour <= 23 else 0,
            'hour_sin': np.sin(2 * np.pi * arrival_hour / 24),
            'hour_cos': np.cos(2 * np.pi * arrival_hour / 24),
            'day_sin': np.sin(2 * np.pi * arrival_day / 7),
            'day_cos': np.cos(2 * np.pi * arrival_day / 7),
            'FacilityOccupancyRate': facility_occupancy,
            'ProvidersOnShift': staff_count,
            'NursesOnShift': staff_count,
            'StaffToPatientRatio': 1.0 / (staff_count + 0.001),
            'occupancy_squared': facility_occupancy ** 2,
            'age_complexity': {'Young Adult (18-35)': 1.0, 'Adult (36-60)': 1.2, 'Senior (61+)': 1.5}.get(age_group, 1.0),
            'insurance_processing_time': {'Private': 1.0, 'Medicare': 1.1, 'Medicaid': 1.2, 'Self-pay': 1.3, 'None': 1.4}.get(insurance_type, 1.0),
            'appointment_complexity': {'New Patient': 1.3, 'Specialist Referral': 1.2, 'Urgent Care': 1.1, 'Routine checkup': 1.0, 'Follow-up procedure': 1.1}.get(appointment_type, 1.0)
        }
        
        # Add department-specific features (simplified)
        features['dept_avg_wait'] = 60.0  # Default average
        features['dept_wait_std'] = 20.0  # Default std
        features['dept_efficiency'] = 1.0  # Default efficiency
        
        # Add staff efficiency features
        features['staff_efficiency'] = 1.0 / (features['StaffToPatientRatio'] + 0.001)
        features['staff_workload'] = features['StaffToPatientRatio'] * facility_occupancy
        features['total_staff'] = staff_count * 2
        features['provider_nurse_ratio'] = 1.0
        
        # Encode categorical variables
        try:
            features['Department_encoded'] = dept_encoder.transform([department])[0]
        except:
            features['Department_encoded'] = 0
        
        try:
            features['AgeGroup_encoded'] = age_encoder.transform([age_group])[0]
        except:
            features['AgeGroup_encoded'] = 0
        
        try:
            features['InsuranceType_encoded'] = insurance_encoder.transform([insurance_type])[0]
        except:
            features['InsuranceType_encoded'] = 0
        
        # Convert to array and predict
        feature_array = np.array([list(features.values())]).reshape(1, -1)
        feature_array_scaled = scaler.transform(feature_array)
        
        predicted_wait = model.predict(feature_array_scaled)[0]
        
        # Add confidence interval (simplified)
        confidence_interval = predicted_wait * 0.2  # ±20% confidence
        
        return {
            'predicted_wait_time': round(predicted_wait, 1),
            'confidence_interval': round(confidence_interval, 1),
            'min_wait_time': round(max(0, predicted_wait - confidence_interval), 1),
            'max_wait_time': round(predicted_wait + confidence_interval, 1),
            'model_used': 'Advanced ML Predictor',
            'features_considered': len(features),
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def get_historical_insights(self) -> Dict:
        """Get insights from historical wait time patterns"""
        return {
            'hourly_patterns': self.historical_patterns.get('hourly', []),
            'daily_patterns': self.historical_patterns.get('daily', []),
            'department_patterns': self.historical_patterns.get('department', []),
            'monthly_patterns': self.historical_patterns.get('monthly', []),
            'feature_importance': self.feature_importance,
            'performance_metrics': self.performance_metrics
        }

if __name__ == "__main__":
    predictor = AdvancedWaitTimePredictor()
    
    # Load and preprocess data
    predictor.load_and_preprocess_data()
    
    # Train models
    best_model, best_results = predictor.train_wait_time_models()
    
    # Example prediction
    prediction = predictor.predict_wait_time(
        arrival_hour=14,
        arrival_day=1,  # Monday
        department='Emergency',
        age_group='Adult (36-60)',
        insurance_type='Private',
        appointment_type='Urgent Care',
        facility_occupancy=0.7,
        staff_count=5
    )
    
    print("\n🎯 Example Prediction:")
    print(f"Predicted wait time: {prediction['predicted_wait_time']} minutes")
    print(f"Confidence interval: ±{prediction['confidence_interval']} minutes")
    print(f"Range: {prediction['min_wait_time']} - {prediction['max_wait_time']} minutes")
