"""
Enhanced AI Model Training with Comprehensive Hospital Dataset
Trains multiple specialized models for different aspects of hospital workflow
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedHospitalModelTrainer:
    """Enhanced trainer for multiple hospital workflow models"""
    
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
        self._engineer_features()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean the dataset"""
        print("🧹 Cleaning dataset...")
        
        # Create a copy for processing
        self.processed_df = self.df.copy()
        
        # Handle missing values
        self.processed_df = self.processed_df.fillna({
            'RegistrationWaitTimeTime': 0,
            'CheckInToNurseTime': 0,
            'NurseToTriageCompleteTime': 0,
            'TriageToProviderStartTime': 0,
            'ConsultationDurationTime': 0,
            'ProviderEndToTestsCompleteTime': 0,
            'TestsToDischargeTime': 0,
            'TotalTimeInHospital': 0,
            'FacilityOccupancyRate': 0.5,
            'ProvidersOnShift': 5,
            'NursesOnShift': 8,
            'StaffToPatientRatio': 0.3
        })
        
        # Remove any remaining infinite values
        self.processed_df = self.processed_df.replace([np.inf, -np.inf], np.nan)
        self.processed_df = self.processed_df.fillna(0)
        
        print(f"   Cleaned data: {len(self.processed_df):,} records")
    
    def _engineer_features(self):
        """Engineer comprehensive features for all models"""
        print("🔧 Engineering comprehensive features...")
        
        # Time-based features
        self.processed_df['hour'] = self.processed_df['ArrivalHour']
        self.processed_df['day_of_week'] = self.processed_df['ArrivalDayOfWeek']
        self.processed_df['month'] = self.processed_df['ArrivalMonth']
        self.processed_df['is_weekend'] = (self.processed_df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding for time features
        self.processed_df['hour_sin'] = np.sin(2 * np.pi * self.processed_df['hour'] / 24)
        self.processed_df['hour_cos'] = np.cos(2 * np.pi * self.processed_df['hour'] / 24)
        self.processed_df['dow_sin'] = np.sin(2 * np.pi * self.processed_df['day_of_week'] / 7)
        self.processed_df['dow_cos'] = np.cos(2 * np.pi * self.processed_df['day_of_week'] / 7)
        
        # Peak hours identification
        self.processed_df['is_peak_hour'] = (
            (self.processed_df['hour'] >= 8) & (self.processed_df['hour'] <= 10) |
            (self.processed_df['hour'] >= 12) & (self.processed_df['hour'] <= 14) |
            (self.processed_df['hour'] >= 17) & (self.processed_df['hour'] <= 19)
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
        
        # Department encoding
        dept_encoder = LabelEncoder()
        self.processed_df['department_encoded'] = dept_encoder.fit_transform(self.processed_df['Department'].astype(str))
        self.encoders['department'] = dept_encoder
        
        # Triage category encoding
        triage_encoder = LabelEncoder()
        self.processed_df['triage_encoded'] = triage_encoder.fit_transform(self.processed_df['TriageCategory'].astype(str))
        self.encoders['triage'] = triage_encoder
        
        # Age group encoding
        age_encoder = LabelEncoder()
        self.processed_df['age_group_encoded'] = age_encoder.fit_transform(self.processed_df['AgeGroup'].astype(str))
        self.encoders['age_group'] = age_encoder
        
        # Insurance type encoding
        insurance_encoder = LabelEncoder()
        self.processed_df['insurance_encoded'] = insurance_encoder.fit_transform(self.processed_df['InsuranceType'].astype(str))
        self.encoders['insurance'] = insurance_encoder
        
        # Appointment type encoding
        appt_encoder = LabelEncoder()
        self.processed_df['appointment_type_encoded'] = appt_encoder.fit_transform(self.processed_df['AppointmentType'].astype(str))
        self.encoders['appointment_type'] = appt_encoder
        
        # Resource features
        self.processed_df['provider_nurse_ratio'] = (
            self.processed_df['ProvidersOnShift'] / (self.processed_df['NursesOnShift'] + 1)
        )
        
        self.processed_df['total_staff'] = (
            self.processed_df['ProvidersOnShift'] + self.processed_df['NursesOnShift']
        )
        
        # Occupancy categories
        self.processed_df['occupancy_level'] = pd.cut(
            self.processed_df['FacilityOccupancyRate'],
            bins=[0, 0.3, 0.6, 0.8, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        occupancy_encoder = LabelEncoder()
        self.processed_df['occupancy_encoded'] = occupancy_encoder.fit_transform(
            self.processed_df['occupancy_level'].astype(str)
        )
        self.encoders['occupancy'] = occupancy_encoder
        
        # Interaction features
        self.processed_df['dept_occupancy_interaction'] = (
            self.processed_df['department_encoded'] * self.processed_df['FacilityOccupancyRate']
        )
        
        self.processed_df['triage_occupancy_interaction'] = (
            self.processed_df['triage_encoded'] * self.processed_df['FacilityOccupancyRate']
        )
        
        self.processed_df['hour_occupancy_interaction'] = (
            self.processed_df['hour'] * self.processed_df['FacilityOccupancyRate']
        )
        
        # Test-related features
        self.processed_df['has_tests'] = (
            self.processed_df['TestsOrdered'].notna() & 
            (self.processed_df['TestsOrdered'] != 'None')
        ).astype(int)
        
        # Consultation features
        self.processed_df['consultation_needed'] = self.processed_df['ConsultationNeeded'].astype(int)
        
        print(f"   Engineered {len(self.processed_df.columns)} features")
    
    def train_wait_time_model(self):
        """Train enhanced wait time prediction model"""
        print("\n⏱️ Training Enhanced Wait Time Prediction Model...")
        
        # Features for wait time prediction
        wait_time_features = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
            'is_peak_hour', 'is_business_hours', 'is_morning_rush', 'is_evening_rush',
            'department_encoded', 'triage_encoded', 'age_group_encoded', 'insurance_encoded',
            'appointment_type_encoded', 'FacilityOccupancyRate', 'ProvidersOnShift',
            'NursesOnShift', 'StaffToPatientRatio', 'provider_nurse_ratio', 'total_staff',
            'occupancy_encoded', 'dept_occupancy_interaction', 'triage_occupancy_interaction',
            'hour_occupancy_interaction', 'has_tests', 'consultation_needed'
        ]
        
        X = self.processed_df[wait_time_features].copy()
        y = self.processed_df['TotalTimeInHospital'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=8,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Store model and results
        self.models['wait_time'] = model
        self.scalers['wait_time'] = scaler
        self.feature_columns['wait_time'] = wait_time_features
        self.model_performance['wait_time'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(wait_time_features)
        }
        
        print(f"   ✅ Wait Time Model - R²: {r2:.3f}, MAE: {mae:.1f} min, RMSE: {rmse:.1f} min")
        
        return model, scaler, wait_time_features
    
    def train_triage_priority_model(self):
        """Train triage priority prediction model"""
        print("\n🚨 Training Triage Priority Prediction Model...")
        
        # Features for triage priority
        triage_features = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
            'is_peak_hour', 'is_business_hours', 'is_morning_rush', 'is_evening_rush',
            'department_encoded', 'age_group_encoded', 'insurance_encoded',
            'appointment_type_encoded', 'FacilityOccupancyRate', 'ProvidersOnShift',
            'NursesOnShift', 'StaffToPatientRatio', 'provider_nurse_ratio', 'total_staff',
            'occupancy_encoded', 'has_tests', 'consultation_needed'
        ]
        
        X = self.processed_df[triage_features].copy()
        y = self.processed_df['triage_encoded'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=150,
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
        self.models['triage_priority'] = model
        self.scalers['triage_priority'] = scaler
        self.feature_columns['triage_priority'] = triage_features
        self.model_performance['triage_priority'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(triage_features)
        }
        
        print(f"   ✅ Triage Priority Model - R²: {r2:.3f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return model, scaler, triage_features
    
    def train_department_performance_model(self):
        """Train department performance prediction model"""
        print("\n🏥 Training Department Performance Model...")
        
        # Aggregate data by department and hour
        dept_hourly = self.processed_df.groupby(['department_encoded', 'hour']).agg({
            'TotalTimeInHospital': 'mean',
            'FacilityOccupancyRate': 'mean',
            'ProvidersOnShift': 'mean',
            'NursesOnShift': 'mean',
            'StaffToPatientRatio': 'mean',
            'triage_encoded': 'mean',
            'has_tests': 'mean',
            'consultation_needed': 'mean'
        }).reset_index()
        
        # Features for department performance
        dept_features = [
            'department_encoded', 'hour', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'triage_encoded', 'has_tests', 'consultation_needed'
        ]
        
        X = dept_hourly[dept_features].copy()
        y = dept_hourly['TotalTimeInHospital'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.15,
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
        self.models['department_performance'] = model
        self.scalers['department_performance'] = scaler
        self.feature_columns['department_performance'] = dept_features
        self.model_performance['department_performance'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(dept_features)
        }
        
        print(f"   ✅ Department Performance Model - R²: {r2:.3f}, MAE: {mae:.1f} min, RMSE: {rmse:.1f} min")
        
        return model, scaler, dept_features
    
    def train_resource_optimization_model(self):
        """Train resource optimization model"""
        print("\n👥 Training Resource Optimization Model...")
        
        # Features for resource optimization
        resource_features = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
            'is_peak_hour', 'is_business_hours', 'is_morning_rush', 'is_evening_rush',
            'department_encoded', 'triage_encoded', 'age_group_encoded',
            'FacilityOccupancyRate', 'has_tests', 'consultation_needed'
        ]
        
        X = self.processed_df[resource_features].copy()
        y = self.processed_df['StaffToPatientRatio'].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Store model and results
        self.models['resource_optimization'] = model
        self.scalers['resource_optimization'] = scaler
        self.feature_columns['resource_optimization'] = resource_features
        self.model_performance['resource_optimization'] = {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'features_count': len(resource_features)
        }
        
        print(f"   ✅ Resource Optimization Model - R²: {r2:.3f}, MAE: {mae:.3f}, RMSE: {rmse:.3f}")
        
        return model, scaler, resource_features
    
    def train_peak_time_model(self):
        """Train peak time prediction model"""
        print("\n🕐 Training Peak Time Prediction Model...")
        
        # Aggregate data by hour and day of week
        hourly_data = self.processed_df.groupby(['hour', 'day_of_week']).agg({
            'TotalTimeInHospital': 'mean',
            'FacilityOccupancyRate': 'mean',
            'ProvidersOnShift': 'mean',
            'NursesOnShift': 'mean',
            'StaffToPatientRatio': 'mean',
            'triage_encoded': 'mean',
            'department_encoded': 'mean'
        }).reset_index()
        
        # Features for peak time prediction
        peak_features = [
            'hour', 'day_of_week', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'triage_encoded', 'department_encoded'
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
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
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
    
    def save_models(self):
        """Save all trained models"""
        print("\n💾 Saving enhanced models...")
        
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
        
        joblib.dump(summary, 'backend/models/model_summary.pkl')
        print(f"   ✅ Saved model summary to backend/models/model_summary.pkl")
    
    def print_performance_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "="*80)
        print("📊 ENHANCED MODEL PERFORMANCE SUMMARY")
        print("="*80)
        
        for model_name, performance in self.model_performance.items():
            print(f"\n🎯 {model_name.replace('_', ' ').title()} Model:")
            print(f"   R² Score: {performance['r2_score']:.3f}")
            print(f"   MAE: {performance['mae']:.2f}")
            print(f"   RMSE: {performance['rmse']:.2f}")
            print(f"   Features: {performance['features_count']}")
        
        print(f"\n📈 Overall Performance:")
        avg_r2 = np.mean([p['r2_score'] for p in self.model_performance.values()])
        print(f"   Average R² Score: {avg_r2:.3f}")
        
        best_model = max(self.model_performance.items(), key=lambda x: x[1]['r2_score'])
        print(f"   Best Performing Model: {best_model[0]} (R²: {best_model[1]['r2_score']:.3f})")
        
        print(f"\n✅ All models trained successfully with {len(self.processed_df):,} records!")
        print("="*80)

def main():
    """Main training function"""
    print("🚀 Starting Enhanced Hospital Model Training")
    print("="*60)
    
    # Initialize trainer
    trainer = EnhancedHospitalModelTrainer()
    
    # Load and preprocess data
    trainer.load_and_preprocess_data()
    
    # Train all models
    trainer.train_wait_time_model()
    trainer.train_triage_priority_model()
    trainer.train_department_performance_model()
    trainer.train_resource_optimization_model()
    trainer.train_peak_time_model()
    
    # Save models
    trainer.save_models()
    
    # Print performance summary
    trainer.print_performance_summary()
    
    print("\n🎉 Enhanced model training completed successfully!")
    print("All models are now ready for production use with the comprehensive hospital dataset.")

if __name__ == "__main__":
    main()
