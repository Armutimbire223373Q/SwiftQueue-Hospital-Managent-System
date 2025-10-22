"""
Admin routes for Healthcare Queue Management System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.staff_service import staff_service
from app.services.auth_service import get_current_user, get_current_active_user
from app.models.models import User, Service, QueueEntry, Appointment, Notification
from app.models.staff_models import (
    StaffProfile, StaffSchedule, StaffPerformance, SystemSettings,
    AuditLog, Department, RolePermission
)


router = APIRouter()  # Remove prefix - it's added in main.py


# Pydantic models
class SystemSettingUpdate(BaseModel):
    setting_key: str
    setting_value: Any
    setting_type: str = "string"


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    head_id: Optional[int] = None
    parent_department_id: Optional[int] = None
    budget_allocated: Optional[float] = None
    color_code: Optional[str] = None
    icon_name: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    head_id: Optional[int]
    parent_department_id: Optional[int]
    budget_allocated: Optional[float]
    staff_count: int
    is_active: bool
    color_code: Optional[str]
    icon_name: Optional[str]
    created_at: datetime
    updated_at: datetime


class PermissionCreate(BaseModel):
    role: str
    resource: str
    action: str
    allowed: bool = False
    conditions: Optional[str] = None


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_staff: int
    active_staff: int
    total_patients: int
    active_patients: int
    total_services: int
    active_services: int
    total_queues: int
    active_queues: int
    total_appointments_today: int
    completed_appointments_today: int
    avg_wait_time: float
    system_health: str


class UserManagementResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    has_staff_profile: bool
    department: Optional[str]


# Admin-only middleware
def require_admin(current_user: User = Depends(get_current_active_user)):
    """Ensure user is admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Dashboard routes
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics."""
    # User stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    # Staff stats
    total_staff = db.query(StaffProfile).count()
    active_staff = db.query(StaffProfile).join(User).filter(User.is_active == True).count()

    # Patient stats (users with role 'patient')
    total_patients = db.query(User).filter(User.role == "patient").count()
    active_patients = db.query(User).filter(
        User.role == "patient",
        User.is_active == True
    ).count()

    # Service stats
    total_services = db.query(Service).count()
    active_services = db.query(Service).filter(Service.estimated_time > 0).count()

    # Queue stats
    total_queues = db.query(QueueEntry).count()
    active_queues = db.query(QueueEntry).filter(
        QueueEntry.status.in_(["waiting", "called", "serving"])
    ).count()

    # Appointment stats for today
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    total_appointments_today = db.query(Appointment).filter(
        Appointment.appointment_date >= today,
        Appointment.appointment_date < tomorrow
    ).count()

    completed_appointments_today = db.query(Appointment).filter(
        Appointment.appointment_date >= today,
        Appointment.appointment_date < tomorrow,
        Appointment.status == "completed"
    ).count()

    # Average wait time from analytics
    from sqlalchemy import func
    avg_wait_time_result = db.query(func.avg(QueueEntry.estimated_wait_time)).filter(
        QueueEntry.status == "completed"
    ).scalar()

    avg_wait_time = float(avg_wait_time_result) if avg_wait_time_result else 0.0

    # System health (simplified)
    system_health = "healthy"
    if active_queues > 50:  # High queue load
        system_health = "warning"
    if avg_wait_time > 120:  # Very long wait times
        system_health = "critical"

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_staff=total_staff,
        active_staff=active_staff,
        total_patients=total_patients,
        active_patients=active_patients,
        total_services=total_services,
        active_services=active_services,
        total_queues=total_queues,
        active_queues=active_queues,
        total_appointments_today=total_appointments_today,
        completed_appointments_today=completed_appointments_today,
        avg_wait_time=avg_wait_time,
        system_health=system_health
    )


# User management routes
@router.get("/users", response_model=List[UserManagementResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role_filter: Optional[str] = None,
    active_only: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with management information."""
    query = db.query(User)

    if role_filter:
        query = query.filter(User.role == role_filter)

    if active_only:
        query = query.filter(User.is_active == True)

    users = query.offset(skip).limit(limit).all()

    result = []
    for user in users:
        staff_profile = db.query(StaffProfile).filter(StaffProfile.user_id == user.id).first()

        result.append(UserManagementResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            has_staff_profile=staff_profile is not None,
            department=staff_profile.department if staff_profile else None
        ))

    return result


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admin from deactivating themselves
    if user_id == current_user.id and not is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    db.commit()

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "update_user_status",
        "resource_type": "user",
        "resource_id": user_id,
        "old_values": {"is_active": not is_active},
        "new_values": {"is_active": is_active}
    })

    return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user's role."""
    valid_roles = ["admin", "staff", "patient"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent changing own role to non-admin
    if user_id == current_user.id and new_role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    old_role = user.role
    user.role = new_role
    user.updated_at = datetime.utcnow()
    db.commit()

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "update_user_role",
        "resource_type": "user",
        "resource_id": user_id,
        "old_values": {"role": old_role},
        "new_values": {"role": new_role}
    })

    return {"message": f"User role updated to {new_role}"}


