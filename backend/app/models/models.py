from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    date_of_birth = Column(DateTime)

class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    queue_number = Column(Integer, index=True)
    status = Column(Enum("waiting", "called", "serving", "completed", name="queue_status"))
    priority = Column(Enum("low", "medium", "high", "urgent", name="priority_level"))
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_wait_time = Column(Integer)
    ai_predicted_wait = Column(Integer)

    patient = relationship("User")
    service = relationship("Service")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    department = Column(String)
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
