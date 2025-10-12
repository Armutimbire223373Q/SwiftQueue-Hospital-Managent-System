"""
Staff management models for Healthcare Queue Management System
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class StaffProfile(Base):
    """Extended staff profile information."""
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    employee_id = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    specialization = Column(String)
    license_number = Column(String, nullable=True)
    years_experience = Column(Integer, default=0)
    certifications = Column(Text, nullable=True)  # JSON string of certifications
    performance_rating = Column(Float, default=0.0)  # 0-5 scale
    is_supervisor = Column(Boolean, default=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hire_date = Column(DateTime)
    contract_type = Column(Enum("full_time", "part_time", "contract", "temporary", name="contract_type"))
    hourly_rate = Column(Float, nullable=True)
    max_patients_per_hour = Column(Integer, default=4)
    languages_spoken = Column(Text, nullable=True)  # JSON array of languages
    emergency_certified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    supervisor = relationship("User", foreign_keys=[supervisor_id])


class StaffSchedule(Base):
    """Staff scheduling and shift management."""
    __tablename__ = "staff_schedules"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"))
    shift_date = Column(DateTime, index=True)
    shift_type = Column(Enum("morning", "afternoon", "night", "weekend", "holiday", name="shift_type"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    break_duration = Column(Integer, default=30)  # minutes
    is_active = Column(Boolean, default=True)
    assigned_service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staff = relationship("User", foreign_keys=[staff_id])
    service = relationship("Service")
    creator = relationship("User", foreign_keys=[created_by])


class StaffPerformance(Base):
    """Staff performance tracking and metrics."""
    __tablename__ = "staff_performance"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, index=True)
    patients_served = Column(Integer, default=0)
    avg_service_time = Column(Float)  # minutes
    patient_satisfaction = Column(Float, default=0.0)  # 0-5 scale
    efficiency_score = Column(Float, default=0.0)  # 0-1 scale
    attendance_score = Column(Float, default=1.0)  # 0-1 scale
    quality_score = Column(Float, default=0.0)  # 0-1 scale
    total_score = Column(Float, default=0.0)  # weighted average
    shift_duration = Column(Integer)  # minutes
    breaks_taken = Column(Integer, default=0)
    emergency_responses = Column(Integer, default=0)
    feedback_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    staff = relationship("User")


class StaffCommunication(Base):
    """Staff communication and messaging system."""
    __tablename__ = "staff_communications"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for broadcasts
    subject = Column(String)
    message = Column(Text)
    message_type = Column(Enum("direct", "broadcast", "announcement", "alert", "task", name="message_type"))
    priority = Column(Enum("low", "normal", "high", "urgent", name="message_priority"), default="normal")
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    department_filter = Column(String, nullable=True)  # for targeted broadcasts
    role_filter = Column(String, nullable=True)  # for role-based broadcasts
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])


class StaffTask(Base):
    """Staff task management and assignments."""
    __tablename__ = "staff_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_by = Column(Integer, ForeignKey("users.id"))
    task_type = Column(Enum("maintenance", "training", "audit", "emergency_prep", "quality_check", "other", name="task_type"))
    priority = Column(Enum("low", "normal", "high", "urgent", name="task_priority"), default="normal")
    status = Column(Enum("pending", "in_progress", "completed", "cancelled", "overdue", name="task_status"), default="pending")
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    department = Column(String, nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship("User", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    service = relationship("Service")
    patient = relationship("User", foreign_keys=[patient_id])


class StaffTraining(Base):
    """Staff training and certification tracking."""
    __tablename__ = "staff_training"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"))
    training_name = Column(String)
    training_type = Column(Enum("mandatory", "optional", "certification", "skill_development", name="training_type"))
    provider = Column(String)
    completion_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    status = Column(Enum("assigned", "in_progress", "completed", "expired", "failed", name="training_status"), default="assigned")
    score = Column(Float, nullable=True)  # for scored trainings
    certificate_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staff = relationship("User")


class SystemSettings(Base):
    """System-wide settings and configuration."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, index=True)
    setting_value = Column(Text)
    setting_type = Column(Enum("string", "integer", "float", "boolean", "json", name="setting_type"))
    category = Column(String, index=True)  # e.g., "queue", "emergency", "staff", "system"
    description = Column(Text, nullable=True)
    is_system_setting = Column(Boolean, default=False)  # system vs user configurable
    requires_restart = Column(Boolean, default=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    updater = relationship("User")


class AuditLog(Base):
    """System audit logging for compliance and security."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, index=True)  # e.g., "login", "update_patient", "delete_record"
    resource_type = Column(String, index=True)  # e.g., "user", "appointment", "queue"
    resource_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON of old values
    new_values = Column(Text, nullable=True)  # JSON of new values
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    user = relationship("User")


class Department(Base):
    """Department management and organization."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    head_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    budget_allocated = Column(Float, nullable=True)
    staff_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    color_code = Column(String, nullable=True)  # for UI theming
    icon_name = Column(String, nullable=True)  # for UI icons
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    head = relationship("User", foreign_keys=[head_id])
    parent = relationship("Department", remote_side=[id])


class RolePermission(Base):
    """Role-based permissions system."""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum("admin", "staff", "patient", name="user_role"))
    resource = Column(String, index=True)  # e.g., "users", "appointments", "queue"
    action = Column(String, index=True)  # e.g., "create", "read", "update", "delete"
    allowed = Column(Boolean, default=False)
    conditions = Column(Text, nullable=True)  # JSON conditions for fine-grained control
    created_at = Column(DateTime, default=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )