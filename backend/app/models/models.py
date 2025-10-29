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


# ==================== PRESCRIPTION MANAGEMENT ====================

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    prescription_number = Column(String, unique=True, index=True, nullable=False)
    diagnosis = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum("active", "completed", "cancelled", "expired", name="prescription_status"), default="active")
    issue_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    refills_allowed = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    medications = relationship("PrescriptionMedication", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionMedication(Base):
    __tablename__ = "prescription_medications"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medication_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)  # e.g., "500mg"
    frequency = Column(String, nullable=False)  # e.g., "twice daily"
    duration = Column(String, nullable=False)  # e.g., "7 days"
    quantity = Column(Integer, nullable=False)  # Total quantity prescribed
    instructions = Column(Text, nullable=True)  # Special instructions
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription", back_populates="medications")


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String, nullable=False, index=True)
    drug_b = Column(String, nullable=False, index=True)
    severity = Column(Enum("minor", "moderate", "major", "severe", name="interaction_severity"), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PrescriptionRefill(Base):
    __tablename__ = "prescription_refills"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    refill_date = Column(DateTime, default=datetime.utcnow)
    dispensed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    pharmacy_notes = Column(Text, nullable=True)
    status = Column(Enum("pending", "approved", "dispensed", "rejected", name="refill_status"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription")
    dispenser = relationship("User")


# ==================== INVENTORY MANAGEMENT ====================

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False, index=True)
    item_code = Column(String, unique=True, nullable=False, index=True)
    category = Column(Enum("medication", "equipment", "supplies", "other", name="inventory_category"), nullable=False)
    description = Column(Text, nullable=True)
    unit_of_measure = Column(String, nullable=False)  # e.g., "boxes", "bottles", "units"
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=10)
    maximum_stock = Column(Integer, nullable=True)
    reorder_point = Column(Integer, default=20)
    unit_cost = Column(Float, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    location = Column(String, nullable=True)  # Storage location
    expiry_date = Column(DateTime, nullable=True)
    batch_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_restocked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier")
    stock_movements = relationship("StockMovement", back_populates="item", cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    payment_terms = Column(String, nullable=True)  # e.g., "Net 30"
    rating = Column(Float, nullable=True)  # Supplier performance rating (0-5)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    movement_type = Column(Enum("in", "out", "adjustment", "expired", "damaged", name="movement_type"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_number = Column(String, nullable=True)  # PO number, invoice number, etc.
    reason = Column(String, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    movement_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("InventoryItem", back_populates="stock_movements")
    user = relationship("User")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    status = Column(Enum("draft", "pending", "approved", "ordered", "received", "cancelled", name="po_status"), default="draft")
    total_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[ordered_by])
    approver = relationship("User", foreign_keys=[approved_by])


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("InventoryItem")


# ==================== PATIENT PORTAL FEATURES ====================

class PatientMessage(Base):
    __tablename__ = "patient_messages"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(Enum("general", "appointment", "prescription", "billing", "emergency", name="message_type"), default="general")
    priority = Column(Enum("low", "normal", "high", "urgent", name="message_priority"), default="normal")
    status = Column(Enum("unread", "read", "replied", "closed", name="message_status"), default="unread")
    is_patient_sender = Column(Boolean, default=True)  # True if sent by patient, False if staff reply
    parent_message_id = Column(Integer, ForeignKey("patient_messages.id"), nullable=True)  # For threading
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    patient = relationship("User", foreign_keys=[patient_id])
    staff = relationship("User", foreign_keys=[staff_id])
    replies = relationship("PatientMessage", backref="parent", remote_side=[id])


class PatientDocument(Base):
    __tablename__ = "patient_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(Enum("lab_result", "imaging", "prescription", "discharge_summary", "consent_form", "insurance", "other", name="document_type"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_patient_visible = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])


class PatientPreference(Base):
    __tablename__ = "patient_preferences"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    notification_email = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    appointment_reminder_days = Column(Integer, default=1)  # Days before appointment
    preferred_language = Column(String, default="en")
    preferred_communication = Column(Enum("email", "sms", "phone", "portal", name="communication_method"), default="email")
    share_medical_history = Column(Boolean, default=True)
    allow_marketing = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User", backref="preferences")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_name = Column(String, nullable=False)
    test_category = Column(String, nullable=True)  # e.g., "Blood", "Urine", "Radiology"
    result_value = Column(String, nullable=True)
    normal_range = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    status = Column(Enum("pending", "in_progress", "completed", "cancelled", name="lab_status"), default="pending")
    abnormal_flag = Column(Boolean, default=False)
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    test_date = Column(DateTime, nullable=True)
    result_date = Column(DateTime, nullable=True)
    is_patient_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    ordering_doctor = relationship("User", foreign_keys=[ordered_by])
    lab_technician = relationship("User", foreign_keys=[performed_by])
