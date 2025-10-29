"""
Reporting Routes - REST API for comprehensive reporting
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import io

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User
from app.services.reporting_service import ReportingService


router = APIRouter()


@router.get("/patient/{patient_id}")
def get_patient_report(
    patient_id: int,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    include_visits: bool = Query(True, description="Include visits in report"),
    include_medical_records: bool = Query(True, description="Include medical records"),
    include_lab_results: bool = Query(True, description="Include lab results"),
    include_medications: bool = Query(True, description="Include medications"),
    include_payments: bool = Query(True, description="Include payments"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive patient report
    
    Includes patient information, visits, medical records, lab results,
    medications, and payment history for the specified date range.
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_patient_report(
            patient_id=patient_id,
            start_date=start_dt,
            end_date=end_dt,
            include_visits=include_visits,
            include_medical_records=include_medical_records,
            include_lab_results=include_lab_results,
            include_medications=include_medications,
            include_payments=include_payments
        )
        
        return {
            "success": True,
            "report": report
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/patient/{patient_id}/export/csv")
def export_patient_report_csv(
    patient_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export patient report to CSV
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_patient_report(
            patient_id=patient_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Export to CSV
        csv_content = reporting_service.export_to_csv(report, "patient")
        
        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=patient_{patient_id}_report.csv"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting report: {str(e)}")


@router.get("/queue/analytics")
def get_queue_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate queue analytics report
    
    Provides comprehensive queue statistics including wait times,
    completion rates, department breakdown, and trends.
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_queue_analytics(
            start_date=start_dt,
            end_date=end_dt,
            department=department,
            service_type=service_type
        )
        
        return {
            "success": True,
            "analytics": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@router.get("/queue/analytics/export/csv")
def export_queue_analytics_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export queue analytics to CSV
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_queue_analytics(
            start_date=start_dt,
            end_date=end_dt,
            department=department,
            service_type=service_type
        )
        
        # Export to CSV
        csv_content = reporting_service.export_to_csv(report, "queue")
        
        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=queue_analytics.csv"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analytics: {str(e)}")


@router.get("/staff/performance")
def get_staff_performance(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    staff_id: Optional[int] = Query(None, description="Filter by staff ID"),
    role: Optional[str] = Query(None, description="Filter by role"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate staff performance report
    
    Provides metrics on staff productivity, queue handling,
    patient visits, and service times.
    """
    try:
        # Only admins can view all staff performance
        if current_user.role != "admin" and not staff_id:
            # Non-admins can only view their own performance
            staff_id = current_user.id
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_staff_performance_report(
            start_date=start_dt,
            end_date=end_dt,
            staff_id=staff_id,
            role=role
        )
        
        return {
            "success": True,
            "performance": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance report: {str(e)}")


@router.get("/financial")
def get_financial_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate financial report
    
    Provides comprehensive financial data including revenue,
    collections, outstanding balances, and payment breakdowns.
    """
    try:
        # Only admins and finance staff can view financial reports
        if current_user.role not in ["admin", "finance", "receptionist"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to view financial reports"
            )
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_financial_report(
            start_date=start_dt,
            end_date=end_dt,
            department=department,
            payment_method=payment_method,
            payment_status=payment_status
        )
        
        return {
            "success": True,
            "financial_report": report
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating financial report: {str(e)}")


@router.get("/financial/export/csv")
def export_financial_report_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export financial report to CSV
    """
    try:
        # Permission check
        if current_user.role not in ["admin", "finance", "receptionist"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to export financial reports"
            )
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Generate report
        reporting_service = ReportingService(db)
        report = reporting_service.get_financial_report(
            start_date=start_dt,
            end_date=end_dt,
            department=department,
            payment_method=payment_method,
            payment_status=payment_status
        )
        
        # Export to CSV
        csv_content = reporting_service.export_to_csv(report, "financial")
        
        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=financial_report.csv"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting financial report: {str(e)}")


@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary with key metrics
    
    Provides quick overview of today's and this week's statistics.
    """
    try:
        from datetime import timedelta
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        
        reporting_service = ReportingService(db)
        
        # Today's queue stats
        today_queue = reporting_service.get_queue_analytics(
            start_date=today,
            end_date=datetime.utcnow()
        )
        
        # This week's financial stats
        week_financial = reporting_service.get_financial_report(
            start_date=week_start,
            end_date=datetime.utcnow()
        )
        
        # Staff performance (if admin)
        staff_performance = None
        if current_user.role == "admin":
            staff_performance = reporting_service.get_staff_performance_report(
                start_date=week_start,
                end_date=datetime.utcnow()
            )
        
        return {
            "success": True,
            "summary": {
                "today": {
                    "date": today.isoformat(),
                    "queue": {
                        "total_entries": today_queue["summary"]["total_entries"],
                        "completed": today_queue["summary"]["completed"],
                        "waiting": today_queue["summary"]["waiting"],
                        "average_wait_time": today_queue["wait_time_statistics"]["average_wait_time_minutes"]
                    }
                },
                "this_week": {
                    "start_date": week_start.isoformat(),
                    "financial": {
                        "total_collected": week_financial["summary"]["total_collected"],
                        "total_outstanding": week_financial["summary"]["total_outstanding"],
                        "collection_rate": week_financial["summary"]["collection_rate"]
                    },
                    "staff": staff_performance if staff_performance else "Restricted"
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
