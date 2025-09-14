from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.models import QueueEntry, User, Service
from datetime import datetime
import random

router = APIRouter()

class PatientDetails(BaseModel):
    name: str
    email: str
    phone: str
    dateOfBirth: str
    symptoms: str = ""
    priority: str = "medium"

class QueueJoinRequest(BaseModel):
    service_id: int
    patient_details: PatientDetails

@router.post("/join")
async def join_queue(
    request: QueueJoinRequest,
    db: Session = Depends(get_db)
):
    # Create or update user
    user = db.query(User).filter(User.email == request.patient_details.email).first()
    if not user:
        user = User(
            name=request.patient_details.name,
            email=request.patient_details.email,
            phone=request.patient_details.phone,
            date_of_birth=datetime.strptime(request.patient_details.dateOfBirth, "%Y-%m-%d")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Get service
    service = db.query(Service).filter(Service.id == request.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Calculate queue number
    last_queue = db.query(QueueEntry).order_by(QueueEntry.queue_number.desc()).first()
    new_queue_number = (last_queue.queue_number + 1) if last_queue else 1

    # Create queue entry
    queue_entry = QueueEntry(
        patient_id=user.id,
        service_id=request.service_id,
        queue_number=new_queue_number,
        status="waiting",
        priority=request.patient_details.priority,
        estimated_wait_time=service.current_wait_time,
        ai_predicted_wait=predict_wait_time(service, request.patient_details.priority)
    )
    db.add(queue_entry)

    # Update service queue length
    service.queue_length += 1
    db.commit()
    db.refresh(queue_entry)

    return {
        "queue_number": new_queue_number,
        "estimated_wait": queue_entry.estimated_wait_time,
        "ai_predicted_wait": queue_entry.ai_predicted_wait
    }

@router.get("/status/{queue_number}")
async def get_queue_status(queue_number: int, db: Session = Depends(get_db)):
    queue_entry = db.query(QueueEntry).filter(QueueEntry.queue_number == queue_number).first()
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    return {
        "status": queue_entry.status,
        "position": get_position(queue_entry, db),
        "estimated_wait": queue_entry.ai_predicted_wait
    }

def predict_wait_time(service: Service, priority: str) -> int:
    # TODO: Implement actual AI prediction
    # For now, using a simple heuristic
    base_time = service.current_wait_time
    priority_multiplier = {
        "urgent": 0.5,
        "high": 0.8,
        "medium": 1.0,
        "low": 1.2
    }
    return int(base_time * priority_multiplier[priority])

def get_position(queue_entry: QueueEntry, db: Session) -> int:
    earlier_entries = db.query(QueueEntry).filter(
        QueueEntry.service_id == queue_entry.service_id,
        QueueEntry.status == "waiting",
        QueueEntry.created_at < queue_entry.created_at
    ).count()
    return earlier_entries + 1

@router.get("/")
async def get_all_queues(db: Session = Depends(get_db)):
    """Get all active queue entries"""
    queues = db.query(QueueEntry).filter(
        QueueEntry.status.in_(["waiting", "called", "serving"])
    ).all()
    return queues

@router.get("/service/{service_id}")
async def get_service_queue(service_id: int, db: Session = Depends(get_db)):
    """Get queue entries for a specific service"""
    queues = db.query(QueueEntry).filter(
        QueueEntry.service_id == service_id,
        QueueEntry.status.in_(["waiting", "called", "serving"])
    ).order_by(QueueEntry.created_at).all()
    return queues

@router.put("/{queue_id}/status")
async def update_queue_status(
    queue_id: int, 
    status: str, 
    db: Session = Depends(get_db)
):
    """Update queue entry status"""
    queue_entry = db.query(QueueEntry).filter(QueueEntry.id == queue_id).first()
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    queue_entry.status = status
    if status == "completed":
        queue_entry.completed_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Status updated successfully"}

@router.post("/call-next")
async def call_next_patient(
    service_id: int,
    counter_id: int,
    db: Session = Depends(get_db)
):
    """Call next patient in queue"""
    # Get next waiting patient for this service
    next_patient = db.query(QueueEntry).filter(
        QueueEntry.service_id == service_id,
        QueueEntry.status == "waiting"
    ).order_by(QueueEntry.created_at).first()
    
    if not next_patient:
        raise HTTPException(status_code=404, detail="No patients waiting")
    
    # Update status to called
    next_patient.status = "called"
    db.commit()
    
    return {
        "queue_entry": next_patient,
        "message": f"Patient {next_patient.queue_number} called to counter {counter_id}"
    }
