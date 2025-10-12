#!/usr/bin/env python3
"""
Initialize staff data and permissions for Healthcare Queue Management System
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.models import User
from app.models.staff_models import (
    StaffProfile, StaffSchedule, Department, RolePermission,
    SystemSettings
)
from app.services.auth_service import get_password_hash
from datetime import datetime, timedelta


def init_departments(db):
    """Initialize default departments."""
    departments = [
        {
            "name": "Emergency Medicine",
            "description": "Emergency and critical care services",
            "color_code": "#ef4444",
            "icon_name": "ambulance"
        },
        {
            "name": "Internal Medicine",
            "description": "General internal medicine and diagnostics",
            "color_code": "#3b82f6",
            "icon_name": "stethoscope"
        },
        {
            "name": "Surgery",
            "description": "Surgical procedures and post-operative care",
            "color_code": "#10b981",
            "icon_name": "scissors"
        },
        {
            "name": "Pediatrics",
            "description": "Child healthcare and development",
            "color_code": "#f59e0b",
            "icon_name": "baby"
        },
        {
            "name": "Obstetrics & Gynecology",
            "description": "Women's health and maternity care",
            "color_code": "#8b5cf6",
            "icon_name": "heart"
        },
        {
            "name": "Radiology",
            "description": "Medical imaging and diagnostics",
            "color_code": "#06b6d4",
            "icon_name": "scan"
        },
        {
            "name": "Laboratory",
            "description": "Medical testing and pathology",
            "color_code": "#84cc16",
            "icon_name": "flask"
        },
        {
            "name": "Pharmacy",
            "description": "Medication dispensing and counseling",
            "color_code": "#f97316",
            "icon_name": "pill"
        }
    ]

    for dept_data in departments:
        dept = Department(**dept_data)
        db.add(dept)

    db.commit()
    print("✅ Departments initialized")


def init_role_permissions(db):
    """Initialize role-based permissions."""
    permissions = [
        # Admin permissions - full access
        {"role": "admin", "resource": "users", "action": "create", "allowed": True},
        {"role": "admin", "resource": "users", "action": "read", "allowed": True},
        {"role": "admin", "resource": "users", "action": "update", "allowed": True},
        {"role": "admin", "resource": "users", "action": "delete", "allowed": True},
        {"role": "admin", "resource": "staff", "action": "create", "allowed": True},
        {"role": "admin", "resource": "staff", "action": "read", "allowed": True},
        {"role": "admin", "resource": "staff", "action": "update", "allowed": True},
        {"role": "admin", "resource": "staff", "action": "delete", "allowed": True},
        {"role": "admin", "resource": "system_settings", "action": "create", "allowed": True},
        {"role": "admin", "resource": "system_settings", "action": "read", "allowed": True},
        {"role": "admin", "resource": "system_settings", "action": "update", "allowed": True},
        {"role": "admin", "resource": "system_settings", "action": "delete", "allowed": True},

        # Staff permissions - limited access
        {"role": "staff", "resource": "users", "action": "read", "allowed": True},
        {"role": "staff", "resource": "appointments", "action": "create", "allowed": True},
        {"role": "staff", "resource": "appointments", "action": "read", "allowed": True},
        {"role": "staff", "resource": "appointments", "action": "update", "allowed": True},
        {"role": "staff", "resource": "queue", "action": "read", "allowed": True},
        {"role": "staff", "resource": "queue", "action": "update", "allowed": True},
        {"role": "staff", "resource": "staff_profiles", "action": "read", "allowed": True},
        {"role": "staff", "resource": "staff_profiles", "action": "update", "allowed": True},
        {"role": "staff", "resource": "staff_communication", "action": "create", "allowed": True},
        {"role": "staff", "resource": "staff_communication", "action": "read", "allowed": True},
        {"role": "staff", "resource": "staff_tasks", "action": "create", "allowed": True},
        {"role": "staff", "resource": "staff_tasks", "action": "read", "allowed": True},
        {"role": "staff", "resource": "staff_tasks", "action": "update", "allowed": True},
        {"role": "staff", "resource": "emergency", "action": "create", "allowed": True},
        {"role": "staff", "resource": "emergency", "action": "read", "allowed": True},
        {"role": "staff", "resource": "emergency", "action": "update", "allowed": True},

        # Patient permissions - minimal access
        {"role": "patient", "resource": "users", "action": "read", "allowed": True},
        {"role": "patient", "resource": "users", "action": "update", "allowed": True},
        {"role": "patient", "resource": "appointments", "action": "create", "allowed": True},
        {"role": "patient", "resource": "appointments", "action": "read", "allowed": True},
        {"role": "patient", "resource": "appointments", "action": "update", "allowed": True},
        {"role": "patient", "resource": "queue", "action": "create", "allowed": True},
        {"role": "patient", "resource": "queue", "action": "read", "allowed": True},
        {"role": "patient", "resource": "notifications", "action": "read", "allowed": True},
        {"role": "patient", "resource": "emergency", "action": "create", "allowed": True},
        {"role": "patient", "resource": "emergency", "action": "read", "allowed": True},
    ]

    for perm_data in permissions:
        perm = RolePermission(**perm_data)
        db.add(perm)

    db.commit()
    print("✅ Role permissions initialized")


def init_system_settings(db):
    """Initialize default system settings."""
    settings = [
        {
            "setting_key": "maintenance_mode",
            "setting_value": "false",
            "setting_type": "boolean",
            "category": "system",
            "description": "Enable maintenance mode",
            "is_system_setting": True
        },
        {
            "setting_key": "max_queue_size",
            "setting_value": "100",
            "setting_type": "integer",
            "category": "queue",
            "description": "Maximum queue size per service",
            "is_system_setting": False
        },
        {
            "setting_key": "auto_call_delay",
            "setting_value": "30",
            "setting_type": "integer",
            "category": "queue",
            "description": "Auto-call next patient delay (seconds)",
            "is_system_setting": False
        },
        {
            "setting_key": "emergency_response_timeout",
            "setting_value": "15",
            "setting_type": "integer",
            "category": "emergency",
            "description": "Emergency response timeout (minutes)",
            "is_system_setting": False
        },
        {
            "setting_key": "max_upload_size_mb",
            "setting_value": "10",
            "setting_type": "integer",
            "category": "system",
            "description": "Maximum file upload size in MB",
            "is_system_setting": False
        },
        {
            "setting_key": "session_timeout_minutes",
            "setting_value": "60",
            "setting_type": "integer",
            "category": "security",
            "description": "User session timeout in minutes",
            "is_system_setting": False
        },
        {
            "setting_key": "enable_emergency_alerts",
            "setting_value": "true",
            "setting_type": "boolean",
            "category": "emergency",
            "description": "Enable emergency alert notifications",
            "is_system_setting": False
        },
        {
            "setting_key": "backup_frequency_hours",
            "setting_value": "24",
            "setting_type": "integer",
            "category": "system",
            "description": "Database backup frequency in hours",
            "is_system_setting": False
        }
    ]

    for setting_data in settings:
        setting = SystemSettings(**setting_data)
        db.add(setting)

    db.commit()
    print("✅ System settings initialized")


def init_sample_staff(db):
    """Initialize sample staff accounts."""
    staff_data = [
        {
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@hospital.com",
            "password": "StaffPass123!",
            "role": "staff",
            "profile": {
                "employee_id": "EMP001",
                "department": "Emergency Medicine",
                "specialization": "Emergency Medicine",
                "license_number": "MD123456",
                "years_experience": 8,
                "is_supervisor": True,
                "contract_type": "full_time",
                "hourly_rate": 85.00,
                "max_patients_per_hour": 6,
                "languages_spoken": ["English", "Spanish"],
                "emergency_certified": True,
                "hire_date": datetime(2020, 3, 15)
            }
        },
        {
            "name": "Dr. Michael Chen",
            "email": "michael.chen@hospital.com",
            "password": "StaffPass123!",
            "role": "staff",
            "profile": {
                "employee_id": "EMP002",
                "department": "Internal Medicine",
                "specialization": "Cardiology",
                "license_number": "MD234567",
                "years_experience": 12,
                "is_supervisor": False,
                "contract_type": "full_time",
                "hourly_rate": 90.00,
                "max_patients_per_hour": 5,
                "languages_spoken": ["English", "Mandarin"],
                "emergency_certified": True,
                "hire_date": datetime(2018, 7, 22)
            }
        },
        {
            "name": "Nurse Emily Davis",
            "email": "emily.davis@hospital.com",
            "password": "StaffPass123!",
            "role": "staff",
            "profile": {
                "employee_id": "EMP003",
                "department": "Emergency Medicine",
                "specialization": "Emergency Nursing",
                "license_number": "RN345678",
                "years_experience": 6,
                "is_supervisor": False,
                "contract_type": "full_time",
                "hourly_rate": 45.00,
                "max_patients_per_hour": 8,
                "languages_spoken": ["English"],
                "emergency_certified": True,
                "hire_date": datetime(2021, 1, 10)
            }
        },
        {
            "name": "Admin User",
            "email": "admin@hospital.com",
            "password": "AdminPass123!",
            "role": "admin",
            "profile": {
                "employee_id": "ADM001",
                "department": "Administration",
                "specialization": "Healthcare Administration",
                "license_number": "ADM001",
                "years_experience": 15,
                "is_supervisor": True,
                "contract_type": "full_time",
                "hourly_rate": 65.00,
                "max_patients_per_hour": 0,
                "languages_spoken": ["English"],
                "emergency_certified": False,
                "hire_date": datetime(2015, 6, 1)
            }
        }
    ]

    for staff_info in staff_data:
        # Create user account
        hashed_password = get_password_hash(staff_info["password"])
        user = User(
            name=staff_info["name"],
            email=staff_info["email"],
            password_hash=hashed_password,
            role=staff_info["role"]
        )
        db.add(user)
        db.flush()  # Get user ID

        # Create staff profile
        profile_data = staff_info["profile"].copy()
        profile_data["user_id"] = user.id
        profile = StaffProfile(**profile_data)
        db.add(profile)

    db.commit()
    print("✅ Sample staff accounts initialized")


def init_sample_schedule(db):
    """Initialize sample staff schedules."""
    # Get staff users
    staff_users = db.query(User).filter(User.role == "staff").all()

    # Create schedules for the next 7 days
    base_date = datetime.now().date()
    shifts = ["morning", "afternoon", "night"]

    for i in range(7):
        shift_date = base_date + timedelta(days=i)

        for idx, user in enumerate(staff_users):
            shift_type = shifts[idx % len(shifts)]

            # Set shift times based on type
            if shift_type == "morning":
                start_time = datetime.combine(shift_date, datetime.min.time().replace(hour=7))
                end_time = datetime.combine(shift_date, datetime.min.time().replace(hour=15))
            elif shift_type == "afternoon":
                start_time = datetime.combine(shift_date, datetime.min.time().replace(hour=15))
                end_time = datetime.combine(shift_date, datetime.min.time().replace(hour=23))
            else:  # night
                start_time = datetime.combine(shift_date, datetime.min.time().replace(hour=23))
                end_time = datetime.combine(shift_date + timedelta(days=1), datetime.min.time().replace(hour=7))

            schedule = StaffSchedule(
                staff_id=user.id,
                shift_date=shift_date,
                shift_type=shift_type,
                start_time=start_time,
                end_time=end_time,
                break_duration=30,
                is_active=True,
                notes=f"Regular {shift_type} shift"
            )
            db.add(schedule)

    db.commit()
    print("✅ Sample staff schedules initialized")


def main():
    """Main initialization function."""
    print("🚀 Initializing Healthcare Queue Management System - Staff Data")

    db = SessionLocal()
    try:
        print("📊 Initializing departments...")
        init_departments(db)

        print("🔐 Initializing role permissions...")
        init_role_permissions(db)

        print("⚙️ Initializing system settings...")
        init_system_settings(db)

        print("👥 Initializing sample staff accounts...")
        init_sample_staff(db)

        print("📅 Initializing sample schedules...")
        init_sample_schedule(db)

        print("✅ Staff data initialization completed successfully!")
        print("\n📋 Default Admin Account:")
        print("   Email: admin@hospital.com")
        print("   Password: AdminPass123!")
        print("\n📋 Sample Staff Accounts:")
        print("   Dr. Sarah Johnson: sarah.johnson@hospital.com")
        print("   Dr. Michael Chen: michael.chen@hospital.com")
        print("   Nurse Emily Davis: emily.davis@hospital.com")
        print("   All passwords: StaffPass123!")

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()