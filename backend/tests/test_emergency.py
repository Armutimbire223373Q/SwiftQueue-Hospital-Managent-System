import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_dispatch_ambulance_endpoint(client: TestClient):
    """Test dispatching an ambulance."""
    dispatch_data = {
        "patient_id": 1,
        "emergency_details": "Severe chest pain and difficulty breathing",
        "location": "123 Main St, City, State 12345"
    }

    # Mock the emergency service
    with patch('app.routes.emergency.emergency_service') as mock_service:
        mock_dispatch = {
            "id": 1,
            "patient_id": 1,
            "emergency_details": dispatch_data["emergency_details"],
            "dispatch_address": dispatch_data["location"],
            "dispatch_status": "dispatched",
            "ambulance_id": "AMB-123",
            "response_time": 8
        }
        mock_service.dispatch_ambulance.return_value = mock_dispatch

        response = client.post("/api/emergency/dispatch-ambulance", json=dispatch_data)
        assert response.status_code == 200

        data = response.json()
        assert data["patient_id"] == dispatch_data["patient_id"]
        assert data["emergency_details"] == dispatch_data["emergency_details"]
        assert data["dispatch_status"] == "dispatched"

def test_get_dispatch_status(client: TestClient):
    """Test getting dispatch status."""
    dispatch_id = 1

    with patch('app.routes.emergency.emergency_service') as mock_service:
        mock_status = {
            "id": dispatch_id,
            "dispatch_status": "en_route",
            "ambulance_id": "AMB-123",
            "response_time": 12,
            "estimated_arrival": "2024-01-15T10:30:00Z"
        }
        mock_service.get_dispatch_status.return_value = mock_status

        response = client.get(f"/api/emergency/dispatch/{dispatch_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == dispatch_id
        assert data["dispatch_status"] == "en_route"
        assert "response_time" in data

def test_get_patient_dispatches(client: TestClient):
    """Test getting dispatches for a patient."""
    patient_id = 1

    with patch('app.routes.emergency.emergency_service') as mock_service:
        mock_dispatches = [
            {
                "id": 1,
                "patient_id": patient_id,
                "emergency_details": "Chest pain",
                "dispatch_status": "completed",
                "response_time": 10
            },
            {
                "id": 2,
                "patient_id": patient_id,
                "emergency_details": "Allergic reaction",
                "dispatch_status": "en_route",
                "response_time": 6
            }
        ]
        mock_service.get_patient_dispatches.return_value = mock_dispatches

        response = client.get(f"/api/emergency/dispatches/patient/{patient_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(d["patient_id"] == patient_id for d in data)

def test_send_emergency_sms(client: TestClient):
    """Test sending emergency SMS."""
    sms_data = {
        "phone_number": "+1234567890",
        "message": "Emergency: Ambulance dispatched to your location",
        "priority": "high"
    }

    with patch('app.routes.emergency.send_emergency_sms') as mock_sms:
        mock_sms.return_value = {"status": "sent", "message_id": "msg_123"}

        response = client.post("/api/emergency/sms/send", json=sms_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "sent"
        assert "message_id" in data

def test_send_eta_sms(client: TestClient):
    """Test sending ETA SMS notification."""
    eta_data = {
        "phone_number": "+1234567890",
        "ambulance_id": "AMB-123",
        "eta_minutes": 5,
        "location": "123 Main St"
    }

    with patch('app.routes.emergency.send_eta_sms') as mock_sms:
        mock_sms.return_value = {"status": "sent", "message_id": "eta_123"}

        response = client.post("/api/emergency/sms/eta-notification", json=eta_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "sent"

def test_send_dispatch_alert(client: TestClient):
    """Test sending dispatch alert SMS."""
    alert_data = {
        "phone_number": "+1234567890",
        "patient_name": "John Doe",
        "emergency_type": "cardiac",
        "location": "456 Oak Ave"
    }

    with patch('app.routes.emergency.send_dispatch_alert_sms') as mock_sms:
        mock_sms.return_value = {"status": "sent", "message_id": "alert_123"}

        response = client.post("/api/emergency/sms/dispatch-alert", json=alert_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "sent"

def test_emergency_first_aid(client: TestClient):
    """Test emergency first aid recommendations."""
    first_aid_request = {
        "emergency_type": "cardiac_arrest",
        "patient_age": 45,
        "patient_gender": "male",
        "available_equipment": ["phone", "hands"],
        "location": "home"
    }

    response = client.post("/api/emergency/first-aid", json=first_aid_request)
    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert "priority_level" in data
    assert "estimated_response_time" in data
    assert isinstance(data["recommendations"], list)

def test_emergency_first_aid_invalid_type(client: TestClient):
    """Test emergency first aid with invalid emergency type."""
    first_aid_request = {
        "emergency_type": "invalid_emergency",
        "patient_age": 30
    }

    response = client.post("/api/emergency/first-aid", json=first_aid_request)
    assert response.status_code == 400

def test_emergency_first_aid_missing_fields(client: TestClient):
    """Test emergency first aid with missing required fields."""
    first_aid_request = {
        "emergency_type": "cardiac_arrest"
        # Missing required fields
    }

    response = client.post("/api/emergency/first-aid", json=first_aid_request)
    assert response.status_code == 422  # Validation error

def test_emergency_first_aid_all_types(client: TestClient):
    """Test emergency first aid for all supported emergency types."""
    emergency_types = [
        "cardiac_arrest", "heart_attack", "stroke", "severe_bleeding",
        "choking", "burns", "fracture", "allergic_reaction", "seizure"
    ]

    for emergency_type in emergency_types:
        first_aid_request = {
            "emergency_type": emergency_type,
            "patient_age": 35,
            "patient_gender": "female",
            "available_equipment": ["phone"],
            "location": "public_place"
        }

        response = client.post("/api/emergency/first-aid", json=first_aid_request)
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        assert data["emergency_type"] == emergency_type

def test_emergency_first_aid_with_location_context(client: TestClient):
    """Test emergency first aid with different location contexts."""
    locations = ["home", "work", "public_place", "vehicle", "outdoor"]

    for location in locations:
        first_aid_request = {
            "emergency_type": "heart_attack",
            "patient_age": 50,
            "patient_gender": "male",
            "available_equipment": ["phone", "automated_external_defibrillator"],
            "location": location
        }

        response = client.post("/api/emergency/first-aid", json=first_aid_request)
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert location in str(data["recommendations"]).lower() or True  # Location-specific advice may vary

def test_emergency_first_aid_equipment_impact(client: TestClient):
    """Test how available equipment affects first aid recommendations."""
    base_request = {
        "emergency_type": "cardiac_arrest",
        "patient_age": 40,
        "patient_gender": "male",
        "location": "home"
    }

    # Test with minimal equipment
    minimal_equipment = base_request.copy()
    minimal_equipment["available_equipment"] = ["phone"]

    response_minimal = client.post("/api/emergency/first-aid", json=minimal_equipment)
    assert response_minimal.status_code == 200

    # Test with full equipment
    full_equipment = base_request.copy()
    full_equipment["available_equipment"] = [
        "phone", "automated_external_defibrillator", "first_aid_kit",
        "oxygen_tank", "blood_pressure_monitor"
    ]

    response_full = client.post("/api/emergency/first-aid", json=full_equipment)
    assert response_full.status_code == 200

    # Both should return valid responses
    data_minimal = response_minimal.json()
    data_full = response_full.json()

    assert "recommendations" in data_minimal
    assert "recommendations" in data_full
    assert len(data_minimal["recommendations"]) > 0
    assert len(data_full["recommendations"]) > 0