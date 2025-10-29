"""
Analytics Dashboard API
Provides comprehensive analytics endpoints for the dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.routes.auth import get_current_active_user
from app.models.models import User


router = APIRouter(prefix="/api/analytics/dashboard", tags=["Analytics Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(
    period_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive dashboard overview with key metrics.
    
    Parameters:
    - period_days: Number of days to analyze (default: 7, max: 365)
    
    Returns:
    - total_patients: Total patients served in period
    - avg_wait_time: Average wait time in minutes
    - active_services: Number of active services
    - efficiency_score: System efficiency (0-1)
    - patient_satisfaction: Average satisfaction rating
    - revenue: Total revenue generated
    """
    analytics = AnalyticsService(db)
    return analytics.get_overview_kpis(period_days=period_days)


@router.get("/services")
async def get_service_analytics(
    service_id: Optional[int] = Query(None),
    period_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get analytics for all services or a specific service.
    
    Parameters:
    - service_id: Optional service ID to filter
    - period_days: Number of days to analyze
    
    Returns list of services with:
    - service_id, service_name
    - total_patients
    - avg_wait_time
    - throughput (patients/hour)
    - utilization (0-1)
    - active_counters
    - current_queue_length
    """
    analytics = AnalyticsService(db)
    return analytics.get_service_kpis(service_id=service_id, period_days=period_days)


@router.get("/staff-performance")
async def get_staff_performance(
    period_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get staff performance metrics.
    
    Parameters:
    - period_days: Number of days to analyze
    
    Returns list of staff with:
    - user_id, name, role
    - patients_served
    - avg_service_time
    - active_hours
    - efficiency_rating
    """
    # Restrict to admin and managers
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators and managers can view staff performance"
        )
    
    analytics = AnalyticsService(db)
    return analytics.get_staff_performance(period_days=period_days)


