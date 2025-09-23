"""
Practical Intelligent Wait Time Prediction System
ML-based estimation using historical patterns with robust implementation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PracticalWaitTimePredictor:
    """Practical ML-based wait time prediction using historical patterns"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.historical_patterns = {}
        self.feature_columns = []
        
    def load_and_preprocess_data(self):
        """Load and preprocess hospital wait time data"""
        print("📊 Loading hospital wait time dataset...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_practical_features()
        self._analyze_patterns()
        
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
        
        # Remove extreme outliers (keep 95th percentile)
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            percentile_95 = self.processed_df[wait_time_col].quantile(0.95)
            before_count = len(self.processed_df)
            self.processed_df = self.processed_df[self.processed_df[wait_time_col] <= percentile_95]
            after_count = len(self.processed_df)
            
            print(f"   Removed {before_count - after_count} extreme outliers (95th percentile: {percentile_95:.1f} min)")
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_practical_features(self):
        """Engineer practical features for wait time prediction"""
        print("🔧 Engineering practical wait time features...")
        
        # Time-based features
        if 'ArrivalHour' in self.processed_df.columns:
            # Peak hours (busiest times)
            self.processed_df['is_peak_hour'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if x in [8, 9, 10, 14, 15, 16] else 0
            )
            
            # Time of day categories
            self.processed_df['time_of_day'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 'morning' if 6 <= x <= 11 else 
                         'afternoon' if 12 <= x <= 17 else 
                         'evening' if 18 <= x <= 23 else 'night'
            )
            
            # Weekend vs weekday
            self.processed_df['is_weekend'] = self.processed_df['ArrivalDayOfWeek'].apply(
                lambda x: 1 if x in [6, 7] else 0
            )
        
        # Department-specific features
        if 'Department' in self.processed_df.columns:
            # Calculate department average wait times
            dept_avg_wait = self.processed_df.groupby('Department')['TotalTimeInHospital'].mean().to_dict()
            self.processed_df['dept_avg_wait'] = self.processed_df['Department'].map(dept_avg_wait)
            
            # Department complexity (some departments are inherently slower)
            dept_complexity = {
                'Emergency': 1.5,
                'Cardiology': 1.3,
                'Neurology': 1.3,
                'General Surgery': 1.2,
                'Orthopedics': 1.1,
                'Internal Medicine': 1.0,
                'Pediatrics': 1.0,
                'Obstetrics': 1.1,
                'Radiology': 0.9
            }
            self.processed_df['dept_complexity'] = self.processed_df['Department'].map(dept_complexity).fillna(1.0)
        
        # Staff and resource features
        if 'StaffToPatientRatio' in self.processed_df.columns:
            # Staff efficiency (lower ratio = more efficient)
            self.processed_df['staff_efficiency'] = 1 / (self.processed_df['StaffToPatientRatio'] + 0.1)
        
        if 'FacilityOccupancyRate' in self.processed_df.columns:
            # Occupancy level categories
            self.processed_df['occupancy_level'] = pd.cut(
                self.processed_df['FacilityOccupancyRate'], 
                bins=[0, 0.4, 0.7, 0.9, 1.0], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        # Patient-specific features
        if 'AgeGroup' in self.processed_df.columns:
            # Age complexity factor
            age_complexity = {
                'Young Adult (18-35)': 1.0,
                'Adult (36-60)': 1.1,
                'Senior (61+)': 1.3
            }
            self.processed_df['age_complexity'] = self.processed_df['AgeGroup'].map(age_complexity).fillna(1.0)
        
        if 'InsuranceType' in self.processed_df.columns:
            # Insurance processing complexity
            insurance_complexity = {
                'Private': 1.0,
                'Medicare': 1.1,
                'Medicaid': 1.2,
                'Self-pay': 1.3,
                'None': 1.4
            }
            self.processed_df['insurance_complexity'] = self.processed_df['InsuranceType'].map(insurance_complexity).fillna(1.0)
        
        if 'AppointmentType' in self.processed_df.columns:
            # Appointment complexity
            appointment_complexity = {
                'New Patient': 1.3,
                'Specialist Referral': 1.2,
                'Urgent Care': 1.1,
                'Routine checkup': 1.0,
                'Follow-up procedure': 1.1
            }
            self.processed_df['appointment_complexity'] = self.processed_df['AppointmentType'].map(appointment_complexity).fillna(1.0)
        
        print("   ✅ Practical features engineered")
    
    def _analyze_patterns(self):
        """Analyze historical patterns in wait times"""
        print("📈 Analyzing historical wait time patterns...")
        
        # Hourly patterns
        if 'ArrivalHour' in self.processed_df.columns:
            hourly_stats = self.processed_df.groupby('ArrivalHour')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['hourly'] = hourly_stats.to_dict('records')
        
        # Department patterns
        if 'Department' in self.processed_df.columns:
            dept_stats = self.processed_df.groupby('Department')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['department'] = dept_stats.to_dict('records')
        
        # Day of week patterns
        if 'ArrivalDayOfWeek' in self.processed_df.columns:
            daily_stats = self.processed_df.groupby('ArrivalDayOfWeek')['TotalTimeInHospital'].agg(['mean', 'std', 'count']).reset_index()
            self.historical_patterns['daily'] = daily_stats.to_dict('records')
        
        print("   ✅ Historical patterns analyzed")
    
    def train_model(self):
        """Train the wait time prediction model"""
        print("🤖 Training practical wait time prediction model...")
        
        # Define feature columns
        self.feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'is_peak_hour', 'is_weekend',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_wait', 'dept_complexity', 'staff_efficiency',
            'age_complexity', 'insurance_complexity', 'appointment_complexity'
        ]
        
        # Encode categorical variables
        if 'Department' in self.processed_df.columns:
            self.encoders['department'] = LabelEncoder()
            self.processed_df['Department_encoded'] = self.encoders['department'].fit_transform(self.processed_df['Department'])
            self.feature_columns.append('Department_encoded')
        
        if 'AgeGroup' in self.processed_df.columns:
            self.encoders['age'] = LabelEncoder()
            self.processed_df['AgeGroup_encoded'] = self.encoders['age'].fit_transform(self.processed_df['AgeGroup'])
            self.feature_columns.append('AgeGroup_encoded')
        
        if 'InsuranceType' in self.processed_df.columns:
            self.encoders['insurance'] = LabelEncoder()
            self.processed_df['InsuranceType_encoded'] = self.encoders['insurance'].fit_transform(self.processed_df['InsuranceType'])
            self.feature_columns.append('InsuranceType_encoded')
        
        # Prepare data
        X = self.processed_df[self.feature_columns].fillna(0)
        y = self.processed_df['TotalTimeInHospital'].fillna(0)
        
        # Remove any infinite values
        X = X.replace([np.inf, -np.inf], 0)
        y = y.replace([np.inf, -np.inf], 0)
        
        print(f"   Features: {len(self.feature_columns)}")
        print(f"   Samples: {len(X):,}")
        print(f"   Target range: {y.min():.1f} - {y.max():.1f} minutes")
        print(f"   Target mean: {y.mean():.1f} minutes")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train RandomForest model (most robust for this type of data)
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"   ✅ Model trained successfully!")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MAE: {mae:.2f} minutes")
        print(f"   RMSE: {rmse:.2f} minutes")
        
        # Get feature importance
        feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print(f"   📊 Top 5 most important features:")
        for feature, importance in sorted_features[:5]:
            print(f"      {feature}: {importance:.4f}")
        
        # Save model and components
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/practical_wait_time_model.pkl')
        joblib.dump(self.scaler, 'models/practical_wait_time_scaler.pkl')
        
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, f'models/practical_{name}_encoder.pkl')
        
        # Save comprehensive results
        results = {
            'model_performance': {
                'r2_score': r2,
                'mae': mae,
                'rmse': rmse
            },
            'feature_importance': feature_importance,
            'historical_patterns': self.historical_patterns,
            'feature_columns': self.feature_columns,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(results, 'models/practical_wait_time_results.pkl')
        
        return r2, mae, rmse
    
    def predict_wait_time(self, 
                         arrival_hour: int,
                         arrival_day: int,
                         department: str,
                         age_group: str,
                         insurance_type: str,
                         appointment_type: str,
                         facility_occupancy: float = 0.5,
                         staff_count: int = 3) -> Dict:
        """Predict wait time for a new patient"""
        
        # Load model and components if not already loaded
        if self.model is None:
            self.model = joblib.load('models/practical_wait_time_model.pkl')
            self.scaler = joblib.load('models/practical_wait_time_scaler.pkl')
            
            # Load encoders
            self.encoders['department'] = joblib.load('models/practical_department_encoder.pkl')
            self.encoders['age'] = joblib.load('models/practical_age_encoder.pkl')
            self.encoders['insurance'] = joblib.load('models/practical_insurance_encoder.pkl')
        
        # Prepare features
        features = {
            'ArrivalHour': arrival_hour,
            'ArrivalDayOfWeek': arrival_day,
            'ArrivalMonth': datetime.now().month,
            'is_peak_hour': 1 if arrival_hour in [8, 9, 10, 14, 15, 16] else 0,
            'is_weekend': 1 if arrival_day in [6, 7] else 0,
            'FacilityOccupancyRate': facility_occupancy,
            'ProvidersOnShift': staff_count,
            'NursesOnShift': staff_count,
            'StaffToPatientRatio': 1.0 / (staff_count + 0.1),
            'staff_efficiency': 1 / (1.0 / (staff_count + 0.1) + 0.1)
        }
        
        # Add department-specific features
        dept_avg_wait = {
            'Emergency': 45.0, 'Cardiology': 35.0, 'Neurology': 40.0,
            'General Surgery': 30.0, 'Orthopedics': 25.0, 'Internal Medicine': 20.0,
            'Pediatrics': 20.0, 'Obstetrics': 30.0, 'Radiology': 15.0
        }
        features['dept_avg_wait'] = dept_avg_wait.get(department, 25.0)
        
        dept_complexity = {
            'Emergency': 1.5, 'Cardiology': 1.3, 'Neurology': 1.3,
            'General Surgery': 1.2, 'Orthopedics': 1.1, 'Internal Medicine': 1.0,
            'Pediatrics': 1.0, 'Obstetrics': 1.1, 'Radiology': 0.9
        }
        features['dept_complexity'] = dept_complexity.get(department, 1.0)
        
        # Add patient-specific features
        age_complexity = {
            'Young Adult (18-35)': 1.0,
            'Adult (36-60)': 1.1,
            'Senior (61+)': 1.3
        }
        features['age_complexity'] = age_complexity.get(age_group, 1.0)
        
        insurance_complexity = {
            'Private': 1.0, 'Medicare': 1.1, 'Medicaid': 1.2,
            'Self-pay': 1.3, 'None': 1.4
        }
        features['insurance_complexity'] = insurance_complexity.get(insurance_type, 1.0)
        
        appointment_complexity = {
            'New Patient': 1.3, 'Specialist Referral': 1.2, 'Urgent Care': 1.1,
            'Routine checkup': 1.0, 'Follow-up procedure': 1.1
        }
        features['appointment_complexity'] = appointment_complexity.get(appointment_type, 1.0)
        
        # Encode categorical variables
        try:
            features['Department_encoded'] = self.encoders['department'].transform([department])[0]
        except:
            features['Department_encoded'] = 0
        
        try:
            features['AgeGroup_encoded'] = self.encoders['age'].transform([age_group])[0]
        except:
            features['AgeGroup_encoded'] = 0
        
        try:
            features['InsuranceType_encoded'] = self.encoders['insurance'].transform([insurance_type])[0]
        except:
            features['InsuranceType_encoded'] = 0
        
        # Convert to array and predict
        feature_array = np.array([list(features.values())]).reshape(1, -1)
        feature_array_scaled = self.scaler.transform(feature_array)
        
        predicted_wait = self.model.predict(feature_array_scaled)[0]
        
        # Ensure positive prediction
        predicted_wait = max(5.0, predicted_wait)  # Minimum 5 minutes
        
        # Add confidence interval based on historical patterns
        confidence_interval = predicted_wait * 0.25  # ±25% confidence
        
        # Get feature importance for explanation
        feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'predicted_wait_time': round(predicted_wait, 1),
            'confidence_interval': round(confidence_interval, 1),
            'min_wait_time': round(max(5.0, predicted_wait - confidence_interval), 1),
            'max_wait_time': round(predicted_wait + confidence_interval, 1),
            'model_used': 'Practical ML Predictor',
            'features_considered': len(features),
            'top_factors': [f"{factor}: {importance:.3f}" for factor, importance in top_factors],
            'prediction_timestamp': datetime.now().isoformat(),
            'department': department,
            'arrival_time': f"{arrival_hour:02d}:00",
            'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][arrival_day]
        }
    
    def get_historical_insights(self) -> Dict:
        """Get insights from historical wait time patterns"""
        return {
            'hourly_patterns': self.historical_patterns.get('hourly', []),
            'department_patterns': self.historical_patterns.get('department', []),
            'daily_patterns': self.historical_patterns.get('daily', []),
            'average_wait_time': self.processed_df['TotalTimeInHospital'].mean(),
            'median_wait_time': self.processed_df['TotalTimeInHospital'].median(),
            'peak_hours': [8, 9, 10, 14, 15, 16],
            'busiest_departments': sorted(
                [(dept, stats['mean']) for dept, stats in 
                 [(d['Department'], d) for d in self.historical_patterns.get('department', [])]],
                key=lambda x: x[1], reverse=True
            )[:5]
        }

