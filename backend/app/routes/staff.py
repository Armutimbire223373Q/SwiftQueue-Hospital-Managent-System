"""
Staff management routes for Healthcare Queue Management System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.staff_service import staff_service
from app.services.auth_service import get_current_user, get_current_active_user
from app.models.models import User
from app.models.staff_models import StaffProfile, StaffSchedule, StaffPerformance, StaffCommunication, StaffTask


router = APIRouter(prefix="/api/staff", tags=["staff"])


# Pydantic models for request/response
class StaffProfileCreate(BaseModel):
    employee_id: str
    department: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    years_experience: int = 0
    certifications: List[str] = []
    is_supervisor: bool = False
    supervisor_id: Optional[int] = None
    hire_date: datetime
    contract_type: str = "full_time"
    hourly_rate: Optional[float] = None
    max_patients_per_hour: int = 4
    languages_spoken: List[str] = []
    emergency_certified: bool = False


class StaffProfileResponse(BaseModel):
    id: int
    user_id: int
    employee_id: str
    department: str
    specialization: Optional[str]
    license_number: Optional[str]
    years_experience: int
    certifications: List[str]
    performance_rating: float
    is_supervisor: bool
    supervisor_id: Optional[int]
    hire_date: datetime
    contract_type: str
    hourly_rate: Optional[float]
    max_patients_per_hour: int
    languages_spoken: List[str]
    emergency_certified: bool
    created_at: datetime
    updated_at: datetime


class StaffScheduleCreate(BaseModel):
    staff_id: int
    shift_date: datetime
    shift_type: str = "morning"
    start_time: datetime
    end_time: datetime
    break_duration: int = 30
    is_active: bool = True
    assigned_service_id: Optional[int] = None
    notes: Optional[str] = None


class StaffScheduleResponse(BaseModel):
    id: int
    staff_id: int
    shift_date: datetime
    shift_type: str
    start_time: datetime
    end_time: datetime
    break_duration: int
    is_active: bool
    assigned_service_id: Optional[int]
    notes: Optional[str]
    created_at: datetime


class StaffPerformanceResponse(BaseModel):
    id: int
    staff_id: int
    date: datetime
    patients_served: int
    avg_service_time: Optional[float]
    patient_satisfaction: float
    efficiency_score: float
    attendance_score: float
    quality_score: float
    total_score: float
    shift_duration: Optional[int]
    breaks_taken: int
    emergency_responses: int
    feedback_count: int


class MessageCreate(BaseModel):
    recipient_id: Optional[int] = None
    subject: str
    message: str
    message_type: str = "direct"
    priority: str = "normal"
    department_filter: Optional[str] = None
    role_filter: Optional[str] = None
    expires_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: Optional[int]
    subject: str
    message: str
    message_type: str
    priority: str
    is_read: bool
    read_at: Optional[datetime]
    department_filter: Optional[str]
    role_filter: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    sender_name: Optional[str]


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int
    task_type: str = "other"
    priority: str = "normal"
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    department: Optional[str] = None
    service_id: Optional[int] = None
    patient_id: Optional[int] = None
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to: int
    assigned_by: int
    task_type: str
    priority: str
    status: str
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    department: Optional[str]
    service_id: Optional[int]
    patient_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    assignee_name: Optional[str]
    assigner_name: Optional[str]


class StaffStatsResponse(BaseModel):
    total_staff: int
    active_staff: int
    supervisors: int
    departments: Dict[str, int]
    avg_performance: float
    emergency_certified: int


# Routes

@router.post("/profile", response_model=StaffProfileResponse)
async def create_staff_profile(
    profile: StaffProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a staff profile for the current user."""
    if not staff_service.check_permission(db, current_user.id, "staff_profiles", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        staff_profile = staff_service.create_staff_profile(db, current_user.id, profile.dict())
        return StaffProfileResponse(**staff_profile.__dict__)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create staff profile: {str(e)}")


@router.get("/profile", response_model=StaffProfileResponse)
async def get_my_staff_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's staff profile."""
    profile = staff_service.get_staff_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Staff profile not found")

    return StaffProfileResponse(**profile.__dict__)


@router.put("/profile", response_model=StaffProfileResponse)
async def update_staff_profile(
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's staff profile."""
    if not staff_service.check_permission(db, current_user.id, "staff_profiles", "update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    profile = staff_service.update_staff_profile(db, current_user.id, updates)
    if not profile:
        raise HTTPException(status_code=404, detail="Staff profile not found")

    return StaffProfileResponse(**profile.__dict__)


@router.get("/department/{department}", response_model=List[Dict[str, Any]])
async def get_staff_by_department(
    department: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all staff in a department."""
    if not staff_service.check_permission(db, current_user.id, "staff", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return staff_service.get_staff_by_department(db, department)


@router.post("/schedule", response_model=StaffScheduleResponse)
async def create_staff_schedule(
    schedule: StaffScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a staff schedule."""
    if not staff_service.check_permission(db, current_user.id, "staff_schedules", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        staff_schedule = staff_service.create_staff_schedule(db, schedule.dict(), current_user.id)
        return StaffScheduleResponse(**staff_schedule.__dict__)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create schedule: {str(e)}")


@router.get("/schedule/{staff_id}")
async def get_staff_schedule(
    staff_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get staff schedule for a date range."""
    if not staff_service.check_permission(db, current_user.id, "staff_schedules", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    schedules = staff_service.get_staff_schedule(db, staff_id, start_date, end_date)
    return [StaffScheduleResponse(**schedule.__dict__) for schedule in schedules]


@router.get("/performance/{staff_id}")
async def get_staff_performance(
    staff_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get staff performance metrics."""
    if not staff_service.check_permission(db, current_user.id, "staff_performance", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    performance = staff_service.get_staff_performance(db, staff_id, start_date, end_date)
    return [StaffPerformanceResponse(**perf.__dict__) for perf in performance]


@router.post("/messages", response_model=MessageResponse)
async def send_staff_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message to staff member(s)."""
    if not staff_service.check_permission(db, current_user.id, "staff_communication", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        msg_data = message.dict()
        msg_data["sender_id"] = current_user.id
        staff_message = staff_service.send_staff_message(db, msg_data)

        # Add sender name
        response = MessageResponse(**staff_message.__dict__)
        response.sender_name = current_user.name
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")


@router.get("/messages", response_model=List[MessageResponse])
async def get_staff_messages(
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages for current user."""
    messages = staff_service.get_staff_messages(db, current_user.id, unread_only)

    result = []
    for msg in messages:
        response = MessageResponse(**msg.__dict__)
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        response.sender_name = sender.name if sender else "Unknown"
        result.append(response)

    return result


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read."""
    success = staff_service.mark_message_read(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or access denied")

    return {"message": "Message marked as read"}


@router.post("/tasks", response_model=TaskResponse)
async def create_staff_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a task for staff member."""
    if not staff_service.check_permission(db, current_user.id, "staff_tasks", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        task_data = task.dict()
        task_data["assigned_by"] = current_user.id
        staff_task = staff_service.create_staff_task(db, task_data)

        # Add names
        response = TaskResponse(**staff_task.__dict__)
        assignee = db.query(User).filter(User.id == staff_task.assigned_to).first()
        assigner = db.query(User).filter(User.id == staff_task.assigned_by).first()
        response.assignee_name = assignee.name if assignee else "Unknown"
        response.assigner_name = assigner.name if assigner else "Unknown"
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create task: {str(e)}")


@router.get("/tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current user."""
    tasks = staff_service.get_staff_tasks(db, current_user.id, status_filter)

    result = []
    for task in tasks:
        response = TaskResponse(**task.__dict__)
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        assigner = db.query(User).filter(User.id == task.assigned_by).first()
        response.assignee_name = assignee.name if assignee else "Unknown"
        response.assigner_name = assigner.name if assigner else "Unknown"
        result.append(response)

    return result


@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task status."""
    valid_statuses = ["pending", "in_progress", "completed", "cancelled", "overdue"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    task = staff_service.update_task_status(db, task_id, status, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    return {"message": f"Task status updated to {status}"}


@router.get("/stats", response_model=StaffStatsResponse)
async def get_staff_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get staff statistics."""
    if not staff_service.check_permission(db, current_user.id, "staff", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Get basic stats
    total_staff = db.query(StaffProfile).count()
    active_staff = db.query(StaffProfile).join(User).filter(User.is_active == True).count()
    supervisors = db.query(StaffProfile).filter(StaffProfile.is_supervisor == True).count()
    emergency_certified = db.query(StaffProfile).filter(StaffProfile.emergency_certified == True).count()

    # Department breakdown
    from sqlalchemy import func
    dept_stats = db.query(
        StaffProfile.department,
        func.count(StaffProfile.id).label('count')
    ).group_by(StaffProfile.department).all()

    departments = {stat.department: stat.count for stat in dept_stats}

    # Average performance
    avg_perf = db.query(func.avg(StaffPerformance.total_score)).scalar() or 0.0

    return StaffStatsResponse(
        total_staff=total_staff,
        active_staff=active_staff,
        supervisors=supervisors,
        departments=departments,
        avg_performance=float(avg_perf),
        emergency_certified=emergency_certified
    )


@router.get("/permissions/check")
async def check_permission(
    resource: str,
    action: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if current user has permission for an action."""
    allowed = staff_service.check_permission(db, current_user.id, resource, action)
    return {"allowed": allowed, "resource": resource, "action": action}


# Admin-only routes
@router.get("/admin/all-profiles", response_model=List[StaffProfileResponse])
async def get_all_staff_profiles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all staff profiles (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    profiles = db.query(StaffProfile).all()
    return [StaffProfileResponse(**profile.__dict__) for profile in profiles]


@router.get("/admin/audit-logs")
async def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if action:
        filters["action"] = action
    if resource_type:
        filters["resource_type"] = resource_type
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date

    logs = staff_service.get_audit_logs(db, filters, limit)
    return [{"id": log.id, "user_id": log.user_id, "action": log.action,
             "resource_type": log.resource_type, "resource_id": log.resource_id,
             "timestamp": log.timestamp, "success": log.success,
             "error_message": log.error_message} for log in logs]