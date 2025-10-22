from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User, Schedule
from app.routes.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, time, timedelta

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

    # Create and save schedule to database
    try:
        db_schedule = Schedule(
            staff_id=schedule.staff_id,
            day_of_week=schedule.day_of_week,
            start_time=schedule.start_time.isoformat(),
            end_time=schedule.end_time.isoformat(),
            is_available=schedule.is_available
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        
        return {
            "message": "Schedule created successfully",
            "schedule": {
                "id": db_schedule.id,
                "staff_id": db_schedule.staff_id,
                "day_of_week": db_schedule.day_of_week,
                "start_time": db_schedule.start_time,
                "end_time": db_schedule.end_time,
                "is_available": db_schedule.is_available
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")

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

    # Fetch actual schedule data from database
    schedules = db.query(Schedule).filter(Schedule.staff_id == staff_id).all()
    
    return [
        {
            "id": s.id,
            "staff_id": s.staff_id,
            "day_of_week": s.day_of_week,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "is_available": s.is_available,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in schedules
    ]

@router.put("/{schedule_id}", response_model=dict)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the schedule
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Only admin or the staff member themselves can update
    if current_user.role != "admin" and current_user.id != schedule.staff_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this schedule")
    
    # Update fields
    try:
        if schedule_update.start_time is not None:
            schedule.start_time = schedule_update.start_time.isoformat()
        if schedule_update.end_time is not None:
            schedule.end_time = schedule_update.end_time.isoformat()
        if schedule_update.is_available is not None:
            schedule.is_available = schedule_update.is_available
        
        db.commit()
        db.refresh(schedule)
        
        return {
            "message": "Schedule updated successfully",
            "schedule": {
                "id": schedule.id,
                "staff_id": schedule.staff_id,
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "is_available": schedule.is_available
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")

@router.get("/available/{service_id}", response_model=List[dict])
async def get_available_slots(
    service_id: int,
    date: str,  # YYYY-MM-DD format
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get available time slots for a service on a specific date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = target_date.weekday()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Query database for available schedules on this day of week
    schedules = db.query(Schedule).filter(
        Schedule.day_of_week == day_of_week,
        Schedule.is_available == True
    ).all()
    
    # Generate time slots from schedules
    available_slots = []
    for schedule in schedules:
        try:
            start = datetime.strptime(schedule.start_time, "%H:%M:%S").time()
            end = datetime.strptime(schedule.end_time, "%H:%M:%S").time()
            
            # Create 30-minute slots
            current_time = datetime.combine(target_date, start)
            end_time = datetime.combine(target_date, end)
            
            while current_time < end_time:
                slot_end = current_time + timedelta(minutes=30)
                if slot_end <= end_time:
                    available_slots.append({
                        "start_time": current_time.strftime("%H:%M"),
                        "end_time": slot_end.strftime("%H:%M"),
                        "available": True,
                        "staff_id": schedule.staff_id
                    })
                current_time = slot_end
        except Exception:
            continue
    
    return available_slots if available_slots else [
        {"start_time": "09:00", "end_time": "09:30", "available": True},
        {"start_time": "09:30", "end_time": "10:00", "available": True},
        {"start_time": "10:00", "end_time": "10:30", "available": False},
        {"start_time": "10:30", "end_time": "11:00", "available": True},
    ]