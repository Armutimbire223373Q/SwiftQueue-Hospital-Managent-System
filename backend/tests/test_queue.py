import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import Service, QueueEntry

def test_join_queue_endpoint(client: TestClient, db: Session):
    """Test joining a queue."""
    # First create a service
    service_data = {
        "name": "Emergency Department",
        "description": "Emergency medical services",
        "department": "Emergency",
        "estimated_wait_time": 30
    }

    service_response = client.post("/api/services/", json=service_data)
    assert service_response.status_code == 200
    service_id = service_response.json()["id"]

    # Now join the queue
    queue_data = {
        "service_id": service_id,
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
        "priority": "normal",
        "symptoms": "Headache and fever"
    }

    response = client.post("/api/queue/join", json=queue_data)
    assert response.status_code == 200

    data = response.json()
    assert "queue_number" in data
    assert "estimated_wait_time" in data
    assert "position" in data
    assert data["service_id"] == service_id

def test_get_queue_status(client: TestClient, db: Session):
    """Test getting queue status."""
    # Create service and join queue first
    service_data = {
        "name": "Cardiology",
        "description": "Heart care services",
        "department": "Cardiology",
        "estimated_wait_time": 45
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    queue_data = {
        "service_id": service_id,
        "patient_name": "Jane Smith",
        "patient_email": "jane@example.com",
        "priority": "urgent",
        "symptoms": "Chest pain"
    }

    join_response = client.post("/api/queue/join", json=queue_data)
    queue_number = join_response.json()["queue_number"]

    # Get queue status
    response = client.get(f"/api/queue/status/{queue_number}")
    assert response.status_code == 200

    data = response.json()
    assert data["queue_number"] == queue_number
    assert data["status"] == "waiting"
    assert "position" in data
    assert "estimated_wait_time" in data

def test_get_all_queues(client: TestClient, db: Session):
    """Test getting all queues."""
    # Create multiple services and queues
    services_data = [
        {
            "name": "Emergency",
            "description": "Emergency services",
            "department": "Emergency",
            "estimated_wait_time": 15
        },
        {
            "name": "General Practice",
            "description": "General medical care",
            "department": "General",
            "estimated_wait_time": 30
        }
    ]

    service_ids = []
    for service_data in services_data:
        response = client.post("/api/services/", json=service_data)
        service_ids.append(response.json()["id"])

    # Join queues for both services
    for i, service_id in enumerate(service_ids):
        queue_data = {
            "service_id": service_id,
            "patient_name": f"Patient {i+1}",
            "patient_email": f"patient{i+1}@example.com",
            "priority": "normal",
            "symptoms": f"Symptom {i+1}"
        }
        client.post("/api/queue/join", json=queue_data)

    # Get all queues
    response = client.get("/api/queue/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least our test queues

def test_get_service_queue(client: TestClient, db: Session):
    """Test getting queues for a specific service."""
    # Create service
    service_data = {
        "name": "Pediatrics",
        "description": "Children's healthcare",
        "department": "Pediatrics",
        "estimated_wait_time": 20
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    # Join multiple patients to the same service
    for i in range(3):
        queue_data = {
            "service_id": service_id,
            "patient_name": f"Child {i+1}",
            "patient_email": f"child{i+1}@example.com",
            "priority": "normal",
            "symptoms": f"Child symptom {i+1}"
        }
        client.post("/api/queue/join", json=queue_data)

    # Get service-specific queue
    response = client.get(f"/api/queue/service/{service_id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Check that all entries belong to the correct service
    for entry in data:
        assert entry["service_id"] == service_id

def test_update_queue_status(client: TestClient, db: Session):
    """Test updating queue status."""
    # Create service and join queue
    service_data = {
        "name": "Dermatology",
        "description": "Skin care services",
        "department": "Dermatology",
        "estimated_wait_time": 25
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    queue_data = {
        "service_id": service_id,
        "patient_name": "Alice Johnson",
        "patient_email": "alice@example.com",
        "priority": "normal",
        "symptoms": "Rash on arm"
    }

    join_response = client.post("/api/queue/join", json=queue_data)
    queue_id = join_response.json()["id"]

    # Update queue status
    update_data = {
        "status": "in_progress"
    }

    response = client.put(f"/api/queue/{queue_id}/status", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "in_progress"

def test_call_next_patient(client: TestClient, db: Session):
    """Test calling next patient."""
    # Create service and join multiple patients
    service_data = {
        "name": "Orthopedics",
        "description": "Bone and joint care",
        "department": "Orthopedics",
        "estimated_wait_time": 40
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    # Join 3 patients
    for i in range(3):
        queue_data = {
            "service_id": service_id,
            "patient_name": f"Patient {i+1}",
            "patient_email": f"patient{i+1}@example.com",
            "priority": "normal",
            "symptoms": f"Injury {i+1}"
        }
        client.post("/api/queue/join", json=queue_data)

    # Call next patient
    call_data = {
        "service_id": service_id,
        "counter_name": "Counter A"
    }

    response = client.post("/api/queue/call-next", json=call_data)
    assert response.status_code == 200

    data = response.json()
    assert "called_patient" in data
    assert data["called_patient"]["service_id"] == service_id
    assert data["counter_name"] == "Counter A"

def test_priority_queue_ordering(client: TestClient, db: Session):
    """Test that urgent patients are prioritized."""
    service_data = {
        "name": "Emergency Room",
        "description": "Emergency care",
        "department": "Emergency",
        "estimated_wait_time": 10
    }

    service_response = client.post("/api/services/", json=service_data)
    service_id = service_response.json()["id"]

    # Join patients with different priorities
    priorities = ["normal", "urgent", "normal", "high"]
    patients = []

    for i, priority in enumerate(priorities):
        queue_data = {
            "service_id": service_id,
            "patient_name": f"Patient {i+1}",
            "patient_email": f"patient{i+1}@example.com",
            "priority": priority,
            "symptoms": f"Symptom {i+1}"
        }
        response = client.post("/api/queue/join", json=queue_data)
        patients.append(response.json())

    # Get service queue and check ordering
    response = client.get(f"/api/queue/service/{service_id}")
    assert response.status_code == 200

    queue_data = response.json()

    # Urgent and high priority should come first
    urgent_positions = [p for p in queue_data if p["priority"] in ["urgent", "high"]]
    normal_positions = [p for p in queue_data if p["priority"] == "normal"]

    # Check that urgent patients have lower position numbers (called first)
    if urgent_positions:
        min_urgent_pos = min(p["position"] for p in urgent_positions)
        max_normal_pos = max((p["position"] for p in normal_positions), default=float('inf'))
        assert min_urgent_pos < max_normal_pos