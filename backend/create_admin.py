#!/usr/bin/env python3
"""
Script to create an ultimate admin user for testing the queue management system.
Run this script to create an admin user with full access.
"""

import sys
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create an ultimate admin user for testing."""

    # Create tables if they don't exist
    create_tables()

    # Create a new database session
    db: Session = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            print("Login credentials:")
            print(f"Email: {existing_admin.email}")
            print("Password: admin123")  # This is just for testing
            return

        # Create the ultimate admin user
        admin_user = User(
            name="Ultimate Admin",
            email="admin@hospital.com",
            phone="+1-555-ADMIN",
            date_of_birth="1980-01-01",
            password_hash=pwd_context.hash("admin123"),
            role="admin",
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Ultimate Admin User Created Successfully!")
        print("=" * 50)
        print("Login Credentials:")
        print(f"Email: {admin_user.email}")
        print("Password: admin123")
        print("=" * 50)
        print("WARNING: This is a test password!")
        print("Change it immediately in production!")
        print("=" * 50)

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def create_staff_user():
    """Create a staff user for testing."""

    # Create tables if they don't exist
    create_tables()

    # Create a new database session
    db: Session = SessionLocal()

    try:
        # Check if staff user already exists
        existing_staff = db.query(User).filter(User.email == "staff@hospital.com").first()
        if existing_staff:
            print(f"Staff user already exists: {existing_staff.email}")
            return

        # Create a staff user
        staff_user = User(
            name="Hospital Staff",
            email="staff@hospital.com",
            phone="+1-555-STAFF",
            date_of_birth="1990-01-01",
            password_hash=pwd_context.hash("staff123"),
            role="staff",
            is_active=True
        )

        db.add(staff_user)
        db.commit()
        db.refresh(staff_user)

        print("Staff User Created Successfully!")
        print("Email: staff@hospital.com")
        print("Password: staff123")

    except Exception as e:
        print(f"Error creating staff user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Hospital Queue Management - User Creation Script")
    print("=" * 60)

    create_admin_user()
    print()
    create_staff_user()

    print("\nUser creation complete!")
    print("You can now login to the application with these credentials.")