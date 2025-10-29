"""
Comprehensive tests for Patient Portal API endpoints.

Tests cover:
- Patient-staff messaging
- Message threading and replies
- Document upload and management
- Patient preferences
- Lab results management
- Dashboard summary
- File handling
- Role-based access control
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import io
from fastapi import UploadFile

from app.main import app
from app.models.models import (
    User, PatientMessage, PatientDocument,
    PatientPreference, LabResult
)
from app.services.auth_service import get_password_hash

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def patient_token(client):
    """Create a patient user and return auth token."""
    # Register patient user
    user_data = {
        "name": "Test Patient",
        "email": "patient.portal@test.com",
        "phone": "1234567890",
        "password": "Test123!@#",
        "role": "patient",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "patient.portal@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def doctor_token(client):
    """Create a staff user (doctor) and return auth token."""
    # Register staff user (doctor role)
    user_data = {
        "name": "Dr. Portal Test",
        "email": "doctor.portal@test.com",
        "phone": "9876543210",
        "password": "Test123!@#",
        "role": "staff",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "doctor.portal@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def lab_tech_token(client):
    """Create a lab_technician user and return auth token."""
    # Register lab_technician user
    user_data = {
        "name": "Lab Tech",
        "email": "labtech@test.com",
        "phone": "5555555555",
        "password": "Test123!@#",
        "role": "lab_technician",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "labtech@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def patient_user(db_session):
    """Get patient user object."""
    return db_session.query(User).filter(
        User.email == "patient.portal@test.com"
    ).first()


@pytest.fixture
def doctor_user(db_session):
    """Get doctor user object."""
    return db_session.query(User).filter(
        User.email == "doctor.portal@test.com"
    ).first()


# ============================================================================
# MESSAGING TESTS
# ============================================================================

def test_send_message_patient_to_staff(client, patient_token, patient_user, doctor_user):
    """Test patient sending message to staff."""
    message_data = {
        "recipient_id": doctor_user.id,
        "subject": "Question about medication",
        "message_body": "I have a question about my prescription dosage.",
        "priority": "normal"
    }
    
    response = client.post(
        "/api/patient-portal/messages",
        json=message_data,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Question about medication"
    assert data["sender_id"] == patient_user.id
    assert data["recipient_id"] == doctor_user.id
    assert data["status"] == "unread"
    assert data["is_from_patient"] == True


def test_send_message_staff_to_patient(client, doctor_token, patient_user, doctor_user):
    """Test staff sending message to patient."""
    message_data = {
        "recipient_id": patient_user.id,
        "subject": "Follow-up appointment",
        "message_body": "Please schedule your follow-up for next week.",
        "priority": "high"
    }
    
    response = client.post(
        "/api/patient-portal/messages",
        json=message_data,
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "high"
    assert data["is_from_patient"] == False


def test_list_messages_as_patient(client, patient_token, patient_user, doctor_user):
    """Test patient listing their messages."""
    # Create a message
    message = PatientMessage(
        sender_id=doctor_user.id,
        recipient_id=patient_user.id,
        subject="Test message",
        message_body="This is a test",
        status="unread"
    )
    db_session.add(message)
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/messages",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Patient should only see messages they sent or received
    for msg in data:
        assert msg["sender_id"] == patient_user.id or msg["recipient_id"] == patient_user.id


def test_get_message_details(client, patient_token, patient_user, doctor_user):
    """Test getting message with thread."""
    # Create parent message
    parent = PatientMessage(
        sender_id=patient_user.id,
        recipient_id=doctor_user.id,
        subject="Original message",
        message_body="Original message body",
        status="read"
    )
    db_session.add(parent)
    db_session.commit()
    
    # Create reply
    reply = PatientMessage(
        sender_id=doctor_user.id,
        recipient_id=patient_user.id,
        subject="Re: Original message",
        message_body="Reply to original",
        status="unread",
        parent_message_id=parent.id
    )
    db_session.add(reply)
    db_session.commit()
    
    response = client.get(
        f"/api/patient-portal/messages/{parent.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Original message"
    assert "replies" in data
    assert len(data["replies"]) == 1


def test_reply_to_message(client, doctor_token, patient_user, doctor_user):
    """Test replying to an existing message."""
    # Create original message
    original = PatientMessage(
        sender_id=patient_user.id,
        recipient_id=doctor_user.id,
        subject="Need help",
        message_body="I need assistance",
        status="read"
    )
    db_session.add(original)
    db_session.commit()
    
    reply_data = {
        "message_body": "I can help you with that. Please come in tomorrow."
    }
    
    response = client.post(
        f"/api/patient-portal/messages/{original.id}/reply",
        json=reply_data,
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["parent_message_id"] == original.id
    assert "Re:" in data["subject"]


def test_close_message_thread(client, doctor_token, patient_user, doctor_user):
    """Test closing a message thread."""
    message = PatientMessage(
        sender_id=patient_user.id,
        recipient_id=doctor_user.id,
        subject="Issue resolved",
        message_body="Thanks for your help",
        status="read"
    )
    db_session.add(message)
    db_session.commit()
    
    response = client.put(
        f"/api/patient-portal/messages/{message.id}/close",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"


def test_filter_messages_by_status(client, patient_token):
    """Test filtering messages by status."""
    response = client.get(
        "/api/patient-portal/messages?status=unread",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for msg in data:
        assert msg["status"] == "unread"


def test_filter_messages_by_priority(client, doctor_token):
    """Test filtering messages by priority."""
    response = client.get(
        "/api/patient-portal/messages?priority=high",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for msg in data:
        assert msg["priority"] == "high"


# ============================================================================
# DOCUMENT MANAGEMENT TESTS
# ============================================================================

def test_upload_document(client, patient_token, patient_user):
    """Test uploading patient document."""
    # Create a test file
    file_content = b"Test document content"
    files = {
        "file": ("test_document.pdf", io.BytesIO(file_content), "application/pdf")
    }
    data = {
        "document_type": "lab_report",
        "description": "Blood test results"
    }
    
    response = client.post(
        "/api/patient-portal/documents",
        data=data,
        files=files,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["document_type"] == "lab_report"
    assert result["file_name"] == "test_document.pdf"
    assert result["patient_id"] == patient_user.id


def test_list_documents(client, patient_token, patient_user):
    """Test listing patient documents."""
    # Create sample document
    doc = PatientDocument(
        patient_id=patient_user.id,
        document_type="prescription",
        file_name="prescription.pdf",
        file_path="/uploads/prescription.pdf",
        file_size=1024
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/documents",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Patient should only see their own documents
    for doc in data:
        assert doc["patient_id"] == patient_user.id


def test_get_document_details(client, patient_token, patient_user):
    """Test getting document metadata."""
    doc = PatientDocument(
        patient_id=patient_user.id,
        document_type="medical_record",
        file_name="record.pdf",
        file_path="/uploads/record.pdf",
        file_size=2048,
        description="Medical history"
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(
        f"/api/patient-portal/documents/{doc.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_type"] == "medical_record"
    assert data["description"] == "Medical history"


def test_filter_documents_by_type(client, patient_token):
    """Test filtering documents by type."""
    response = client.get(
        "/api/patient-portal/documents?document_type=lab_report",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for doc in data:
        assert doc["document_type"] == "lab_report"


def test_staff_can_view_patient_documents(client, doctor_token, patient_user):
    """Test staff can view patient documents."""
    doc = PatientDocument(
        patient_id=patient_user.id,
        document_type="test_result",
        file_name="test.pdf",
        file_path="/uploads/test.pdf",
        file_size=1024
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(
        f"/api/patient-portal/documents?patient_id={patient_user.id}",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200


# ============================================================================
# PATIENT PREFERENCES TESTS
# ============================================================================

def test_get_patient_preferences(client, patient_token, patient_user):
    """Test getting patient preferences."""
    # Create preferences
    prefs = PatientPreference(
        patient_id=patient_user.id,
        language="en",
        notification_email=True,
        notification_sms=True,
        notification_push=False,
        communication_preference="email"
    )
    db_session.add(prefs)
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/preferences",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["notification_email"] == True


def test_update_patient_preferences(client, patient_token):
    """Test updating patient preferences."""
    update_data = {
        "language": "es",
        "notification_sms": False,
        "communication_preference": "phone"
    }
    
    response = client.put(
        "/api/patient-portal/preferences",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es"
    assert data["notification_sms"] == False
    assert data["communication_preference"] == "phone"


def test_create_preferences_if_not_exist(client, patient_token):
    """Test creating preferences if they don't exist."""
    update_data = {
        "language": "fr",
        "notification_email": True
    }
    
    response = client.put(
        "/api/patient-portal/preferences",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 201  # 201 Created for POST


# ============================================================================
# LAB RESULTS TESTS
# ============================================================================

def test_create_lab_result(client, lab_tech_token, patient_user):
    """Test lab technician creating lab result."""
    result_data = {
        "patient_id": patient_user.id,
        "test_name": "Complete Blood Count",
        "test_category": "Hematology",
        "result_value": "Normal",
        "reference_range": "4.5-11.0 x10^9/L",
        "unit": "x10^9/L",
        "status": "final",
        "is_abnormal": False,
        "notes": "All values within normal range"
    }
    
    response = client.post(
        "/api/patient-portal/lab-results",
        json=result_data,
        headers={"Authorization": f"Bearer {lab_tech_token}"}
    )
    
    assert response.status_code == 201  # 201 Created for POST
    data = response.json()
    assert data["test_name"] == "Complete Blood Count"
    assert data["status"] == "final"
    assert data["is_abnormal"] == False


def test_list_lab_results_as_patient(client, patient_token, patient_user):
    """Test patient viewing their lab results."""
    # Create lab result
    result = LabResult(
        patient_id=patient_user.id,
        test_name="Blood Glucose",
        test_category="Chemistry",
        result_value="95 mg/dL",
        status="final",
        is_abnormal=False,
        test_date=datetime.now()
    )
    db_session.add(result)
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/lab-results",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for result in data:
        assert result["patient_id"] == patient_user.id


def test_get_lab_result_details(client, patient_token, patient_user):
    """Test getting detailed lab result."""
    result = LabResult(
        patient_id=patient_user.id,
        test_name="Lipid Panel",
        test_category="Chemistry",
        result_value="Cholesterol: 180 mg/dL",
        reference_range="< 200 mg/dL",
        unit="mg/dL",
        status="final",
        is_abnormal=False,
        notes="Good cholesterol levels",
        test_date=datetime.now()
    )
    db_session.add(result)
    db_session.commit()
    
    response = client.get(
        f"/api/patient-portal/lab-results/{result.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["test_name"] == "Lipid Panel"
    assert "Good cholesterol levels" in data["notes"]


def test_update_lab_result(client, lab_tech_token, patient_user):
    """Test updating lab result status."""
    result = LabResult(
        patient_id=patient_user.id,
        test_name="Pending Test",
        test_category="Microbiology",
        result_value="Pending",
        status="pending",
        test_date=datetime.now()
    )
    db_session.add(result)
    db_session.commit()
    
    update_data = {
        "status": "final",
        "result_value": "Negative",
        "notes": "Culture shows no growth"
    }
    
    response = client.put(
        f"/api/patient-portal/lab-results/{result.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {lab_tech_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "final"
    assert data["result_value"] == "Negative"


def test_filter_abnormal_results(client, patient_token, patient_user):
    """Test filtering for abnormal lab results."""
    # Create normal and abnormal results
    normal = LabResult(
        patient_id=patient_user.id,
        test_name="Normal Test",
        test_category="Test",
        result_value="Normal",
        status="final",
        is_abnormal=False,
        test_date=datetime.now()
    )
    abnormal = LabResult(
        patient_id=patient_user.id,
        test_name="Abnormal Test",
        test_category="Test",
        result_value="High",
        status="final",
        is_abnormal=True,
        test_date=datetime.now()
    )
    db_session.add_all([normal, abnormal])
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/lab-results?abnormal_only=true",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for result in data:
        assert result["is_abnormal"] == True


def test_filter_results_by_category(client, patient_token):
    """Test filtering lab results by category."""
    response = client.get(
        "/api/patient-portal/lab-results?category=Hematology",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for result in data:
        assert result["test_category"] == "Hematology"


# ============================================================================
# DASHBOARD TESTS
# ============================================================================

def test_get_patient_dashboard(client, patient_token, patient_user):
    """Test getting patient dashboard summary."""
    # Create some test data
    message = PatientMessage(
        sender_id=1,
        recipient_id=patient_user.id,
        subject="Test",
        message_body="Test",
        status="unread"
    )
    db_session.add(message)
    
    doc = PatientDocument(
        patient_id=patient_user.id,
        document_type="test",
        file_name="test.pdf",
        file_path="/test.pdf",
        file_size=1024
    )
    db_session.add(doc)
    
    result = LabResult(
        patient_id=patient_user.id,
        test_name="Test",
        test_category="Test",
        result_value="Test",
        status="final",
        is_abnormal=True,
        test_date=datetime.now()
    )
    db_session.add(result)
    db_session.commit()
    
    response = client.get(
        "/api/patient-portal/dashboard",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "unread_messages" in data
    assert "total_documents" in data
    assert "recent_lab_results" in data
    assert "abnormal_results_count" in data


# ============================================================================
# PERMISSION TESTS
# ============================================================================

def test_patient_cannot_create_lab_results(client, patient_token, patient_user):
    """Test that patients cannot create lab results."""
    result_data = {
        "patient_id": patient_user.id,
        "test_name": "Unauthorized",
        "test_category": "Test",
        "result_value": "Test",
        "status": "final"
    }
    
    response = client.post(
        "/api/patient-portal/lab-results",
        json=result_data,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 403


def test_patient_cannot_view_other_patient_messages(client, patient_token, doctor_user):
    """Test patient cannot see other patients' messages."""
    # Create another patient
    other_patient = User(
        name="Other Patient",
        email="other@test.com",
        phone="9999999999",
        role="patient",
        is_active=True,
        date_of_birth=datetime(1990, 1, 1)
    )
    other_patient.password_hash = get_password_hash("Test123!@#")
    db_session.add(other_patient)
    db_session.commit()
    
    # Create message for other patient
    message = PatientMessage(
        sender_id=doctor_user.id,
        recipient_id=other_patient.id,
        subject="Private message",
        message_body="This is private",
        status="unread"
    )
    db_session.add(message)
    db_session.commit()
    
    # Try to access the message
    response = client.get(
        f"/api/patient-portal/messages/{message.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 403


def test_patient_cannot_view_other_patient_documents(client, patient_token):
    """Test patient cannot see other patients' documents."""
    # Create another patient
    other_patient = User(
        name="Another Patient",
        email="another@test.com",
        phone="8888888888",
        role="patient",
        is_active=True,
        date_of_birth=datetime(1990, 1, 1)
    )
    other_patient.password_hash = get_password_hash("Test123!@#")
    db_session.add(other_patient)
    db_session.commit()
    
    # Create document for other patient
    doc = PatientDocument(
        patient_id=other_patient.id,
        document_type="private",
        file_name="private.pdf",
        file_path="/private.pdf",
        file_size=1024
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(
        f"/api/patient-portal/documents/{doc.id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 403


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_message_without_subject(client, patient_token, doctor_user):
    """Test creating message without subject."""
    message_data = {
        "recipient_id": doctor_user.id,
        "message_body": "Quick question",
        "priority": "normal"
    }
    
    response = client.post(
        "/api/patient-portal/messages",
        json=message_data,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    # Should auto-generate subject or use default
    assert response.status_code in [200, 422]


def test_upload_large_file(client, patient_token):
    """Test uploading file exceeding size limit."""
    # Create a large file (simulated)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {
        "file": ("large.pdf", io.BytesIO(large_content), "application/pdf")
    }
    data = {"document_type": "test"}
    
    response = client.post(
        "/api/patient-portal/documents",
        data=data,
        files=files,
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    # Should reject if over limit
    assert response.status_code in [400, 413, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
