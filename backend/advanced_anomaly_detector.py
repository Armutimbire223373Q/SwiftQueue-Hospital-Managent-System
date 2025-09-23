"""
Advanced Anomaly Detection System
Automatic identification of system irregularities using multiple ML algorithms
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnomalyDetector:
    """Advanced anomaly detection system for hospital queue management"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.anomaly_thresholds = {}
        self.baseline_metrics = {}
        self.detection_history = []
        
        # Initialize detection models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize multiple anomaly detection models"""
        print("🔍 Initializing advanced anomaly detection models...")
        
        # Isolation Forest - Good for general anomaly detection
        self.models['isolation_forest'] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Local Outlier Factor - Good for local density-based anomalies
        self.models['lof'] = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.1
        )
        
        # One-Class SVM - Good for high-dimensional data
        self.models['one_class_svm'] = OneClassSVM(
            nu=0.1,
            kernel='rbf',
            gamma='scale'
        )
        
        # DBSCAN - Good for clustering-based anomaly detection
        self.models['dbscan'] = DBSCAN(
            eps=0.5,
            min_samples=5
        )
        
        # Scalers for different data types
        self.scalers['standard'] = StandardScaler()
        self.scalers['robust'] = RobustScaler()
        
        print(f"   ✅ Initialized {len(self.models)} detection models")
    
    def load_and_preprocess_data(self):
        """Load and preprocess hospital data for anomaly detection"""
        print("📊 Loading hospital data for anomaly detection...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._engineer_features()
        self._calculate_baseline_metrics()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean and validate the dataset"""
        print("🧹 Cleaning anomaly detection dataset...")
        
        self.processed_df = self.df.copy()
        
        # Handle missing values
        numeric_columns = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_columns] = self.processed_df[numeric_columns].fillna(
            self.processed_df[numeric_columns].median()
        )
        
        # Remove extreme outliers (keep 99th percentile)
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            percentile_99 = self.processed_df[wait_time_col].quantile(0.99)
            before_count = len(self.processed_df)
            self.processed_df = self.processed_df[self.processed_df[wait_time_col] <= percentile_99]
            after_count = len(self.processed_df)
            
            if before_count != after_count:
                print(f"   Removed {before_count - after_count} extreme outliers (99th percentile: {percentile_99:.1f} min)")
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _engineer_features(self):
        """Engineer features for anomaly detection"""
        print("⚙️ Engineering features for anomaly detection...")
        
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
        
        # Wait time features
        wait_time_col = 'TotalTimeInHospital'
        if wait_time_col in self.processed_df.columns:
            self.processed_df['WaitTimeLog'] = np.log1p(self.processed_df[wait_time_col])
            self.processed_df['WaitTimeSqrt'] = np.sqrt(self.processed_df[wait_time_col])
            
            # Rolling statistics
            self.processed_df['WaitTimeMean'] = self.processed_df.groupby('Department')[wait_time_col].transform('mean')
            self.processed_df['WaitTimeStd'] = self.processed_df.groupby('Department')[wait_time_col].transform('std')
            self.processed_df['WaitTimeZScore'] = (self.processed_df[wait_time_col] - self.processed_df['WaitTimeMean']) / self.processed_df['WaitTimeStd']
        
        # Department efficiency features
        dept_stats = self.processed_df.groupby('Department').agg({
            wait_time_col: ['mean', 'std', 'count'],
            'AgeGroup': 'nunique'
        }).round(2)
        
        dept_stats.columns = ['DeptMeanWait', 'DeptStdWait', 'DeptCount', 'DeptAgeGroups']
        self.processed_df = self.processed_df.merge(dept_stats, left_on='Department', right_index=True, how='left')
        
        # Patient flow features
        self.processed_df['PatientFlowRate'] = self.processed_df.groupby('Department').size() / self.processed_df.groupby('Department').size().sum()
        
        print(f"   ✅ Feature engineering completed: {len(self.processed_df.columns)} features")
    
    def _calculate_baseline_metrics(self):
        """Calculate baseline metrics for anomaly detection"""
        print("📏 Calculating baseline metrics...")
        
        wait_time_col = 'TotalTimeInHospital'
        
        # Overall baselines
        self.baseline_metrics['overall'] = {
            'mean_wait_time': self.processed_df[wait_time_col].mean(),
            'median_wait_time': self.processed_df[wait_time_col].median(),
            'std_wait_time': self.processed_df[wait_time_col].std(),
            'q75_wait_time': self.processed_df[wait_time_col].quantile(0.75),
            'q95_wait_time': self.processed_df[wait_time_col].quantile(0.95),
            'total_patients': len(self.processed_df)
        }
        
        # Department-specific baselines
        for dept in self.processed_df['Department'].unique():
            dept_data = self.processed_df[self.processed_df['Department'] == dept]
            self.baseline_metrics[f'dept_{dept}'] = {
                'mean_wait_time': dept_data[wait_time_col].mean(),
                'median_wait_time': dept_data[wait_time_col].median(),
                'std_wait_time': dept_data[wait_time_col].std(),
                'q75_wait_time': dept_data[wait_time_col].quantile(0.75),
                'q95_wait_time': dept_data[wait_time_col].quantile(0.95),
                'patient_count': len(dept_data)
            }
        
        # Time-based baselines
        if 'Hour' in self.processed_df.columns:
            hourly_stats = self.processed_df.groupby('Hour')[wait_time_col].agg(['mean', 'std', 'count']).round(2)
            self.baseline_metrics['hourly'] = hourly_stats.to_dict()
        
        print(f"   ✅ Baseline metrics calculated for {len(self.baseline_metrics)} categories")
    
    def train_anomaly_models(self):
        """Train multiple anomaly detection models"""
        print("🤖 Training anomaly detection models...")
        
        # Prepare features for training
        feature_columns = [
            'TotalTimeInHospital', 'Hour', 'DayOfWeekNumeric', 'IsWeekend', 'IsPeakHour',
            'WaitTimeLog', 'WaitTimeSqrt', 'WaitTimeZScore', 'DeptMeanWait', 
            'DeptStdWait', 'DeptCount', 'PatientFlowRate'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in self.processed_df.columns]
        X = self.processed_df[available_features].fillna(0)
        
        print(f"   Training with {len(available_features)} features: {available_features}")
        
        # Scale features
        X_scaled_standard = self.scalers['standard'].fit_transform(X)
        X_scaled_robust = self.scalers['robust'].fit_transform(X)
        
        # Train Isolation Forest
        self.models['isolation_forest'].fit(X_scaled_standard)
        print("   ✅ Isolation Forest trained")
        
        # Train One-Class SVM
        self.models['one_class_svm'].fit(X_scaled_robust)
        print("   ✅ One-Class SVM trained")
        
        # Train DBSCAN (for clustering-based detection)
        dbscan_labels = self.models['dbscan'].fit_predict(X_scaled_standard)
        n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
        n_noise = list(dbscan_labels).count(-1)
        print(f"   ✅ DBSCAN trained: {n_clusters} clusters, {n_noise} noise points")
        
        # Calculate feature importance (using decision function variance)
        try:
            # Get feature importance from Isolation Forest decision function
            decision_scores = self.models['isolation_forest'].decision_function(X_scaled_standard)
            feature_importance = np.abs(np.corrcoef(X_scaled_standard.T, decision_scores)[:-1, -1])
            self.feature_importance = dict(zip(available_features, feature_importance))
        except:
            # Fallback: equal importance
            self.feature_importance = {feature: 1.0/len(available_features) for feature in available_features}
        
        # Set anomaly thresholds
        self._set_anomaly_thresholds(X_scaled_standard)
        
        # Save models
        self._save_models()
        
        print(f"   ✅ All models trained successfully!")
        return len(available_features)
    
    def _set_anomaly_thresholds(self, X_scaled):
        """Set dynamic anomaly thresholds based on training data"""
        print("📊 Setting anomaly thresholds...")
        
        # Get anomaly scores from Isolation Forest
        anomaly_scores = self.models['isolation_forest'].decision_function(X_scaled)
        
        # Set thresholds based on percentiles
        self.anomaly_thresholds = {
            'low': np.percentile(anomaly_scores, 10),      # Bottom 10% - likely anomalies
            'medium': np.percentile(anomaly_scores, 25),   # Bottom 25% - potential anomalies
            'high': np.percentile(anomaly_scores, 5),      # Bottom 5% - definite anomalies
            'extreme': np.percentile(anomaly_scores, 1)    # Bottom 1% - extreme anomalies
        }
        
        print(f"   ✅ Anomaly thresholds set:")
        for level, threshold in self.anomaly_thresholds.items():
            print(f"      {level}: {threshold:.3f}")
    
    def _save_models(self):
        """Save trained models and components"""
        os.makedirs('models', exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'models/anomaly_{name}.pkl')
        
        # Save scalers
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/anomaly_scaler_{name}.pkl')
        
        # Save metadata
        metadata = {
            'feature_importance': self.feature_importance,
            'anomaly_thresholds': self.anomaly_thresholds,
            'baseline_metrics': self.baseline_metrics,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(metadata, 'models/anomaly_detection_metadata.pkl')
        print("   ✅ Models and metadata saved")
    
    def detect_anomalies(self, 
                        data: pd.DataFrame = None, 
                        real_time: bool = False) -> Dict:
        """Detect anomalies in the data"""
        
        if data is None:
            data = self.processed_df
        
        # Prepare features
        feature_columns = list(self.feature_importance.keys())
        available_features = [col for col in feature_columns if col in data.columns]
        X = data[available_features].fillna(0)
        
        # Scale features
        X_scaled_standard = self.scalers['standard'].transform(X)
        X_scaled_robust = self.scalers['robust'].transform(X)
        
        # Get predictions from all models
        predictions = {}
        
        # Isolation Forest
        iso_predictions = self.models['isolation_forest'].predict(X_scaled_standard)
        iso_scores = self.models['isolation_forest'].decision_function(X_scaled_standard)
        predictions['isolation_forest'] = {
            'predictions': iso_predictions,
            'scores': iso_scores,
            'anomalies': iso_predictions == -1
        }
        
        # One-Class SVM
        svm_predictions = self.models['one_class_svm'].predict(X_scaled_robust)
        svm_scores = self.models['one_class_svm'].decision_function(X_scaled_robust)
        predictions['one_class_svm'] = {
            'predictions': svm_predictions,
            'scores': svm_scores,
            'anomalies': svm_predictions == -1
        }
        
        # Local Outlier Factor (skip for single samples)
        if len(X_scaled_standard) > 1:
            lof_scores = self.models['lof'].fit_predict(X_scaled_standard)
            predictions['lof'] = {
                'scores': lof_scores,
                'anomalies': lof_scores == -1
            }
        else:
            predictions['lof'] = {
                'scores': [0],
                'anomalies': [False]
            }
        
        # DBSCAN
        dbscan_labels = self.models['dbscan'].fit_predict(X_scaled_standard)
        predictions['dbscan'] = {
            'labels': dbscan_labels,
            'anomalies': dbscan_labels == -1
        }
        
        # Combine results
        combined_results = self._combine_predictions(predictions, X_scaled_standard)
        
        # Analyze anomalies
        anomaly_analysis = self._analyze_anomalies(data, combined_results)
        
        return {
            'anomaly_count': combined_results['anomaly_count'],
            'anomaly_rate': combined_results['anomaly_rate'],
            'anomalies': combined_results['anomalies'],
            'analysis': anomaly_analysis,
            'model_predictions': predictions,
            'detection_timestamp': datetime.now().isoformat(),
            'real_time': real_time
        }
    
    def _combine_predictions(self, predictions: Dict, X_scaled: np.ndarray) -> Dict:
        """Combine predictions from multiple models"""
        
        n_samples = len(X_scaled)
        anomaly_votes = np.zeros(n_samples)
        
        # Weighted voting based on model performance
        model_weights = {
            'isolation_forest': 0.4,
            'one_class_svm': 0.3,
            'lof': 0.2,
            'dbscan': 0.1
        }
        
        for model_name, pred_data in predictions.items():
            if 'anomalies' in pred_data:
                anomalies = np.array(pred_data['anomalies'], dtype=float)
                anomaly_votes += anomalies * model_weights.get(model_name, 0.25)
        
        # Determine final anomalies (threshold: 0.5)
        final_anomalies = anomaly_votes >= 0.5
        
        return {
            'anomaly_count': int(np.sum(final_anomalies)),
            'anomaly_rate': float(np.mean(final_anomalies)),
            'anomalies': final_anomalies,
            'anomaly_scores': anomaly_votes,
            'model_agreement': anomaly_votes
        }
    
    def _analyze_anomalies(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Analyze detected anomalies for insights"""
        
        anomalies = results['anomalies']
        anomaly_data = data[anomalies]
        
        if len(anomaly_data) == 0:
            return {'message': 'No anomalies detected', 'insights': []}
        
        analysis = {
            'total_anomalies': len(anomaly_data),
            'anomaly_rate': results['anomaly_rate'],
            'insights': []
        }
        
        # Analyze by department
        if 'Department' in anomaly_data.columns:
            dept_anomalies = anomaly_data['Department'].value_counts()
            analysis['department_anomalies'] = dept_anomalies.to_dict()
            
            # Find departments with highest anomaly rates
            dept_rates = {}
            for dept in data['Department'].unique():
                dept_total = len(data[data['Department'] == dept])
                dept_anomaly_count = len(anomaly_data[anomaly_data['Department'] == dept])
                dept_rates[dept] = dept_anomaly_count / dept_total if dept_total > 0 else 0
            
            top_anomaly_dept = max(dept_rates, key=dept_rates.get)
            analysis['insights'].append(f"Department with highest anomaly rate: {top_anomaly_dept} ({dept_rates[top_anomaly_dept]:.1%})")
        
        # Analyze wait times
        if 'TotalTimeInHospital' in anomaly_data.columns:
            anomaly_wait_times = anomaly_data['TotalTimeInHospital']
            baseline_wait = self.baseline_metrics['overall']['mean_wait_time']
            
            analysis['wait_time_analysis'] = {
                'anomaly_mean_wait': float(anomaly_wait_times.mean()),
                'baseline_mean_wait': float(baseline_wait),
                'wait_time_ratio': float(anomaly_wait_times.mean() / baseline_wait)
            }
            
            if anomaly_wait_times.mean() > baseline_wait * 1.5:
                analysis['insights'].append(f"Anomalies show significantly longer wait times ({anomaly_wait_times.mean():.1f} vs {baseline_wait:.1f} min)")
        
        # Analyze time patterns
        if 'Hour' in anomaly_data.columns:
            hourly_anomalies = anomaly_data['Hour'].value_counts().sort_index()
            peak_anomaly_hour = hourly_anomalies.idxmax()
            analysis['insights'].append(f"Peak anomaly hour: {peak_anomaly_hour}:00 ({hourly_anomalies[peak_anomaly_hour]} anomalies)")
        
        return analysis
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of anomaly detection system"""
        return {
            'models_available': list(self.models.keys()),
            'scalers_available': list(self.scalers.keys()),
            'feature_count': len(self.feature_importance),
            'baseline_categories': len(self.baseline_metrics),
            'anomaly_thresholds': self.anomaly_thresholds,
            'top_features': dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def get_real_time_anomaly(self, current_metrics: Dict) -> Dict:
        """Detect anomalies in real-time metrics"""
        
        # Convert to DataFrame and ensure all required features are present
        current_df = pd.DataFrame([current_metrics])
        
        # Add missing features with default values
        required_features = list(self.feature_importance.keys())
        for feature in required_features:
            if feature not in current_df.columns:
                if feature == 'DayOfWeekNumeric':
                    current_df[feature] = 1  # Default to Tuesday
                elif feature == 'Hour':
                    current_df[feature] = 12  # Default to noon
                elif feature == 'IsWeekend':
                    current_df[feature] = 0  # Default to weekday
                elif feature == 'IsPeakHour':
                    current_df[feature] = 0  # Default to non-peak
                else:
                    current_df[feature] = 0  # Default to 0
        
        # Detect anomalies
        result = self.detect_anomalies(current_df, real_time=True)
        
        # Add real-time specific analysis
        if result['anomaly_count'] > 0:
            result['alert_level'] = 'HIGH' if result['anomaly_rate'] > 0.8 else 'MEDIUM'
            result['recommended_actions'] = self._get_recommended_actions(current_metrics)
        else:
            result['alert_level'] = 'LOW'
            result['recommended_actions'] = ['Continue monitoring']
        
        return result
    
    def _get_recommended_actions(self, metrics: Dict) -> List[str]:
        """Get recommended actions based on detected anomalies"""
        actions = []
        
        if 'wait_time' in metrics and metrics['wait_time'] > self.baseline_metrics['overall']['q95_wait_time']:
            actions.append("Consider adding more staff or opening additional service counters")
        
        if 'queue_length' in metrics and metrics['queue_length'] > 20:
            actions.append("Implement queue management strategies or patient flow optimization")
        
        if 'service_rate' in metrics and metrics['service_rate'] < 0.5:
            actions.append("Review service processes for efficiency improvements")
        
        if not actions:
            actions.append("Monitor system closely and investigate root causes")
        
        return actions

if __name__ == "__main__":
    detector = AdvancedAnomalyDetector()
    
    # Load and preprocess data
    detector.load_and_preprocess_data()
    
    # Train models
    feature_count = detector.train_anomaly_models()
    
    # Detect anomalies
    print("\n🔍 Detecting Anomalies:")
    print("=" * 50)
    
    anomaly_results = detector.detect_anomalies()
    
    print(f"📊 Anomaly Detection Results:")
    print(f"   Total anomalies detected: {anomaly_results['anomaly_count']}")
    print(f"   Anomaly rate: {anomaly_results['anomaly_rate']:.1%}")
    
    if anomaly_results['analysis']['insights']:
        print(f"\n💡 Key Insights:")
        for insight in anomaly_results['analysis']['insights']:
            print(f"   • {insight}")
    
    # Test real-time detection
    print(f"\n⚡ Real-time Anomaly Detection Test:")
    test_metrics = {
        'TotalTimeInHospital': 120,  # High wait time
        'Hour': 14,  # Peak hour
        'DayOfWeek': 1,  # Tuesday
        'IsWeekend': 0,
        'IsPeakHour': 1,
        'WaitTimeLog': np.log1p(120),
        'WaitTimeSqrt': np.sqrt(120),
        'WaitTimeZScore': 2.5,  # High z-score
        'DeptMeanWait': 60,
        'DeptStdWait': 20,
        'DeptCount': 100,
        'PatientFlowRate': 0.1
    }
    
    real_time_result = detector.get_real_time_anomaly(test_metrics)
    print(f"   Alert Level: {real_time_result['alert_level']}")
    print(f"   Recommended Actions: {real_time_result['recommended_actions']}")
    
    # Get system summary
    summary = detector.get_anomaly_summary()
    print(f"\n📋 System Summary:")
    print(f"   Models: {len(summary['models_available'])}")
    print(f"   Features: {summary['feature_count']}")
    print(f"   Baseline categories: {summary['baseline_categories']}")
    print(f"   Top features: {list(summary['top_features'].keys())}")
    
    print("\n✅ Advanced Anomaly Detection System Ready!")
