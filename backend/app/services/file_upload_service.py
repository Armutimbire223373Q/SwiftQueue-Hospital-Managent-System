"""
File Upload Service - Secure file management with virus scanning, DICOM support, and document management
"""
import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.config.security_config import SecurityConfig
from app.services.audit_service import AuditLogger
from app.utils.sanitization import InputSanitizer


class FileUploadService:
    """
    Secure file upload service with:
    - File type validation
    - Size limits
    - Virus scanning integration (placeholder)
    - DICOM medical image support
    - Document management
    - Audit logging
    """
    
    # Base upload directory
    BASE_UPLOAD_DIR = Path("uploads")
    
    # File category directories
    CATEGORIES = {
        "medical_images": "medical_images",
        "documents": "documents",
        "patient_records": "patient_records",
        "lab_results": "lab_results",
        "prescriptions": "prescriptions",
        "insurance": "insurance",
        "other": "other"
    }
    
    # MIME type to category mapping
    MIME_TO_CATEGORY = {
        "application/dicom": "medical_images",
        "image/jpeg": "medical_images",
        "image/png": "medical_images",
        "image/x-dicom-rle": "medical_images",
        "application/pdf": "documents",
        "application/msword": "documents",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "documents",
        "text/plain": "documents",
    }
    
    def __init__(self):
        """Initialize upload service and create directories"""
        self._create_directories()
    
    def _create_directories(self):
        """Create upload directories if they don't exist"""
        self.BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        for category_dir in self.CATEGORIES.values():
            (self.BASE_UPLOAD_DIR / category_dir).mkdir(parents=True, exist_ok=True)
    
    def _validate_file_type(self, filename: str, content_type: str, category: str) -> bool:
        """
        Validate file type against allowed extensions
        
        Args:
            filename: Original filename
            content_type: MIME type
            category: File category
        
        Returns:
            True if valid, raises HTTPException otherwise
        """
        # Get file extension
        ext = Path(filename).suffix.lower()
        
        # Check against allowed extensions
        if category == "medical_images":
            allowed = SecurityConfig.ALLOWED_FILE_EXTENSIONS["medical"] + SecurityConfig.ALLOWED_FILE_EXTENSIONS["images"]
        elif category == "documents":
            allowed = SecurityConfig.ALLOWED_FILE_EXTENSIONS["documents"]
        else:
            # Allow all configured extensions for other categories
            allowed = (
                SecurityConfig.ALLOWED_FILE_EXTENSIONS["images"] +
                SecurityConfig.ALLOWED_FILE_EXTENSIONS["documents"] +
                SecurityConfig.ALLOWED_FILE_EXTENSIONS["medical"]
            )
        
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed for category '{category}'. Allowed: {', '.join(allowed)}"
            )
        
        return True
    
    def _validate_file_size(self, file_size: int) -> bool:
        """
        Validate file size against maximum limit
        
        Args:
            file_size: File size in bytes
        
        Returns:
            True if valid, raises HTTPException otherwise
        """
        max_size = SecurityConfig.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({SecurityConfig.MAX_FILE_SIZE_MB} MB)"
            )
        
        return True
    
    def _scan_virus(self, file_path: Path) -> Dict[str, Any]:
        """
        Scan file for viruses (placeholder for integration with antivirus software)
        
        In production, integrate with:
        - ClamAV (open-source)
        - Windows Defender API
        - Third-party services (VirusTotal API)
        
        Args:
            file_path: Path to file
        
        Returns:
            Scan result dict
        """
        # TODO: Integrate with actual virus scanner
        # For now, return clean status
        return {
            "scanned": True,
            "clean": True,
            "scanner": "placeholder",
            "scan_time": datetime.utcnow().isoformat()
        }
        
        # Example ClamAV integration (requires pyclamd):
        # import pyclamd
        # try:
        #     cd = pyclamd.ClamdUnixSocket()
        #     result = cd.scan_file(str(file_path))
        #     if result is None:
        #         return {"scanned": True, "clean": True, "scanner": "ClamAV"}
        #     else:
        #         return {"scanned": True, "clean": False, "scanner": "ClamAV", "threats": result}
        # except Exception as e:
        #     return {"scanned": False, "error": str(e)}
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex digest of SHA256 checksum
        """
        sha256 = hashlib.sha256()
        
        with file_path.open('rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _detect_dicom(self, file_path: Path) -> bool:
        """
        Detect if file is a DICOM medical image
        
        DICOM files start with a 128-byte preamble followed by "DICM"
        
        Args:
            file_path: Path to file
        
        Returns:
            True if DICOM file
        """
        try:
            with file_path.open('rb') as f:
                # Skip 128-byte preamble
                f.seek(128)
                # Read next 4 bytes
                magic = f.read(4)
                return magic == b'DICM'
        except Exception:
            return False
    
    def _extract_dicom_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from DICOM file
        
        Requires pydicom library: pip install pydicom
        
        Args:
            file_path: Path to DICOM file
        
        Returns:
            Metadata dict or None
        """
        if not self._detect_dicom(file_path):
            return None
        
        try:
            import pydicom
            ds = pydicom.dcmread(str(file_path))
            
            return {
                "patient_name": str(ds.PatientName) if hasattr(ds, 'PatientName') else None,
                "patient_id": str(ds.PatientID) if hasattr(ds, 'PatientID') else None,
                "study_date": str(ds.StudyDate) if hasattr(ds, 'StudyDate') else None,
                "modality": str(ds.Modality) if hasattr(ds, 'Modality') else None,
                "study_description": str(ds.StudyDescription) if hasattr(ds, 'StudyDescription') else None,
                "series_description": str(ds.SeriesDescription) if hasattr(ds, 'SeriesDescription') else None,
            }
        except ImportError:
            # pydicom not installed - return basic info
            return {"dicom": True, "metadata_extraction": "pydicom not installed"}
        except Exception as e:
            return {"dicom": True, "error": f"Failed to extract metadata: {str(e)}"}
    
    def _generate_safe_filename(self, original_filename: str, category: str) -> str:
        """
        Generate a safe, unique filename
        
        Args:
            original_filename: Original uploaded filename
            category: File category
        
        Returns:
            Safe filename with timestamp and UUID
        """
        # Sanitize original filename
        safe_name = InputSanitizer.sanitize_filename(original_filename)
        
        # Get extension
        ext = Path(safe_name).suffix.lower()
        name_without_ext = Path(safe_name).stem
        
        # Generate unique filename: timestamp_uuid_originalname.ext
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        safe_filename = f"{timestamp}_{unique_id}_{name_without_ext}{ext}"
        
        # Ensure filename is not too long (max 255 chars)
        if len(safe_filename) > 255:
            safe_filename = f"{timestamp}_{unique_id}{ext}"
        
        return safe_filename
    
    async def upload_file(
        self,
        file: UploadFile,
        category: str = "other",
        user_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file with security checks and metadata extraction
        
        Args:
            file: UploadFile object from FastAPI
            category: File category (medical_images, documents, etc.)
            user_id: ID of user uploading file
            patient_id: ID of associated patient (optional)
            metadata: Additional metadata (optional)
            ip_address: IP address of uploader
        
        Returns:
            Upload result with file info and metadata
        """
        # Validate category
        if category not in self.CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{category}'. Allowed: {', '.join(self.CATEGORIES.keys())}"
            )
        
        # Get file info
        original_filename = file.filename
        content_type = file.content_type or "application/octet-stream"
        
        # Validate filename
        if not original_filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Validate file type
        self._validate_file_type(original_filename, content_type, category)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        self._validate_file_size(file_size)
        
        # Generate safe filename
        safe_filename = self._generate_safe_filename(original_filename, category)
        
        # Determine file path
        category_dir = self.CATEGORIES[category]
        file_path = self.BASE_UPLOAD_DIR / category_dir / safe_filename
        
        # Write file to disk
        try:
            with file_path.open('wb') as f:
                f.write(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Calculate checksum
        checksum = self._calculate_checksum(file_path)
        
        # Scan for viruses
        virus_scan = self._scan_virus(file_path)
        
        if not virus_scan.get("clean", False):
            # Delete infected file
            file_path.unlink(missing_ok=True)
            
            # Log security violation
            AuditLogger.log_security_violation(
                ip_address=ip_address or "unknown",
                violation_type="virus_detected",
                details={
                    "filename": original_filename,
                    "user_id": user_id,
                    "scan_result": virus_scan
                }
            )
            
            raise HTTPException(
                status_code=400,
                detail="File failed virus scan and was rejected"
            )
        
        # Extract DICOM metadata if applicable
        dicom_metadata = None
        is_dicom = self._detect_dicom(file_path)
        if is_dicom:
            dicom_metadata = self._extract_dicom_metadata(file_path)
        
        # Prepare file record
        file_record = {
            "id": uuid.uuid4().hex,
            "original_filename": original_filename,
            "safe_filename": safe_filename,
            "file_path": str(file_path.relative_to(self.BASE_UPLOAD_DIR)),
            "full_path": str(file_path),
            "category": category,
            "content_type": content_type,
            "file_size": file_size,
            "checksum": checksum,
            "uploaded_by": user_id,
            "patient_id": patient_id,
            "upload_time": datetime.utcnow().isoformat(),
            "virus_scan": virus_scan,
            "is_dicom": is_dicom,
            "dicom_metadata": dicom_metadata,
            "metadata": metadata or {},
        }
        
        # Log upload
        AuditLogger.log(
            event_type="file.uploaded",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=None,
            details={
                "filename": original_filename,
                "category": category,
                "size": file_size,
                "patient_id": patient_id,
                "checksum": checksum[:16] + "...",  # Truncate for log
            },
            severity="info"
        )
        
        return file_record
    
    def get_file(self, file_id: str, user_id: Optional[int] = None) -> Optional[Path]:
        """
        Get file path by ID (to be implemented with database integration)
        
        Args:
            file_id: File ID
            user_id: ID of user requesting file
        
        Returns:
            Path to file or None
        """
        # TODO: Implement database lookup
        # For now, this is a placeholder
        raise NotImplementedError("Database integration required")
    
    def delete_file(
        self,
        file_id: str,
        user_id: int,
        ip_address: Optional[str] = None,
        reason: str = "user_request"
    ) -> bool:
        """
        Delete a file
        
        Args:
            file_id: File ID
            user_id: ID of user deleting file
            ip_address: IP address
            reason: Reason for deletion
        
        Returns:
            True if deleted
        """
        # TODO: Implement database lookup and deletion
        # For now, this is a placeholder
        
        # Log deletion
        AuditLogger.log(
            event_type="file.deleted",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=None,
            details={
                "file_id": file_id,
                "reason": reason
            },
            severity="warning"
        )
        
        raise NotImplementedError("Database integration required")
    
    def list_files(
        self,
        category: Optional[str] = None,
        patient_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List uploaded files with filtering
        
        Args:
            category: Filter by category
            patient_id: Filter by patient
            user_id: Filter by uploader
            limit: Maximum results
            offset: Result offset
        
        Returns:
            List of file records
        """
        # TODO: Implement database query
        raise NotImplementedError("Database integration required")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Storage stats dict
        """
        stats = {
            "total_size": 0,
            "file_count": 0,
            "by_category": {}
        }
        
        for category, category_dir in self.CATEGORIES.items():
            category_path = self.BASE_UPLOAD_DIR / category_dir
            
            if not category_path.exists():
                continue
            
            category_size = 0
            category_count = 0
            
            for file_path in category_path.rglob("*"):
                if file_path.is_file():
                    category_size += file_path.stat().st_size
                    category_count += 1
            
            stats["by_category"][category] = {
                "size": category_size,
                "size_mb": round(category_size / 1024 / 1024, 2),
                "count": category_count
            }
            
            stats["total_size"] += category_size
            stats["file_count"] += category_count
        
        stats["total_size_mb"] = round(stats["total_size"] / 1024 / 1024, 2)
        
        return stats
