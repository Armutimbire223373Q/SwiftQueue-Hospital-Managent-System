"""
Demo Data Generator for SwiftQueue Hospital Management System
Simple version that matches the actual database models
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.models import (
    User, Service, ServiceCounter, QueueEntry, Appointment,
    Notification, Checkin, Schedule, EmergencyDispatch, Analytics, Base
)

# Simple password hashing for demo - faster than bcrypt
import hashlib
def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("\n" + "="*60)
    print("  SwiftQueue Demo Data Generator")
    print("="*60 + "\n")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Create Services
        print("🏥 Creating services...")
        services = []
        departments = ["Emergency", "Cardiology", "Pediatrics", "Radiology", "General"]
        service_data = [
            ("General Consultation", "General medical consultation", 30, "General"),
            ("Emergency Care", "Emergency medical treatment", 45, "Emergency"),
            ("Cardiology Consultation", "Heart specialist", 45, "Cardiology"),
            ("Pediatric Care", "Children's medical care", 30, "Pediatrics"),
            ("X-Ray Imaging", "X-ray imaging", 20, "Radiology"),
            ("Blood Test", "Laboratory testing", 15, "General"),
            ("CT Scan", "CT imaging", 30, "Radiology"),
            ("Vaccination", "Immunization services", 15, "Pediatrics"),
        ]
        
        for name, desc, est_time, dept in service_data:
            service = Service(
                name=name,
                description=desc,
                estimated_time=est_time,
                department=dept,
                current_wait_time=random.randint(10, 60),
                queue_length=random.randint(0, 10),
                staff_count=random.randint(1, 3),
                service_rate=random.uniform(0.5, 2.0)
            )
            db.add(service)
            services.append(service)
        db.commit()
        print(f"   ✅ Created {len(services)} services")
        
        # Create Users
        print("👥 Creating users...")
        users = []
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@hospital.com").first()
        if existing_admin:
            print("   ℹ️  Admin user already exists, using existing")
            users.append(existing_admin)
        else:
            admin = User(
                name="System Administrator",
                email="admin@hospital.com",
                phone="+1234567890",
                password_hash=get_password_hash("Admin123!"),
                role="admin",
                date_of_birth=datetime.now() - timedelta(days=365*35)
            )
            db.add(admin)
            users.append(admin)
        
        # Staff
        staff_data = [
            ("Dr. John Smith", "dr.smith@hospital.com"),
            ("Dr. Sarah Johnson", "dr.johnson@hospital.com"),
            ("Nurse Emily Williams", "nurse.williams@hospital.com"),
            ("Dr. Michael Brown", "dr.brown@hospital.com"),
            ("Dr. Jessica Davis", "dr.davis@hospital.com"),
        ]
        
        for name, email in staff_data:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                users.append(existing)
            else:
                user = User(
                    name=name,
                    email=email,
                    phone=f"+12345678{random.randint(10,99)}",
                    password_hash=get_password_hash("Staff123!"),
                    role="staff",
                    date_of_birth=datetime.now() - timedelta(days=365*random.randint(30,50))
                )
                db.add(user)
                users.append(user)
        
        # Patients
        patient_names = [
            ("John Doe", "john.doe@email.com"),
            ("Jane Smith", "jane.smith@email.com"),
            ("Robert Jones", "robert.jones@email.com"),
            ("Mary Williams", "mary.williams@email.com"),
            ("James Miller", "james.miller@email.com"),
            ("Patricia Davis", "patricia.davis@email.com"),
            ("Michael Garcia", "michael.garcia@email.com"),
            ("Linda Rodriguez", "linda.rodriguez@email.com"),
        ]
        
        for name, email in patient_names:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                users.append(existing)
            else:
                user = User(
                    name=name,
                    email=email,
                    phone=f"+12345678{random.randint(10,99)}",
                    password_hash=get_password_hash("Patient123!"),
                    role="patient",
                    date_of_birth=datetime.now() - timedelta(days=365*random.randint(20,60))
                )
                db.add(user)
                users.append(user)
        
        db.commit()
        print(f"   ✅ Created {len(users)} users (1 admin, 5 staff, 8 patients)")
        
        # Get users by role
        staff_users = [u for u in users if u.role == "staff"]
        patient_users = [u for u in users if u.role == "patient"]
        
        # Create Service Counters
        print("🪟 Creating service counters...")
        counters = []
        for i, service in enumerate(services):
            num_counters = random.randint(1, 2)
            for j in range(num_counters):
                counter = ServiceCounter(
                    name=f"Counter {chr(65 + i)}{j + 1}",
                    service_id=service.id,
                    is_active=1,
                    staff_member=random.choice(staff_users).name if random.random() > 0.3 else None
                )
                db.add(counter)
                counters.append(counter)
        db.commit()
        print(f"   ✅ Created {len(counters)} service counters")
        
        # Create Queue Entries
        print("📝 Creating queue entries...")
        queue_entries = []
        statuses = ["waiting", "called", "serving", "completed"]
        priorities = ["low", "medium", "high", "urgent"]
        
        for i in range(25):
            patient = random.choice(patient_users)
            service = random.choice(services)
            created = datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(0,23))
            status = random.choice(statuses)
            
            entry = QueueEntry(
                patient_id=patient.id,
                service_id=service.id,
                queue_number=1000 + i,
                status=status,
                priority=random.choice(priorities),
                created_at=created,
                estimated_wait_time=random.randint(15, 90),
                ai_predicted_wait=random.randint(10, 85),
                completed_at=created + timedelta(minutes=random.randint(30,90)) if status == "completed" else None
            )
            db.add(entry)
            queue_entries.append(entry)
        db.commit()
        print(f"   ✅ Created {len(queue_entries)} queue entries")
        
        # Create Appointments
        print("📅 Creating appointments...")
        appointments = []
        statuses = ["scheduled", "confirmed", "in_progress", "completed", "cancelled"]
        
        for i in range(30):
            patient = random.choice(patient_users)
            service = random.choice(services)
            staff = random.choice(staff_users)
            
            appt_date = datetime.now() + timedelta(days=random.randint(-7, 14), hours=random.randint(8,17))
            
            if appt_date < datetime.now() - timedelta(days=1):
                status = random.choice(["completed", "cancelled"])
            elif appt_date < datetime.now():
                status = "in_progress"
            else:
                status = random.choice(["scheduled", "confirmed"])
            
            appt = Appointment(
                patient_id=patient.id,
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=appt_date,
                duration=service.estimated_time,
                status=status,
                notes=f"Appointment for {service.name}"
            )
            db.add(appt)
            appointments.append(appt)
        db.commit()
        print(f"   ✅ Created {len(appointments)} appointments")
        
        # Create Check-ins
        print("✅ Creating check-ins...")
        checkins = []
        for appt in appointments[:15]:
            if appt.status in ["in_progress", "completed"]:
                checkin = Checkin(
                    appointment_id=appt.id,
                    patient_id=appt.patient_id,
                    checkin_time=appt.appointment_date - timedelta(minutes=random.randint(5,30)),
                    status="checked_in"
                )
                db.add(checkin)
                checkins.append(checkin)
        db.commit()
        print(f"   ✅ Created {len(checkins)} check-ins")
        
        # Create Staff Schedules
        print("📆 Creating staff schedules...")
        schedules = []
        for staff in staff_users:
            for day in range(7):  # Days of week
                if random.random() > 0.2:  # 80% chance of working
                    schedule = Schedule(
                        staff_id=staff.id,
                        day_of_week=day,
                        start_time="08:00",
                        end_time="17:00" if random.random() > 0.3 else "14:00",
                        is_available=True
                    )
                    db.add(schedule)
                    schedules.append(schedule)
        db.commit()
        print(f"   ✅ Created {len(schedules)} staff schedules")
        
        # Create Notifications
        print("🔔 Creating notifications...")
        notifications = []
        notif_templates = [
            ("Appointment Reminder", "Your appointment is tomorrow at 10:00 AM", "info"),
            ("Queue Update", "You are now number 3 in the queue", "info"),
            ("Test Results Ready", "Your lab results are available", "success"),
            ("Appointment Confirmed", "Your appointment has been confirmed", "success"),
            ("Payment Received", "Payment processed successfully", "success"),
        ]
        
        for user in users:
            num_notifs = random.randint(2, 5)
            for _ in range(num_notifs):
                title, message, ntype = random.choice(notif_templates)
                notif = Notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    type=ntype,
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(0,7))
                )
                db.add(notif)
                notifications.append(notif)
        db.commit()
        print(f"   ✅ Created {len(notifications)} notifications")
        
        # Create Emergency Dispatches
        print("🚨 Creating emergency dispatches...")
        dispatches = []
        dispatch_statuses = ["pending", "dispatched", "en_route", "arrived", "completed"]
        
        for i in range(10):
            patient = random.choice(patient_users)
            status = random.choice(dispatch_statuses)
            created = datetime.now() - timedelta(days=random.randint(0,7))
            
            dispatch = EmergencyDispatch(
                patient_id=patient.id,
                emergency_details=f"Emergency case {i+1}",
                dispatch_address=f"{random.randint(100,999)} Main St, City",
                dispatch_status=status,
                dispatched_at=created if status != "pending" else None,
                response_time=random.randint(5,30) if status in ["completed", "arrived"] else None,
                ambulance_id=f"AMB{random.randint(100,999)}" if status != "pending" else None,
                created_at=created
            )
            db.add(dispatch)
            dispatches.append(dispatch)
        db.commit()
        print(f"   ✅ Created {len(dispatches)} emergency dispatches")
        
        # Create Analytics Data
        print("📊 Creating analytics data...")
        analytics_records = []
        for service in services:
            for day in range(7):
                timestamp = datetime.now() - timedelta(days=day)
                analytics = Analytics(
                    timestamp=timestamp,
                    service_id=service.id,
                    queue_length=random.randint(0, 15),
                    avg_wait_time=random.uniform(10, 60),
                    avg_service_time=random.uniform(15, 45),
                    efficiency_score=random.uniform(0.6, 0.95),
                    peak_hour=random.randint(9, 16),
                    peak_load=random.randint(10, 30),
                    staff_utilization=random.uniform(0.5, 0.9),
                    patient_satisfaction=random.uniform(0.7, 0.95),
                    patients_served=random.randint(20, 80)
                )
                db.add(analytics)
                analytics_records.append(analytics)
        db.commit()
        print(f"   ✅ Created {len(analytics_records)} analytics records")
        
        print("\n✅ Demo Data Generation Complete!")
        print("\n📊 Summary:")
        print(f"  • Services: {len(services)}")
        print(f"  • Users: {len(users)} (1 admin, 5 staff, 8 patients)")
        print(f"  • Service Counters: {len(counters)}")
        print(f"  • Queue Entries: {len(queue_entries)}")
        print(f"  • Appointments: {len(appointments)}")
        print(f"  • Check-ins: {len(checkins)}")
        print(f"  • Staff Schedules: {len(schedules)}")
        print(f"  • Notifications: {len(notifications)}")
        print(f"  • Emergency Dispatches: {len(dispatches)}")
        print(f"  • Analytics Records: {len(analytics_records)}")
        
        print("\n🔐 Demo Credentials:")
        print("  Admin:")
        print("    Email: admin@hospital.com")
        print("    Password: Admin123!")
        print("\n  Staff:")
        print("    Email: dr.smith@hospital.com")
        print("    Password: Staff123!")
        print("\n  Patient:")
        print("    Email: john.doe@email.com")
        print("    Password: Patient123!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("  Done! Start your server and login.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
