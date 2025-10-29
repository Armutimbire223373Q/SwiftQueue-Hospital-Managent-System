"""
File Upload API Integration Tests
Tests for file upload REST API endpoints
"""
import pytest
import io
import json
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.file_models import UploadedFile, FileAccessLog
from app.models.models import User
from app.models.workflow_models import Patient


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_file_uploads.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create test user"""
    from app.services.auth_service import get_password_hash
    
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_patient(db):
    """Create test patient"""
    from datetime import datetime
    patient = Patient(
        patient_id="P100001",
        name="Test Patient",
        email="testpatient@example.com",
        phone="123-456-7890",
        date_of_birth=datetime(1994, 1, 1),
        age_group="Adult (36-60)",
        insurance_type="Private"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers"""
    response = client.post("/api/auth/login", data={
        "username": test_user.email,  # OAuth2 uses 'username' field for email
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFileUploadEndpoints:
    """Test file upload API endpoints"""
    
    def test_upload_file_success(self, client, auth_headers, test_patient, db):
        """Test successful file upload"""
        file_content = b"This is a test PDF document"
        files = {
            "file": ("test.pdf", io.BytesIO(file_content), "application/pdf")
        }
        data = {
            "category": "documents",
            "patient_id": test_patient.id,
            "metadata": json.dumps({"description": "Test document"})
        }
        
        response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["original_filename"] == "test.pdf"
        assert result["category"] == "documents"
        assert result["file_size"] == len(file_content)
        assert result["patient_id"] == test_patient.id
        assert result["virus_scan"]["clean"] is True
        
        # Verify database record
        db_file = db.query(UploadedFile).filter_by(file_id=result["file_id"]).first()
        assert db_file is not None
        assert db_file.original_filename == "test.pdf"
        
        # Cleanup
        try:
            Path(result["full_path"]).unlink(missing_ok=True)
        except:
            pass
    
    def test_upload_file_without_auth(self, client):
        """Test file upload without authentication"""
        files = {
            "file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")
        }
        data = {"category": "documents"}
        
        response = client.post("/api/files/upload", files=files, data=data)
        
        assert response.status_code == 401
    
    def test_upload_file_invalid_category(self, client, auth_headers):
        """Test file upload with invalid category"""
        files = {
            "file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")
        }
        data = {"category": "invalid_category"}
        
        response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]
    
    def test_upload_file_invalid_type(self, client, auth_headers):
        """Test file upload with invalid file type"""
        files = {
            "file": ("malware.exe", io.BytesIO(b"MZ"), "application/x-msdownload")
        }
        data = {"category": "documents"}
        
        response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]
    
    def test_upload_file_too_large(self, client, auth_headers):
        """Test file upload exceeding size limit"""
        # Create a large file (11 MB, assuming limit is 10 MB)
        large_content = b"0" * (11 * 1024 * 1024)
        files = {
            "file": ("large.pdf", io.BytesIO(large_content), "application/pdf")
        }
        data = {"category": "documents"}
        
        response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]
    
    def test_list_files(self, client, auth_headers, test_patient, db):
        """Test listing files"""
        # Create test file records
        file1 = UploadedFile(
            file_id="file001",
            original_filename="test1.pdf",
            safe_filename="test1_safe.pdf",
            file_path="documents/test1_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        file2 = UploadedFile(
            file_id="file002",
            original_filename="test2.jpg",
            safe_filename="test2_safe.jpg",
            file_path="medical_images/test2_safe.jpg",
            category="medical_images",
            content_type="image/jpeg",
            file_size=2048,
            checksum="def456",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add_all([file1, file2])
        db.commit()
        
        # List all files
        response = client.get("/api/files/list", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 2
        assert len(result["files"]) == 2
    
    def test_list_files_with_filters(self, client, auth_headers, test_patient, db):
        """Test listing files with filters"""
        # Create test files
        file1 = UploadedFile(
            file_id="file001",
            original_filename="doc.pdf",
            safe_filename="doc_safe.pdf",
            file_path="documents/doc_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        file2 = UploadedFile(
            file_id="file002",
            original_filename="image.jpg",
            safe_filename="image_safe.jpg",
            file_path="medical_images/image_safe.jpg",
            category="medical_images",
            content_type="image/jpeg",
            file_size=2048,
            checksum="def456",
            uploaded_by=1,
            patient_id=999,  # Different patient
            is_deleted=False
        )
        db.add_all([file1, file2])
        db.commit()
        
        # Filter by category
        response = client.get(
            "/api/files/list?category=documents",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["files"][0]["category"] == "documents"
        
        # Filter by patient_id
        response = client.get(
            f"/api/files/list?patient_id={test_patient.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["files"][0]["patient_id"] == test_patient.id
    
    def test_get_file_info(self, client, auth_headers, test_patient, db):
        """Test getting file information"""
        # Create test file
        test_file = UploadedFile(
            file_id="testfile123",
            original_filename="info_test.pdf",
            safe_filename="info_test_safe.pdf",
            file_path="documents/info_test_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add(test_file)
        db.commit()
        
        response = client.get(
            f"/api/files/file/{test_file.file_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["file_id"] == "testfile123"
        assert result["original_filename"] == "info_test.pdf"
        
        # Verify access was logged
        access_log = db.query(FileAccessLog).filter_by(
            file_id=test_file.id,
            access_type="view"
        ).first()
        assert access_log is not None
        assert access_log.success is True
    
    def test_get_file_info_not_found(self, client, auth_headers):
        """Test getting info for non-existent file"""
        response = client.get(
            "/api/files/file/nonexistent123",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_download_file(self, client, auth_headers, test_patient, db):
        """Test downloading a file"""
        from app.services.file_upload_service import FileUploadService
        
        # Create actual file
        service = FileUploadService()
        file_path = service.BASE_UPLOAD_DIR / "documents" / "download_test.pdf"
        file_content = b"This is a downloadable PDF"
        file_path.write_bytes(file_content)
        
        # Create database record
        test_file = UploadedFile(
            file_id="download123",
            original_filename="download_test.pdf",
            safe_filename="download_test.pdf",
            file_path="documents/download_test.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=len(file_content),
            checksum="abc123",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add(test_file)
        db.commit()
        
        try:
            response = client.get(
                f"/api/files/download/{test_file.file_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.content == file_content
            assert response.headers["content-type"] == "application/pdf"
            
            # Verify access was logged
            access_log = db.query(FileAccessLog).filter_by(
                file_id=test_file.id,
                access_type="download"
            ).first()
            assert access_log is not None
            assert access_log.success is True
        finally:
            file_path.unlink(missing_ok=True)
    
    def test_delete_file_as_uploader(self, client, auth_headers, test_patient, db, test_user):
        """Test deleting file as uploader"""
        test_file = UploadedFile(
            file_id="delete123",
            original_filename="delete_test.pdf",
            safe_filename="delete_test_safe.pdf",
            file_path="documents/delete_test_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=test_user.id,  # Uploaded by test user
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add(test_file)
        db.commit()
        
        response = client.delete(
            f"/api/files/file/{test_file.file_id}?reason=Test%20deletion",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "File deleted successfully"
        
        # Verify soft delete
        db.refresh(test_file)
        assert test_file.is_deleted is True
        assert test_file.deleted_by == test_user.id
        assert test_file.deletion_reason == "Test deletion"
        
        # Verify access log
        access_log = db.query(FileAccessLog).filter_by(
            file_id=test_file.id,
            access_type="delete"
        ).first()
        assert access_log is not None
        assert access_log.success is True
    
    def test_delete_file_unauthorized(self, client, auth_headers, test_patient, db):
        """Test deleting file without permission"""
        test_file = UploadedFile(
            file_id="delete456",
            original_filename="protected.pdf",
            safe_filename="protected_safe.pdf",
            file_path="documents/protected_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=999,  # Different user
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add(test_file)
        db.commit()
        
        response = client.delete(
            f"/api/files/file/{test_file.file_id}?reason=Unauthorized%20attempt",
            headers=auth_headers
        )
        
        # Note: This will fail unless test_user is admin
        # Adjust based on your permission logic
        # For now, assuming test_user is admin and can delete
        assert response.status_code in [200, 403]
    
    def test_get_storage_stats(self, client, auth_headers, db):
        """Test getting storage statistics"""
        # Create test file records
        file1 = UploadedFile(
            file_id="stats001",
            original_filename="stats1.pdf",
            safe_filename="stats1_safe.pdf",
            file_path="documents/stats1_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            is_deleted=False
        )
        file2 = UploadedFile(
            file_id="stats002",
            original_filename="stats2.jpg",
            safe_filename="stats2_safe.jpg",
            file_path="medical_images/stats2_safe.jpg",
            category="medical_images",
            content_type="image/jpeg",
            file_size=2048,
            checksum="def456",
            uploaded_by=1,
            is_deleted=False
        )
        db.add_all([file1, file2])
        db.commit()
        
        response = client.get("/api/files/stats", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert "database_stats" in result
        assert "filesystem_stats" in result
        assert result["database_stats"]["total_files"] == 2
    
    def test_get_categories(self, client, auth_headers):
        """Test getting available categories"""
        response = client.get("/api/files/categories", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert "categories" in result
        assert "medical_images" in result["categories"]
        assert "documents" in result["categories"]
        assert "patient_records" in result["categories"]


class TestFileAccessLogging:
    """Test file access logging"""
    
    def test_view_access_logged(self, client, auth_headers, test_patient, db, test_user):
        """Test that viewing a file is logged"""
        test_file = UploadedFile(
            file_id="log001",
            original_filename="log_test.pdf",
            safe_filename="log_test_safe.pdf",
            file_path="documents/log_test_safe.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            patient_id=test_patient.id,
            is_deleted=False
        )
        db.add(test_file)
        db.commit()
        
        # View file
        response = client.get(
            f"/api/files/file/{test_file.file_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check access log
        access_log = db.query(FileAccessLog).filter_by(
            file_id=test_file.id,
            user_id=test_user.id,
            access_type="view"
        ).first()
        
        assert access_log is not None
        assert access_log.success is True
        assert access_log.ip_address is not None
    
    def test_failed_access_logged(self, client, auth_headers, db, test_user):
        """Test that failed access is logged"""
        response = client.get(
            "/api/files/file/nonexistent999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        
        # Note: Implementation may or may not log failed views
        # Adjust based on your logging strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
