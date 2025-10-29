from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user
from app.services.patient_history_service import patient_history_service
from app.models.models import User

router = APIRouter()


# Request Models
class CreateMedicalRecordRequest(BaseModel):
    patient_id: int
    visit_type: str = Field(..., description="Type of visit: routine_checkup, emergency, follow_up, consultation")
    chief_complaint: str
    diagnosis: str
    treatment: str
    notes: Optional[str] = None
    vital_signs: Optional[Dict[str, Any]] = None


class UpdateMedicalRecordRequest(BaseModel):
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AddMedicationRequest(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    route: str = Field(..., description="Route of administration: Oral, IV, IM, etc.")
    start_date: str
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    refills: int = 0


class AddAllergyRequest(BaseModel):
    allergen: str
    reaction: str
    severity: str = Field(..., description="Severity: mild, moderate, severe")


# Endpoints
@router.get('/{patient_id}')
async def get_patient_history(
    patient_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete medical history for a patient
    
    - **patient_id**: Patient ID
    - **limit**: Maximum number of records (default: 100)
    - **offset**: Pagination offset (default: 0)
    """
    try:
        # In production, verify user has permission to view this patient's records
        history = patient_history_service.get_patient_history(
            db=db,
            patient_id=patient_id,
            limit=limit,
            offset=offset
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve patient history: {str(e)}")


@router.post('/medical-record')
async def create_medical_record(
    request: CreateMedicalRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new medical record for a patient
    
    - **patient_id**: Patient ID
    - **visit_type**: Type of visit (routine_checkup, emergency, follow_up, consultation)
    - **chief_complaint**: Patient's main complaint
    - **diagnosis**: Medical diagnosis
    - **treatment**: Prescribed treatment
    - **notes**: Additional notes
    - **vital_signs**: Optional vital signs data
    """
    try:
        record = patient_history_service.create_medical_record(
            db=db,
            patient_id=request.patient_id,
            visit_type=request.visit_type,
            chief_complaint=request.chief_complaint,
            diagnosis=request.diagnosis,
            treatment=request.treatment,
            physician_id=current_user.id,
            notes=request.notes,
            vital_signs=request.vital_signs
        )
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create medical record: {str(e)}")


@router.put('/medical-record/{record_id}')
async def update_medical_record(
    record_id: str,
    request: UpdateMedicalRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing medical record
    
    - **record_id**: Medical record ID
    - **diagnosis**: Updated diagnosis
    - **treatment**: Updated treatment
    - **notes**: Updated notes
    - **status**: Updated status
    """
    try:
        result = patient_history_service.update_medical_record(
            db=db,
            record_id=record_id,
            diagnosis=request.diagnosis,
            treatment=request.treatment,
            notes=request.notes,
            status=request.status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update medical record: {str(e)}")


@router.get('/{patient_id}/medications')
async def get_medications(
    patient_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient's medication list
    
    - **patient_id**: Patient ID
    - **active_only**: Filter for active medications only (default: True)
    """
    try:
        medications = patient_history_service.get_medications(
            db=db,
            patient_id=patient_id,
            active_only=active_only
        )
        return medications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve medications: {str(e)}")


@router.post('/{patient_id}/medications')
async def add_medication(
    patient_id: int,
    request: AddMedicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new medication to patient's record
    
    - **medication_name**: Name of medication
    - **dosage**: Dosage (e.g., "100mg")
    - **frequency**: Frequency (e.g., "Once daily")
    - **route**: Route of administration
    - **start_date**: Start date
    - **end_date**: Optional end date
    - **instructions**: Optional special instructions
    - **refills**: Number of refills allowed
    """
    try:
        medication = patient_history_service.add_medication(
            db=db,
            patient_id=patient_id,
            medication_name=request.medication_name,
            dosage=request.dosage,
            frequency=request.frequency,
            route=request.route,
            prescribed_by=f"Dr. {current_user.name}",
            start_date=request.start_date,
            end_date=request.end_date,
            instructions=request.instructions,
            refills=request.refills
        )
        return medication
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add medication: {str(e)}")


@router.get('/{patient_id}/allergies')
async def get_allergies(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient's allergy information"""
    try:
        allergies = patient_history_service.get_allergies(db=db, patient_id=patient_id)
        return allergies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve allergies: {str(e)}")


@router.post('/{patient_id}/allergies')
async def add_allergy(
    patient_id: int,
    request: AddAllergyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new allergy to patient's record
    
    - **allergen**: Allergen name
    - **reaction**: Type of reaction
    - **severity**: Severity level (mild, moderate, severe)
    """
    try:
        allergy = patient_history_service.add_allergy(
            db=db,
            patient_id=patient_id,
            allergen=request.allergen,
            reaction=request.reaction,
            severity=request.severity
        )
        return allergy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add allergy: {str(e)}")


@router.get('/{patient_id}/lab-results')
async def get_lab_results(
    patient_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient's laboratory test results
    
    - **patient_id**: Patient ID
    - **limit**: Maximum number of results (default: 50)
    """
    try:
        results = patient_history_service.get_lab_results(
            db=db,
            patient_id=patient_id,
            limit=limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lab results: {str(e)}")


@router.get('/{patient_id}/vital-signs')
async def get_vital_signs_history(
    patient_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient's vital signs history
    
    - **patient_id**: Patient ID
    - **limit**: Maximum number of records (default: 20)
    """
    try:
        vital_signs = patient_history_service.get_vital_signs_history(
            db=db,
            patient_id=patient_id,
            limit=limit
        )
        return vital_signs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vital signs: {str(e)}")
