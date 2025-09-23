"""
Advanced Peak Time Prediction System
Forecasting busy periods for better preparation using ML and time series analysis
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedPeakTimePredictor:
    """Advanced peak time prediction system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.department_patterns = {}
        self.seasonal_patterns = {}
        self.holiday_patterns = {}
        self.peak_thresholds = {}
        
        # Initialize prediction parameters
        self._initialize_parameters()
        
    def _initialize_parameters(self):
        """Initialize prediction parameters and thresholds"""
        print("⚙️ Initializing peak time prediction parameters...")
        
        # Peak time thresholds (percentiles)
        self.peak_thresholds = {
            'low': 0.25,      # Bottom 25% - off-peak
            'medium': 0.50,   # Middle 50% - normal
            'high': 0.75,    # Top 25% - peak
            'extreme': 0.90   # Top 10% - extreme peak
        }
        
        # Seasonal patterns
        self.seasonal_patterns = {
            'spring': {'multiplier': 1.0, 'peak_hours': [9, 14, 16]},
            'summer': {'multiplier': 0.9, 'peak_hours': [8, 13, 15]},
            'fall': {'multiplier': 1.1, 'peak_hours': [9, 14, 16]},
            'winter': {'multiplier': 1.2, 'peak_hours': [8, 12, 15]}
        }
        
        # Holiday patterns
        self.holiday_patterns = {
            'regular': {'multiplier': 1.0, 'pattern': 'normal'},
            'holiday': {'multiplier': 0.7, 'pattern': 'reduced'},
            'pre_holiday': {'multiplier': 1.3, 'pattern': 'increased'},
            'post_holiday': {'multiplier': 1.4, 'pattern': 'catch_up'}
        }
        
        # Department-specific patterns
        self.department_patterns = {
            'Emergency': {'base_multiplier': 1.0, 'peak_hours': [8, 14, 20], 'weekend_factor': 1.2},
            'Cardiology': {'base_multiplier': 0.9, 'peak_hours': [9, 15, 16], 'weekend_factor': 0.8},
            'Neurology': {'base_multiplier': 0.9, 'peak_hours': [10, 14, 15], 'weekend_factor': 0.9},
            'Orthopedics': {'base_multiplier': 0.8, 'peak_hours': [9, 13, 16], 'weekend_factor': 1.1},
            'General Surgery': {'base_multiplier': 0.9, 'peak_hours': [8, 12, 15], 'weekend_factor': 0.7},
            'Internal Medicine': {'base_multiplier': 0.6, 'peak_hours': [9, 14, 16], 'weekend_factor': 0.8},
            'Pediatrics': {'base_multiplier': 0.8, 'peak_hours': [10, 15, 17], 'weekend_factor': 1.0},
            'Obstetrics': {'base_multiplier': 0.9, 'peak_hours': [8, 14, 20], 'weekend_factor': 1.1},
            'Radiology': {'base_multiplier': 0.7, 'peak_hours': [9, 13, 15], 'weekend_factor': 0.6},
            'Oncology': {'base_multiplier': 0.9, 'peak_hours': [9, 14, 16], 'weekend_factor': 0.8}
        }
        
        print(f"   ✅ Initialized parameters for {len(self.department_patterns)} departments")
    
    def load_and_preprocess_data(self):
        """Load and preprocess hospital data for peak time prediction"""
        print("📊 Loading hospital data for peak time prediction...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_features()
        self._analyze_patterns()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean and validate the dataset"""
        print("🧹 Cleaning peak time prediction dataset...")
        
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
        """Engineer features for peak time prediction"""
        print("⚙️ Engineering features for peak time prediction...")
        
        # Time-based features
        if 'ArrivalTime' in self.processed_df.columns:
            self.processed_df['ArrivalTime'] = pd.to_datetime(self.processed_df['ArrivalTime'])
            self.processed_df['Hour'] = self.processed_df['ArrivalTime'].dt.hour
            self.processed_df['DayOfWeek'] = self.processed_df['ArrivalTime'].dt.dayofweek
            self.processed_df['DayOfMonth'] = self.processed_df['ArrivalTime'].dt.day
            self.processed_df['Month'] = self.processed_df['ArrivalTime'].dt.month
            self.processed_df['IsWeekend'] = self.processed_df['DayOfWeek'].isin([5, 6]).astype(int)
            self.processed_df['IsPeakHour'] = self.processed_df['Hour'].isin([8, 9, 10, 14, 15, 16]).astype(int)
        elif 'DayOfWeek' in self.processed_df.columns:
            # Handle string day names
            day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
            self.processed_df['DayOfWeekNumeric'] = self.processed_df['DayOfWeek'].map(day_mapping)
            self.processed_df['IsWeekend'] = self.processed_df['DayOfWeekNumeric'].isin([5, 6]).astype(int)
            # Create synthetic hour data for demonstration
            self.processed_df['Hour'] = np.random.randint(6, 22, len(self.processed_df))
        else:
            # Create synthetic time data for demonstration
            self.processed_df['Hour'] = np.random.randint(6, 22, len(self.processed_df))
            self.processed_df['DayOfWeek'] = np.random.randint(0, 7, len(self.processed_df))
            self.processed_df['IsWeekend'] = (self.processed_df['DayOfWeek'] >= 5).astype(int)
        
        # Cyclical time features
        if 'Hour' in self.processed_df.columns:
            self.processed_df['HourSin'] = np.sin(2 * np.pi * self.processed_df['Hour'] / 24)
            self.processed_df['HourCos'] = np.cos(2 * np.pi * self.processed_df['Hour'] / 24)
            self.processed_df['HourSquared'] = self.processed_df['Hour'] ** 2
        
        if 'DayOfWeek' in self.processed_df.columns:
            # Convert to numeric if it's string
            if self.processed_df['DayOfWeek'].dtype == 'object':
                day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
                self.processed_df['DayOfWeekNumeric'] = self.processed_df['DayOfWeek'].map(day_mapping)
                self.processed_df['DaySin'] = np.sin(2 * np.pi * self.processed_df['DayOfWeekNumeric'] / 7)
                self.processed_df['DayCos'] = np.cos(2 * np.pi * self.processed_df['DayOfWeekNumeric'] / 7)
            else:
                self.processed_df['DaySin'] = np.sin(2 * np.pi * self.processed_df['DayOfWeek'] / 7)
                self.processed_df['DayCos'] = np.cos(2 * np.pi * self.processed_df['DayOfWeek'] / 7)
        
        # Patient volume features
        self.processed_df['PatientVolume'] = 1  # Each record represents one patient
        
        # Department-specific features
        dept_stats = self.processed_df.groupby('Department').agg({
            'PatientVolume': ['count', 'sum'],
            'TotalTimeInHospital': ['mean', 'std']
        }).round(2)
        
        dept_stats.columns = ['DeptPatientCount', 'DeptPatientSum', 'DeptMeanWait', 'DeptStdWait']
        self.processed_df = self.processed_df.merge(dept_stats, left_on='Department', right_index=True, how='left')
        
        # Hourly patterns
        hourly_stats = self.processed_df.groupby('Hour').agg({
            'PatientVolume': ['count', 'sum'],
            'TotalTimeInHospital': ['mean', 'std']
        }).round(2)
        
        hourly_stats.columns = ['HourlyPatientCount', 'HourlyPatientSum', 'HourlyMeanWait', 'HourlyStdWait']
        self.processed_df = self.processed_df.merge(hourly_stats, left_on='Hour', right_index=True, how='left')
        
        # Rolling statistics
        if 'Hour' in self.processed_df.columns:
            self.processed_df['HourlyVolumeMA3'] = self.processed_df.groupby('Department')['PatientVolume'].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean()
            )
            self.processed_df['HourlyVolumeMA7'] = self.processed_df.groupby('Department')['PatientVolume'].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean()
            )
        
        print(f"   ✅ Feature engineering completed: {len(self.processed_df.columns)} features")
    
    def _analyze_patterns(self):
        """Analyze historical patterns for peak time prediction"""
        print("📈 Analyzing historical patterns...")
        
        # Overall hourly patterns
        hourly_counts = self.processed_df.groupby('Hour').size()
        self.overall_hourly_pattern = hourly_counts.to_dict()
        
        # Department-specific patterns
        for dept in self.processed_df['Department'].unique():
            dept_data = self.processed_df[self.processed_df['Department'] == dept]
            dept_hourly = dept_data.groupby('Hour').size()
            self.department_patterns[dept]['hourly_pattern'] = dept_hourly.to_dict()
            
            # Calculate peak hours for this department
            peak_threshold = dept_hourly.quantile(0.75)
            peak_hours = dept_hourly[dept_hourly >= peak_threshold].index.tolist()
            self.department_patterns[dept]['peak_hours'] = sorted(peak_hours)
        
        # Day of week patterns
        dow_counts = self.processed_df.groupby('DayOfWeek').size()
        self.day_of_week_pattern = dow_counts.to_dict()
        
        # Weekend vs weekday patterns
        weekend_data = self.processed_df[self.processed_df['IsWeekend'] == 1]
        weekday_data = self.processed_df[self.processed_df['IsWeekend'] == 0]
        
        self.weekend_pattern = weekend_data.groupby('Hour').size().to_dict()
        self.weekday_pattern = weekday_data.groupby('Hour').size().to_dict()
        
        print(f"   ✅ Pattern analysis completed for {len(self.department_patterns)} departments")
    
    def train_peak_time_models(self):
        """Train ML models for peak time prediction"""
        print("🤖 Training peak time prediction models...")
        
        # Prepare features for training
        feature_columns = [
            'Hour', 'DayOfWeek', 'IsWeekend', 'IsPeakHour',
            'HourSin', 'HourCos', 'HourSquared', 'DaySin', 'DayCos',
            'DeptPatientCount', 'DeptMeanWait', 'DeptStdWait',
            'HourlyPatientCount', 'HourlyMeanWait', 'HourlyStdWait',
            'HourlyVolumeMA3', 'HourlyVolumeMA7'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in self.processed_df.columns]
        X = self.processed_df[available_features].fillna(0)
        
        # Convert all columns to numeric
        for col in X.columns:
            if X[col].dtype == 'object':
                # Try to convert to numeric, if fails, use label encoding
                try:
                    X[col] = pd.to_numeric(X[col])
                except:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
        
        # Target: Patient volume (count per hour)
        y = self.processed_df.groupby(['Hour', 'DayOfWeek', 'Department']).size().reset_index(name='PatientVolume')
        y = y['PatientVolume']
        
        # Align X and y
        X_aligned = X.iloc[:len(y)]
        
        print(f"   Training with {len(available_features)} features: {available_features}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_aligned, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scalers['standard'] = StandardScaler()
        X_train_scaled = self.scalers['standard'].fit_transform(X_train)
        X_test_scaled = self.scalers['standard'].transform(X_test)
        
        # Train RandomForest model
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        
        self.models['random_forest'].fit(X_train_scaled, y_train)
        
        # Train GradientBoosting model
        self.models['gradient_boosting'] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
        
        self.models['gradient_boosting'].fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = self.models['random_forest'].predict(X_test_scaled)
        gb_pred = self.models['gradient_boosting'].predict(X_test_scaled)
        
        rf_mse = mean_squared_error(y_test, rf_pred)
        rf_r2 = r2_score(y_test, rf_pred)
        gb_mse = mean_squared_error(y_test, gb_pred)
        gb_r2 = r2_score(y_test, gb_pred)
        
        print(f"   ✅ RandomForest - MSE: {rf_mse:.2f}, R²: {rf_r2:.4f}")
        print(f"   ✅ GradientBoosting - MSE: {gb_mse:.2f}, R²: {gb_r2:.4f}")
        
        # Calculate feature importance
        self.feature_importance = dict(zip(available_features, self.models['random_forest'].feature_importances_))
        
        # Save models
        self._save_models()
        
        return len(available_features)
    
    def _save_models(self):
        """Save trained models and components"""
        os.makedirs('models', exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'models/peak_time_{name}.pkl')
        
        # Save scaler
        joblib.dump(self.scalers['standard'], 'models/peak_time_scaler.pkl')
        
        # Save metadata
        metadata = {
            'feature_importance': self.feature_importance,
            'department_patterns': self.department_patterns,
            'seasonal_patterns': self.seasonal_patterns,
            'holiday_patterns': self.holiday_patterns,
            'peak_thresholds': self.peak_thresholds,
            'overall_hourly_pattern': self.overall_hourly_pattern,
            'day_of_week_pattern': self.day_of_week_pattern,
            'weekend_pattern': self.weekend_pattern,
            'weekday_pattern': self.weekday_pattern,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(metadata, 'models/peak_time_prediction_metadata.pkl')
        print("   ✅ Models and metadata saved")
    
    def predict_peak_times(self, 
                          department: str = None,
                          day_of_week: int = None,
                          hours_ahead: int = 24,
                          include_weekend: bool = True) -> Dict:
        """Predict peak times for a department or overall"""
        
        # Load models if not already loaded
        if not self.models:
            self._load_models()
        
        # Use current day if not provided
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        
        is_weekend = day_of_week >= 5
        
        # Get predictions for all hours
        hours = np.arange(24)
        predictions = []
        
        for hour in hours:
            # Prepare features for this hour
            features = self._prepare_prediction_features(
                hour, day_of_week, is_weekend, department
            )
            
            # Scale features
            features_scaled = self.scalers['standard'].transform([features])
            
            # Get prediction from ensemble
            rf_pred = self.models['random_forest'].predict(features_scaled)[0]
            gb_pred = self.models['gradient_boosting'].predict(features_scaled)[0]
            
            # Ensemble prediction (weighted average)
            ensemble_pred = 0.6 * rf_pred + 0.4 * gb_pred
            
            # Apply department-specific adjustments
            if department and department in self.department_patterns:
                dept_multiplier = self.department_patterns[department]['base_multiplier']
                ensemble_pred *= dept_multiplier
                
                # Weekend adjustment
                if is_weekend:
                    weekend_factor = self.department_patterns[department]['weekend_factor']
                    ensemble_pred *= weekend_factor
            
            predictions.append({
                'hour': int(hour),
                'predicted_volume': round(ensemble_pred, 2),
                'random_forest_pred': round(rf_pred, 2),
                'gradient_boosting_pred': round(gb_pred, 2),
                'ensemble_pred': round(ensemble_pred, 2)
            })
        
        # Identify peak times
        volumes = [p['predicted_volume'] for p in predictions]
        peak_analysis = self._analyze_peak_times(volumes)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            peak_analysis, department, day_of_week
        )
        
        return {
            'department': department or 'Overall',
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'hours_ahead': hours_ahead,
            'peak_analysis': peak_analysis,
            'hourly_predictions': predictions,
            'recommendations': recommendations,
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _prepare_prediction_features(self, hour: int, day_of_week: int, is_weekend: bool, department: str = None) -> List[float]:
        """Prepare features for ML prediction"""
        
        # Base features
        features = [
            hour,  # Hour
            day_of_week,  # DayOfWeek
            int(is_weekend),  # IsWeekend
            np.sin(2 * np.pi * hour / 24),  # HourSin
            np.cos(2 * np.pi * hour / 24),  # HourCos
            hour ** 2,  # HourSquared
            np.sin(2 * np.pi * day_of_week / 7),  # DaySin
            np.cos(2 * np.pi * day_of_week / 7),  # DayCos
        ]
        
        # Department-specific features
        if department and department in self.department_patterns:
            dept_pattern = self.department_patterns[department]
            features.extend([
                dept_pattern.get('DeptPatientCount', 100),  # DeptPatientCount
                dept_pattern.get('DeptMeanWait', 45),  # DeptMeanWait
                dept_pattern.get('DeptStdWait', 15),  # DeptStdWait
            ])
        else:
            features.extend([100, 45, 15])  # Default values
        
        # Hourly features
        hourly_pattern = self.overall_hourly_pattern.get(hour, 50)
        features.extend([
            hourly_pattern,  # HourlyPatientCount
            hourly_pattern * 0.8,  # HourlyMeanWait
            hourly_pattern * 0.2,  # HourlyStdWait
            hourly_pattern,  # HourlyVolumeMA3
            hourly_pattern,  # HourlyVolumeMA7
        ])
        
        return features
    
    def _analyze_peak_times(self, volumes: List[float]) -> Dict:
        """Analyze predicted volumes to identify peak times"""
        
        volumes_array = np.array(volumes)
        
        # Calculate thresholds
        low_threshold = np.percentile(volumes_array, self.peak_thresholds['low'] * 100)
        medium_threshold = np.percentile(volumes_array, self.peak_thresholds['medium'] * 100)
        high_threshold = np.percentile(volumes_array, self.peak_thresholds['high'] * 100)
        extreme_threshold = np.percentile(volumes_array, self.peak_thresholds['extreme'] * 100)
        
        # Categorize hours
        low_hours = [i for i, vol in enumerate(volumes) if vol <= low_threshold]
        medium_hours = [i for i, vol in enumerate(volumes) if low_threshold < vol <= medium_threshold]
        high_hours = [i for i, vol in enumerate(volumes) if medium_threshold < vol <= high_threshold]
        extreme_hours = [i for i, vol in enumerate(volumes) if vol > extreme_threshold]
        
        # Peak hours (high + extreme)
        peak_hours = high_hours + extreme_hours
        
        return {
            'thresholds': {
                'low': round(low_threshold, 2),
                'medium': round(medium_threshold, 2),
                'high': round(high_threshold, 2),
                'extreme': round(extreme_threshold, 2)
            },
            'hour_categories': {
                'low': low_hours,
                'medium': medium_hours,
                'high': high_hours,
                'extreme': extreme_hours
            },
            'peak_hours': sorted(peak_hours),
            'extreme_peak_hours': sorted(extreme_hours),
            'total_predicted_volume': round(sum(volumes), 2),
            'average_volume': round(np.mean(volumes), 2),
            'peak_volume': round(max(volumes), 2),
            'peak_hour': int(np.argmax(volumes))
        }
    
    def _generate_recommendations(self, peak_analysis: Dict, department: str, day_of_week: int) -> List[str]:
        """Generate recommendations based on peak time predictions"""
        
        recommendations = []
        
        peak_hours = peak_analysis['peak_hours']
        extreme_hours = peak_analysis['extreme_peak_hours']
        
        if len(peak_hours) > 0:
            peak_hours_str = ', '.join([f"{h}:00" for h in peak_hours])
            recommendations.append(f"📈 Peak hours predicted: {peak_hours_str}")
            
            if len(extreme_hours) > 0:
                extreme_hours_str = ', '.join([f"{h}:00" for h in extreme_hours])
                recommendations.append(f"🚨 Extreme peak hours: {extreme_hours_str} - consider additional staff")
        
        # Department-specific recommendations
        if department and department in self.department_patterns:
            dept_pattern = self.department_patterns[department]
            if department == 'Emergency':
                recommendations.append("🚨 Emergency department - ensure 24/7 coverage")
            elif department == 'Pediatrics':
                recommendations.append("👶 Pediatrics - consider family-friendly scheduling")
            elif department == 'Oncology':
                recommendations.append("🎗️ Oncology - plan for longer consultation times")
        
        # Day-specific recommendations
        if day_of_week == 0:  # Monday
            recommendations.append("📅 Monday - expect higher volume after weekend")
        elif day_of_week == 4:  # Friday
            recommendations.append("📅 Friday - consider pre-weekend rush")
        elif day_of_week >= 5:  # Weekend
            recommendations.append("📅 Weekend - reduced staffing may be appropriate")
        
        # Volume-based recommendations
        total_volume = peak_analysis['total_predicted_volume']
        if total_volume > 1000:
            recommendations.append("📊 High predicted volume - consider opening additional service counters")
        elif total_volume < 500:
            recommendations.append("📊 Low predicted volume - opportunity for staff training or maintenance")
        
        return recommendations
    
    def _load_models(self):
        """Load trained models and components"""
        try:
            # Load models
            self.models['random_forest'] = joblib.load('models/peak_time_random_forest.pkl')
            self.models['gradient_boosting'] = joblib.load('models/peak_time_gradient_boosting.pkl')
            
            # Load scaler
            self.scalers['standard'] = joblib.load('models/peak_time_scaler.pkl')
            
            # Load metadata
            metadata = joblib.load('models/peak_time_prediction_metadata.pkl')
            self.feature_importance = metadata.get('feature_importance', {})
            self.department_patterns = metadata.get('department_patterns', {})
            self.seasonal_patterns = metadata.get('seasonal_patterns', {})
            self.holiday_patterns = metadata.get('holiday_patterns', {})
            self.peak_thresholds = metadata.get('peak_thresholds', {})
            
        except Exception as e:
            print(f"❌ Error loading peak time prediction models: {e}")
            self.models = {}
            self.scalers = {}
    
    def get_department_analysis(self, department: str) -> Dict:
        """Get detailed analysis for a department"""
        
        dept_pattern = self.department_patterns.get(department, {})
        
        return {
            'department': department,
            'base_multiplier': dept_pattern.get('base_multiplier', 1.0),
            'peak_hours': dept_pattern.get('peak_hours', [9, 14, 16]),
            'weekend_factor': dept_pattern.get('weekend_factor', 1.0),
            'hourly_pattern': dept_pattern.get('hourly_pattern', {}),
            'pattern_description': f"{department} shows peak activity during {', '.join([f'{h}:00' for h in dept_pattern.get('peak_hours', [9, 14, 16])])}"
        }
    
    def get_prediction_summary(self) -> Dict:
        """Get summary of peak time prediction system"""
        return {
            'models_available': list(self.models.keys()),
            'departments_analyzed': len(self.department_patterns),
            'feature_count': len(self.feature_importance),
            'peak_thresholds': self.peak_thresholds,
            'seasonal_patterns': list(self.seasonal_patterns.keys()),
            'holiday_patterns': list(self.holiday_patterns.keys()),
            'top_features': dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        }

if __name__ == "__main__":
    predictor = AdvancedPeakTimePredictor()
    
    # Load and preprocess data
    predictor.load_and_preprocess_data()
    
    # Train models
    feature_count = predictor.train_peak_time_models()
    
    # Example predictions
    print("\n🎯 Example Peak Time Predictions:")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {'department': 'Emergency', 'day_of_week': 1, 'description': 'Emergency Department - Tuesday'},
        {'department': 'Internal Medicine', 'day_of_week': 2, 'description': 'Internal Medicine - Wednesday'},
        {'department': 'Pediatrics', 'day_of_week': 5, 'description': 'Pediatrics - Saturday'},
        {'department': None, 'day_of_week': 0, 'description': 'Overall Hospital - Monday'}
    ]
    
    for test_case in test_cases:
        prediction = predictor.predict_peak_times(
            department=test_case['department'],
            day_of_week=test_case['day_of_week']
        )
        
        print(f"\n🏥 {test_case['description']}")
        print(f"   Peak hours: {', '.join([f'{h}:00' for h in prediction['peak_analysis']['peak_hours']])}")
        print(f"   Extreme peaks: {', '.join([f'{h}:00' for h in prediction['peak_analysis']['extreme_peak_hours']])}")
        print(f"   Total predicted volume: {prediction['peak_analysis']['total_predicted_volume']}")
        print(f"   Peak hour: {prediction['peak_analysis']['peak_hour']}:00")
        
        if prediction['recommendations']:
            print(f"   Recommendations:")
            for rec in prediction['recommendations'][:3]:  # Show first 3
                print(f"     • {rec}")
    
    # Get system summary
    summary = predictor.get_prediction_summary()
    print(f"\n📋 System Summary:")
    print(f"   Models: {len(summary['models_available'])}")
    print(f"   Departments: {summary['departments_analyzed']}")
    print(f"   Features: {summary['feature_count']}")
    print(f"   Top features: {list(summary['top_features'].keys())}")
    
    print("\n✅ Advanced Peak Time Prediction System Ready!")