@router.get("/trends/wait-times")
async def get_wait_time_trends(
    period_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get wait time trends over time.
    
    Parameters:
    - period_days: Number of days to analyze (default: 30)
    
    Returns daily trends with:
    - date
    - avg_wait_time
    - min_wait_time
    - max_wait_time
    - patient_count
    """
    analytics = AnalyticsService(db)
    return analytics.get_wait_time_trends(period_days=period_days)


@router.get("/trends/hourly-traffic")
async def get_hourly_traffic(
    period_days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get hourly traffic patterns.
    
    Parameters:
    - period_days: Number of days to analyze
    
    Returns hourly data (0-23) with:
    - hour
    - avg_patients
    - avg_wait_time
    """
    analytics = AnalyticsService(db)
    return analytics.get_hourly_traffic(period_days=period_days)


@router.get("/trends/services")
async def get_service_trends(
    period_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get service usage trends over time.
    
    Parameters:
    - period_days: Number of days to analyze
    
    Returns service trends with:
    - service_id, service_name
    - daily_trends: [{date, patient_count, avg_wait}]
    """
    analytics = AnalyticsService(db)
    return analytics.get_service_trends(period_days=period_days)


@router.get("/predictions/peak-times")
async def predict_peak_times(
    look_ahead_days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict peak times based on historical data.
    
    Parameters:
    - look_ahead_days: Number of days to predict
    
    Returns predicted peaks with:
    - day_of_week (0=Sunday, 6=Saturday)
    - hour (0-23)
    - expected_patients
    - confidence_level (0-1)
    """
    analytics = AnalyticsService(db)
    return analytics.predict_peak_times(look_ahead_days=look_ahead_days)


@router.get("/bottlenecks")
async def identify_bottlenecks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Identify system bottlenecks and congestion points.
    
    Returns list of bottlenecks with:
    - bottleneck_type (service, staff, time)
    - description
    - severity (critical, high, medium, low)
    - affected_entity
    - metric_value
    - recommended_action
    """
    analytics = AnalyticsService(db)
    return analytics.identify_bottlenecks()


@router.get("/comparison")
async def compare_periods(
    current_days: int = Query(7, ge=1, le=90),
    previous_days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare current period with previous period.
    
    Parameters:
    - current_days: Days in current period
    - previous_days: Days in previous period
    
    Returns:
    - current_period: Current period KPIs
    - previous_period: Previous period KPIs
    - changes: Percentage changes for each KPI
    - comparison_note: Description of comparison
    """
    analytics = AnalyticsService(db)
    return analytics.compare_periods(
        current_days=current_days,
        previous_days=previous_days
    )


@router.get("/revenue")
async def get_revenue_analytics(
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed revenue analytics.
    
    Parameters:
    - period_days: Number of days to analyze
    
    Returns:
    - total_revenue
    - revenue_by_service: [{service, revenue}]
    - revenue_trend: [{date, revenue}]
    - payment_methods: [{method, count, total}]
    - outstanding_payments
    """
    # Restrict to admin and managers
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators and managers can view revenue analytics"
        )
    
    analytics = AnalyticsService(db)
    return analytics.get_revenue_analytics(period_days=period_days)


@router.get("/real-time")
async def get_realtime_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get real-time metrics for live dashboard updates.
    
    Returns:
    - current_patients_waiting: Patients currently in queue
    - active_counters: Number of active service counters
    - avg_current_wait: Current average wait time
    - services_status: [{service_id, name, queue_length, status}]
    - recent_activities: Last 10 patient check-ins
    """
    from app.models.models import Service, ServiceCounter, QueueEntry
    from sqlalchemy import func, and_
    
    # Current patients waiting
    current_patients = db.query(func.count(QueueEntry.id)).filter(
        QueueEntry.status == "waiting"
    ).scalar() or 0
    
    # Active counters
    active_counters = db.query(func.count(ServiceCounter.id)).filter(
        ServiceCounter.is_active == True
    ).scalar() or 0
    
    # Average current wait
    avg_wait = db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
        and_(
            QueueEntry.status == "waiting",
            QueueEntry.ai_predicted_wait.isnot(None)
        )
    ).scalar() or 0
    
    # Services status
    services = db.query(Service).all()
    services_status = [
        {
            "service_id": s.id,
            "name": s.name,
            "queue_length": s.queue_length or 0,
            "status": "busy" if (s.queue_length or 0) > 10 else "normal"
        }
        for s in services
    ]
    
    # Recent activities (last 10 check-ins)
    recent = db.query(QueueEntry).order_by(
        QueueEntry.created_at.desc()
    ).limit(10).all()
    
    recent_activities = [
        {
            "queue_number": entry.queue_number,
            "service_id": entry.service_id,
            "status": entry.status,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        }
        for entry in recent
    ]
    
    return {
        "current_patients_waiting": current_patients,
        "active_counters": active_counters,
        "avg_current_wait": round(float(avg_wait), 2),
        "services_status": services_status,
        "recent_activities": recent_activities,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/export")
async def export_analytics(
    period_days: int = Query(30, ge=1, le=365),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Export analytics data in JSON or CSV format.
    
    Parameters:
    - period_days: Number of days to include
    - format: Export format (json or csv)
    
    Returns:
    - Comprehensive analytics data in requested format
    """
    # Restrict to admin and managers
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators and managers can export analytics"
        )
    
    analytics = AnalyticsService(db)
    
    # Gather all analytics
    data = {
        "overview": analytics.get_overview_kpis(period_days=period_days),
        "services": analytics.get_service_kpis(period_days=period_days),
        "staff_performance": analytics.get_staff_performance(period_days=period_days),
        "wait_time_trends": analytics.get_wait_time_trends(period_days=period_days),
        "hourly_traffic": analytics.get_hourly_traffic(period_days=period_days),
        "peak_predictions": analytics.predict_peak_times(),
        "bottlenecks": analytics.identify_bottlenecks(),
        "revenue": analytics.get_revenue_analytics(period_days=period_days),
        "export_metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user.name,
            "period_days": period_days
        }
    }
    
    if format == "csv":
        # For CSV, return a simplified version
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write overview section
        writer.writerow(["OVERVIEW METRICS"])
        writer.writerow(["Metric", "Value"])
        for key, value in data["overview"].items():
            writer.writerow([key, value])
        
        writer.writerow([])
        writer.writerow(["SERVICE METRICS"])
        if data["services"]:
            writer.writerow(list(data["services"][0].keys()))
            for service in data["services"]:
                writer.writerow(list(service.values()))
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        )
    
    return data