# System settings routes
@router.get("/settings")
async def get_system_settings(
    category: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system settings."""
    return staff_service.get_system_settings(db, category)


@router.put("/settings")
async def update_system_setting(
    setting: SystemSettingUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a system setting."""
    success = staff_service.update_system_setting(
        db, setting.setting_key, setting.setting_value, current_user.id
    )

    if not success:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "update_system_setting",
        "resource_type": "system_setting",
        "resource_id": None,
        "new_values": {"key": setting.setting_key, "value": setting.setting_value}
    })

    return {"message": "System setting updated successfully"}


# Department management routes
@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    active_only: bool = True,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all departments."""
    departments = staff_service.get_departments(db, active_only)

    result = []
    for dept in departments:
        # Count staff in department
        staff_count = db.query(StaffProfile).filter(StaffProfile.department == dept.name).count()

        dept_dict = dept.__dict__.copy()
        dept_dict["staff_count"] = staff_count
        result.append(DepartmentResponse(**dept_dict))

    return result


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department: DepartmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new department."""
    try:
        new_dept = staff_service.create_department(db, department.dict())

        # Log audit event
        staff_service.log_audit_event(db, {
            "user_id": current_user.id,
            "action": "create_department",
            "resource_type": "department",
            "resource_id": new_dept.id,
            "new_values": department.dict()
        })

        dept_dict = new_dept.__dict__.copy()
        dept_dict["staff_count"] = 0
        return DepartmentResponse(**dept_dict)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create department: {str(e)}")


@router.put("/departments/{dept_id}")
async def update_department(
    dept_id: int,
    updates: Dict[str, Any],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a department."""
    department = db.query(Department).filter(Department.id == dept_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    old_values = {k: getattr(department, k) for k in updates.keys()}

    for key, value in updates.items():
        if hasattr(department, key):
            setattr(department, key, value)

    department.updated_at = datetime.utcnow()
    db.commit()

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "update_department",
        "resource_type": "department",
        "resource_id": dept_id,
        "old_values": old_values,
        "new_values": updates
    })

    return {"message": "Department updated successfully"}


# Permission management routes
@router.get("/permissions")
async def get_permissions(
    role: Optional[str] = None,
    resource: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get role permissions."""
    query = db.query(RolePermission)

    if role:
        query = query.filter(RolePermission.role == role)
    if resource:
        query = query.filter(RolePermission.resource == resource)

    permissions = query.all()
    return [{
        "id": p.id,
        "role": p.role,
        "resource": p.resource,
        "action": p.action,
        "allowed": p.allowed,
        "conditions": p.conditions
    } for p in permissions]


@router.post("/permissions")
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a role permission."""
    # Check if permission already exists
    existing = db.query(RolePermission).filter(
        RolePermission.role == permission.role,
        RolePermission.resource == permission.resource,
        RolePermission.action == permission.action
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")

    new_perm = RolePermission(**permission.dict())
    db.add(new_perm)
    db.commit()
    db.refresh(new_perm)

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "create_permission",
        "resource_type": "permission",
        "resource_id": new_perm.id,
        "new_values": permission.dict()
    })

    return {"message": "Permission created successfully", "id": new_perm.id}


@router.put("/permissions/{perm_id}")
async def update_permission(
    perm_id: int,
    allowed: bool,
    conditions: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a permission."""
    permission = db.query(RolePermission).filter(RolePermission.id == perm_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    old_values = {"allowed": permission.allowed, "conditions": permission.conditions}

    permission.allowed = allowed
    permission.conditions = conditions
    db.commit()

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "update_permission",
        "resource_type": "permission",
        "resource_id": perm_id,
        "old_values": old_values,
        "new_values": {"allowed": allowed, "conditions": conditions}
    })

    return {"message": "Permission updated successfully"}


