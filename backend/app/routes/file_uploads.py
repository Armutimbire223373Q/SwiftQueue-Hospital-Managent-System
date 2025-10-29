"""
Enhanced File Upload Routes - Secure file upload with database integration
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User
from app.models.workflow_models import Patient
from app.models.file_models import UploadedFile, FileAccessLog
from app.services.file_upload_service import FileUploadService
from app.services.audit_service import AuditLogger
from app.utils.sanitization import InputSanitizer

router = APIRouter()
file_service = FileUploadService()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("other"),
    patient_id: Optional[int] = Form(None),
    metadata: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file with security checks
    
    Args:
        file: File to upload
        category: File category (medical_images, documents, patient_records, etc.)
        patient_id: Associated patient ID (optional)
        metadata: Additional metadata as JSON string (optional)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Upload result with file info
    """
    # Parse metadata
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
            # Sanitize metadata
            metadata_dict = InputSanitizer.sanitize_dict(metadata_dict, allow_html=False)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    
    # Upload file using service
    try:
        client_ip = request.client.host if request.client else "unknown"
        
        upload_result = await file_service.upload_file(
            file=file,
            category=category,
            user_id=current_user.id,
            patient_id=patient_id,
            metadata=metadata_dict,
            ip_address=client_ip
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Save to database
    try:
        db_file = UploadedFile(
            file_id=upload_result["id"],
            original_filename=upload_result["original_filename"],
            safe_filename=upload_result["safe_filename"],
            file_path=upload_result["file_path"],
            category=upload_result["category"],
            content_type=upload_result["content_type"],
            file_size=upload_result["file_size"],
            checksum=upload_result["checksum"],
            uploaded_by=upload_result["uploaded_by"],
            patient_id=upload_result["patient_id"],
            virus_scanned=upload_result["virus_scan"].get("scanned", False),
            virus_scan_clean=upload_result["virus_scan"].get("clean", False),
            virus_scanner=upload_result["virus_scan"].get("scanner"),
            is_dicom=upload_result["is_dicom"],
            metadata_json=json.dumps(upload_result["metadata"]) if upload_result["metadata"] else None,
        )
        
        # Add DICOM metadata if available
        if upload_result["dicom_metadata"]:
            dicom = upload_result["dicom_metadata"]
            db_file.dicom_patient_name = dicom.get("patient_name")
            db_file.dicom_patient_id = dicom.get("patient_id")
            db_file.dicom_study_date = dicom.get("study_date")
            db_file.dicom_modality = dicom.get("modality")
            db_file.dicom_study_description = dicom.get("study_description")
            db_file.dicom_series_description = dicom.get("series_description")
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": db_file.to_dict()
        }
    
    except Exception as e:
        db.rollback()
        # Clean up uploaded file
        try:
            Path(upload_result["full_path"]).unlink(missing_ok=True)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to save file record: {str(e)}")


