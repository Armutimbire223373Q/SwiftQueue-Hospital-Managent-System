"""
File Upload Models - Database models for file management
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class UploadedFile(Base):
    """
    Uploaded file record
    """
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(32), unique=True, index=True, nullable=False)  # UUID hex
    
    # File information
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path from BASE_UPLOAD_DIR
    category = Column(String(50), nullable=False, index=True)  # medical_images, documents, etc.
    content_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    checksum = Column(String(64), nullable=False)  # SHA256 hex digest
    
    # Upload metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    upload_ip = Column(String(45), nullable=True)  # IPv6 max length
    
    # Security
    virus_scanned = Column(Boolean, default=False, nullable=False)
    virus_scan_clean = Column(Boolean, default=True, nullable=False)
    virus_scan_time = Column(DateTime, nullable=True)
    virus_scanner = Column(String(50), nullable=True)
    
    # DICOM metadata (for medical images)
    is_dicom = Column(Boolean, default=False, nullable=False)
    dicom_patient_name = Column(String(255), nullable=True)
    dicom_patient_id = Column(String(100), nullable=True)
    dicom_study_date = Column(String(20), nullable=True)
    dicom_modality = Column(String(50), nullable=True)
    dicom_study_description = Column(Text, nullable=True)
    dicom_series_description = Column(Text, nullable=True)
    
    # Additional metadata (JSON stored as text)
    metadata_json = Column(Text, nullable=True)
    
    # Status
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deletion_reason = Column(String(255), nullable=True)
    
    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by], backref="uploaded_files")
    patient = relationship("Patient", backref="uploaded_files")
    deleter = relationship("User", foreign_keys=[deleted_by])
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.original_filename}, category={self.category})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "original_filename": self.original_filename,
            "safe_filename": self.safe_filename,
            "file_path": self.file_path,
            "category": self.category,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "file_size_mb": round(self.file_size / 1024 / 1024, 2),
            "checksum": self.checksum,
            "uploaded_by": self.uploaded_by,
            "patient_id": self.patient_id,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "virus_scanned": self.virus_scanned,
            "virus_scan_clean": self.virus_scan_clean,
            "is_dicom": self.is_dicom,
            "dicom_metadata": {
                "patient_name": self.dicom_patient_name,
                "patient_id": self.dicom_patient_id,
                "study_date": self.dicom_study_date,
                "modality": self.dicom_modality,
                "study_description": self.dicom_study_description,
                "series_description": self.dicom_series_description,
            } if self.is_dicom else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }


class FileAccessLog(Base):
    """
    Log of file access attempts (for HIPAA compliance)
    """
    __tablename__ = "file_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    access_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    access_type = Column(String(20), nullable=False)  # view, download, delete
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    
    # Relationships
    file = relationship("UploadedFile", backref="access_logs")
    user = relationship("User", backref="file_accesses")
    
    def __repr__(self):
        return f"<FileAccessLog(file_id={self.file_id}, user_id={self.user_id}, type={self.access_type})>"
