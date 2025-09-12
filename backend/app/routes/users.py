from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, QueueEntry

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/queue_history")
async def get_user_queue_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(QueueEntry).filter(
        QueueEntry.patient_id == user_id
    ).order_by(QueueEntry.created_at.desc()).all()
    return history
