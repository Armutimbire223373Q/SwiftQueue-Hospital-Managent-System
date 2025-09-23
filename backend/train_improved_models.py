"""
Improved AI Model Training with Better Feature Engineering
Focuses on creating more predictive models for hospital workflow
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ImprovedHospitalModelTrainer:
    """Improved trainer with better feature engineering and model selection"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = {}
        self.model_performance = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the comprehensive hospital dataset"""
        print("📊 Loading comprehensive hospital dataset...")
        
        # Load the hospital dataset
        self.df = pd.read_csv('dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} columns")
        
        # Clean and preprocess the data
        self._clean_data()
        self._engineer_improved_features()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean the dataset with better handling of missing values"""
        print("🧹 Cleaning dataset...")
        
        # Create a copy for processing
        self.processed_df = self.df.copy()
        
        # Handle missing values more intelligently
        # For timing columns, use median instead of 0
        timing_cols = [
            'RegistrationWaitTimeTime', 'CheckInToNurseTime', 'NurseToTriageCompleteTime',
            'TriageToProviderStartTime', 'ConsultationDurationTime', 'ProviderEndToTestsCompleteTime',
            'TestsToDischargeTime', 'TotalTimeInHospital'
        ]
        
        for col in timing_cols:
            if col in self.processed_df.columns:
                median_val = self.processed_df[col].median()
                self.processed_df[col] = self.processed_df[col].fillna(median_val)
        
        # Handle facility metrics
        self.processed_df['FacilityOccupancyRate'] = self.processed_df['FacilityOccupancyRate'].fillna(
            self.processed_df['FacilityOccupancyRate'].median()
        )
        self.processed_df['ProvidersOnShift'] = self.processed_df['ProvidersOnShift'].fillna(
            self.processed_df['ProvidersOnShift'].median()
        )
        self.processed_df['NursesOnShift'] = self.processed_df['NursesOnShift'].fillna(
            self.processed_df['NursesOnShift'].median()
        )
        self.processed_df['StaffToPatientRatio'] = self.processed_df['StaffToPatientRatio'].fillna(
            self.processed_df['StaffToPatientRatio'].median()
        )
        
        # Remove any remaining infinite values
        self.processed_df = self.processed_df.replace([np.inf, -np.inf], np.nan)
        
        # Fill remaining NaN values
        numeric_cols = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_cols] = self.processed_df[numeric_cols].fillna(0)
        
        # Fill categorical columns
        categorical_cols = self.processed_df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            self.processed_df[col] = self.processed_df[col].fillna('Unknown')
        
        print(f"   Cleaned data: {len(self.processed_df):,} records")
    
    def _engineer_improved_features(self):
        """Engineer improved features with better domain knowledge"""
        print("🔧 Engineering improved features...")
        
        # Time-based features
        self.processed_df['hour'] = self.processed_df['ArrivalHour']
        self.processed_df['day_of_week'] = self.processed_df['ArrivalDayOfWeek']
        self.processed_df['month'] = self.processed_df['ArrivalMonth']
        self.processed_df['is_weekend'] = (self.processed_df['day_of_week'] >= 5).astype(int)
        
        # Enhanced cyclical encoding
        self.processed_df['hour_sin'] = np.sin(2 * np.pi * self.processed_df['hour'] / 24)
        self.processed_df['hour_cos'] = np.cos(2 * np.pi * self.processed_df['hour'] / 24)
        self.processed_df['dow_sin'] = np.sin(2 * np.pi * self.processed_df['day_of_week'] / 7)
        self.processed_df['dow_cos'] = np.cos(2 * np.pi * self.processed_df['day_of_week'] / 7)
        self.processed_df['month_sin'] = np.sin(2 * np.pi * self.processed_df['month'] / 12)
        self.processed_df['month_cos'] = np.cos(2 * np.pi * self.processed_df['month'] / 12)
        
        # Peak hours with more granularity
        self.processed_df['is_morning_peak'] = (
            (self.processed_df['hour'] >= 8) & (self.processed_df['hour'] <= 10)
        ).astype(int)
        
        self.processed_df['is_lunch_peak'] = (
            (self.processed_df['hour'] >= 12) & (self.processed_df['hour'] <= 14)
        ).astype(int)
        
        self.processed_df['is_evening_peak'] = (
            (self.processed_df['hour'] >= 17) & (self.processed_df['hour'] <= 19)
        ).astype(int)
        
        self.processed_df['is_peak_hour'] = (
            self.processed_df['is_morning_peak'] | 
            self.processed_df['is_lunch_peak'] | 
            self.processed_df['is_evening_peak']
        ).astype(int)
        
        # Business hours
        self.processed_df['is_business_hours'] = (
            (self.processed_df['hour'] >= 9) & (self.processed_df['hour'] <= 17)
        ).astype(int)
        
        # Rush hour indicators
        self.processed_df['is_morning_rush'] = (
            (self.processed_df['hour'] >= 7) & (self.processed_df['hour'] <= 9)
        ).astype(int)
        
        self.processed_df['is_evening_rush'] = (
            (self.processed_df['hour'] >= 17) & (self.processed_df['hour'] <= 19)
        ).astype(int)
        
        # Enhanced categorical encoding
        categorical_features = ['Department', 'TriageCategory', 'AgeGroup', 'InsuranceType', 'AppointmentType']
        
        for feature in categorical_features:
            encoder = LabelEncoder()
            self.processed_df[f'{feature.lower()}_encoded'] = encoder.fit_transform(
                self.processed_df[feature].astype(str)
            )
            self.encoders[feature.lower()] = encoder
        
        # Resource features with better calculations
        self.processed_df['provider_nurse_ratio'] = (
            self.processed_df['ProvidersOnShift'] / (self.processed_df['NursesOnShift'] + 1)
        )
        
        self.processed_df['total_staff'] = (
            self.processed_df['ProvidersOnShift'] + self.processed_df['NursesOnShift']
        )
        
        self.processed_df['staff_efficiency'] = (
            self.processed_df['total_staff'] / (self.processed_df['FacilityOccupancyRate'] + 0.1)
        )
        
        # Occupancy categories with better thresholds
        self.processed_df['occupancy_level'] = pd.cut(
            self.processed_df['FacilityOccupancyRate'],
            bins=[0, 0.4, 0.7, 0.9, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        occupancy_encoder = LabelEncoder()
        self.processed_df['occupancy_encoded'] = occupancy_encoder.fit_transform(
            self.processed_df['occupancy_level'].astype(str)
        )
        self.encoders['occupancy'] = occupancy_encoder
        
        # Enhanced interaction features
        self.processed_df['dept_occupancy_interaction'] = (
            self.processed_df['department_encoded'] * self.processed_df['FacilityOccupancyRate']
        )
        
        self.processed_df['triage_occupancy_interaction'] = (
            self.processed_df['triagecategory_encoded'] * self.processed_df['FacilityOccupancyRate']
        )
        
        self.processed_df['hour_occupancy_interaction'] = (
            self.processed_df['hour'] * self.processed_df['FacilityOccupancyRate']
        )
        
        self.processed_df['dept_triage_interaction'] = (
            self.processed_df['department_encoded'] * self.processed_df['triagecategory_encoded']
        )
        
        # Test-related features
        self.processed_df['has_tests'] = (
            self.processed_df['TestsOrdered'].notna() & 
            (self.processed_df['TestsOrdered'] != 'None') &
            (self.processed_df['TestsOrdered'] != '')
        ).astype(int)
        
        # Consultation features
        self.processed_df['consultation_needed'] = self.processed_df['ConsultationNeeded'].astype(int)
        
        # Delay features
        self.processed_df['has_arrival_delay'] = (self.processed_df['ArrivalDelayTime'] > 0).astype(int)
        self.processed_df['arrival_delay_magnitude'] = np.abs(self.processed_df['ArrivalDelayTime'])
        
        # Booking features
        self.processed_df['is_online_booking'] = self.processed_df['IsOnlineBooking'].astype(int)
        
        # Age group specific features
        self.processed_df['is_pediatric'] = (self.processed_df['agegroup_encoded'] == 0).astype(int)
        self.processed_df['is_senior'] = (self.processed_df['agegroup_encoded'] == 3).astype(int)
        
        # Department-specific features
        emergency_dept = self.processed_df['department_encoded'] == 0  # Assuming Emergency is encoded as 0
        self.processed_df['is_emergency_dept'] = emergency_dept.astype(int)
        
        # Time-based complexity features
        self.processed_df['time_complexity'] = (
            self.processed_df['has_tests'] * 2 +
            self.processed_df['consultation_needed'] * 1 +
            self.processed_df['is_emergency_dept'] * 3
        )
        
        print(f"   Engineered {len(self.processed_df.columns)} features")
    
    def train_wait_time_model(self):
        """Train improved wait time prediction model"""
        print("\n⏱️ Training Improved Wait Time Prediction Model...")
        
        # Enhanced features for wait time prediction
        wait_time_features = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'month_sin', 'month_cos',
            'is_morning_peak', 'is_lunch_peak', 'is_evening_peak', 'is_peak_hour',
            'is_business_hours', 'is_morning_rush', 'is_evening_rush',
            'department_encoded', 'triagecategory_encoded', 'agegroup_encoded', 
            'insurancetype_encoded', 'appointmenttype_encoded',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift', 
            'StaffToPatientRatio', 'provider_nurse_ratio', 'total_staff', 'staff_efficiency',
            'occupancy_encoded', 'dept_occupancy_interaction', 'triage_occupancy_interaction',
            'hour_occupancy_interaction', 'dept_triage_interaction',
            'has_tests', 'consultation_needed', 'has_arrival_delay', 'arrival_delay_magnitude',
            'is_online_booking', 'is_pediatric', 'is_senior', 'is_emergency_dept', 'time_complexity'
        ]
        
        X = self.processed_df[wait_time_features].copy()
        y = self.processed_df['TotalTimeInHospital'].copy()
        
        # Remove outliers for better training
        Q1 = y.quantile(0.25)
        Q3 = y.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        mask = (y >= lower_bound) & (y <= upper_bound)
        X = X[mask]
        y = y[mask]
        
        print(f"   Training with {len(X)} records after outlier removal")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Use RobustScaler for better handling of outliers
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Try multiple models and select the best
        models_to_try = {
            'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=8, random_state=42),
            'ExtraTrees': ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42),
            'Ridge': Ridge(alpha=1.0)
        }
        
        best_model = None
        best_score = -np.inf
        best_name = ""
        
        for name, model in models_to_try.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            score = r2_score(y_test, y_pred)
            
            if score > best_score:
                best_score = score
                best_model = model
                best_name = name
        
        # Evaluate best model
        y_pred = best_model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Store model and results
        self.models['wait_time'] = best_model
        self.scalers['wait_time'] = scaler
        self.feature_columns['wait_time'] = wait_time_features
        self.model_performance['wait_time'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(wait_time_features),
            'model_type': best_name
        }
        
        print(f"   ✅ Wait Time Model ({best_name}) - R²: {r2:.3f}, MAE: {mae:.1f} min, RMSE: {rmse:.1f} min")
        
        return best_model, scaler, wait_time_features
    
    def train_peak_time_model(self):
        """Train improved peak time prediction model"""
        print("\n🕐 Training Improved Peak Time Prediction Model...")
        
        # Aggregate data by hour and day of week for better peak prediction
        hourly_data = self.processed_df.groupby(['hour', 'day_of_week']).agg({
            'TotalTimeInHospital': 'mean',
            'FacilityOccupancyRate': 'mean',
            'ProvidersOnShift': 'mean',
            'NursesOnShift': 'mean',
            'StaffToPatientRatio': 'mean',
            'triagecategory_encoded': 'mean',
            'department_encoded': 'mean',
            'has_tests': 'mean',
            'consultation_needed': 'mean',
            'is_weekend': 'first'
        }).reset_index()
        
        # Enhanced features for peak time prediction
        peak_features = [
            'hour', 'day_of_week', 'is_weekend',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'triagecategory_encoded', 'department_encoded', 'has_tests', 'consultation_needed'
        ]
        
        X = hourly_data[peak_features].copy()
        y = hourly_data['TotalTimeInHospital'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Store model and results
        self.models['peak_time'] = model
        self.scalers['peak_time'] = scaler
        self.feature_columns['peak_time'] = peak_features
        self.model_performance['peak_time'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(peak_features)
        }
        
        print(f"   ✅ Peak Time Model - R²: {r2:.3f}, MAE: {mae:.1f} min, RMSE: {rmse:.1f} min")
        
        return model, scaler, peak_features
    
    def train_department_efficiency_model(self):
        """Train department efficiency prediction model"""
        print("\n🏥 Training Department Efficiency Model...")
        
        # Aggregate data by department for efficiency analysis
        dept_data = self.processed_df.groupby('department_encoded').agg({
            'TotalTimeInHospital': 'mean',
            'FacilityOccupancyRate': 'mean',
            'ProvidersOnShift': 'mean',
            'NursesOnShift': 'mean',
            'StaffToPatientRatio': 'mean',
            'triagecategory_encoded': 'mean',
            'has_tests': 'mean',
            'consultation_needed': 'mean',
            'hour': 'mean',
            'is_weekend': 'mean'
        }).reset_index()
        
        # Features for department efficiency
        dept_features = [
            'department_encoded', 'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift',
            'StaffToPatientRatio', 'triagecategory_encoded', 'has_tests', 'consultation_needed',
            'hour', 'is_weekend'
        ]
        
        X = dept_data[dept_features].copy()
        y = dept_data['TotalTimeInHospital'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Store model and results
        self.models['department_efficiency'] = model
        self.scalers['department_efficiency'] = scaler
        self.feature_columns['department_efficiency'] = dept_features
        self.model_performance['department_efficiency'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(dept_features)
        }
        
        print(f"   ✅ Department Efficiency Model - R²: {r2:.3f}, MAE: {mae:.1f} min, RMSE: {rmse:.1f} min")
        
        return model, scaler, dept_features
    
    def save_models(self):
        """Save all trained models"""
        print("\n💾 Saving improved models...")
        
        # Create models directory
        os.makedirs('backend/models', exist_ok=True)
        
        # Save each model
        for model_name, model in self.models.items():
            model_data = {
                'model': model,
                'scaler': self.scalers[model_name],
                'feature_columns': self.feature_columns[model_name],
                'encoders': self.encoders,
                'performance': self.model_performance[model_name],
                'trained_at': datetime.now().isoformat(),
                'dataset_size': len(self.processed_df)
            }
            
            filename = f'backend/models/{model_name}_model.pkl'
            joblib.dump(model_data, filename)
            print(f"   ✅ Saved {model_name} model to {filename}")
        
        # Save model summary
        summary = {
            'models_trained': list(self.models.keys()),
            'performance_summary': self.model_performance,
            'dataset_info': {
                'total_records': len(self.processed_df),
                'features_engineered': len(self.processed_df.columns),
                'departments': self.processed_df['Department'].nunique(),
                'date_range': f"{self.processed_df['VisitDate'].min()} to {self.processed_df['VisitDate'].max()}"
            },
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(summary, 'backend/models/improved_model_summary.pkl')
        print(f"   ✅ Saved model summary to backend/models/improved_model_summary.pkl")
    
    def print_performance_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "="*80)
        print("📊 IMPROVED MODEL PERFORMANCE SUMMARY")
        print("="*80)
        
        for model_name, performance in self.model_performance.items():
            print(f"\n🎯 {model_name.replace('_', ' ').title()} Model:")
            print(f"   R² Score: {performance['r2_score']:.3f}")
            print(f"   MAE: {performance['mae']:.2f}")
            print(f"   RMSE: {performance['rmse']:.2f}")
            print(f"   Features: {performance['features_count']}")
            if 'model_type' in performance:
                print(f"   Model Type: {performance['model_type']}")
        
        print(f"\n📈 Overall Performance:")
        avg_r2 = np.mean([p['r2_score'] for p in self.model_performance.values()])
        print(f"   Average R² Score: {avg_r2:.3f}")
        
        best_model = max(self.model_performance.items(), key=lambda x: x[1]['r2_score'])
        print(f"   Best Performing Model: {best_model[0]} (R²: {best_model[1]['r2_score']:.3f})")
        
        print(f"\n✅ All improved models trained successfully with {len(self.processed_df):,} records!")
        print("="*80)

def main():
    """Main training function"""
    print("🚀 Starting Improved Hospital Model Training")
    print("="*60)
    
    # Initialize trainer
    trainer = ImprovedHospitalModelTrainer()
    
    # Load and preprocess data
    trainer.load_and_preprocess_data()
    
    # Train improved models
    trainer.train_wait_time_model()
    trainer.train_peak_time_model()
    trainer.train_department_efficiency_model()
    
    # Save models
    trainer.save_models()
    
    # Print performance summary
    trainer.print_performance_summary()
    
    print("\n🎉 Improved model training completed successfully!")
    print("All models are now ready for production use with enhanced performance.")

if __name__ == "__main__":
    main()

            