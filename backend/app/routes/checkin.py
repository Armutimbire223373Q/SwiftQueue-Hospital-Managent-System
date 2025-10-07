from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Checkin, Appointment, User
from app.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CheckinCreate(BaseModel):
    appointment_id: int

@router.post("/", response_model=dict)
async def checkin_patient(
    checkin: CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the appointment
    appointment = db.query(Appointment).filter(Appointment.id == checkin.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check if user is authorized (patient themselves or staff/admin)
    if current_user.role not in ["admin", "staff"] and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to check in for this appointment")

    # Check if already checked in
    existing_checkin = db.query(Checkin).filter(Checkin.appointment_id == checkin.appointment_id).first()
    if existing_checkin:
        raise HTTPException(status_code=400, detail="Patient already checked in for this appointment")

    # Create checkin record
    db_checkin = Checkin(
        appointment_id=checkin.appointment_id,
        patient_id=appointment.patient_id,
        status="checked_in"
    )
    db.add(db_checkin)

    # Update appointment status
    appointment.status = "in_progress"

    db.commit()
    db.refresh(db_checkin)
    return {"message": "Patient checked in successfully", "checkin_id": db_checkin.id}

@router.get("/appointment/{appointment_id}", response_model=dict)
async def get_checkin_status(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check permissions
    if current_user.role not in ["admin", "staff"] and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this checkin")

    checkin = db.query(Checkin).filter(Checkin.appointment_id == appointment_id).first()

    if checkin:
        return {
            "checked_in": True,
            "checkin_time": checkin.checkin_time,
            "status": checkin.status
        }
    else:
        return {"checked_in": False}

@router.put("/{checkin_id}/status", response_model=dict)
async def update_checkin_status(
    checkin_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only staff and admin can update checkin status
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized to update checkin status")

    db_checkin = db.query(Checkin).filter(Checkin.id == checkin_id).first()
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Checkin not found")

    if status not in ["checked_in", "no_show", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    db_checkin.status = status
    db.commit()
    return {"message": "Checkin status updated successfully"}