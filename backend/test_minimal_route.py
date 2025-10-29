"""Minimal test to isolate the FastAPI routing issue"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.models import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/test", tags=["Test"])

class TestResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint"""
    return {"id": 1, "name": "test", "created_at": datetime.utcnow()}

@router.get("/", response_model=list[TestResponse])
async def list_tests(
    db: Session = Depends(get_db)
):
    """List test items"""
    return []
