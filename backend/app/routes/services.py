from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Service, ServiceCounter

router = APIRouter()

class ServiceCreate(BaseModel):
    name: str
    description: str
    department: str
    estimated_wait_time: int = None  # Optional for backward compatibility
    estimated_time: int = None  # Actual field name

@router.post("/")
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Create a new service."""
    # Use estimated_wait_time if provided, otherwise estimated_time
    estimated = service_data.estimated_time or service_data.estimated_wait_time or 30
    
    service = Service(
        name=service_data.name,
        description=service_data.description,
        department=service_data.department,
        estimated_time=estimated
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    # Return formatted response with both field names for compatibility
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "department": service.department,
        "estimated_time": service.estimated_time,
        "estimated_wait_time": service.estimated_time,  # Alias for test compatibility
        "staff_count": service.staff_count,
        "service_rate": service.service_rate,
        "queue_length": service.queue_length
    }

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
