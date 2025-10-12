from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Appointment, User
from app.routes.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AppointmentCreate(BaseModel):
    service_id: int
    appointment_date: datetime
    duration: int = 30
    notes: str = None

class AppointmentUpdate(BaseModel):
    status: str = None
    notes: str = None
    staff_id: int = None

@router.post("/", response_model=dict)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_appointment = Appointment(
        patient_id=current_user.id,
        service_id=appointment.service_id,
        appointment_date=appointment.appointment_date,
        duration=appointment.duration,
        status="scheduled",
        notes=appointment.notes
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return {"message": "Appointment created successfully", "appointment_id": db_appointment.id}

@router.get("/", response_model=List[dict])
async def get_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin" or current_user.role == "staff":
        appointments = db.query(Appointment).all()
    else:
        appointments = db.query(Appointment).filter(Appointment.patient_id == current_user.id).all()

    return [
        {
            "id": apt.id,
            "patient_id": apt.patient_id,
            "service_id": apt.service_id,
            "staff_id": apt.staff_id,
            "appointment_date": apt.appointment_date,
            "duration": apt.duration,
            "status": apt.status,
            "notes": apt.notes,
            "patient_name": apt.patient.name if apt.patient else None,
            "service_name": apt.service.name if apt.service else None,
            "staff_name": apt.staff.name if apt.staff else None
        }
        for apt in appointments
    ]

@router.put("/{appointment_id}", response_model=dict)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check permissions
    if current_user.role not in ["admin", "staff"] and db_appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this appointment")

    if appointment_update.status:
        db_appointment.status = appointment_update.status
    if appointment_update.notes is not None:
        db_appointment.notes = appointment_update.notes
    if appointment_update.staff_id:
        db_appointment.staff_id = appointment_update.staff_id

    db.commit()
    return {"message": "Appointment updated successfully"}

@router.delete("/{appointment_id}", response_model=dict)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check permissions
    if current_user.role not in ["admin", "staff"] and db_appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    db_appointment.status = "cancelled"
    db.commit()
    return {"message": "Appointment cancelled successfully"}