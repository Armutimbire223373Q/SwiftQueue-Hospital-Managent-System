from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Analytics, QueueEntry, Service, ServiceCounter
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

@router.get("/wait-times")
async def get_wait_time_analytics(db: Session = Depends(get_db)):
    # Get average wait times for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    wait_times = (
        db.query(
            func.date(QueueEntry.created_at).label('date'),
            func.avg(QueueEntry.ai_predicted_wait).label('avg_wait')
        )
        .filter(QueueEntry.created_at >= seven_days_ago)
        .group_by(func.date(QueueEntry.created_at))
        .all()
    )
    
    return [{"date": str(wt.date), "avgWait": float(wt.avg_wait)} for wt in wait_times]

@router.get("/peak-hours")
async def get_peak_hours(db: Session = Depends(get_db)):
    # Get busiest hours in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    peak_hours = (
        db.query(
            func.extract('hour', QueueEntry.created_at).label('hour'),
            func.count(QueueEntry.id).label('count')
        )
        .filter(QueueEntry.created_at >= seven_days_ago)
        .group_by(func.extract('hour', QueueEntry.created_at))
        .order_by(func.count(QueueEntry.id).desc())
        .all()
    )
    
    return [{"hour": int(ph.hour), "count": int(ph.count)} for ph in peak_hours]

@router.get("/service-distribution")
async def get_service_distribution(db: Session = Depends(get_db)):
    # Get distribution of services used in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    distribution = (
        db.query(
            QueueEntry.service_id,
            func.count(QueueEntry.id).label('count')
        )
        .filter(QueueEntry.created_at >= seven_days_ago)
        .group_by(QueueEntry.service_id)
        .all()
    )
    
    return [{"serviceId": d.service_id, "count": int(d.count)} for d in distribution]

@router.get("/recommendations")
async def get_recommendations(db: Session = Depends(get_db)) -> List[dict]:
    recommendations = []
    
    # Get current queue state
    current_time = datetime.utcnow()
    active_services = db.query(Service).all()
    
    for service in active_services:
        # Check wait times
        avg_wait = db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
            QueueEntry.service_id == service.id,
            QueueEntry.status == "waiting"
        ).scalar() or 0

        if avg_wait > 30:  # If average wait time > 30 minutes
            active_counters = db.query(ServiceCounter).filter(
                and_(
                    ServiceCounter.service_id == service.id,
                    ServiceCounter.is_active == 1
                )
            ).count()
            
            recommendations.append({
                "type": "critical" if avg_wait > 45 else "warning",
                "message": f"High wait times for {service.name}",
                "action": f"Consider activating additional counters for {service.name}" if active_counters < 3 else "Review service efficiency"
            })

        # Check staff utilization
        counters = db.query(ServiceCounter).filter(
            ServiceCounter.service_id == service.id
        ).all()
        active_staff = len([c for c in counters if c.is_active and c.staff_member])
        
        if service.queue_length > active_staff * 5:  # More than 5 patients per staff
            recommendations.append({
                "type": "warning",
                "message": f"High load on {service.name} staff",
                "action": f"Consider adding more staff to {service.name}"
            })

    # Get historical analytics for optimization recommendations
    latest_analytics = db.query(Analytics).filter(
        Analytics.timestamp >= current_time - timedelta(hours=24)
    ).order_by(Analytics.timestamp.desc()).first()

    if latest_analytics and latest_analytics.efficiency_score < 0.7:
        recommendations.append({
            "type": "improvement",
            "message": "System efficiency below target",
            "action": "Review resource allocation and service procedures"
        })

    if not recommendations:
        recommendations.append({
            "type": "info",
            "message": "System operating within normal parameters",
            "action": "Continue monitoring"
        })

    return recommendations
