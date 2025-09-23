"""
Enhanced Database Models for Multi-Stage Hospital Workflow
Based on insights from the comprehensive hospital dataset
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Patient(Base):
    """Enhanced patient model with comprehensive information"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)  # P100000 format
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    date_of_birth = Column(DateTime)
    age_group = Column(Enum("Pediatric (0-17)", "Young Adult (18-35)", "Adult (36-60)", "Senior (61+)", name="age_group"))
    insurance_type = Column(Enum("Private", "Medicare", "Medicaid", "Self-pay", "None", name="insurance_type"))
    
    # Relationships
    visits = relationship("PatientVisit", back_populates="patient")

class PatientVisit(Base):
    """Comprehensive patient visit tracking through all stages"""
    __tablename__ = "patient_visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(String, unique=True, index=True)  # V100000 format
    
    # Visit Information
    department = Column(Enum("Emergency", "Cardiology", "Orthopedics", "Neurology", "Oncology", 
                           "Pediatrics", "Internal Medicine", "General Surgery", "Radiology", 
                           "Obstetrics", name="department"))
    appointment_type = Column(Enum("New Patient", "Specialist Referral", "Urgent Care", "Follow-up", name="appointment_type"))
    booking_type = Column(Enum("Online", "Walk-in", "Phone", name="booking_type"))
    is_online_booking = Column(Boolean, default=False)
    
    # Triage Information
    triage_category = Column(Enum("Emergency", "Urgent", "Semi-urgent", "Non-urgent", name="triage_category"))
    reason_for_visit = Column(Text)
    consultation_needed = Column(Boolean, default=False)
    
    # Timing Information
    appointment_time = Column(DateTime)
    actual_arrival_time = Column(DateTime)
    registration_time = Column(DateTime)
    check_in_time = Column(DateTime)
    first_seen_by_nurse_time = Column(DateTime)
    triage_complete_time = Column(DateTime)
    provider_start_time = Column(DateTime)
    provider_end_time = Column(DateTime)
    tests_complete_time = Column(DateTime)
    discharge_time = Column(DateTime)
    
    # Calculated Wait Times
    arrival_delay_time = Column(Float)  # minutes
    registration_wait_time = Column(Float)
    registration_to_checkin_time = Column(Float)
    checkin_to_nurse_time = Column(Float)
    nurse_to_triage_time = Column(Float)
    triage_to_provider_time = Column(Float)
    consultation_duration = Column(Float)
    provider_to_tests_time = Column(Float)
    tests_to_discharge_time = Column(Float)
    total_time_in_hospital = Column(Float)
    total_delay_time = Column(Float)
    
    # Resource Information
    provider_id = Column(String)
    room_number = Column(String)
    facility_occupancy_rate = Column(Float)
    providers_on_shift = Column(Integer)
    nurses_on_shift = Column(Integer)
    staff_to_patient_ratio = Column(Float)
    
    # Status Tracking
    current_stage = Column(Enum("Scheduled", "Arrived", "Registered", "Checked-in", "Triage", 
                              "Provider", "Tests", "Discharged", name="visit_stage"))
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="visits")
    workflow_stages = relationship("WorkflowStage", back_populates="visit")

class WorkflowStage(Base):
    """Track individual stages of patient workflow"""
    __tablename__ = "workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("patient_visits.id"))
    stage_name = Column(Enum("Registration", "Check-in", "Triage", "Provider", "Tests", "Discharge", name="stage_name"))
    stage_order = Column(Integer)  # 1, 2, 3, etc.
    
    # Timing
    stage_start_time = Column(DateTime)
    stage_end_time = Column(DateTime)
    stage_duration = Column(Float)  # minutes
    
    # Stage-specific data
    stage_data = Column(Text)  # JSON string for stage-specific information
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    visit = relationship("PatientVisit", back_populates="workflow_stages")

class Department(Base):
    """Enhanced department model with performance metrics"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    
    # Performance Metrics
    avg_wait_time = Column(Float)
    avg_total_time = Column(Float)
    avg_occupancy_rate = Column(Float)
    typical_tests = Column(Text)  # JSON string of common tests
    
    # Resource Allocation
    providers_count = Column(Integer, default=1)
    nurses_count = Column(Integer, default=1)
    rooms_count = Column(Integer, default=1)
    
    # Relationships
    visits = relationship("PatientVisit")

class Provider(Base):
    """Provider/Doctor information"""
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String, unique=True, index=True)  # DR1, DR2, etc.
    name = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    specialization = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Performance Metrics
    avg_consultation_time = Column(Float)
    patients_served_today = Column(Integer, default=0)
    
    # Relationships
    department = relationship("Department")

class TestOrder(Base):
    """Track ordered tests and their completion"""
    __tablename__ = "test_orders"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("patient_visits.id"))
    test_type = Column(Enum("Basic labs", "Comprehensive labs", "X-ray", "CT scan", "Ultrasound", 
                          "MRI", "Biopsy", "Stress test", "None", name="test_type"))
    
    # Timing
    ordered_time = Column(DateTime)
    started_time = Column(DateTime)
    completed_time = Column(DateTime)
    estimated_duration = Column(Float)  # minutes
    
    # Status
    status = Column(Enum("Ordered", "In Progress", "Completed", "Cancelled", name="test_status"))
    
    # Relationships
    visit = relationship("PatientVisit")

class FacilityMetrics(Base):
    """Real-time facility metrics"""
    __tablename__ = "facility_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Occupancy Metrics
    overall_occupancy_rate = Column(Float)
    department_occupancy = Column(Text)  # JSON string
    
    # Staff Metrics
    total_providers_on_shift = Column(Integer)
    total_nurses_on_shift = Column(Integer)
    staff_to_patient_ratio = Column(Float)
    
    # Queue Metrics
    total_patients_waiting = Column(Integer)
    avg_wait_time = Column(Float)
    longest_wait_time = Column(Float)
    
    # Performance Metrics
    patients_completed_today = Column(Integer)
    avg_total_time = Column(Float)

class WorkflowAnalytics(Base):
    """Analytics for workflow optimization"""
    __tablename__ = "workflow_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Stage Performance
    avg_registration_time = Column(Float)
    avg_triage_time = Column(Float)
    avg_provider_time = Column(Float)
    avg_test_time = Column(Float)
    
    # Bottleneck Analysis
    bottleneck_stage = Column(String)
    bottleneck_duration = Column(Float)
    
    # Efficiency Metrics
    total_patients = Column(Integer)
    completed_patients = Column(Integer)
    completion_rate = Column(Float)
    
    # Relationships
    department = relationship("Department")
