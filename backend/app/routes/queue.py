from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import QueueEntry, User, Service
from datetime import datetime
import random

router = APIRouter()

@router.post("/join")
async def join_queue(
    service_id: int,
    patient_details: dict,
    db: Session = Depends(get_db)
):
    # Create or update user
    user = db.query(User).filter(User.email == patient_details["email"]).first()
    if not user:
        user = User(
            name=patient_details["name"],
            email=patient_details["email"],
            phone=patient_details["phone"],
            date_of_birth=datetime.strptime(patient_details["dateOfBirth"], "%Y-%m-%d")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Get service
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Calculate queue number
    last_queue = db.query(QueueEntry).order_by(QueueEntry.queue_number.desc()).first()
    new_queue_number = (last_queue.queue_number + 1) if last_queue else 1

    # Create queue entry
    queue_entry = QueueEntry(
        patient_id=user.id,
        service_id=service_id,
        queue_number=new_queue_number,
        status="waiting",
        priority=patient_details["priority"],
        estimated_wait_time=service.current_wait_time,
        ai_predicted_wait=predict_wait_time(service, patient_details["priority"])
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
