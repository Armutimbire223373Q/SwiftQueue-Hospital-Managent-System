"""
Data Augmentation Retraining for Improved Model Effectiveness
Increases dataset size and diversity through synthetic data generation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.neighbors import NearestNeighbors
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AugmentedDataRetrainer:
    """Retrainer using data augmentation techniques"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.augmentation_stats = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the hospital dataset"""
        print("📊 Loading hospital dataset for augmented retraining...")
        
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
        """Feature engineering"""
        print("🔧 Engineering features...")
        
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
        
        print("   ✅ Features engineered")
    
    def smote_augmentation(self, X, y, target_ratio=0.5):
        """SMOTE-like augmentation for regression data"""
        print("🔄 Applying SMOTE-like augmentation...")
        
        # Find nearest neighbors for each sample
        nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(X)
        distances, indices = nbrs.kneighbors(X)
        
        augmented_X = []
        augmented_y = []
        
        # Generate synthetic samples
        n_samples = int(len(X) * target_ratio)
        
        for i in range(n_samples):
            # Randomly select a sample
            idx = np.random.randint(0, len(X))
            
            # Select a random neighbor
            neighbor_idx = np.random.choice(indices[idx][1:])  # Exclude self
            
            # Generate synthetic sample
            alpha = np.random.random()
            synthetic_x = X.iloc[idx] + alpha * (X.iloc[neighbor_idx] - X.iloc[idx])
            synthetic_y = y.iloc[idx] + alpha * (y.iloc[neighbor_idx] - y.iloc[idx])
            
            augmented_X.append(synthetic_x)
            augmented_y.append(synthetic_y)
        
        # Convert to DataFrames
        augmented_X_df = pd.DataFrame(augmented_X, columns=X.columns)
        augmented_y_series = pd.Series(augmented_y)
        
        print(f"   ✅ Generated {len(augmented_X)} synthetic samples")
        
        return augmented_X_df, augmented_y_series
    
    def noise_augmentation(self, X, y, noise_factor=0.1):
        """Add controlled noise to existing data"""
        print("🔊 Applying noise augmentation...")
        
        # Add Gaussian noise to numeric features
        numeric_features = X.select_dtypes(include=[np.number]).columns
        
        augmented_X = X.copy()
        augmented_y = y.copy()
        
        for feature in numeric_features:
            noise = np.random.normal(0, X[feature].std() * noise_factor, len(X))
            augmented_X[feature] = X[feature] + noise
        
        # Add small random variation to target
        target_noise = np.random.normal(0, y.std() * noise_factor, len(y))
        augmented_y = y + target_noise
        
        print(f"   ✅ Added noise to {len(numeric_features)} features")
        
        return augmented_X, augmented_y
    
    def time_shift_augmentation(self, X, y):
        """Create time-shifted variations"""
        print("⏰ Applying time shift augmentation...")
        
        augmented_X = X.copy()
        augmented_y = y.copy()
        
        # Shift arrival hour by ±1 hour
        if 'ArrivalHour' in X.columns:
            hour_shift = np.random.choice([-1, 1], len(X))
            augmented_X['ArrivalHour'] = (X['ArrivalHour'] + hour_shift) % 24
        
        # Adjust peak hour indicator
        if 'is_peak_hour' in X.columns:
            augmented_X['is_peak_hour'] = augmented_X['ArrivalHour'].apply(
                lambda x: 1 if x in [8, 9, 10, 14, 15, 16] else 0
            )
        
        print(f"   ✅ Applied time shifts to {len(X)} samples")
        
        return augmented_X, augmented_y
    
    def retrain_with_augmentation(self):
        """Retrain models with augmented data"""
        print("🚀 Starting Augmented Data Retraining...")
        print("=" * 60)
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Prepare features for wait time prediction
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
        
        print(f"📊 Original dataset: {len(X)} samples")
        
        # Apply different augmentation techniques
        augmented_datasets = []
        
        # 1. SMOTE-like augmentation
        smote_X, smote_y = self.smote_augmentation(X, y, target_ratio=0.3)
        augmented_datasets.append((smote_X, smote_y, "SMOTE"))
        
        # 2. Noise augmentation
        noise_X, noise_y = self.noise_augmentation(X, y, noise_factor=0.05)
        augmented_datasets.append((noise_X, noise_y, "Noise"))
        
        # 3. Time shift augmentation
        shift_X, shift_y = self.time_shift_augmentation(X, y)
        augmented_datasets.append((shift_X, shift_y, "TimeShift"))
        
        # Combine all augmented data
        all_X = pd.concat([X] + [aug_X for aug_X, _, _ in augmented_datasets], ignore_index=True)
        all_y = pd.concat([y] + [aug_y for _, aug_y, _ in augmented_datasets], ignore_index=True)
        
        print(f"📈 Augmented dataset: {len(all_X)} samples ({len(all_X)/len(X):.1f}x increase)")
        
        # Split augmented data
        X_train, X_test, y_train, y_test = train_test_split(all_X, all_y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models on augmented data
        models_to_train = {
            'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, random_state=42)
        }
        
        results = {}
        
        for name, model in models_to_train.items():
            print(f"🤖 Training {name} on augmented data...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            print(f"   R² Score: {r2:.4f}")
            print(f"   MAE: {mae:.2f}")
            
            results[name] = {'r2': r2, 'mae': mae}
            
            # Save model
            os.makedirs('models', exist_ok=True)
            joblib.dump(model, f'models/augmented_{name.lower()}_model.pkl')
        
        # Save scaler and encoder
        joblib.dump(scaler, 'models/augmented_scaler.pkl')
        joblib.dump(le_department, 'models/augmented_department_encoder.pkl')
        
        # Save augmentation statistics
        self.augmentation_stats = {
            'original_samples': len(X),
            'augmented_samples': len(all_X),
            'augmentation_ratio': len(all_X) / len(X),
            'augmentation_methods': [method for _, _, method in augmented_datasets],
            'performance_results': results,
            'retraining_date': datetime.now().isoformat()
        }
        
        joblib.dump(self.augmentation_stats, 'models/augmentation_stats.pkl')
        
        print("=" * 60)
        print("🎉 Augmented Data Retraining Complete!")
        print(f"📊 Dataset size increased by {len(all_X)/len(X):.1f}x")
        print(f"🤖 Models trained: {len(results)}")
        for name, metrics in results.items():
            print(f"   {name}: R² = {metrics['r2']:.4f}, MAE = {metrics['mae']:.2f}")
        print("✅ All augmented models saved to models/ directory")
        
        return results

if __name__ == "__main__":
    augmented_retrainer = AugmentedDataRetrainer()
    results = augmented_retrainer.retrain_with_augmentation()
