import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_analyze_symptoms_endpoint(client: TestClient):
    """Test symptom analysis endpoint."""
    symptom_data = {
        "symptoms": "severe headache, nausea, sensitivity to light",
        "age": "25",
        "gender": "female",
        "duration": "2 hours"
    }

    response = client.post("/api/ai/analyze-symptoms", json=symptom_data)
    assert response.status_code == 200

    data = response.json()
    assert "analysis" in data
    assert "possible_conditions" in data
    assert "urgency_level" in data
    assert "recommendations" in data

def test_ai_health_check(client: TestClient):
    """Test AI service health check."""
    response = client.get("/api/ai/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "services" in data

def test_triage_calculation_endpoint(client: TestClient):
    """Test AI triage calculation."""
    triage_data = {
        "symptoms": ["chest pain", "shortness of breath"],
        "vital_signs": {
            "blood_pressure": "160/95",
            "heart_rate": 110,
            "temperature": 98.6
        },
        "patient_info": {
            "age": 45,
            "gender": "male",
            "medical_history": ["hypertension"]
        }
    }

    response = client.post("/api/ai/triage/calculate", json=triage_data)
    assert response.status_code == 200

    data = response.json()
    assert "triage_level" in data
    assert "priority_score" in data
    assert "recommendations" in data

def test_ai_enhanced_triage(client: TestClient):
    """Test AI-enhanced triage with local LLM."""
    triage_data = {
        "symptoms": "severe abdominal pain, vomiting, fever",
        "patient_age": 35,
        "patient_gender": "female",
        "pain_level": 8,
        "duration": "6 hours"
    }

    response = client.post("/api/ai/triage/ai-enhanced", json=triage_data)
    assert response.status_code == 200

    data = response.json()
    assert "triage_result" in data
    assert "ai_analysis" in data
    assert "confidence_score" in data

def test_batch_symptom_analysis(client: TestClient):
    """Test batch symptom analysis."""
    batch_data = [
        {
            "symptoms": "cough, fever, fatigue",
            "age": "30",
            "urgency": "moderate"
        },
        {
            "symptoms": "chest pain, sweating",
            "age": "50",
            "urgency": "high"
        }
    ]

    response = client.post("/api/ai/symptoms/batch-analyze", json=batch_data)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    for result in data:
        assert "analysis" in result
        assert "possible_conditions" in result

def test_workflow_start_visit(client: TestClient):
    """Test starting a patient visit workflow."""
    workflow_data = {
        "patient_id": 1,
        "visit_type": "emergency",
        "initial_symptoms": "chest pain, difficulty breathing",
        "triage_level": "urgent"
    }

    response = client.post("/api/ai/workflow/start-visit", json=workflow_data)
    assert response.status_code == 200

    data = response.json()
    assert "workflow_id" in data
    assert "current_stage" in data
    assert "stages" in data

def test_workflow_update_stage(client: TestClient):
    """Test updating workflow stage."""
    update_data = {
        "workflow_id": "wf_123",
        "stage_name": "triage",
        "status": "completed",
        "notes": "Patient triaged and moved to examination"
    }

    response = client.post("/api/ai/workflow/update-stage", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert "workflow_id" in data
    assert "current_stage" in data
    assert "status" in data

def test_get_active_patients(client: TestClient):
    """Test getting active patients in workflow."""
    response = client.get("/api/ai/workflow/active-patients")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for patient in data:
        assert "patient_id" in patient
        assert "current_stage" in patient
        assert "workflow_status" in patient

def test_resource_allocation_optimization(client: TestClient):
    """Test resource allocation optimization."""
    optimization_data = {
        "current_workload": {
            "emergency_dept": 15,
            "cardiology": 8,
            "general_medicine": 12
        },
        "available_staff": {
            "doctors": 25,
            "nurses": 40,
            "technicians": 15
        },
        "time_period": "next_4_hours"
    }

    response = client.post("/api/ai/optimization/resource-allocation", json=optimization_data)
    assert response.status_code == 200

    data = response.json()
    assert "optimized_allocation" in data
    assert "efficiency_gain" in data
    assert "recommendations" in data

def test_workflow_bottleneck_analysis(client: TestClient):
    """Test workflow bottleneck analysis."""
    response = client.get("/api/ai/analytics/workflow-bottlenecks")
    assert response.status_code == 200

    data = response.json()
    assert "bottlenecks" in data
    assert "recommendations" in data
    assert isinstance(data["bottlenecks"], list)

def test_department_performance_analytics(client: TestClient):
    """Test department performance analytics."""
    response = client.get("/api/ai/analytics/department-performance")
    assert response.status_code == 200

    data = response.json()
    assert "departments" in data
    assert "performance_metrics" in data
    assert isinstance(data["departments"], list)

def test_cache_stats(client: TestClient):
    """Test AI cache statistics."""
    response = client.get("/api/ai/cache/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total_requests" in data
    assert "cache_hits" in data
    assert "cache_miss_rate" in data

def test_clear_cache(client: TestClient):
    """Test clearing AI response cache."""
    response = client.post("/api/ai/cache/clear")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "cleared_entries" in data

def test_service_recommendation(client: TestClient):
    """Test AI-powered service recommendation."""
    recommendation_data = {
        "symptoms": "persistent cough, chest congestion, fever",
        "age_group": "adult",
        "urgency_level": "moderate",
        "patient_history": ["asthma"]
    }

    response = client.post("/api/ai/service-recommend", json=recommendation_data)
    assert response.status_code == 200

    data = response.json()
    assert "recommended_service" in data
    assert "department" in data
    assert "confidence_score" in data
    assert "reasoning" in data

def test_anomaly_detection(client: TestClient):
    """Test anomaly detection in hospital metrics."""
    anomaly_data = {
        "metrics": {
            "wait_time_avg": 45,
            "patient_volume": 150,
            "staff_utilization": 85,
            "error_rate": 2.5
        },
        "time_window": "last_hour",
        "department": "emergency"
    }

    response = client.post("/api/ai/anomaly-detection", json=anomaly_data)
    assert response.status_code == 200

    data = response.json()
    assert "anomalies_detected" in data
    assert "severity_score" in data
    assert "recommendations" in data

def test_peak_time_prediction(client: TestClient):
    """Test peak time prediction."""
    prediction_data = {
        "department": "emergency",
        "day_of_week": 1,  # Monday
        "hour": 14,
        "current_trends": {
            "patient_arrivals": 25,
            "wait_times": 35
        }
    }

    response = client.post("/api/ai/peak-time-predict", json=prediction_data)
    assert response.status_code == 200

    data = response.json()
    assert "predicted_volume" in data
    assert "peak_probability" in data
    assert "recommended_actions" in data

def test_staff_optimization(client: TestClient):
    """Test staff optimization recommendations."""
    optimization_data = {
        "department": "cardiology",
        "current_staff": {
            "doctors": 5,
            "nurses": 8
        },
        "patient_load": {
            "current": 45,
            "predicted_next_hour": 52
        },
        "time_of_day": "afternoon"
    }

    response = client.post("/api/ai/staff-optimize", json=optimization_data)
    assert response.status_code == 200

    data = response.json()
    assert "recommended_staffing" in data
    assert "efficiency_improvement" in data
    assert "cost_impact" in data

def test_wait_time_prediction(client: TestClient):
    """Test wait time prediction for patients."""
    prediction_data = {
        "service_type": "emergency",
        "patient_priority": "urgent",
        "current_queue_length": 12,
        "time_of_day": 15,
        "day_of_week": 2,
        "patient_age": 35,
        "insurance_type": "private"
    }

    response = client.post("/api/ai/wait-time-predict", json=prediction_data)
    assert response.status_code == 200

    data = response.json()
    assert "predicted_wait_time" in data
    assert "confidence_interval" in data
    assert "factors_influencing" in data

def test_ai_fallback_behavior(client: TestClient):
    """Test AI service fallback when primary service is unavailable."""
    # This test ensures the system gracefully handles AI service failures
    with patch('app.services.openrouter_service.OpenRouterService.analyze_symptoms') as mock_openrouter:
        mock_openrouter.side_effect = Exception("OpenRouter service unavailable")

        symptom_data = {
            "symptoms": "headache, dizziness",
            "age": "28"
        }

        response = client.post("/api/ai/analyze-symptoms", json=symptom_data)
        # Should still return a response using fallback logic
        assert response.status_code in [200, 206]  # 206 for partial/degraded response

        data = response.json()
        assert "analysis" in data
        assert "fallback_used" in data or "degraded_mode" in data

def test_ai_response_caching(client: TestClient):
    """Test that AI responses are properly cached."""
    symptom_data = {
        "symptoms": "fever, cough, fatigue",
        "age": "25"
    }

    # First request
    response1 = client.post("/api/ai/analyze-symptoms", json=symptom_data)
    assert response1.status_code == 200

    # Second identical request (should use cache)
    response2 = client.post("/api/ai/analyze-symptoms", json=symptom_data)
    assert response2.status_code == 200

    # Check cache stats
    cache_response = client.get("/api/ai/cache/stats")
    assert cache_response.status_code == 200

    cache_data = cache_response.json()
    assert cache_data["total_requests"] >= 2
    assert cache_data["cache_hits"] >= 1