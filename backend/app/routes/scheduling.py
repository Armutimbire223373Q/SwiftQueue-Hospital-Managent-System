from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User
from app.routes.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, time

router = APIRouter()

class ScheduleCreate(BaseModel):
    staff_id: int
    day_of_week: int  # 0-6 (Monday-Sunday)
    start_time: time
    end_time: time
    is_available: bool = True

class ScheduleUpdate(BaseModel):
    start_time: time = None
    end_time: time = None
    is_available: bool = None

# Note: This is a simplified scheduling system. In a real application,
# you might want a more complex Schedule model in the database.
# For now, we'll use a simple in-memory approach or extend the User model.

@router.post("/", response_model=dict)
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can create schedules for others
    if current_user.role != "admin" and schedule.staff_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create schedules")

    # Check if staff exists and is staff/admin
    staff = db.query(User).filter(User.id == schedule.staff_id).first()
    if not staff or staff.role not in ["admin", "staff"]:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # For now, we'll store schedule info in a simple way
    # In a real app, you'd have a Schedule model
    schedule_data = {
        "staff_id": schedule.staff_id,
        "day_of_week": schedule.day_of_week,
        "start_time": schedule.start_time.isoformat(),
        "end_time": schedule.end_time.isoformat(),
        "is_available": schedule.is_available
    }

    # TODO: Save to database (would need Schedule model)
    # For now, just return success
    return {"message": "Schedule created successfully", "schedule": schedule_data}

@router.get("/staff/{staff_id}", response_model=List[dict])
async def get_staff_schedule(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check permissions
    if current_user.role not in ["admin", "staff"] and current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this schedule")

    staff = db.query(User).filter(User.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # TODO: Return actual schedule data from database
    # For now, return empty list
    return []

@router.put("/{schedule_id}", response_model=dict)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement schedule update logic
    # Only admin or the staff member themselves can update
    return {"message": "Schedule updated successfully"}

@router.get("/available/{service_id}", response_model=List[dict])
async def get_available_slots(
    service_id: int,
    date: str,  # YYYY-MM-DD format
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get available time slots for a service on a specific date
    # This would integrate with staff schedules and existing appointments

    # TODO: Implement availability logic
    # For now, return some sample slots
    return [
        {"start_time": "09:00", "end_time": "09:30", "available": True},
        {"start_time": "09:30", "end_time": "10:00", "available": True},
        {"start_time": "10:00", "end_time": "10:30", "available": False},
        {"start_time": "10:30", "end_time": "11:00", "available": True},
    ]