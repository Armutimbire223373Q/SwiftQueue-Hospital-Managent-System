#!/usr/bin/env python3
"""
Comprehensive Model Testing Script
Tests all trained models to ensure they are working correctly.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Add backend to path
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelTester:
    """Comprehensive model testing class."""
    
    def __init__(self, models_dir="backend/models"):
        self.models_dir = models_dir
        self.test_results = {}
        
    def test_model_loading(self, model_path):
        """Test if a model can be loaded successfully."""
        try:
            model_data = joblib.load(model_path)
            logger.info(f"✓ Successfully loaded: {os.path.basename(model_path)}")
            return True, model_data
        except Exception as e:
            logger.error(f"✗ Failed to load: {os.path.basename(model_path)} - {e}")
            return False, None
    
    def test_wait_time_prediction(self):
        """Test wait time prediction models."""
        logger.info("\n=== Testing Wait Time Prediction Models ===")
        
        models_to_test = [
            "wait_time_model.pkl",
            "practical_wait_time_model.pkl",
            "advanced_wait_time_model.pkl",
            "optimized_wait_time_model.pkl",
            "ensemble_wait_time_model.pkl"
        ]
        
        for model_file in models_to_test:
            model_path = os.path.join(self.models_dir, model_file)
            if os.path.exists(model_path):
                success, model_data = self.test_model_loading(model_path)
                if success:
                    self.test_results[model_file] = self._test_wait_time_prediction_logic(model_data, model_file)
            else:
                logger.warning(f"Model not found: {model_file}")
    
    def _test_wait_time_prediction_logic(self, model_data, model_name):
        """Test the actual prediction logic for wait time models."""
        try:
            model = model_data.get('model')
            scaler = model_data.get('scaler')
            
            if model is None:
                return {"status": "error", "message": "No model found in data"}
            
            # Create sample input data
            sample_data = pd.DataFrame({
                'hour': [14],  # 2 PM
                'day_of_week': [1],  # Tuesday
                'queue_length': [5],
                'is_peak_hour': [1],
                'is_weekend': [0]
            })
            
            # Add additional features if they exist in the model
            feature_columns = model_data.get('feature_columns', [])
            for col in feature_columns:
                if col not in sample_data.columns:
                    sample_data[col] = [0]  # Default value
            
            # Scale data if scaler exists
            if scaler is not None:
                # Ensure we have the right columns for scaling
                scaled_data = scaler.transform(sample_data[feature_columns])
                prediction = model.predict(scaled_data)
            else:
                prediction = model.predict(sample_data)
            
            logger.info(f"  ✓ {model_name}: Predicted wait time = {prediction[0]:.2f} minutes")
            return {"status": "success", "prediction": float(prediction[0])}
            
        except Exception as e:
            logger.error(f"  ✗ {model_name}: Prediction failed - {e}")
            return {"status": "error", "message": str(e)}
    
    def test_triage_models(self):
        """Test triage prediction models."""
        logger.info("\n=== Testing Triage Models ===")
        
        models_to_test = [
            "triage_priority_model.pkl",
            "optimized_triage_model.pkl",
            "ensemble_triage_model.pkl"
        ]
        
        for model_file in models_to_test:
            model_path = os.path.join(self.models_dir, model_file)
            if os.path.exists(model_path):
                success, model_data = self.test_model_loading(model_path)
                if success:
                    self.test_results[model_file] = self._test_triage_prediction_logic(model_data, model_file)
            else:
                logger.warning(f"Model not found: {model_file}")
    
    def _test_triage_prediction_logic(self, model_data, model_name):
        """Test the actual prediction logic for triage models."""
        try:
            model = model_data.get('model')
            scaler = model_data.get('scaler')
            
            if model is None:
                return {"status": "error", "message": "No model found in data"}
            
            # Create sample input data for triage
            sample_data = pd.DataFrame({
                'age_group_Adult': [1],
                'insurance_type_Private': [1],
                'department_Emergency': [1],
                'hour': [14],
                'day_of_week': [1],
                'is_weekend': [0]
            })
            
            # Add additional features if they exist in the model
            feature_columns = model_data.get('feature_columns', [])
            for col in feature_columns:
                if col not in sample_data.columns:
                    sample_data[col] = [0]  # Default value
            
            # Scale data if scaler exists
            if scaler is not None:
                scaled_data = scaler.transform(sample_data[feature_columns])
                prediction = model.predict(scaled_data)
            else:
                prediction = model.predict(sample_data)
            
            logger.info(f"  ✓ {model_name}: Predicted triage priority = {prediction[0]}")
            return {"status": "success", "prediction": str(prediction[0])}
            
        except Exception as e:
            logger.error(f"  ✗ {model_name}: Prediction failed - {e}")
            return {"status": "error", "message": str(e)}
    
    def test_anomaly_detection_models(self):
        """Test anomaly detection models."""
        logger.info("\n=== Testing Anomaly Detection Models ===")
        
        models_to_test = [
            "anomaly_isolation_forest.pkl",
            "anomaly_dbscan.pkl",
            "anomaly_lof.pkl",
            "anomaly_one_class_svm.pkl"
        ]
        
        for model_file in models_to_test:
            model_path = os.path.join(self.models_dir, model_file)
            if os.path.exists(model_path):
                success, model_data = self.test_model_loading(model_path)
                if success:
                    self.test_results[model_file] = self._test_anomaly_detection_logic(model_data, model_file)
            else:
                logger.warning(f"Model not found: {model_file}")
    
    def _test_anomaly_detection_logic(self, model_data, model_name):
        """Test the actual prediction logic for anomaly detection models."""
        try:
            model = model_data.get('model')
            scaler = model_data.get('scaler')
            
            if model is None:
                return {"status": "error", "message": "No model found in data"}
            
            # Create sample input data
            sample_data = pd.DataFrame({
                'wait_time': [30.0],
                'queue_length': [5],
                'hour': [14],
                'day_of_week': [1],
                'is_peak_hour': [1]
            })
            
            # Add additional features if they exist in the model
            feature_columns = model_data.get('feature_columns', [])
            for col in feature_columns:
                if col not in sample_data.columns:
                    sample_data[col] = [0]  # Default value
            
            # Scale data if scaler exists
            if scaler is not None:
                scaled_data = scaler.transform(sample_data[feature_columns])
                prediction = model.predict(scaled_data)
            else:
                prediction = model.predict(sample_data)
            
            # For anomaly detection, -1 = anomaly, 1 = normal
            result = "ANOMALY" if prediction[0] == -1 else "NORMAL"
            logger.info(f"  ✓ {model_name}: Anomaly detection = {result}")
            return {"status": "success", "prediction": result}
            
        except Exception as e:
            logger.error(f"  ✗ {model_name}: Prediction failed - {e}")
            return {"status": "error", "message": str(e)}
    
    def test_peak_time_prediction(self):
        """Test peak time prediction models."""
        logger.info("\n=== Testing Peak Time Prediction Models ===")
        
        models_to_test = [
            "peak_time_model.pkl",
            "optimized_peak_time_model.pkl",
            "peak_time_gradient_boosting.pkl",
            "peak_time_random_forest.pkl"
        ]
        
        for model_file in models_to_test:
            model_path = os.path.join(self.models_dir, model_file)
            if os.path.exists(model_path):
                success, model_data = self.test_model_loading(model_path)
                if success:
                    self.test_results[model_file] = self._test_peak_time_prediction_logic(model_data, model_file)
            else:
                logger.warning(f"Model not found: {model_file}")
    
    def _test_peak_time_prediction_logic(self, model_data, model_name):
        """Test the actual prediction logic for peak time models."""
        try:
            model = model_data.get('model')
            scaler = model_data.get('scaler')
            
            if model is None:
                return {"status": "error", "message": "No model found in data"}
            
            # Create sample input data
            sample_data = pd.DataFrame({
                'hour': [14],
                'day_of_week': [1],
                'month': [12],
                'is_weekend': [0],
                'current_patients': [25]
            })
            
            # Add additional features if they exist in the model
            feature_columns = model_data.get('feature_columns', [])
            for col in feature_columns:
                if col not in sample_data.columns:
                    sample_data[col] = [0]  # Default value
            
            # Scale data if scaler exists
            if scaler is not None:
                scaled_data = scaler.transform(sample_data[feature_columns])
                prediction = model.predict(scaled_data)
            else:
                prediction = model.predict(sample_data)
            
            logger.info(f"  ✓ {model_name}: Predicted peak intensity = {prediction[0]:.2f}")
            return {"status": "success", "prediction": float(prediction[0])}
            
        except Exception as e:
            logger.error(f"  ✗ {model_name}: Prediction failed - {e}")
            return {"status": "error", "message": str(e)}
    
    def test_encoders(self):
        """Test that encoders can be loaded."""
        logger.info("\n=== Testing Encoders ===")
        
        encoders_to_test = [
            "department_encoder.pkl",
            "age_encoder.pkl",
            "insurance_encoder.pkl",
            "triage_encoder.pkl"
        ]
        
        for encoder_file in encoders_to_test:
            encoder_path = os.path.join(self.models_dir, encoder_file)
            if os.path.exists(encoder_path):
                success, encoder_data = self.test_model_loading(encoder_path)
                if success:
                    self.test_results[encoder_file] = {"status": "success", "type": "encoder"}
            else:
                logger.warning(f"Encoder not found: {encoder_file}")
    
    def test_scalers(self):
        """Test that scalers can be loaded."""
        logger.info("\n=== Testing Scalers ===")
        
        scalers_to_test = [
            "wait_time_scaler.pkl",
            "triage_scaler.pkl",
            "peak_time_scaler.pkl"
        ]
        
        for scaler_file in scalers_to_test:
            scaler_path = os.path.join(self.models_dir, scaler_file)
            if os.path.exists(scaler_path):
                success, scaler_data = self.test_model_loading(scaler_path)
                if success:
                    self.test_results[scaler_file] = {"status": "success", "type": "scaler"}
            else:
                logger.warning(f"Scaler not found: {scaler_file}")
    
    def run_all_tests(self):
        """Run all model tests."""
        logger.info("Starting comprehensive model testing...")
        
        # Test different types of models
        self.test_wait_time_prediction()
        self.test_triage_models()
        self.test_anomaly_detection_models()
        self.test_peak_time_prediction()
        self.test_encoders()
        self.test_scalers()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print a summary of all test results."""
        logger.info("\n" + "="*60)
        logger.info("MODEL TESTING SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if result.get("status") == "success")
        
        logger.info(f"Total models tested: {total_tests}")
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {total_tests - successful_tests}")
        logger.info(f"Success rate: {(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        # List failed tests
        failed_tests = [name for name, result in self.test_results.items() 
                       if result.get("status") != "success"]
        
        if failed_tests:
            logger.info(f"\nFailed tests:")
            for failed_test in failed_tests:
                logger.info(f"  - {failed_test}: {self.test_results[failed_test].get('message', 'Unknown error')}")
        
        logger.info("\n" + "="*60)
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests/total_tests)*100 if total_tests > 0 else 0,
            "details": self.test_results
        }

def main():
    """Main function to run the model tests."""
    tester = ModelTester()
    results = tester.run_all_tests()
    
    # Return results for external usage
    return results

if __name__ == "__main__":
    main()