"""
Patient History Service - Manages medical records, diagnoses, medications, and patient history
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
from pathlib import Path
import csv


class PatientHistoryService:
    """Service for managing patient medical history and records"""
    
    @staticmethod
    def get_patient_history(
        db: Session,
        patient_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get complete medical history for a patient"""
        
        # Try to read from CSV first (legacy data)
        csv_history = PatientHistoryService._read_csv_history(patient_id)
        
        # Mock additional history records
        history_records = []
        
        for i in range(min(5, limit)):
            record = {
                "id": f"visit_{uuid.uuid4().hex[:12]}",
                "patient_id": patient_id,
                "visit_date": (datetime.utcnow() - timedelta(days=30*i)).isoformat(),
                "visit_type": ["routine_checkup", "emergency", "follow_up", "consultation"][i % 4],
                "chief_complaint": ["Headache", "Fever", "Chest pain", "Cough", "Back pain"][i % 5],
                "diagnosis": ["Migraine", "Viral infection", "Anxiety", "Bronchitis", "Muscle strain"][i % 5],
                "treatment": ["Prescribed medication", "Rest and fluids", "Therapy recommended", "Antibiotics", "Physical therapy"][i % 5],
                "notes": "Patient responded well to treatment",
                "attending_physician": f"Dr. Smith",
                "created_at": datetime.utcnow().isoformat()
            }
            history_records.append(record)
        
        # Combine CSV and database records
        all_records = csv_history + history_records
        return all_records[offset:offset + limit]
    
    @staticmethod
    def _read_csv_history(patient_id: int) -> List[Dict[str, Any]]:
        """Read patient history from CSV file"""
        try:
            csv_path = Path(__file__).resolve().parents[2] / 'dataset' / 'patient_history.csv'
            if not csv_path.exists():
                return []
            
            records = []
            with csv_path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('patient_id') == str(patient_id):
                        records.append(dict(row))
            return records
        except Exception:
            return []
    
    @staticmethod
    def create_medical_record(
        db: Session,
        patient_id: int,
        visit_type: str,
        chief_complaint: str,
        diagnosis: str,
        treatment: str,
        physician_id: int,
        notes: Optional[str] = None,
        vital_signs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new medical record"""
        
        record_id = f"rec_{uuid.uuid4().hex[:12]}"
        
        record = {
            "record_id": record_id,
            "patient_id": patient_id,
            "visit_date": datetime.utcnow().isoformat(),
            "visit_type": visit_type,
            "chief_complaint": chief_complaint,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "physician_id": physician_id,
            "notes": notes,
            "vital_signs": vital_signs,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return record
    
    @staticmethod
    def update_medical_record(
        db: Session,
        record_id: str,
        diagnosis: Optional[str] = None,
        treatment: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing medical record"""
        
        # In production, fetch and update from database
        # For now, return a complete updated record
        record = {
            "record_id": record_id,
            "patient_id": 1,  # Mock patient ID
            "visit_date": datetime.utcnow().isoformat(),
            "visit_type": "follow_up",
            "chief_complaint": "Follow-up examination",
            "diagnosis": diagnosis if diagnosis else "Initial diagnosis",
            "treatment": treatment if treatment else "Initial treatment",
            "physician_id": 1,
            "notes": notes if notes else "Initial notes",
            "vital_signs": None,
            "status": status if status else "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return record
    
    @staticmethod
    def get_medications(
        db: Session,
        patient_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get patient's medication list"""
        
        medications = [
            {
                "medication_id": f"med_{uuid.uuid4().hex[:8]}",
                "patient_id": patient_id,
                "medication_name": "Aspirin",
                "dosage": "100mg",
                "frequency": "Once daily",
                "route": "Oral",
                "prescribed_by": "Dr. Smith",
                "prescribed_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "status": "active",
                "instructions": "Take with food",
                "refills_remaining": 2
            },
            {
                "medication_id": f"med_{uuid.uuid4().hex[:8]}",
                "patient_id": patient_id,
                "medication_name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "Once daily",
                "route": "Oral",
                "prescribed_by": "Dr. Johnson",
                "prescribed_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "start_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "end_date": None,  # Ongoing
                "status": "active",
                "instructions": "Take in the morning",
                "refills_remaining": 5
            }
        ]
        
        if active_only:
            medications = [m for m in medications if m["status"] == "active"]
        
        return medications
    
    @staticmethod
    def add_medication(
        db: Session,
        patient_id: int,
        medication_name: str,
        dosage: str,
        frequency: str,
        route: str,
        prescribed_by: str,
        start_date: str,
        end_date: Optional[str] = None,
        instructions: Optional[str] = None,
        refills: int = 0
    ) -> Dict[str, Any]:
        """Add a new medication to patient's record"""
        
        medication_id = f"med_{uuid.uuid4().hex[:8]}"
        
        medication = {
            "medication_id": medication_id,
            "patient_id": patient_id,
            "medication_name": medication_name,
            "dosage": dosage,
            "frequency": frequency,
            "route": route,
            "prescribed_by": prescribed_by,
            "prescribed_date": datetime.utcnow().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "status": "active",
            "instructions": instructions,
            "refills": refills,
            "refills_remaining": refills,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return medication
    
    @staticmethod
    def get_allergies(db: Session, patient_id: int) -> List[Dict[str, Any]]:
        """Get patient's allergy information"""
        
        allergies = [
            {
                "allergy_id": f"alg_{uuid.uuid4().hex[:8]}",
                "patient_id": patient_id,
                "allergen": "Penicillin",
                "reaction": "Rash and itching",
                "severity": "moderate",
                "verified_date": (datetime.utcnow() - timedelta(days=365)).isoformat(),
                "status": "active"
            },
            {
                "allergy_id": f"alg_{uuid.uuid4().hex[:8]}",
                "patient_id": patient_id,
                "allergen": "Peanuts",
                "reaction": "Anaphylaxis",
                "severity": "severe",
                "verified_date": (datetime.utcnow() - timedelta(days=730)).isoformat(),
                "status": "active"
            }
        ]
        
        return allergies
    
    @staticmethod
    def add_allergy(
        db: Session,
        patient_id: int,
        allergen: str,
        reaction: str,
        severity: str
    ) -> Dict[str, Any]:
        """Add a new allergy to patient's record"""
        
        allergy_id = f"alg_{uuid.uuid4().hex[:8]}"
        
        allergy = {
            "allergy_id": allergy_id,
            "patient_id": patient_id,
            "allergen": allergen,
            "reaction": reaction,
            "severity": severity,
            "verified_date": datetime.utcnow().isoformat(),
            "recorded_date": datetime.utcnow().isoformat(),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return allergy
    
    @staticmethod
    def get_lab_results(
        db: Session,
        patient_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get patient's laboratory test results"""
        
        lab_results = [
            {
                "test_id": f"lab_{uuid.uuid4().hex[:12]}",
                "patient_id": patient_id,
                "test_name": "Complete Blood Count (CBC)",
                "test_type": "Complete Blood Count",
                "test_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "ordered_by": "Dr. Smith",
                "status": "completed",
                "results": {
                    "WBC": {"value": 7.5, "unit": "K/uL", "normal_range": "4.5-11.0"},
                    "RBC": {"value": 4.8, "unit": "M/uL", "normal_range": "4.5-5.9"},
                    "Hemoglobin": {"value": 14.2, "unit": "g/dL", "normal_range": "13.5-17.5"},
                    "Platelets": {"value": 250, "unit": "K/uL", "normal_range": "150-400"}
                },
                "interpretation": "All values within normal range",
                "notes": "No abnormalities detected"
            },
            {
                "test_id": f"lab_{uuid.uuid4().hex[:12]}",
                "patient_id": patient_id,
                "test_name": "Lipid Panel",
                "test_type": "Lipid Panel",
                "test_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "ordered_by": "Dr. Johnson",
                "status": "completed",
                "results": {
                    "Total Cholesterol": {"value": 195, "unit": "mg/dL", "normal_range": "<200"},
                    "LDL": {"value": 115, "unit": "mg/dL", "normal_range": "<100"},
                    "HDL": {"value": 55, "unit": "mg/dL", "normal_range": ">40"},
                    "Triglycerides": {"value": 125, "unit": "mg/dL", "normal_range": "<150"}
                },
                "interpretation": "LDL slightly elevated",
                "notes": "Recommend lifestyle modifications"
            }
        ]
        
        return lab_results[:limit]
    
    @staticmethod
    def get_vital_signs_history(
        db: Session,
        patient_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get patient's vital signs history"""
        
        vital_signs = []
        
        for i in range(min(limit, 10)):
            vital_signs.append({
                "record_id": f"vitals_{uuid.uuid4().hex[:8]}",
                "patient_id": patient_id,
                "recorded_at": (datetime.utcnow() - timedelta(days=i*7)).isoformat(),
                "blood_pressure": {
                    "systolic": 120 + (i * 2),
                    "diastolic": 80 + i
                },
                "heart_rate": 72 + (i % 5),
                "temperature": 98.6,
                "respiratory_rate": 16,
                "oxygen_saturation": 98,
                "weight": 70.5,
                "height": 175,
                "bmi": 23.0,
                "recorded_by": "Nurse Smith"
            })
        
        return vital_signs


# Singleton instance
patient_history_service = PatientHistoryService()