@router.get("/list")
def list_files(
    category: Optional[str] = Query(None),
    patient_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List uploaded files with filtering
    
    Args:
        category: Filter by category
        patient_id: Filter by patient ID
        limit: Maximum results (1-100)
        offset: Result offset
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of files
    """
    query = db.query(UploadedFile).filter(UploadedFile.is_deleted == False)
    
    if category:
        query = query.filter(UploadedFile.category == category)
    
    if patient_id:
        query = query.filter(UploadedFile.patient_id == patient_id)
    
    # Order by upload time (newest first)
    query = query.order_by(UploadedFile.upload_time.desc())
    
    # Apply pagination
    total = query.count()
    files = query.offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "files": [f.to_dict() for f in files]
    }


@router.get("/file/{file_id}")
def get_file_info(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file information by ID
    
    Args:
        file_id: File ID (UUID hex)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        File information
    """
    file_record = db.query(UploadedFile).filter(
        UploadedFile.file_id == file_id,
        UploadedFile.is_deleted == False
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Log access
    client_ip = request.client.host if request.client else "unknown"
    
    access_log = FileAccessLog(
        file_id=file_record.id,
        user_id=current_user.id,
        access_type="view",
        ip_address="127.0.0.1",  # TODO: Get real IP
        success=True
    )
    db.add(access_log)
    db.commit()
    
    return {
        "success": True,
        "file": file_record.to_dict()
    }


@router.get("/download/{file_id}")
def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a file
    
    Args:
        file_id: File ID (UUID hex)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        File download response
    """
    file_record = db.query(UploadedFile).filter(
        UploadedFile.file_id == file_id,
        UploadedFile.is_deleted == False
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check file exists on disk
    file_path = file_service.BASE_UPLOAD_DIR / file_record.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Log access
    client_ip = request.client.host if request.client else "unknown"
    
    access_log = FileAccessLog(
        file_id=file_record.id,
        user_id=current_user.id,
        access_type="download",
        ip_address=client_ip,
        success=True
    )
    db.add(access_log)
    db.commit()
    
    # Log download
    AuditLogger.log(
        event_type="file.downloaded",
        user_id=current_user.id,
        ip_address="127.0.0.1",
        user_agent=None,
        details={
            "file_id": file_id,
            "filename": file_record.original_filename,
            "category": file_record.category
        },
        severity="info"
    )
    
    return FileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type=file_record.content_type
    )


@router.delete("/file/{file_id}")
def delete_file(
    file_id: str,
    reason: str = Query("user_request", max_length=255),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file (soft delete)
    
    Args:
        file_id: File ID (UUID hex)
        reason: Reason for deletion
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Deletion confirmation
    """
    file_record = db.query(UploadedFile).filter(
        UploadedFile.file_id == file_id,
        UploadedFile.is_deleted == False
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions (only uploader or admin can delete)
    if file_record.uploaded_by != current_user.id and current_user.role != "admin":
        # Log unauthorized attempt
        access_log = FileAccessLog(
            file_id=file_record.id,
            user_id=current_user.id,
            access_type="delete",
            ip_address="127.0.0.1",
            success=False,
            failure_reason="Permission denied"
        )
        db.add(access_log)
        db.commit()
        
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Soft delete
    from datetime import datetime
    file_record.is_deleted = True
    file_record.deleted_at = datetime.utcnow()
    file_record.deleted_by = current_user.id
    file_record.deletion_reason = InputSanitizer.sanitize_string(reason)
    
    # Log access
    access_log = FileAccessLog(
        file_id=file_record.id,
        user_id=current_user.id,
        access_type="delete",
        ip_address="127.0.0.1",
        success=True
    )
    db.add(access_log)
    
    db.commit()
    
    # Log deletion
    AuditLogger.log(
        event_type="file.deleted",
        user_id=current_user.id,
        ip_address="127.0.0.1",
        user_agent=None,
        details={
            "file_id": file_id,
            "filename": file_record.original_filename,
            "reason": reason
        },
        severity="warning"
    )
    
    return {
        "success": True,
        "message": "File deleted successfully",
        "file_id": file_id
    }


@router.get("/stats")
def get_storage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get storage statistics
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Storage statistics
    """
    # Get filesystem stats
    fs_stats = file_service.get_storage_stats()
    
    # Get database stats
    total_files = db.query(UploadedFile).filter(UploadedFile.is_deleted == False).count()
    total_deleted = db.query(UploadedFile).filter(UploadedFile.is_deleted == True).count()
    
    # Get stats by category
    from sqlalchemy import func
    category_stats = db.query(
        UploadedFile.category,
        func.count(UploadedFile.id).label("count"),
        func.sum(UploadedFile.file_size).label("total_size")
    ).filter(
        UploadedFile.is_deleted == False
    ).group_by(
        UploadedFile.category
    ).all()
    
    db_by_category = {}
    for cat, count, total_size in category_stats:
        db_by_category[cat] = {
            "count": count,
            "size": total_size or 0,
            "size_mb": round((total_size or 0) / 1024 / 1024, 2)
        }
    
    return {
        "success": True,
        "stats": {
            "filesystem": fs_stats,
            "database": {
                "total_files": total_files,
                "total_deleted": total_deleted,
                "by_category": db_by_category
            }
        }
    }


@router.get("/categories")
def get_categories(current_user: User = Depends(get_current_user)):
    """
    Get available file categories
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        List of categories
    """
    return {
        "success": True,
        "categories": list(file_service.CATEGORIES.keys())
    }
