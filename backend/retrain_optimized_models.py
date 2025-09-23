"""
Advanced Model Retraining with Hyperparameter Optimization
Increases model effectiveness through systematic parameter tuning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class OptimizedModelRetrainer:
    """Advanced retrainer with hyperparameter optimization"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.best_params = {}
        self.performance_history = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the hospital dataset"""
        print("📊 Loading hospital dataset for retraining...")
        
        # Load the dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} columns")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_features()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean the dataset"""
        print("🧹 Cleaning dataset...")
        
        self.processed_df = self.df.copy()
        
        # Handle missing values
        numeric_columns = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_columns] = self.processed_df[numeric_columns].fillna(self.processed_df[numeric_columns].median())
        
        # Handle categorical missing values
        categorical_columns = self.processed_df.select_dtypes(include=['object']).columns
        self.processed_df[categorical_columns] = self.processed_df[categorical_columns].fillna('Unknown')
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_features(self):
        """Advanced feature engineering"""
        print("🔧 Engineering advanced features...")
        
        # Time-based features
        if 'ArrivalHour' in self.processed_df.columns:
            self.processed_df['is_peak_hour'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if x in [8, 9, 10, 14, 15, 16] else 0
            )
            self.processed_df['is_weekend'] = self.processed_df['ArrivalDayOfWeek'].apply(
                lambda x: 1 if x in [6, 7] else 0
            )
        
        # Department efficiency features
        if 'Department' in self.processed_df.columns:
            dept_stats = self.processed_df.groupby('Department')['TotalTimeInHospital'].agg(['mean', 'std']).reset_index()
            dept_stats.columns = ['Department', 'dept_avg_time', 'dept_time_std']
            self.processed_df = self.processed_df.merge(dept_stats, on='Department', how='left')
        
        # Staff efficiency features
        if 'StaffToPatientRatio' in self.processed_df.columns:
            self.processed_df['staff_efficiency'] = 1 / (self.processed_df['StaffToPatientRatio'] + 0.001)
        
        # Resource utilization features
        if 'FacilityOccupancyRate' in self.processed_df.columns:
            self.processed_df['occupancy_level'] = pd.cut(
                self.processed_df['FacilityOccupancyRate'], 
                bins=[0, 0.3, 0.6, 0.8, 1.0], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        print("   ✅ Advanced features engineered")
    
    def optimize_wait_time_model(self):
        """Optimize wait time prediction model with hyperparameter tuning"""
        print("⏱️ Optimizing Wait Time Prediction Model...")
        
        # Prepare features and target
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'is_peak_hour', 'is_weekend', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_time', 'staff_efficiency'
        ]
        
        # Encode categorical variables
        le_department = LabelEncoder()
        self.processed_df['Department_encoded'] = le_department.fit_transform(self.processed_df['Department'])
        feature_columns.append('Department_encoded')
        
        X = self.processed_df[feature_columns].fillna(0)
        y = self.processed_df['TotalTimeInHospital'].fillna(0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define hyperparameter grids for different algorithms
        models_to_tune = {
            'RandomForest': {
                'model': RandomForestRegressor(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7, 10],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'ExtraTrees': {
                'model': ExtraTreesRegressor(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None]
                }
            }
        }
        
        best_model = None
        best_score = -np.inf
        best_name = ""
        
        # Tune each model
        for name, config in models_to_tune.items():
            print(f"   🔍 Tuning {name}...")
            
            # Use RandomizedSearchCV for efficiency
            search = RandomizedSearchCV(
                config['model'],
                config['params'],
                n_iter=50,  # Number of parameter settings sampled
                cv=5,
                scoring='r2',
                random_state=42,
                n_jobs=-1
            )
            
            search.fit(X_train_scaled, y_train)
            
            # Evaluate on test set
            y_pred = search.best_estimator_.predict(X_test_scaled)
            test_score = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            print(f"      Best R² Score: {test_score:.4f}")
            print(f"      MAE: {mae:.2f}")
            print(f"      Best Params: {search.best_params_}")
            
            # Track best model
            if test_score > best_score:
                best_score = test_score
                best_model = search.best_estimator_
                best_name = name
                self.best_params['wait_time'] = search.best_params_
        
        # Save the best model
        os.makedirs('models', exist_ok=True)
        joblib.dump(best_model, 'models/optimized_wait_time_model.pkl')
        joblib.dump(scaler, 'models/wait_time_scaler.pkl')
        joblib.dump(le_department, 'models/department_encoder.pkl')
        
        self.models['wait_time'] = best_model
        self.scalers['wait_time'] = scaler
        self.encoders['department'] = le_department
        
        print(f"   ✅ Best model: {best_name} with R² = {best_score:.4f}")
        return best_model, best_score
    
    def optimize_triage_model(self):
        """Optimize triage priority prediction model"""
        print("🏥 Optimizing Triage Priority Model...")
        
        # Prepare features for triage
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_time', 'staff_efficiency'
        ]
        
        # Encode triage categories
        le_triage = LabelEncoder()
        self.processed_df['TriageCategory_encoded'] = le_triage.fit_transform(self.processed_df['TriageCategory'])
        
        # Encode age groups
        le_age = LabelEncoder()
        self.processed_df['AgeGroup_encoded'] = le_age.fit_transform(self.processed_df['AgeGroup'])
        feature_columns.append('AgeGroup_encoded')
        
        # Encode departments
        le_department = LabelEncoder()
        self.processed_df['Department_encoded'] = le_department.fit_transform(self.processed_df['Department'])
        feature_columns.append('Department_encoded')
        
        X = self.processed_df[feature_columns].fillna(0)
        y = self.processed_df['TriageCategory_encoded']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Use RandomForest for classification
        from sklearn.ensemble import RandomForestClassifier
        
        rf_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
        
        search = RandomizedSearchCV(
            RandomForestClassifier(random_state=42),
            rf_params,
            n_iter=30,
            cv=5,
            scoring='accuracy',
            random_state=42,
            n_jobs=-1
        )
        
        search.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = search.best_estimator_.predict(X_test_scaled)
        accuracy = search.best_estimator_.score(X_test_scaled, y_test)
        
        print(f"   ✅ Triage model accuracy: {accuracy:.4f}")
        print(f"   Best params: {search.best_params_}")
        
        # Save model
        joblib.dump(search.best_estimator_, 'models/optimized_triage_model.pkl')
        joblib.dump(scaler, 'models/triage_scaler.pkl')
        joblib.dump(le_triage, 'models/triage_encoder.pkl')
        joblib.dump(le_age, 'models/age_encoder.pkl')
        
        self.models['triage'] = search.best_estimator_
        self.scalers['triage'] = scaler
        self.encoders['triage'] = le_triage
        self.encoders['age'] = le_age
        self.best_params['triage'] = search.best_params_
        
        return search.best_estimator_, accuracy
    
    def optimize_peak_time_model(self):
        """Optimize peak time prediction model"""
        print("📈 Optimizing Peak Time Prediction Model...")
        
        # Create peak time target (1 if peak hour, 0 otherwise)
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'FacilityOccupancyRate', 'ProvidersOnShift', 'NursesOnShift'
        ]
        
        X = self.processed_df[feature_columns].fillna(0)
        y = self.processed_df['is_peak_hour']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Use GradientBoosting for peak time prediction
        gb_params = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        search = RandomizedSearchCV(
            GradientBoostingRegressor(random_state=42),
            gb_params,
            n_iter=30,
            cv=5,
            scoring='r2',
            random_state=42,
            n_jobs=-1
        )
        
        search.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = search.best_estimator_.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        
        print(f"   ✅ Peak time model R²: {r2:.4f}")
        print(f"   Best params: {search.best_params_}")
        
        # Save model
        joblib.dump(search.best_estimator_, 'models/optimized_peak_time_model.pkl')
        joblib.dump(scaler, 'models/peak_time_scaler.pkl')
        
        self.models['peak_time'] = search.best_estimator_
        self.scalers['peak_time'] = scaler
        self.best_params['peak_time'] = search.best_params_
        
        return search.best_estimator_, r2
    
    def retrain_all_models(self):
        """Retrain all models with optimization"""
        print("🚀 Starting comprehensive model retraining...")
        print("=" * 60)
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Retrain each model
        results = {}
        
        # Wait time model
        wait_model, wait_score = self.optimize_wait_time_model()
        results['wait_time'] = wait_score
        
        # Triage model
        triage_model, triage_score = self.optimize_triage_model()
        results['triage'] = triage_score
        
        # Peak time model
        peak_model, peak_score = self.optimize_peak_time_model()
        results['peak_time'] = peak_score
        
        # Save performance summary
        performance_summary = {
            'retraining_date': datetime.now().isoformat(),
            'models_retrained': len(results),
            'performance_scores': results,
            'best_parameters': self.best_params,
            'dataset_size': len(self.processed_df),
            'features_used': len(self.processed_df.columns)
        }
        
        joblib.dump(performance_summary, 'models/retraining_summary.pkl')
        
        print("=" * 60)
        print("🎉 Model Retraining Complete!")
        print(f"📊 Models retrained: {len(results)}")
        print(f"⏱️ Wait Time Model R²: {results['wait_time']:.4f}")
        print(f"🏥 Triage Model Accuracy: {results['triage']:.4f}")
        print(f"📈 Peak Time Model R²: {results['peak_time']:.4f}")
        print("✅ All optimized models saved to models/ directory")
        
        return results

if __name__ == "__main__":
    retrainer = OptimizedModelRetrainer()
    results = retrainer.retrain_all_models()
