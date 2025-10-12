"""
Staff management service for Healthcare Queue Management System
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json

from app.models.models import User
from app.models.staff_models import (
    StaffProfile, StaffSchedule, StaffPerformance, StaffCommunication,
    StaffTask, StaffTraining, SystemSettings, AuditLog, Department, RolePermission
)
from app.services.auth_service import get_user_by_id


class StaffService:
    """Service for managing staff operations and data."""

    def __init__(self):
        pass

    def create_staff_profile(self, db: Session, user_id: int, profile_data: Dict[str, Any]) -> StaffProfile:
        """Create a staff profile for a user."""
        profile = StaffProfile(
            user_id=user_id,
            employee_id=profile_data.get("employee_id"),
            department=profile_data.get("department"),
            specialization=profile_data.get("specialization"),
            license_number=profile_data.get("license_number"),
            years_experience=profile_data.get("years_experience", 0),
            certifications=json.dumps(profile_data.get("certifications", [])),
            performance_rating=profile_data.get("performance_rating", 0.0),
            is_supervisor=profile_data.get("is_supervisor", False),
            supervisor_id=profile_data.get("supervisor_id"),
            hire_date=profile_data.get("hire_date"),
            contract_type=profile_data.get("contract_type", "full_time"),
            hourly_rate=profile_data.get("hourly_rate"),
            max_patients_per_hour=profile_data.get("max_patients_per_hour", 4),
            languages_spoken=json.dumps(profile_data.get("languages_spoken", [])),
            emergency_certified=profile_data.get("emergency_certified", False)
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def get_staff_profile(self, db: Session, user_id: int) -> Optional[StaffProfile]:
        """Get staff profile by user ID."""
        return db.query(StaffProfile).filter(StaffProfile.user_id == user_id).first()

    def update_staff_profile(self, db: Session, user_id: int, updates: Dict[str, Any]) -> Optional[StaffProfile]:
        """Update staff profile."""
        profile = self.get_staff_profile(db, user_id)
        if not profile:
            return None

        for key, value in updates.items():
            if hasattr(profile, key):
                if key in ["certifications", "languages_spoken"]:
                    setattr(profile, key, json.dumps(value))
                else:
                    setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile

    def get_staff_by_department(self, db: Session, department: str) -> List[Dict[str, Any]]:
        """Get all staff in a department."""
        staff_profiles = db.query(StaffProfile).filter(StaffProfile.department == department).all()

        result = []
        for profile in staff_profiles:
            user = get_user_by_id(db, profile.user_id)
            if user:
                result.append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "profile": {
                        "employee_id": profile.employee_id,
                        "specialization": profile.specialization,
                        "performance_rating": profile.performance_rating,
                        "is_supervisor": profile.is_supervisor,
                        "contract_type": profile.contract_type
                    }
                })

        return result

    def create_staff_schedule(self, db: Session, schedule_data: Dict[str, Any], created_by: int) -> StaffSchedule:
        """Create a staff schedule."""
        schedule = StaffSchedule(
            staff_id=schedule_data["staff_id"],
            shift_date=schedule_data["shift_date"],
            shift_type=schedule_data.get("shift_type", "morning"),
            start_time=schedule_data["start_time"],
            end_time=schedule_data["end_time"],
            break_duration=schedule_data.get("break_duration", 30),
            is_active=schedule_data.get("is_active", True),
            assigned_service_id=schedule_data.get("assigned_service_id"),
            notes=schedule_data.get("notes"),
            created_by=created_by
        )

        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def get_staff_schedule(self, db: Session, staff_id: int, start_date: datetime, end_date: datetime) -> List[StaffSchedule]:
        """Get staff schedule for a date range."""
        return db.query(StaffSchedule).filter(
            and_(
                StaffSchedule.staff_id == staff_id,
                StaffSchedule.shift_date >= start_date,
                StaffSchedule.shift_date <= end_date,
                StaffSchedule.is_active == True
            )
        ).all()

    def update_staff_performance(self, db: Session, staff_id: int, date: datetime, metrics: Dict[str, Any]) -> StaffPerformance:
        """Update or create staff performance record."""
        performance = db.query(StaffPerformance).filter(
            and_(
                StaffPerformance.staff_id == staff_id,
                func.date(StaffPerformance.date) == date.date()
            )
        ).first()

        if performance:
            # Update existing record
            for key, value in metrics.items():
                if hasattr(performance, key):
                    setattr(performance, key, value)
        else:
            # Create new record
            performance = StaffPerformance(
                staff_id=staff_id,
                date=date,
                **metrics
            )
            db.add(performance)

        db.commit()
        db.refresh(performance)
        return performance

    def get_staff_performance(self, db: Session, staff_id: int, start_date: datetime, end_date: datetime) -> List[StaffPerformance]:
        """Get staff performance metrics for a date range."""
        return db.query(StaffPerformance).filter(
            and_(
                StaffPerformance.staff_id == staff_id,
                StaffPerformance.date >= start_date,
                StaffPerformance.date <= end_date
            )
        ).order_by(StaffPerformance.date).all()

    def send_staff_message(self, db: Session, message_data: Dict[str, Any]) -> StaffCommunication:
        """Send a message to staff member(s)."""
        message = StaffCommunication(
            sender_id=message_data["sender_id"],
            recipient_id=message_data.get("recipient_id"),
            subject=message_data["subject"],
            message=message_data["message"],
            message_type=message_data.get("message_type", "direct"),
            priority=message_data.get("priority", "normal"),
            department_filter=message_data.get("department_filter"),
            role_filter=message_data.get("role_filter"),
            expires_at=message_data.get("expires_at")
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_staff_messages(self, db: Session, user_id: int, unread_only: bool = False) -> List[StaffCommunication]:
        """Get messages for a staff member."""
        query = db.query(StaffCommunication).filter(
            or_(
                StaffCommunication.recipient_id == user_id,
                and_(
                    StaffCommunication.recipient_id.is_(None),
                    or_(
                        StaffCommunication.department_filter.is_(None),
                        StaffCommunication.department_filter == self._get_user_department(db, user_id)
                    ),
                    or_(
                        StaffCommunication.role_filter.is_(None),
                        StaffCommunication.role_filter == self._get_user_role(db, user_id)
                    )
                )
            )
        )

        if unread_only:
            query = query.filter(StaffCommunication.is_read == False)

        return query.order_by(StaffCommunication.created_at.desc()).all()

    def mark_message_read(self, db: Session, message_id: int, user_id: int) -> bool:
        """Mark a message as read."""
        message = db.query(StaffCommunication).filter(
            and_(
                StaffCommunication.id == message_id,
                or_(
                    StaffCommunication.recipient_id == user_id,
                    StaffCommunication.recipient_id.is_(None)
                )
            )
        ).first()

        if message:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def create_staff_task(self, db: Session, task_data: Dict[str, Any]) -> StaffTask:
        """Create a task for staff member."""
        task = StaffTask(
            title=task_data["title"],
            description=task_data.get("description"),
            assigned_to=task_data["assigned_to"],
            assigned_by=task_data["assigned_by"],
            task_type=task_data.get("task_type", "other"),
            priority=task_data.get("priority", "normal"),
            status=task_data.get("status", "pending"),
            due_date=task_data.get("due_date"),
            estimated_hours=task_data.get("estimated_hours"),
            department=task_data.get("department"),
            service_id=task_data.get("service_id"),
            patient_id=task_data.get("patient_id"),
            notes=task_data.get("notes")
        )

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get_staff_tasks(self, db: Session, staff_id: int, status_filter: Optional[str] = None) -> List[StaffTask]:
        """Get tasks assigned to a staff member."""
        query = db.query(StaffTask).filter(StaffTask.assigned_to == staff_id)

        if status_filter:
            query = query.filter(StaffTask.status == status_filter)

        return query.order_by(StaffTask.created_at.desc()).all()

    def update_task_status(self, db: Session, task_id: int, status: str, staff_id: int) -> Optional[StaffTask]:
        """Update task status."""
        task = db.query(StaffTask).filter(
            and_(
                StaffTask.id == task_id,
                StaffTask.assigned_to == staff_id
            )
        ).first()

        if task:
            task.status = status
            if status == "completed":
                task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

        return task

    def get_system_settings(self, db: Session, category: Optional[str] = None) -> Dict[str, Any]:
        """Get system settings."""
        query = db.query(SystemSettings)
        if category:
            query = query.filter(SystemSettings.category == category)

        settings = query.all()
        return {setting.setting_key: self._parse_setting_value(setting) for setting in settings}

    def update_system_setting(self, db: Session, key: str, value: Any, updated_by: int) -> bool:
        """Update a system setting."""
        setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()

        if setting:
            setting.setting_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            setting.updated_by = updated_by
            setting.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def log_audit_event(self, db: Session, audit_data: Dict[str, Any]) -> AuditLog:
        """Log an audit event."""
        audit_log = AuditLog(
            user_id=audit_data.get("user_id"),
            action=audit_data["action"],
            resource_type=audit_data["resource_type"],
            resource_id=audit_data.get("resource_id"),
            old_values=json.dumps(audit_data.get("old_values")) if audit_data.get("old_values") else None,
            new_values=json.dumps(audit_data.get("new_values")) if audit_data.get("new_values") else None,
            ip_address=audit_data.get("ip_address"),
            user_agent=audit_data.get("user_agent"),
            success=audit_data.get("success", True),
            error_message=audit_data.get("error_message")
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    def get_audit_logs(self, db: Session, filters: Dict[str, Any] = None, limit: int = 100) -> List[AuditLog]:
        """Get audit logs with optional filters."""
        query = db.query(AuditLog)

        if filters:
            if "user_id" in filters:
                query = query.filter(AuditLog.user_id == filters["user_id"])
            if "action" in filters:
                query = query.filter(AuditLog.action == filters["action"])
            if "resource_type" in filters:
                query = query.filter(AuditLog.resource_type == filters["resource_type"])
            if "start_date" in filters:
                query = query.filter(AuditLog.timestamp >= filters["start_date"])
            if "end_date" in filters:
                query = query.filter(AuditLog.timestamp <= filters["end_date"])

        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    def check_permission(self, db: Session, user_id: int, resource: str, action: str) -> bool:
        """Check if user has permission for an action on a resource."""
        user = get_user_by_id(db, user_id)
        if not user:
            return False

        # Admins have all permissions
        if user.role == "admin":
            return True

        # Check role-based permissions
        permission = db.query(RolePermission).filter(
            and_(
                RolePermission.role == user.role,
                RolePermission.resource == resource,
                RolePermission.action == action
            )
        ).first()

        return permission.allowed if permission else False

    def get_departments(self, db: Session, active_only: bool = True) -> List[Department]:
        """Get all departments."""
        query = db.query(Department)
        if active_only:
            query = query.filter(Department.is_active == True)
        return query.all()

    def create_department(self, db: Session, dept_data: Dict[str, Any]) -> Department:
        """Create a new department."""
        department = Department(
            name=dept_data["name"],
            description=dept_data.get("description"),
            head_id=dept_data.get("head_id"),
            parent_department_id=dept_data.get("parent_department_id"),
            budget_allocated=dept_data.get("budget_allocated"),
            color_code=dept_data.get("color_code"),
            icon_name=dept_data.get("icon_name")
        )

        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    def _get_user_department(self, db: Session, user_id: int) -> Optional[str]:
        """Get user's department."""
        profile = self.get_staff_profile(db, user_id)
        return profile.department if profile else None

    def _get_user_role(self, db: Session, user_id: int) -> Optional[str]:
        """Get user's role."""
        user = get_user_by_id(db, user_id)
        return user.role if user else None

    def _parse_setting_value(self, setting: SystemSettings) -> Any:
        """Parse setting value based on type."""
        if setting.setting_type == "boolean":
            return setting.setting_value.lower() == "true"
        elif setting.setting_type == "integer":
            return int(setting.setting_value)
        elif setting.setting_type == "float":
            return float(setting.setting_value)
        elif setting.setting_type == "json":
            return json.loads(setting.setting_value)
        else:
            return setting.setting_value


# Global staff service instance
staff_service = StaffService()