import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_service(client: TestClient):
    """Test creating a new service."""
    service_data = {
        "name": "Neurology",
        "description": "Brain and nervous system care",
        "department": "Neurology",
        "estimated_wait_time": 60
    }

    response = client.post("/api/services/", json=service_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == service_data["name"]
    assert data["department"] == service_data["department"]
    assert data["estimated_wait_time"] == service_data["estimated_wait_time"]

def test_get_all_services(client: TestClient):
    """Test getting all services."""
    # Create a few services first
    services_data = [
        {
            "name": "Radiology",
            "description": "Imaging services",
            "department": "Radiology",
            "estimated_wait_time": 45
        },
        {
            "name": "Laboratory",
            "description": "Blood tests and diagnostics",
            "department": "Laboratory",
            "estimated_wait_time": 20
        }
    ]

    for service_data in services_data:
        client.post("/api/services/", json=service_data)

    response = client.get("/api/services/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_service_by_id(client: TestClient):
    """Test getting a specific service by ID."""
    service_data = {
        "name": "Oncology",
        "description": "Cancer treatment and care",
        "department": "Oncology",
        "estimated_wait_time": 90
    }

    create_response = client.post("/api/services/", json=service_data)
    service_id = create_response.json()["id"]

    response = client.get(f"/api/services/{service_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == service_id
    assert data["name"] == service_data["name"]

def test_get_service_counters(client: TestClient):
    """Test getting counters for a service."""
    service_data = {
        "name": "Pharmacy",
        "description": "Medication dispensing",
        "department": "Pharmacy",
        "estimated_wait_time": 15
    }

    create_response = client.post("/api/services/", json=service_data)
    service_id = create_response.json()["id"]

    response = client.get(f"/api/services/{service_id}/counters")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # Should return counters associated with this service

def test_service_not_found(client: TestClient):
    """Test getting a non-existent service."""
    response = client.get("/api/services/99999")
    assert response.status_code == 404

def test_create_appointment(auth_client: TestClient):
    """Test creating an appointment."""
    # First create a user and service
    user_data = {
        "name": "Appointment Patient",
        "email": "appt_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = auth_client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Dentistry",
        "description": "Dental care services",
        "department": "Dentistry",
        "estimated_wait_time": 30
    }

    service_response = auth_client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-02-15T10:00:00Z",
        "notes": "Regular checkup"
    }

    response = auth_client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 200

    data = response.json()
    assert data["patient_id"] == user_id
    assert data["service_id"] == service_id
    assert "appointment_date" in data

def test_get_appointments(auth_client: TestClient):
    """Test getting appointments."""
    response = auth_client.get("/api/appointments/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

def test_update_appointment(auth_client: TestClient):
    """Test updating an appointment."""
    # Create appointment first
    user_data = {
        "name": "Update Patient",
        "email": "update_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Physical Therapy",
        "description": "Rehabilitation services",
        "department": "Physical Therapy",
        "estimated_wait_time": 45
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-02-20T14:00:00Z",
        "notes": "Initial consultation"
    }

    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["id"]

    # Update appointment
    update_data = {
        "status": "confirmed",
        "notes": "Updated notes"
    }

    response = client.put(f"/api/appointments/{appointment_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "confirmed"
    assert data["notes"] == "Updated notes"

def test_cancel_appointment(auth_client: TestClient):
    """Test canceling an appointment."""
    # Create appointment first
    user_data = {
        "name": "Cancel Patient",
        "email": "cancel_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Ophthalmology",
        "description": "Eye care services",
        "department": "Ophthalmology",
        "estimated_wait_time": 40
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-02-25T11:00:00Z"
    }

    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["id"]

    # Cancel appointment
    response = client.delete(f"/api/appointments/{appointment_id}")
    assert response.status_code == 200

def test_create_notification(auth_client: TestClient):
    """Test creating a notification."""
    notification_data = {
        "user_id": 1,
        "title": "Appointment Reminder",
        "message": "Your appointment is tomorrow at 2:00 PM",
        "type": "appointment",
        "priority": "normal"
    }

    response = client.post("/api/notifications/", json=notification_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == notification_data["title"]
    assert data["message"] == notification_data["message"]
    assert data["type"] == notification_data["type"]

def test_get_notifications(auth_client: TestClient):
    """Test getting notifications."""
    response = client.get("/api/notifications/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

def test_mark_notification_read(auth_client: TestClient):
    """Test marking a notification as read."""
    # Create notification first
    notification_data = {
        "user_id": 1,
        "title": "Test Notification",
        "message": "This is a test notification",
        "type": "system",
        "priority": "low"
    }

    create_response = client.post("/api/notifications/", json=notification_data)
    notification_id = create_response.json()["id"]

    # Mark as read
    response = client.put(f"/api/notifications/{notification_id}/read")
    assert response.status_code == 200

    data = response.json()
    assert data["is_read"] == True

def test_delete_notification(auth_client: TestClient):
    """Test deleting a notification."""
    # Create notification first
    notification_data = {
        "user_id": 1,
        "title": "Delete Test",
        "message": "This notification will be deleted",
        "type": "test",
        "priority": "low"
    }

    create_response = client.post("/api/notifications/", json=notification_data)
    notification_id = create_response.json()["id"]

    # Delete notification
    response = client.delete(f"/api/notifications/{notification_id}")
    assert response.status_code == 200

def test_navigation_route(auth_client: TestClient):
    """Test getting navigation route."""
    navigation_data = {
        "start_location": "Emergency Entrance",
        "end_location": "Cardiology Department",
        "accessibility_needs": ["wheelchair"],
        "preferred_route": "elevator"
    }

    response = client.post("/api/navigation/route", json=navigation_data)
    assert response.status_code == 200

    data = response.json()
    assert "route" in data
    assert "estimated_time" in data
    assert "instructions" in data
    assert isinstance(data["instructions"], list)

def test_get_available_locations(auth_client: TestClient):
    """Test getting available navigation locations."""
    response = client.get("/api/navigation/locations")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_request_emergency_assistance(auth_client: TestClient):
    """Test requesting emergency assistance via navigation."""
    assistance_data = {
        "current_location": "Main Lobby",
        "emergency_type": "medical_emergency",
        "patient_condition": "unconscious",
        "additional_info": "Patient collapsed suddenly"
    }

    response = client.post("/api/navigation/emergency", json=assistance_data)
    assert response.status_code == 200

    data = response.json()
    assert "assistance_requested" in data
    assert "estimated_response_time" in data
    assert "instructions" in data

def test_checkin_patient(client: TestClient):
    """Test patient check-in."""
    # Create appointment first
    user_data = {
        "name": "Checkin Patient",
        "email": "checkin_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Check-in Service",
        "description": "Check-in test service",
        "department": "General",
        "estimated_wait_time": 10
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-01-15T10:00:00Z"
    }

    appointment_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    # Check-in patient
    checkin_data = {
        "appointment_id": appointment_id,
        "checkin_method": "kiosk",
        "identification_verified": True
    }

    response = client.post("/api/checkin/", json=checkin_data)
    assert response.status_code == 200

    data = response.json()
    assert "checkin_id" in data
    assert "queue_number" in data
    assert "estimated_wait_time" in data

def test_get_checkin_status(client: TestClient):
    """Test getting check-in status."""
    # Create check-in first
    user_data = {
        "name": "Status Patient",
        "email": "status_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Status Service",
        "description": "Status check service",
        "department": "General",
        "estimated_wait_time": 15
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-01-16T11:00:00Z"
    }

    appointment_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    checkin_data = {
        "appointment_id": appointment_id,
        "checkin_method": "mobile_app"
    }

    checkin_response = client.post("/api/checkin/", json=checkin_data)
    checkin_id = checkin_response.json()["checkin_id"]

    # Get check-in status
    response = client.get(f"/api/checkin/appointment/{appointment_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["appointment_id"] == appointment_id
    assert "status" in data
    assert "checkin_time" in data

def test_update_checkin_status(client: TestClient):
    """Test updating check-in status."""
    # Create check-in first
    user_data = {
        "name": "Update Status Patient",
        "email": "update_status_patient@example.com",
        "password": "testpass123",
        "role": "patient"
    }

    user_response = client.post("/api/auth/register", json=user_data)
    user_id = user_response.json()["id"]

    service_data = {
        "name": "Update Status Service",
        "description": "Update status service",
        "department": "General",
        "estimated_wait_time": 20
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    appointment_data = {
        "patient_id": user_id,
        "service_id": service_id,
        "appointment_date": "2024-01-17T12:00:00Z"
    }

    appointment_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    checkin_data = {
        "appointment_id": appointment_id,
        "checkin_method": "reception"
    }

    checkin_response = client.post("/api/checkin/", json=checkin_data)
    checkin_id = checkin_response.json()["checkin_id"]

    # Update check-in status
    update_data = {
        "status": "completed"
    }

    response = client.put(f"/api/checkin/{checkin_id}/status", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
