"""
Patient Portal API Routes
Handles patient-staff messaging, document management, preferences, and lab results
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import shutil

from app.database import get_db
from app.models.models import (
    PatientMessage, PatientDocument, PatientPreference, 
    LabResult, User
)
from app.routes.auth import get_current_user

router = APIRouter(prefix="/patient-portal", tags=["Patient Portal"])

UPLOAD_DIR = "uploads/patient_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==================== Pydantic Models ====================

class MessageCreate(BaseModel):
    subject: str
    message: str
    message_type: str = "general"
    priority: str = "normal"
    staff_id: Optional[int] = None


class MessageReply(BaseModel):
    message: str


class PatientPreferenceUpdate(BaseModel):
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    notification_push: Optional[bool] = None
    appointment_reminder_days: Optional[int] = None
    preferred_language: Optional[str] = None
    preferred_communication: Optional[str] = None
    share_medical_history: Optional[bool] = None
    allow_marketing: Optional[bool] = None


class LabResultCreate(BaseModel):
    patient_id: int
    test_name: str
    test_category: Optional[str] = None
    result_value: Optional[str] = None
    normal_range: Optional[str] = None
    unit: Optional[str] = None
    abnormal_flag: bool = False
    notes: Optional[str] = None
    test_date: Optional[datetime] = None
    is_patient_visible: bool = True


class DocumentMetadata(BaseModel):
    title: str
    document_type: str
    description: Optional[str] = None
    is_patient_visible: bool = True


# ==================== Messaging ====================

@router.post("/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message between patient and staff
    
    - Patients can send to any staff
    - Staff can send to any patient
    """
    # Determine sender and recipient
    if current_user.role == "patient":
        patient_id = current_user.id
        staff_id = message_data.staff_id
        is_patient_sender = True
        
        if not staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Staff ID required when patient sends message"
            )
    else:
        # Staff sending to patient - need patient_id in the message
        patient_id = message_data.staff_id  # Reusing field for patient_id
        staff_id = current_user.id
        is_patient_sender = False
    
    message = PatientMessage(
        patient_id=patient_id,
        staff_id=staff_id,
        subject=message_data.subject,
        message=message_data.message,
        message_type=message_data.message_type,
        priority=message_data.priority,
        is_patient_sender=is_patient_sender
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "message_id": message.id,
        "status": "sent",
        "created_at": message.created_at
    }


