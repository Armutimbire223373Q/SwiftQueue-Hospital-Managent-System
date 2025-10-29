# 🎭 Demo Data Guide

## Overview

This guide explains how to populate your SwiftQueue Hospital Management System with realistic demo data for demonstration, testing, and showcase purposes.

## 🚀 Quick Start

### Generate Demo Data

```powershell
# Navigate to backend directory
cd backend

# Run the demo data generator
python create_demo_data.py
```

## 📊 What Gets Created

The demo data generator creates a complete, realistic hospital management scenario:

### 🏢 Departments (8)
- Emergency
- Cardiology
- Pediatrics
- Orthopedics
- Radiology
- Laboratory
- General Medicine
- Surgery

### 👥 Users (14 total)

#### 1 Administrator
- **Email**: admin@hospital.com
- **Password**: Admin123!
- **Full Name**: System Administrator
- **Phone**: +1234567890

#### 5 Staff Members
1. **Dr. John Smith** (Cardiology)
   - Email: dr.smith@hospital.com
   - Password: Staff123!

2. **Dr. Sarah Johnson** (Emergency Medicine)
   - Email: dr.johnson@hospital.com
   - Password: Staff123!

3. **Nurse Emily Williams** (Pediatrics)
   - Email: nurse.williams@hospital.com
   - Password: Staff123!

4. **Dr. Michael Brown** (Orthopedics)
   - Email: dr.brown@hospital.com
   - Password: Staff123!

5. **Dr. Jessica Davis** (General Practice)
   - Email: dr.davis@hospital.com
   - Password: Staff123!

#### 8 Patients
1. **John Doe** - john.doe@email.com
2. **Jane Smith** - jane.smith@email.com
3. **Robert Jones** - robert.jones@email.com
4. **Mary Williams** - mary.williams@email.com
5. **James Miller** - james.miller@email.com
6. **Patricia Davis** - patricia.davis@email.com
7. **Michael Garcia** - michael.garcia@email.com
8. **Linda Rodriguez** - linda.rodriguez@email.com

**All patient passwords**: Patient123!

### 🏥 Medical Services (10)
- General Consultation (30 min)
- Emergency Care (45 min)
- Cardiology Consultation (45 min)
- Pediatric Care (30 min)
- X-Ray Imaging (20 min)
- Blood Test (15 min)
- Orthopedic Consultation (40 min)
- CT Scan (30 min)
- Vaccination (15 min)
- Physical Therapy (60 min)

### 🪟 Service Counters (15-30)
- 1-3 counters per service
- Named as A1, A2, B1, B2, etc.
- ~75% active at any time

### 📝 Queue Entries (25)
- Various statuses: waiting, called, in_progress, completed
- Priority levels: 1-5
- Distributed across last 3 days
- Realistic wait times (15-90 minutes)

### 📅 Appointments (30)
- Past, present, and future appointments
- Statuses: scheduled, confirmed, in_progress, completed, cancelled
- Distributed from -7 to +14 days
- Linked to services and staff

### ✅ Check-ins (15)
- Associated with appointments
- Realistic check-in times (5-30 min before appointment)

### 📆 Staff Schedules (70+)
- 14 days of schedules for each staff member
- Morning, afternoon, and full-day shifts
- Random days off (~20% of days)
- Realistic working hours (8 AM - 8 PM)

### 🔔 Notifications (40+)
- 2-5 notifications per user
- Various types: info, warning, success
- Mix of read/unread statuses
- Realistic content (appointments, queue updates, test results)

### 📁 File Uploads (20)
- Lab results (PDF)
- X-Ray images (JPEG)
- Prescriptions (PDF)
- Medical reports (PDF)
- CT scans (JPEG)
- Distributed across last 30 days

## 🎯 Use Cases

### 1. **Live Demo**
Perfect for showcasing the system to potential clients or stakeholders.

### 2. **Development Testing**
Test features with realistic data scenarios.

### 3. **UI/UX Testing**
See how the interface handles various data states.

### 4. **Performance Testing**
Test system performance with populated database.

### 5. **Portfolio Showcase**
Create screenshots and videos with professional-looking data.

### 6. **Training**
Train new users or administrators with realistic scenarios.

## 🔄 Resetting Demo Data

To reset and regenerate demo data:

```powershell
# Delete the database
rm queue_management.db

# Recreate and populate
python create_demo_data.py
```

**Note**: This will clear ALL data, including any custom data you've added.

## 🎭 Demo Scenarios

