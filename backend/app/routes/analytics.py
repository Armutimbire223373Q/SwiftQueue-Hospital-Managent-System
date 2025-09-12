from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Analytics, QueueEntry
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/wait-times")
async def get_wait_time_analytics(db: Session = Depends(get_db)):
    # Get average wait times for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    wait_times = db.query(
        func.date(QueueEntry.created_at).label('date'),
        func.avg(QueueEntry.ai_predicted_wait).label('avg_wait')
    ).filter(
        QueueEntry.created_at >= seven_days_ago
    ).group_by(
        func.date(QueueEntry.created_at)
    ).all()
    
    return wait_times

@router.get("/peak-hours")
async def get_peak_hours(db: Session = Depends(get_db)):
    # Get busiest hours in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    peak_hours = db.query(
        func.extract('hour', QueueEntry.created_at).label('hour'),
        func.count(QueueEntry.id).label('count')
    ).filter(
        QueueEntry.created_at >= seven_days_ago
    ).group_by(
        func.extract('hour', QueueEntry.created_at)
    ).order_by(
        func.count(QueueEntry.id).desc()
    ).all()
    
    return peak_hours

@router.get("/service-distribution")
async def get_service_distribution(db: Session = Depends(get_db)):
    # Get distribution of services used in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    distribution = db.query(
        QueueEntry.service_id,
        func.count(QueueEntry.id).label('count')
    ).filter(
        QueueEntry.created_at >= seven_days_ago
    ).group_by(
        QueueEntry.service_id
    ).all()
    
    return distribution

@router.get("/recommendations")
async def get_ai_recommendations(db: Session = Depends(get_db)):
    # TODO: Implement actual AI recommendations
    # For now, returning static recommendations based on simple analysis
    return [
        {
            "title": "Staff Allocation",
            "description": "Consider adding more staff during peak hours (11 AM - 2 PM)"
        },
        {
            "title": "Service Optimization",
            "description": "Laboratory services showing longer than average wait times"
        }
    ]
