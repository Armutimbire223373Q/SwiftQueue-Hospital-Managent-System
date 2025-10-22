from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    street_address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    date_of_birth = Column(DateTime)
    password_hash = Column(String, nullable=True)  # Nullable to allow users created via queue join
    role = Column(Enum("admin", "staff", "patient", name="user_role"), default="patient")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Password reset fields
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    queue_number = Column(Integer, index=True)
    status = Column(Enum("waiting", "called", "serving", "completed", name="queue_status"))
    priority = Column(Enum("low", "medium", "high", "urgent", name="priority_level"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    estimated_wait_time = Column(Integer)
    ai_predicted_wait = Column(Integer)

    patient = relationship("User")
    service = relationship("Service")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    appointment_date = Column(DateTime)
    duration = Column(Integer)  # in minutes
    status = Column(Enum("scheduled", "confirmed", "in_progress", "completed", "cancelled", name="appointment_status"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    service = relationship("Service")
    staff = relationship("User", foreign_keys=[staff_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(Enum("info", "warning", "success", "error", name="notification_type"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    checkin_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("checked_in", "no_show", "cancelled", name="checkin_status"))

    appointment = relationship("Appointment")
    patient = relationship("User")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    staff_count = Column(Integer, default=1)  # Number of staff assigned
    service_rate = Column(Float, default=1.0)  # Average patients served per hour
    department = Column(String, default="General")
    estimated_time = Column(Integer)
    current_wait_time = Column(Integer)
    queue_length = Column(Integer, default=0)

class ServiceCounter(Base):
    __tablename__ = "service_counters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    service_id = Column(Integer, ForeignKey("services.id"))
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean
    current_queue_entry_id = Column(Integer, ForeignKey("queue_entries.id"), nullable=True)
    staff_member = Column(String, nullable=True)
    
class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    service_id = Column(Integer, ForeignKey("services.id"))
    queue_length = Column(Integer)
    avg_wait_time = Column(Float)
    avg_service_time = Column(Float)
    efficiency_score = Column(Float)  # 0-1 score based on performance metrics
    peak_hour = Column(Integer)  # Hour of day (0-23)
    peak_load = Column(Integer)  # Number of patients during peak hour
    staff_utilization = Column(Float)  # 0-1 score
    patient_satisfaction = Column(Float)  # 0-1 score based on feedback
    patients_served = Column(Integer)

    service = relationship("Service")

class EmergencyDispatch(Base):
    __tablename__ = "emergency_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    emergency_details = Column(Text, nullable=False)
    dispatch_address = Column(String, nullable=False)
    dispatch_status = Column(Enum("pending", "dispatched", "en_route", "arrived", "completed", "cancelled", name="dispatch_status"), default="pending")
    dispatched_at = Column(DateTime, nullable=True)
    response_time = Column(Integer, nullable=True)  # in minutes
    ambulance_id = Column(String, nullable=True)  # simulated ambulance identifier
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday-Sunday)
    start_time = Column(String, nullable=False)  # Store as HH:MM format
    end_time = Column(String, nullable=False)  # Store as HH:MM format
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staff = relationship("User", backref="schedules")
