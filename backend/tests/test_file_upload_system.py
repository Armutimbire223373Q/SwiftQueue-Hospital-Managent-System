"""
File Upload System Tests
Comprehensive tests for file upload, storage, and management
"""
import pytest
import io
from pathlib import Path
from fastapi.testclient import TestClient
from app.services.file_upload_service import FileUploadService


class TestFileUploadService:
    """Test file upload service functionality"""
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = FileUploadService()
        
        # Check base directory exists
        assert service.BASE_UPLOAD_DIR.exists()
        assert service.BASE_UPLOAD_DIR.is_dir()
        
        # Check all category directories exist
        for category_dir in service.CATEGORIES.values():
            category_path = service.BASE_UPLOAD_DIR / category_dir
            assert category_path.exists()
            assert category_path.is_dir()
    
    def test_validate_file_type_valid(self):
        """Test file type validation with valid files"""
        service = FileUploadService()
        
        # Test valid file types
        valid_files = [
            ("document.pdf", "application/pdf", "documents"),
            ("image.jpg", "image/jpeg", "medical_images"),
            ("scan.dcm", "application/dicom", "medical_images"),
            ("report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "documents"),
        ]
        
        for filename, content_type, category in valid_files:
            result = service._validate_file_type(filename, content_type, category)
            assert result is True
    
    def test_validate_file_type_invalid(self):
        """Test file type validation with invalid files"""
        from fastapi import HTTPException
        service = FileUploadService()
        
        # Test invalid file types
        with pytest.raises(HTTPException) as exc_info:
            service._validate_file_type("script.exe", "application/x-msdownload", "documents")
        assert exc_info.value.status_code == 400
        
        with pytest.raises(HTTPException) as exc_info:
            service._validate_file_type("video.mp4", "video/mp4", "medical_images")
        assert exc_info.value.status_code == 400
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid sizes"""
        service = FileUploadService()
        
        # Test valid file sizes (1 MB, 5 MB, 9 MB)
        valid_sizes = [
            1 * 1024 * 1024,
            5 * 1024 * 1024,
            9 * 1024 * 1024,
        ]
        
        for size in valid_sizes:
            result = service._validate_file_size(size)
            assert result is True
    
    def test_validate_file_size_invalid(self):
        """Test file size validation with invalid sizes"""
        from fastapi import HTTPException
        service = FileUploadService()
        
        # Test file size over limit (15 MB, assuming limit is 10 MB)
        with pytest.raises(HTTPException) as exc_info:
            service._validate_file_size(15 * 1024 * 1024)
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail
    
    def test_scan_virus(self):
        """Test virus scanning (placeholder)"""
        service = FileUploadService()
        
        # Create a temporary file
        test_file = service.BASE_UPLOAD_DIR / "test.txt"
        test_file.write_text("This is a test file")
        
        try:
            result = service._scan_virus(test_file)
            
            assert "scanned" in result
            assert "clean" in result
            assert result["scanned"] is True
            assert result["clean"] is True  # Placeholder always returns clean
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_calculate_checksum(self):
        """Test checksum calculation"""
        service = FileUploadService()
        
        # Create a test file with known content
        test_file = service.BASE_UPLOAD_DIR / "test_checksum.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)
        
        try:
            checksum = service._calculate_checksum(test_file)
            
            # Checksum should be a 64-character hex string (SHA256)
            assert len(checksum) == 64
            assert all(c in "0123456789abcdef" for c in checksum)
            
            # Calculate expected checksum
            import hashlib
            expected = hashlib.sha256(test_content).hexdigest()
            assert checksum == expected
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_detect_dicom_non_dicom(self):
        """Test DICOM detection with non-DICOM file"""
        service = FileUploadService()
        
        # Create a non-DICOM file
        test_file = service.BASE_UPLOAD_DIR / "test.txt"
        test_file.write_text("This is not a DICOM file")
        
        try:
            is_dicom = service._detect_dicom(test_file)
            assert is_dicom is False
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_detect_dicom_valid(self):
        """Test DICOM detection with valid DICOM file"""
        service = FileUploadService()
        
        # Create a mock DICOM file (128-byte preamble + "DICM")
        test_file = service.BASE_UPLOAD_DIR / "test.dcm"
        with test_file.open('wb') as f:
            f.write(b'\x00' * 128)  # Preamble
            f.write(b'DICM')  # Magic number
            f.write(b'\x00' * 100)  # Additional data
        
        try:
            is_dicom = service._detect_dicom(test_file)
            assert is_dicom is True
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_generate_safe_filename(self):
        """Test safe filename generation"""
        service = FileUploadService()
        
        # Test with various filenames
        test_cases = [
            "document.pdf",
            "my file with spaces.docx",
            "../../../etc/passwd",
            "file<script>alert()</script>.pdf",
        ]
        
        for original in test_cases:
            safe = service._generate_safe_filename(original, "documents")
            
            # Check safe filename properties
            assert len(safe) <= 255  # Not too long
            assert ".." not in safe  # No path traversal
            assert "/" not in safe  # No path separators
            assert "\\" not in safe  # No Windows path separators
            assert "<" not in safe  # No HTML/script tags
            assert ">" not in safe
            
            # Should contain timestamp and UUID
            assert "_" in safe
    
    def test_get_storage_stats(self):
        """Test storage statistics"""
        service = FileUploadService()
        
        # Create some test files
        test_files = [
            (service.BASE_UPLOAD_DIR / "documents" / "test1.pdf", b"Test content 1"),
            (service.BASE_UPLOAD_DIR / "medical_images" / "test2.jpg", b"Test content 2 - longer"),
        ]
        
        try:
            for file_path, content in test_files:
                file_path.write_bytes(content)
            
            stats = service.get_storage_stats()
            
            assert "total_size" in stats
            assert "file_count" in stats
            assert "by_category" in stats
            assert "total_size_mb" in stats
            
            # Should have counted our test files
            assert stats["file_count"] >= 2
            assert stats["total_size"] > 0
        finally:
            for file_path, _ in test_files:
                file_path.unlink(missing_ok=True)


class TestFileUploadModels:
    """Test file upload database models"""
    
    def test_uploaded_file_model_creation(self):
        """Test UploadedFile model creation"""
        from app.models.file_models import UploadedFile
        from datetime import datetime
        
        file_record = UploadedFile(
            file_id="test123abc",
            original_filename="test.pdf",
            safe_filename="20251023_abc123_test.pdf",
            file_path="documents/20251023_abc123_test.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123def456",
            uploaded_by=1,
            patient_id=1,
            virus_scanned=True,
            virus_scan_clean=True,
            is_dicom=False
        )
        
        assert file_record.file_id == "test123abc"
        assert file_record.original_filename == "test.pdf"
        assert file_record.category == "documents"
        assert file_record.virus_scanned is True
        assert file_record.is_dicom is False
    
    def test_uploaded_file_to_dict(self):
        """Test UploadedFile to_dict method"""
        from app.models.file_models import UploadedFile
        from datetime import datetime
        
        file_record = UploadedFile(
            file_id="test123",
            original_filename="test.pdf",
            safe_filename="20251023_test.pdf",
            file_path="documents/20251023_test.pdf",
            category="documents",
            content_type="application/pdf",
            file_size=1024,
            checksum="abc123",
            uploaded_by=1,
            patient_id=1,
            upload_time=datetime.utcnow(),
            virus_scanned=True,
            virus_scan_clean=True,
            is_dicom=False,
            is_deleted=False
        )
        
        result = file_record.to_dict()
        
        assert isinstance(result, dict)
        assert result["file_id"] == "test123"
        assert result["original_filename"] == "test.pdf"
        assert result["category"] == "documents"
        assert result["file_size_mb"] == round(1024 / 1024 / 1024, 2)
        assert result["is_deleted"] is False
    
    def test_file_access_log_model(self):
        """Test FileAccessLog model creation"""
        from app.models.file_models import FileAccessLog
        from datetime import datetime
        
        access_log = FileAccessLog(
            file_id=1,
            user_id=1,
            access_type="download",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=True
        )
        
        assert access_log.file_id == 1
        assert access_log.user_id == 1
        assert access_log.access_type == "download"
        assert access_log.success is True


class TestFileUploadIntegration:
    """Integration tests for file upload system"""
    
    def test_upload_file_service_integration(self):
        """Test complete file upload flow"""
        from unittest.mock import Mock
        import asyncio
        
        service = FileUploadService()
        
        # Create a mock UploadFile
        file_content = b"This is a test PDF document"
        mock_file = Mock()
        mock_file.filename = "test_document.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.file = io.BytesIO(file_content)
        
        # Mock the read method
        async def mock_read():
            return file_content
        mock_file.read = mock_read
        
        # Upload file
        async def upload():
            return await service.upload_file(
                file=mock_file,
                category="documents",
                user_id=1,
                patient_id=None,
                metadata={"description": "Test upload"},
                ip_address="127.0.0.1"
            )
        
        result = asyncio.run(upload())
        
        try:
            # Verify result
            assert result["original_filename"] == "test_document.pdf"
            assert result["category"] == "documents"
            assert result["file_size"] == len(file_content)
            assert result["uploaded_by"] == 1
            assert result["virus_scan"]["scanned"] is True
            assert result["virus_scan"]["clean"] is True
            assert result["is_dicom"] is False
            
            # Verify file was saved
            file_path = Path(result["full_path"])
            assert file_path.exists()
            assert file_path.read_bytes() == file_content
        finally:
            # Cleanup
            try:
                Path(result["full_path"]).unlink(missing_ok=True)
            except:
                pass


# Fixtures
@pytest.fixture
def test_service():
    """Create test service"""
    return FileUploadService()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
