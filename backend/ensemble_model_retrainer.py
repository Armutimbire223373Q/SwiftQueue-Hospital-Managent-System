"""
Ensemble Model Retraining for Maximum Effectiveness
Combines multiple models to achieve superior performance
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor, StackingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnsembleModelRetrainer:
    """Advanced ensemble retrainer for maximum model effectiveness"""
    
    def __init__(self):
        self.ensemble_models = {}
        self.base_models = {}
        self.scalers = {}
        self.encoders = {}
        self.performance_metrics = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the hospital dataset"""
        print("📊 Loading hospital dataset for ensemble retraining...")
        
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} columns")
        
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
        
        categorical_columns = self.processed_df.select_dtypes(include=['object']).columns
        self.processed_df[categorical_columns] = self.processed_df[categorical_columns].fillna('Unknown')
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_features(self):
        """Advanced feature engineering for ensemble models"""
        print("🔧 Engineering features for ensemble models...")
        
        # Time-based features
        if 'ArrivalHour' in self.processed_df.columns:
            self.processed_df['is_peak_hour'] = self.processed_df['ArrivalHour'].apply(
                lambda x: 1 if x in [8, 9, 10, 14, 15, 16] else 0
            )
            self.processed_df['is_weekend'] = self.processed_df['ArrivalDayOfWeek'].apply(
                lambda x: 1 if x in [6, 7] else 0
            )
            self.processed_df['hour_sin'] = np.sin(2 * np.pi * self.processed_df['ArrivalHour'] / 24)
            self.processed_df['hour_cos'] = np.cos(2 * np.pi * self.processed_df['ArrivalHour'] / 24)
        
        # Department efficiency features
        if 'Department' in self.processed_df.columns:
            dept_stats = self.processed_df.groupby('Department')['TotalTimeInHospital'].agg(['mean', 'std', 'median']).reset_index()
            dept_stats.columns = ['Department', 'dept_avg_time', 'dept_time_std', 'dept_median_time']
            self.processed_df = self.processed_df.merge(dept_stats, on='Department', how='left')
        
        # Staff efficiency features
        if 'StaffToPatientRatio' in self.processed_df.columns:
            self.processed_df['staff_efficiency'] = 1 / (self.processed_df['StaffToPatientRatio'] + 0.001)
            self.processed_df['staff_workload'] = self.processed_df['StaffToPatientRatio'] * self.processed_df['FacilityOccupancyRate']
        
        # Resource utilization features
        if 'FacilityOccupancyRate' in self.processed_df.columns:
            self.processed_df['occupancy_level'] = pd.cut(
                self.processed_df['FacilityOccupancyRate'], 
                bins=[0, 0.3, 0.6, 0.8, 1.0], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            self.processed_df['occupancy_squared'] = self.processed_df['FacilityOccupancyRate'] ** 2
        
        # Interaction features
        if 'ProvidersOnShift' in self.processed_df.columns and 'NursesOnShift' in self.processed_df.columns:
            self.processed_df['total_staff'] = self.processed_df['ProvidersOnShift'] + self.processed_df['NursesOnShift']
            self.processed_df['provider_nurse_ratio'] = self.processed_df['ProvidersOnShift'] / (self.processed_df['NursesOnShift'] + 0.001)
        
        print("   ✅ Advanced features engineered for ensemble")
    
    def create_wait_time_ensemble(self):
        """Create ensemble model for wait time prediction"""
        print("⏱️ Creating Wait Time Ensemble Model...")
        
        # Prepare features
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'ArrivalMonth',
            'is_peak_hour', 'is_weekend', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_time', 'staff_efficiency', 'hour_sin', 'hour_cos',
            'staff_workload', 'occupancy_squared', 'total_staff', 'provider_nurse_ratio'
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
        
        # Create base models with optimized parameters
        base_models = {
            'rf': RandomForestRegressor(n_estimators=300, max_depth=20, min_samples_split=5, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=7, random_state=42),
            'et': ExtraTreesRegressor(n_estimators=300, max_depth=20, min_samples_split=5, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'elastic': ElasticNet(alpha=0.1, l1_ratio=0.5),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale')
        }
        
        # Evaluate individual models
        individual_scores = {}
        for name, model in base_models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            score = r2_score(y_test, y_pred)
            individual_scores[name] = score
            print(f"   {name}: R² = {score:.4f}")
        
        # Create Voting Ensemble
        voting_ensemble = VotingRegressor([
            ('rf', base_models['rf']),
            ('gb', base_models['gb']),
            ('et', base_models['et']),
            ('ridge', base_models['ridge'])
        ])
        
        voting_ensemble.fit(X_train_scaled, y_train)
        voting_score = voting_ensemble.score(X_test_scaled, y_test)
        print(f"   Voting Ensemble: R² = {voting_score:.4f}")
        
        # Create Stacking Ensemble
        stacking_ensemble = StackingRegressor(
            estimators=[
                ('rf', base_models['rf']),
                ('gb', base_models['gb']),
                ('et', base_models['et'])
            ],
            final_estimator=Ridge(alpha=1.0),
            cv=5
        )
        
        stacking_ensemble.fit(X_train_scaled, y_train)
        stacking_score = stacking_ensemble.score(X_test_scaled, y_test)
        print(f"   Stacking Ensemble: R² = {stacking_score:.4f}")
        
        # Choose best ensemble
        if stacking_score > voting_score:
            best_ensemble = stacking_ensemble
            best_score = stacking_score
            ensemble_type = "Stacking"
        else:
            best_ensemble = voting_ensemble
            best_score = voting_score
            ensemble_type = "Voting"
        
        print(f"   ✅ Best Ensemble: {ensemble_type} with R² = {best_score:.4f}")
        
        # Save ensemble model
        os.makedirs('models', exist_ok=True)
        joblib.dump(best_ensemble, 'models/ensemble_wait_time_model.pkl')
        joblib.dump(scaler, 'models/ensemble_wait_time_scaler.pkl')
        joblib.dump(le_department, 'models/ensemble_department_encoder.pkl')
        
        self.ensemble_models['wait_time'] = best_ensemble
        self.scalers['wait_time'] = scaler
        self.encoders['department'] = le_department
        self.performance_metrics['wait_time'] = {
            'ensemble_score': best_score,
            'individual_scores': individual_scores,
            'ensemble_type': ensemble_type
        }
        
        return best_ensemble, best_score
    
    def create_triage_ensemble(self):
        """Create ensemble model for triage prediction"""
        print("🏥 Creating Triage Priority Ensemble Model...")
        
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, VotingClassifier
        
        # Prepare features
        feature_columns = [
            'ArrivalHour', 'ArrivalDayOfWeek', 'FacilityOccupancyRate',
            'ProvidersOnShift', 'NursesOnShift', 'StaffToPatientRatio',
            'dept_avg_time', 'staff_efficiency', 'hour_sin', 'hour_cos'
        ]
        
        # Encode categorical variables
        le_triage = LabelEncoder()
        self.processed_df['TriageCategory_encoded'] = le_triage.fit_transform(self.processed_df['TriageCategory'])
        
        le_age = LabelEncoder()
        self.processed_df['AgeGroup_encoded'] = le_age.fit_transform(self.processed_df['AgeGroup'])
        feature_columns.append('AgeGroup_encoded')
        
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
        
        # Create base classifiers
        base_classifiers = {
            'rf': RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
            'gb': GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, random_state=42),
            'et': ExtraTreesClassifier(n_estimators=200, max_depth=15, random_state=42)
        }
        
        # Evaluate individual models
        individual_scores = {}
        for name, model in base_classifiers.items():
            model.fit(X_train_scaled, y_train)
            score = model.score(X_test_scaled, y_test)
            individual_scores[name] = score
            print(f"   {name}: Accuracy = {score:.4f}")
        
        # Create Voting Ensemble
        voting_ensemble = VotingClassifier([
            ('rf', base_classifiers['rf']),
            ('gb', base_classifiers['gb']),
            ('et', base_classifiers['et'])
        ], voting='soft')
        
        voting_ensemble.fit(X_train_scaled, y_train)
        voting_score = voting_ensemble.score(X_test_scaled, y_test)
        print(f"   Voting Ensemble: Accuracy = {voting_score:.4f}")
        
        # Save ensemble model
        joblib.dump(voting_ensemble, 'models/ensemble_triage_model.pkl')
        joblib.dump(scaler, 'models/ensemble_triage_scaler.pkl')
        joblib.dump(le_triage, 'models/ensemble_triage_encoder.pkl')
        joblib.dump(le_age, 'models/ensemble_age_encoder.pkl')
        
        self.ensemble_models['triage'] = voting_ensemble
        self.scalers['triage'] = scaler
        self.encoders['triage'] = le_triage
        self.encoders['age'] = le_age
        self.performance_metrics['triage'] = {
            'ensemble_score': voting_score,
            'individual_scores': individual_scores,
            'ensemble_type': 'Voting'
        }
        
        return voting_ensemble, voting_score
    
    def retrain_all_ensembles(self):
        """Retrain all models using ensemble methods"""
        print("🚀 Starting Ensemble Model Retraining...")
        print("=" * 60)
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Create ensemble models
        results = {}
        
        # Wait time ensemble
        wait_ensemble, wait_score = self.create_wait_time_ensemble()
        results['wait_time'] = wait_score
        
        # Triage ensemble
        triage_ensemble, triage_score = self.create_triage_ensemble()
        results['triage'] = triage_score
        
        # Save performance summary
        performance_summary = {
            'retraining_date': datetime.now().isoformat(),
            'retraining_type': 'ensemble',
            'models_retrained': len(results),
            'performance_scores': results,
            'performance_metrics': self.performance_metrics,
            'dataset_size': len(self.processed_df),
            'features_used': len(self.processed_df.columns)
        }
        
        joblib.dump(performance_summary, 'models/ensemble_retraining_summary.pkl')
        
        print("=" * 60)
        print("🎉 Ensemble Model Retraining Complete!")
        print(f"📊 Models retrained: {len(results)}")
        print(f"⏱️ Wait Time Ensemble R²: {results['wait_time']:.4f}")
        print(f"🏥 Triage Ensemble Accuracy: {results['triage']:.4f}")
        print("✅ All ensemble models saved to models/ directory")
        
        return results

if __name__ == "__main__":
    ensemble_retrainer = EnsembleModelRetrainer()
    results = ensemble_retrainer.retrain_all_ensembles()
