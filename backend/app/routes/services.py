from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Service, ServiceCounter

router = APIRouter()

@router.get("/")
@router.get("")  # Handle both /api/services and /api/services/
async def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services

@router.get("/{service_id}")
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.get("/{service_id}/counters")
async def get_service_counters(service_id: int, db: Session = Depends(get_db)):
    counters = db.query(ServiceCounter).filter(
        ServiceCounter.service_id == service_id
    ).all()
    return counters