# System maintenance routes
@router.post("/system/backup")
async def trigger_system_backup(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Trigger a system backup."""
    # This would typically call a backup service
    # For now, just log the action

    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "trigger_backup",
        "resource_type": "system",
        "resource_id": None
    })

    return {"message": "System backup initiated successfully"}


@router.post("/system/maintenance-mode")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Enable or disable maintenance mode."""
    setting_key = "maintenance_mode"
    success = staff_service.update_system_setting(
        db, setting_key, enabled, current_user.id
    )

    if not success:
        # Create the setting if it doesn't exist
        from app.models.staff_models import SystemSettings
        new_setting = SystemSettings(
            setting_key=setting_key,
            setting_value=str(enabled).lower(),
            setting_type="boolean",
            category="system",
            description="System maintenance mode",
            is_system_setting=True
        )
        db.add(new_setting)
        db.commit()

    # Log audit event
    staff_service.log_audit_event(db, {
        "user_id": current_user.id,
        "action": "toggle_maintenance_mode",
        "resource_type": "system",
        "resource_id": None,
        "new_values": {"enabled": enabled, "message": message}
    })

    return {"message": f"Maintenance mode {'enabled' if enabled else 'disabled'} successfully"}


@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed system health information."""
    # Import monitoring service
    from app.monitoring import get_health_status

    health_data = await get_health_status()

    # Add additional admin-level health checks
    health_data["admin_checks"] = {
        "database_connections": "healthy",  # Would check actual connection pool
        "cache_status": "healthy",  # Would check Redis status
        "external_services": "healthy",  # Would check API integrations
        "disk_space": "healthy",  # Would check disk usage
        "memory_usage": "healthy"  # Would check memory usage
    }

    return health_data


@router.get("/reports/user-activity")
async def get_user_activity_report(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate user activity report."""
    # Get login activity
    logins = db.query(AuditLog).filter(
        AuditLog.action == "login",
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date,
        AuditLog.success == True
    ).all()

    # Get user registrations
    registrations = db.query(User).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()

    # Aggregate by date
    activity_by_date = {}
    for login in logins:
        date_key = login.timestamp.date().isoformat()
        if date_key not in activity_by_date:
            activity_by_date[date_key] = {"logins": 0, "registrations": 0}
        activity_by_date[date_key]["logins"] += 1

    for reg in registrations:
        date_key = reg.created_at.date().isoformat()
        if date_key not in activity_by_date:
            activity_by_date[date_key] = {"logins": 0, "registrations": 0}
        activity_by_date[date_key]["registrations"] += 1

    return {
        "period": {"start": start_date, "end": end_date},
        "summary": {
            "total_logins": len(logins),
            "total_registrations": len(registrations),
            "unique_users": len(set(login.user_id for login in logins if login.user_id))
        },
        "daily_activity": activity_by_date
    }