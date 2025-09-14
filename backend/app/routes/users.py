from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.models import User, QueueEntry

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    date_of_birth: str  # ISO format date string

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    date_of_birth: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Parse date of birth
    try:
        dob = datetime.fromisoformat(user.date_of_birth.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        date_of_birth=dob
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        # Check if new email is already taken by another user
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken by another user")
        user.email = user_update.email
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.date_of_birth is not None:
        try:
            user.date_of_birth = datetime.fromisoformat(user_update.date_of_birth.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has active queue entries
    active_entries = db.query(QueueEntry).filter(
        QueueEntry.patient_id == user_id,
        QueueEntry.status.in_(["waiting", "called", "serving"])
    ).count()
    
    if active_entries > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete user with active queue entries. Please complete or cancel their queue entries first."
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/queue-history")
async def get_user_queue_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    queue_entries = db.query(QueueEntry).filter(QueueEntry.patient_id == user_id).order_by(QueueEntry.created_at.desc()).all()
    
    return [
        {
            "id": entry.id,
            "queue_number": entry.queue_number,
            "service_name": entry.service.name if entry.service else "Unknown",
            "status": entry.status,
            "priority": entry.priority,
            "created_at": entry.created_at,
            "completed_at": entry.completed_at,
            "estimated_wait_time": entry.estimated_wait_time,
            "ai_predicted_wait": entry.ai_predicted_wait
        }
        for entry in queue_entries
    ]

@router.get("/{user_id}/active-queues")
async def get_user_active_queues(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    active_entries = db.query(QueueEntry).filter(
        QueueEntry.patient_id == user_id,
        QueueEntry.status.in_(["waiting", "called", "serving"])
    ).all()
    
    return [
        {
            "id": entry.id,
            "queue_number": entry.queue_number,
            "service_name": entry.service.name if entry.service else "Unknown",
            "status": entry.status,
            "priority": entry.priority,
            "created_at": entry.created_at,
            "estimated_wait_time": entry.estimated_wait_time,
            "ai_predicted_wait": entry.ai_predicted_wait,
            "position_in_queue": get_queue_position(entry, db)
        }
        for entry in active_entries
    ]

def get_queue_position(queue_entry: QueueEntry, db: Session) -> int:
    """Get the position of a queue entry in the waiting line"""
    if queue_entry.status != "waiting":
        return 0
    
    earlier_entries = db.query(QueueEntry).filter(
        QueueEntry.service_id == queue_entry.service_id,
        QueueEntry.status == "waiting",
        QueueEntry.created_at < queue_entry.created_at
    ).count()
    return earlier_entries + 1