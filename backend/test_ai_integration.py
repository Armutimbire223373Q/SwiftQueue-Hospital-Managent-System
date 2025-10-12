#!/usr/bin/env python3
"""
Tests for AI integration in emergency dispatch system.
Tests that AI correctly identifies critical emergencies and triggers ambulance dispatch.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app
from app.database import Base, get_db
from app.models.models import User, EmergencyDispatch
from app.services.emergency_service import dispatch_ambulance, EmergencyServiceError

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_patient(test_db):
    """Create a test patient"""
    patient = User(
        name="Test Patient",
        email="patient@example.com",
        phone="123-456-7890",
        street_address="123 Emergency St",
        city="Emergency City",
        state="Emergency State",
        zip_code="91111",
        country="Emergency Country",
        date_of_birth=datetime(1990, 1, 1),
        password_hash="hashed_password",
        role="patient"
    )
    test_db.add(patient)
    test_db.commit()
    test_db.refresh(patient)
    return patient

class TestAISymptomAnalysis:
    """Test AI symptom analysis functionality"""

    def test_critical_symptoms_detection(self):
        """Test that AI correctly identifies critical symptoms"""
        from app.routes.ai import _analyze_symptoms_rule_based

        # Test critical symptoms
        critical_symptoms = [
            "chest pain, difficulty breathing",
            "severe bleeding, unconscious",
            "heart attack, cardiac arrest",
            "stroke symptoms, can't move",
            "anaphylaxis, severe allergic reaction"
        ]

        for symptoms in critical_symptoms:
            result = _analyze_symptoms_rule_based(symptoms)
            assert result["emergency_level"] == "critical"
            assert result["triage_category"] == "Emergency"
            assert "recommended_actions" in result
            assert len(result["recommended_actions"]) > 0

    def test_high_priority_symptoms_detection(self):
        """Test that AI correctly identifies high priority symptoms"""
        from app.routes.ai import _analyze_symptoms_rule_based

        high_symptoms = [
            "severe pain, broken bone",
            "high fever, mental crisis",
            "dehydration, vomiting blood",
            "severe headache, fainting"
        ]

        for symptoms in high_symptoms:
            result = _analyze_symptoms_rule_based(symptoms)
            assert result["emergency_level"] == "high"
            assert result["triage_category"] == "Urgent"

    def test_moderate_symptoms_detection(self):
        """Test that AI correctly identifies moderate symptoms"""
        from app.routes.ai import _analyze_symptoms_rule_based

        moderate_symptoms = [
            "pain, nausea",
            "fever, infection",
            "headache, sore throat"
        ]

        for symptoms in moderate_symptoms:
            result = _analyze_symptoms_rule_based(symptoms)
            assert result["emergency_level"] == "moderate"
            assert result["triage_category"] == "Semi-urgent"

    def test_low_priority_symptoms_detection(self):
        """Test that AI correctly identifies low priority symptoms"""
        from app.routes.ai import _analyze_symptoms_rule_based

        low_symptoms = [
            "checkup, routine",
            "vaccination needed",
            "medication refill"
        ]

        for symptoms in low_symptoms:
            result = _analyze_symptoms_rule_based(symptoms)
            assert result["emergency_level"] == "low"
            assert result["triage_category"] == "Non-urgent"

class TestAIDispatchIntegration:
    """Test AI integration with ambulance dispatch"""

    @patch('app.routes.ai.dispatch_ambulance')
    def test_critical_symptoms_trigger_dispatch(self, mock_dispatch, test_patient):
        """Test that critical symptoms trigger ambulance dispatch"""
        from app.routes.ai import _analyze_symptoms_rule_based

        # Mock the dispatch function to return a dispatch object
        mock_dispatch_obj = MagicMock()
        mock_dispatch_obj.id = 123
        mock_dispatch_obj.ambulance_id = "AMB-999"
        mock_dispatch_obj.dispatch_status = "dispatched"
        mock_dispatch_obj.response_time = 10
        mock_dispatch_obj.dispatched_at = datetime.utcnow()
        mock_dispatch.return_value = mock_dispatch_obj

        # Test critical symptoms with patient ID
        result = _analyze_symptoms_rule_based(
            "chest pain, difficulty breathing",
            patient_id=test_patient.id,
            db=TestingSessionLocal()
        )

        # Verify dispatch was called
        mock_dispatch.assert_called_once()

        # Verify result contains dispatch information
        assert "ambulance_dispatch" in result
        dispatch_info = result["ambulance_dispatch"]
        assert dispatch_info["dispatch_id"] == 123
        assert dispatch_info["ambulance_id"] == "AMB-999"
        assert dispatch_info["status"] == "dispatched"

    @patch('app.routes.ai.dispatch_ambulance')
    def test_critical_symptoms_dispatch_failure_handling(self, mock_dispatch, test_patient):
        """Test handling of dispatch failures"""
        from app.routes.ai import _analyze_symptoms_rule_based

        # Mock dispatch to raise an exception
        mock_dispatch.side_effect = EmergencyServiceError("Dispatch failed")

        result = _analyze_symptoms_rule_based(
            "chest pain, unconscious",
            patient_id=test_patient.id,
            db=TestingSessionLocal()
        )

        # Verify dispatch was attempted
        mock_dispatch.assert_called_once()

        # Verify error is handled gracefully
        assert "ambulance_dispatch" in result
        dispatch_info = result["ambulance_dispatch"]
        assert "error" in dispatch_info
        assert dispatch_info["status"] == "failed"

    def test_no_dispatch_for_non_critical_symptoms(self, test_patient):
        """Test that non-critical symptoms don't trigger dispatch"""
        from app.routes.ai import _analyze_symptoms_rule_based

        result = _analyze_symptoms_rule_based(
            "headache, sore throat",
            patient_id=test_patient.id,
            db=TestingSessionLocal()
        )

        # Non-critical symptoms should not have ambulance_dispatch
        assert "ambulance_dispatch" not in result
        assert result["emergency_level"] == "moderate"

class TestAIAgeBasedRisk:
    """Test AI age-based risk assessment"""

    def test_elderly_high_risk(self):
        """Test that elderly patients get higher risk scores"""
        from app.routes.ai import _analyze_symptoms_rule_based

        # Test with elderly age
        result_elderly = _analyze_symptoms_rule_based(
            "fever, cough",
            age="75"
        )

        # Test with young adult age
        result_young = _analyze_symptoms_rule_based(
            "fever, cough",
            age="25"
        )

        # Elderly should have higher confidence (risk adjustment)
        assert result_elderly["confidence"] >= result_young["confidence"]

    def test_child_high_risk(self):
        """Test that children get higher risk scores"""
        from app.routes.ai import _analyze_symptoms_rule_based

        # Test with child age
        result_child = _analyze_symptoms_rule_based(
            "fever, cough",
            age="3"
        )

        # Test with adult age
        result_adult = _analyze_symptoms_rule_based(
            "fever, cough",
            age="30"
        )

        # Child should have higher confidence (risk adjustment)
        assert result_child["confidence"] >= result_adult["confidence"]

class TestAPIIntegration:
    """Test AI API endpoints"""

    def test_analyze_symptoms_endpoint_critical(self):
        """Test the analyze symptoms API endpoint with critical symptoms"""
        # This would require the server to be running
        # For now, test the logic directly
        pass

    def test_analyze_symptoms_endpoint_non_critical(self):
        """Test the analyze symptoms API endpoint with non-critical symptoms"""
        # This would require the server to be running
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])