@router.get("/messages")
async def list_messages(
    status_filter: Optional[str] = Query(None, alias="status"),
    message_type: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List messages for current user
    
    - Patients see messages where they are the patient
    - Staff see messages where they are the staff member
    """
    query = db.query(PatientMessage)
    
    # Filter by role
    if current_user.role == "patient":
        query = query.filter(PatientMessage.patient_id == current_user.id)
    else:
        query = query.filter(PatientMessage.staff_id == current_user.id)
    
    # Apply additional filters
    if status_filter:
        query = query.filter(PatientMessage.status == status_filter)
    
    if message_type:
        query = query.filter(PatientMessage.message_type == message_type)
    
    if unread_only:
        query = query.filter(PatientMessage.status == "unread")
    
    messages = query.order_by(PatientMessage.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "unread_count": query.filter(PatientMessage.status == "unread").count(),
        "messages": messages
    }


@router.get("/messages/{message_id}")
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message details and mark as read"""
    message = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    # Check authorization
    is_authorized = (
        (current_user.role == "patient" and message.patient_id == current_user.id) or
        (current_user.role != "patient" and message.staff_id == current_user.id) or
        current_user.role == "admin"
    )
    
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Mark as read if unread
    if message.status == "unread" and message.read_at is None:
        message.status = "read"
        message.read_at = datetime.utcnow()
        db.commit()
    
    # Get thread (replies)
    replies = db.query(PatientMessage).filter(
        PatientMessage.parent_message_id == message_id
    ).order_by(PatientMessage.created_at.asc()).all()
    
    return {
        "message": message,
        "replies": replies,
        "patient": db.query(User).filter(User.id == message.patient_id).first(),
        "staff": db.query(User).filter(User.id == message.staff_id).first() if message.staff_id else None
    }


@router.post("/messages/{message_id}/reply", status_code=status.HTTP_201_CREATED)
async def reply_to_message(
    message_id: int,
    reply_data: MessageReply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reply to a message"""
    parent = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()
    
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Determine reply details based on user role
    if current_user.role == "patient":
        is_patient_sender = True
        patient_id = current_user.id
        staff_id = parent.staff_id
    else:
        is_patient_sender = False
        patient_id = parent.patient_id
        staff_id = current_user.id
    
    reply = PatientMessage(
        patient_id=patient_id,
        staff_id=staff_id,
        subject=f"Re: {parent.subject}",
        message=reply_data.message,
        message_type=parent.message_type,
        priority=parent.priority,
        is_patient_sender=is_patient_sender,
        parent_message_id=message_id
    )
    
    db.add(reply)
    
    # Update parent status
    parent.status = "replied"
    
    db.commit()
    db.refresh(reply)
    
    return reply


@router.put("/messages/{message_id}/close")
async def close_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a message thread (staff only)"""
    if current_user.role not in ["staff", "nurse", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    message = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    message.status = "closed"
    db.commit()
    
    return {"message": "Message thread closed"}


# ==================== Documents ====================

@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    patient_id: int = Query(...),
    document_type: str = Query(...),
    title: str = Query(...),
    description: Optional[str] = Query(None),
    is_patient_visible: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a patient document
    
    - Staff can upload for any patient
    - Patients can upload their own documents
    """
    # Check authorization
    if current_user.role == "patient" and current_user.id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Save file
    patient_dir = os.path.join(UPLOAD_DIR, str(patient_id))
    os.makedirs(patient_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(patient_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create document record
    document = PatientDocument(
        patient_id=patient_id,
        document_type=document_type,
        title=title,
        description=description,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        is_patient_visible=is_patient_visible
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/documents")
async def list_documents(
    patient_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List patient documents
    
    - Patients see only their visible documents
    - Staff see all documents based on patient_id filter
    """
    query = db.query(PatientDocument)
    
    # Role-based filtering
    if current_user.role == "patient":
        query = query.filter(
            PatientDocument.patient_id == current_user.id,
            PatientDocument.is_patient_visible == True
        )
    else:
        if patient_id:
            query = query.filter(PatientDocument.patient_id == patient_id)
    
    if document_type:
        query = query.filter(PatientDocument.document_type == document_type)
    
    documents = query.order_by(PatientDocument.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "documents": documents
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = db.query(PatientDocument).filter(PatientDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Check authorization
    is_authorized = (
        (current_user.role == "patient" and document.patient_id == current_user.id and document.is_patient_visible) or
        current_user.role in ["staff", "nurse", "admin"]
    )
    
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return document


# ==================== Preferences ====================

@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient preferences"""
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access preferences"
        )
    
    prefs = db.query(PatientPreference).filter(
        PatientPreference.patient_id == current_user.id
    ).first()
    
    # Create default preferences if none exist
    if not prefs:
        prefs = PatientPreference(patient_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


@router.put("/preferences")
async def update_preferences(
    prefs_data: PatientPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update patient preferences"""
    if current_user.role != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    prefs = db.query(PatientPreference).filter(
        PatientPreference.patient_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = PatientPreference(patient_id=current_user.id)
        db.add(prefs)
    
    # Update fields
    for field, value in prefs_data.dict(exclude_unset=True).items():
        setattr(prefs, field, value)
    
    db.commit()
    db.refresh(prefs)
    
    return prefs


# ==================== Lab Results ====================

@router.post("/lab-results", status_code=status.HTTP_201_CREATED)
async def create_lab_result(
    result_data: LabResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a lab result (staff only)"""
    if current_user.role not in ["staff", "nurse", "lab_technician", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    result = LabResult(
        **result_data.dict(),
        ordered_by=current_user.id
    )
    
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return result


@router.get("/lab-results")
async def list_lab_results(
    patient_id: Optional[int] = Query(None),
    test_category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    abnormal_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List lab results
    
    - Patients see only their own visible results
    - Staff can filter by patient_id
    """
    query = db.query(LabResult)
    
    # Role-based filtering
    if current_user.role == "patient":
        query = query.filter(
            LabResult.patient_id == current_user.id,
            LabResult.is_patient_visible == True
        )
    else:
        if patient_id:
            query = query.filter(LabResult.patient_id == patient_id)
    
    if test_category:
        query = query.filter(LabResult.test_category == test_category)
    
    if status_filter:
        query = query.filter(LabResult.status == status_filter)
    
    if abnormal_only:
        query = query.filter(LabResult.abnormal_flag == True)
    
    results = query.order_by(LabResult.result_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "abnormal_count": query.filter(LabResult.abnormal_flag == True).count(),
        "results": results
    }


@router.get("/lab-results/{result_id}")
async def get_lab_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed lab result"""
    result = db.query(LabResult).filter(LabResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Check authorization
    is_authorized = (
        (current_user.role == "patient" and result.patient_id == current_user.id and result.is_patient_visible) or
        current_user.role in ["staff", "nurse", "lab_technician", "admin"]
    )
    
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return result


@router.put("/lab-results/{result_id}")
async def update_lab_result(
    result_id: int,
    result_value: Optional[str] = None,
    abnormal_flag: Optional[bool] = None,
    notes: Optional[str] = None,
    status_update: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lab result (lab technician/doctor only)"""
    if current_user.role not in ["staff", "lab_technician", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    result = db.query(LabResult).filter(LabResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if result_value is not None:
        result.result_value = result_value
        result.result_date = datetime.utcnow()
        result.performed_by = current_user.id
    
    if abnormal_flag is not None:
        result.abnormal_flag = abnormal_flag
    
    if notes is not None:
        result.notes = notes
    
    if status_update is not None:
        result.status = status_update
    
    db.commit()
    db.refresh(result)
    
    return result


# ==================== Dashboard/Summary ====================

@router.get("/dashboard")
async def get_patient_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient dashboard summary"""
    if current_user.role != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Unread messages
    unread_messages = db.query(PatientMessage).filter(
        PatientMessage.patient_id == current_user.id,
        PatientMessage.status == "unread"
    ).count()
    
    # Recent documents
    recent_docs = db.query(PatientDocument).filter(
        PatientDocument.patient_id == current_user.id,
        PatientDocument.is_patient_visible == True
    ).order_by(PatientDocument.uploaded_at.desc()).limit(5).all()
    
    # Recent lab results
    recent_labs = db.query(LabResult).filter(
        LabResult.patient_id == current_user.id,
        LabResult.is_patient_visible == True
    ).order_by(LabResult.result_date.desc()).limit(5).all()
    
    # Abnormal results
    abnormal_results = db.query(LabResult).filter(
        LabResult.patient_id == current_user.id,
        LabResult.abnormal_flag == True,
        LabResult.is_patient_visible == True
    ).count()
    
    # Preferences
    prefs = db.query(PatientPreference).filter(
        PatientPreference.patient_id == current_user.id
    ).first()
    
    return {
        "unread_messages": unread_messages,
        "recent_documents": recent_docs,
        "recent_lab_results": recent_labs,
        "abnormal_results_count": abnormal_results,
        "preferences": prefs,
        "total_documents": db.query(PatientDocument).filter(
            PatientDocument.patient_id == current_user.id,
            PatientDocument.is_patient_visible == True
        ).count()
    }
