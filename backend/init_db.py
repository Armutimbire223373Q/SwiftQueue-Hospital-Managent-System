#!/usr/bin/env python3
"""
Database initialization script for the Queue Management System.
This script creates initial data for services, counters, and sample analytics.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.models import Service, ServiceCounter, Analytics, User, QueueEntry

def init_services(db):
    """Initialize hospital services/departments"""
    services = [
        {
            "name": "Emergency Care",
            "description": "24/7 emergency medical services",
            "department": "Emergency",
            "staff_count": 3,
            "service_rate": 2.5,  # patients per hour per staff
            "estimated_time": 15,
            "current_wait_time": 20
        },
        {
            "name": "General Medicine",
            "description": "Primary care and general consultations",
            "department": "Internal Medicine",
            "staff_count": 2,
            "service_rate": 3.0,
            "estimated_time": 20,
            "current_wait_time": 25
        },
        {
            "name": "Cardiology",
            "description": "Heart and cardiovascular care",
            "department": "Cardiology",
            "staff_count": 1,
            "service_rate": 2.0,
            "estimated_time": 30,
            "current_wait_time": 35
        },
        {
            "name": "Laboratory Services",
            "description": "Blood tests and diagnostic lab work",
            "department": "Laboratory",
            "staff_count": 2,
            "service_rate": 4.0,
            "estimated_time": 10,
            "current_wait_time": 15
        },
        {
            "name": "Radiology",
            "description": "X-rays, CT scans, and medical imaging",
            "department": "Radiology",
            "staff_count": 1,
            "service_rate": 2.5,
            "estimated_time": 25,
            "current_wait_time": 30
        },
        {
            "name": "Pediatrics",
            "description": "Medical care for children and infants",
            "department": "Pediatrics",
            "staff_count": 2,
            "service_rate": 2.8,
            "estimated_time": 18,
            "current_wait_time": 22
        }
    ]

    for service_data in services:
        # Check if service already exists
        existing = db.query(Service).filter(Service.name == service_data["name"]).first()
        if not existing:
            service = Service(**service_data)
            db.add(service)
            print(f"Created service: {service_data['name']}")

    db.commit()

def init_service_counters(db):
    """Initialize service counters/stations"""
    services = db.query(Service).all()
    
    counter_configs = {
        "Emergency Care": [
            {"name": "Emergency Bay 1", "staff_member": "Dr. Alice Johnson"},
            {"name": "Emergency Bay 2", "staff_member": "Nurse Carol Davis"},
            {"name": "Emergency Bay 3", "staff_member": None}
        ],
        "General Medicine": [
            {"name": "Room 101", "staff_member": "Dr. Bob Smith"},
            {"name": "Room 102", "staff_member": "Dr. Sarah Wilson"}
        ],
        "Cardiology": [
            {"name": "Cardiology Suite 1", "staff_member": "Dr. Michael Chen"}
        ],
        "Laboratory Services": [
            {"name": "Lab Station 1", "staff_member": "Tech Lisa Brown"},
            {"name": "Lab Station 2", "staff_member": "Tech James Davis"}
        ],
        "Radiology": [
            {"name": "X-Ray Room 1", "staff_member": "Tech Maria Garcia"}
        ],
        "Pediatrics": [
            {"name": "Pediatric Room 1", "staff_member": "Dr. Emily Rodriguez"},
            {"name": "Pediatric Room 2", "staff_member": "Nurse Jennifer Lee"}
        ]
    }

    for service in services:
        if service.name in counter_configs:
            for counter_data in counter_configs[service.name]:
                # Check if counter already exists
                existing = db.query(ServiceCounter).filter(
                    ServiceCounter.service_id == service.id,
                    ServiceCounter.name == counter_data["name"]
                ).first()
                
                if not existing:
                    counter = ServiceCounter(
                        name=counter_data["name"],
                        service_id=service.id,
                        is_active=1,
                        staff_member=counter_data["staff_member"]
                    )
                    db.add(counter)
                    print(f"Created counter: {counter_data['name']} for {service.name}")

    db.commit()

def init_sample_users(db):
    """Initialize sample users for testing"""
    sample_users = [
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0101",
            "date_of_birth": datetime(1985, 3, 15)
        },
        {
            "name": "Mary Johnson",
            "email": "mary.johnson@email.com",
            "phone": "+1-555-0102",
            "date_of_birth": datetime(1990, 7, 22)
        },
        {
            "name": "Robert Davis",
            "email": "robert.davis@email.com",
            "phone": "+1-555-0103",
            "date_of_birth": datetime(1978, 11, 8)
        },
        {
            "name": "Lisa Wilson",
            "email": "lisa.wilson@email.com",
            "phone": "+1-555-0104",
            "date_of_birth": datetime(1992, 5, 30)
        },
        {
            "name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0105",
            "date_of_birth": datetime(1987, 9, 12)
        }
    ]

    for user_data in sample_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            print(f"Created user: {user_data['name']}")

    db.commit()

def init_sample_analytics(db):
    """Initialize sample analytics data for the past week"""
    services = db.query(Service).all()
    
    # Generate analytics for the past 7 days
    for days_back in range(7):
        date = datetime.utcnow() - timedelta(days=days_back)
        
        for service in services:
            # Generate realistic metrics based on service type
            base_queue_length = {
                "Emergency Care": random.randint(8, 15),
                "General Medicine": random.randint(5, 12),
                "Cardiology": random.randint(3, 8),
                "Laboratory Services": random.randint(6, 10),
                "Radiology": random.randint(4, 9),
                "Pediatrics": random.randint(4, 10)
            }.get(service.name, random.randint(3, 10))
            
            # Add some variation based on time of day
            hour_variation = random.uniform(0.7, 1.3)
            queue_length = max(1, int(base_queue_length * hour_variation))
            
            analytics = Analytics(
                timestamp=date,
                service_id=service.id,
                queue_length=queue_length,
                avg_wait_time=random.uniform(15, 45),
                avg_service_time=random.uniform(10, 30),
                efficiency_score=random.uniform(0.75, 0.95),
                peak_hour=random.randint(9, 17),
                peak_load=random.randint(queue_length, queue_length + 5),
                staff_utilization=random.uniform(0.6, 0.9),
                patient_satisfaction=random.uniform(0.8, 0.95),
                patients_served=random.randint(20, 50)
            )
            db.add(analytics)

    db.commit()
    print("Created sample analytics data for the past 7 days")

def init_sample_queue_entries(db):
    """Initialize some current queue entries for testing"""
    services = db.query(Service).all()
    users = db.query(User).all()
    
    if not users:
        print("No users found. Please run init_sample_users first.")
        return
    
    priorities = ["low", "medium", "high", "urgent"]
    statuses = ["waiting", "called", "serving"]
    
    queue_number = 1
    
    for service in services[:3]:  # Only add to first 3 services
        num_entries = random.randint(2, 5)
        
        for i in range(num_entries):
            user = random.choice(users)
            priority = random.choice(priorities)
            status = random.choice(statuses) if i > 0 else "waiting"  # First entry is always waiting
            
            # Calculate estimated wait time based on position and service
            estimated_wait = service.current_wait_time + (i * 10)
            ai_predicted_wait = int(estimated_wait * random.uniform(0.8, 1.2))
            
            queue_entry = QueueEntry(
                patient_id=user.id,
                service_id=service.id,
                queue_number=queue_number,
                status=status,
                priority=priority,
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 60)),
                estimated_wait_time=estimated_wait,
                ai_predicted_wait=ai_predicted_wait
            )
            
            db.add(queue_entry)
            queue_number += 1
        
        # Update service queue length
        service.queue_length = num_entries
    
    db.commit()
    print("Created sample queue entries")

def main():
    """Main initialization function"""
    print("Initializing Queue Management System Database...")
    
    # Create tables
    create_tables()
    print("Database tables created successfully")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize data
        print("\n1. Initializing services...")
        init_services(db)
        
        print("\n2. Initializing service counters...")
        init_service_counters(db)
        
        print("\n3. Initializing sample users...")
        init_sample_users(db)
        
        print("\n4. Initializing sample analytics...")
        init_sample_analytics(db)
        
        print("\n5. Initializing sample queue entries...")
        init_sample_queue_entries(db)
        
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now start the application with: python run.py")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()