if __name__ == "__main__":
    predictor = PracticalWaitTimePredictor()
    
    # Load and preprocess data
    predictor.load_and_preprocess_data()
    
    # Train model
    r2, mae, rmse = predictor.train_model()
    
    # Example predictions
    print("\n🎯 Example Predictions:")
    print("=" * 50)
    
    # Emergency case
    emergency_pred = predictor.predict_wait_time(
        arrival_hour=14,
        arrival_day=1,  # Monday
        department='Emergency',
        age_group='Adult (36-60)',
        insurance_type='Private',
        appointment_type='Urgent Care',
        facility_occupancy=0.8,
        staff_count=4
    )
    
    print(f"🚨 Emergency Department (Monday 2 PM):")
    print(f"   Predicted wait: {emergency_pred['predicted_wait_time']} minutes")
    print(f"   Range: {emergency_pred['min_wait_time']} - {emergency_pred['max_wait_time']} minutes")
    print(f"   Top factors: {', '.join(emergency_pred['top_factors'][:2])}")
    
    # Routine checkup
    routine_pred = predictor.predict_wait_time(
        arrival_hour=10,
        arrival_day=2,  # Tuesday
        department='Internal Medicine',
        age_group='Young Adult (18-35)',
        insurance_type='Private',
        appointment_type='Routine checkup',
        facility_occupancy=0.4,
        staff_count=3
    )
    
    print(f"\n🩺 Internal Medicine (Tuesday 10 AM):")
    print(f"   Predicted wait: {routine_pred['predicted_wait_time']} minutes")
    print(f"   Range: {routine_pred['min_wait_time']} - {routine_pred['max_wait_time']} minutes")
    print(f"   Top factors: {', '.join(routine_pred['top_factors'][:2])}")
    
    # Weekend case
    weekend_pred = predictor.predict_wait_time(
        arrival_hour=16,
        arrival_day=6,  # Saturday
        department='Orthopedics',
        age_group='Senior (61+)',
        insurance_type='Medicare',
        appointment_type='Specialist Referral',
        facility_occupancy=0.6,
        staff_count=2
    )
    
    print(f"\n🦴 Orthopedics (Saturday 4 PM):")
    print(f"   Predicted wait: {weekend_pred['predicted_wait_time']} minutes")
    print(f"   Range: {weekend_pred['min_wait_time']} - {weekend_pred['max_wait_time']} minutes")
    print(f"   Top factors: {', '.join(weekend_pred['top_factors'][:2])}")
    
    # Get historical insights
    insights = predictor.get_historical_insights()
    print(f"\n📊 Historical Insights:")
    print(f"   Average wait time: {insights['average_wait_time']:.1f} minutes")
    print(f"   Median wait time: {insights['median_wait_time']:.1f} minutes")
    print(f"   Peak hours: {insights['peak_hours']}")
    print(f"   Busiest departments: {[dept for dept, _ in insights['busiest_departments'][:3]]}")
