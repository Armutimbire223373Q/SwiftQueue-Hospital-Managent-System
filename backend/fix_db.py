#!/usr/bin/env python3
"""
Fix database schema by adding missing columns
"""

import sqlite3
import os

def fix_database():
    db_path = "queue_management.db"
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if staff_count column exists in services table
        cursor.execute("PRAGMA table_info(services)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'staff_count' not in columns:
            print("Adding staff_count column...")
            cursor.execute("ALTER TABLE services ADD COLUMN staff_count INTEGER DEFAULT 1")

        if 'service_rate' not in columns:
            print("Adding service_rate column...")
            cursor.execute("ALTER TABLE services ADD COLUMN service_rate REAL DEFAULT 1.0")

        # Check if address columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]

        address_columns = ['street_address', 'city', 'state', 'zip_code', 'country']
        for col in address_columns:
            if col not in user_columns:
                print(f"Adding {col} column to users table...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        
        # Commit changes
        conn.commit()
        print("✅ Database schema updated successfully!")
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM services")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Inserting sample services...")
            services = [
                ("Emergency Care", "24/7 emergency medical services", 1, 1.5, "Emergency", 5, 5, 3),
                ("Cardiology", "Heart and cardiovascular care", 2, 1.2, "Cardiology", 15, 15, 2),
                ("General Medicine", "Primary care and consultations", 3, 1.0, "General", 12, 12, 4),
                ("Laboratory", "Blood tests and diagnostics", 2, 2.0, "Laboratory", 8, 8, 1),
                ("Radiology", "Medical imaging and scans", 2, 0.8, "Radiology", 20, 20, 2),
                ("Pediatrics", "Child and infant care", 2, 1.3, "Pediatrics", 10, 10, 1)
            ]
            
            cursor.executemany(
                "INSERT INTO services (name, description, staff_count, service_rate, department, estimated_time, current_wait_time, queue_length) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                services
            )
            conn.commit()
            print("✅ Sample services inserted!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