### Scenario 1: Administrator Dashboard
1. Login as admin@hospital.com
2. View comprehensive dashboard with all stats
3. Manage departments, services, and users
4. Review analytics and reports

### Scenario 2: Staff Member Workflow
1. Login as dr.smith@hospital.com
2. View assigned patients and appointments
3. Call next patient from queue
4. Update patient status
5. View personal performance metrics

### Scenario 3: Patient Experience
1. Login as john.doe@email.com
2. Join a queue for service
3. Book an appointment
4. Check queue position
5. Receive notifications
6. View medical history

### Scenario 4: Queue Management
1. Login as staff member
2. View current queue (shows ~5-10 waiting patients)
3. Call next patient
4. See real-time updates
5. Handle different priority levels

### Scenario 5: Analytics Review
1. Login as admin
2. View analytics dashboard
3. See trends over past 3 days
4. Review bottleneck detection
5. Check staff performance
6. Export reports

## 📸 Best Demo Practices

### For Screenshots
1. Use the **admin** account to show full features
2. **Queue Management** page shows live queues
3. **Analytics Dashboard** displays comprehensive metrics
4. **Appointments** page shows calendar view

### For Videos
1. Start with patient workflow (join queue)
2. Switch to staff view (call patient)
3. Show real-time updates
4. Demonstrate analytics
5. End with admin dashboard

### For Presentations
1. Highlight the variety of services
2. Show multiple user roles
3. Demonstrate real-time features
4. Display analytics and reports
5. Show mobile responsiveness

## 🔐 Security Note

**⚠️ IMPORTANT**: This is DEMO DATA ONLY!

- All passwords are simple and well-known
- Do NOT use this data in production
- Change all passwords if using in a live environment
- The data is public and not secure

## 🛠️ Customization

To customize the demo data, edit `create_demo_data.py`:

### Add More Patients
```python
# In create_users() function, add more entries to users_data list
{
    "email": "newpatient@email.com",
    "full_name": "New Patient Name",
    "password": "Patient123!",
    "role": "patient",
    "phone": "+1234567XXX"
}
```

### Add More Services
```python
# In create_services() function, add to services_data list
{
    "name": "New Service",
    "description": "Service description",
    "estimated_time": 30,
    "department_id": 0
}
```

### Modify Date Ranges
```python
# Change this line in create_queue_entries() or create_appointments()
days=random.randint(0, 3)  # Adjust the range
```

## 📊 Data Statistics

After running the generator, you'll have:

| Entity | Count | Purpose |
|--------|-------|---------|
| Departments | 8 | Hospital organizational structure |
| Users | 14 | 1 admin, 5 staff, 8 patients |
| Staff Profiles | 5 | Complete staff information |
| Services | 10 | Medical services offered |
| Counters | 15-30 | Service delivery points |
| Queue Entries | 25 | Current and recent queues |
| Appointments | 30 | Past and future bookings |
| Check-ins | 15 | Patient check-in records |
| Schedules | 70+ | Staff availability |
| Notifications | 40+ | User notifications |
| File Records | 20 | Sample documents |

**Total Database Records**: ~250+

## 🎯 Next Steps

After generating demo data:

1. ✅ **Start the backend server**
   ```powershell
   python run.py
   ```

2. ✅ **Start the frontend**
   ```powershell
   npm run dev
   ```

3. ✅ **Login and explore**
   - Try different user roles
   - Navigate through features
   - Test real-time updates

4. ✅ **Take screenshots**
   - Capture key features
   - Show different user views
   - Highlight analytics

5. ✅ **Create demo video**
   - Record workflow
   - Show real-time features
   - Demonstrate value

6. ✅ **Share your work**
   - Update portfolio
   - Post on LinkedIn
   - Share on GitHub

## 🆘 Troubleshooting

### "Module not found" error
```powershell
# Make sure you're in the backend directory
cd backend
python create_demo_data.py
```

### Database locked error
```powershell
# Stop the backend server first
# Then run the demo data generator
```

### Import errors
```powershell
# Install all dependencies
pip install -r requirements.txt
```

### Permission errors
```powershell
# Run PowerShell as administrator (if needed)
```

## 📝 Notes

- Demo data is generated with realistic timestamps
- Queue entries span the last 3 days
- Appointments range from -7 to +14 days
- All data is randomly distributed for realism
- Statuses reflect realistic progression
- Staff schedules cover the next 2 weeks

---

**Happy Demoing! 🎭**

For questions or issues, refer to the main [README.md](README.md) or [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md).
