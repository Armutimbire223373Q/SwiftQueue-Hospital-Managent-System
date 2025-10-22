"""
FHIR Integration Module for Healthcare Queue Management System

This module provides FHIR API endpoints and resource management
for modern healthcare interoperability.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.database import get_db
from app.models.models import Patient, Appointment, QueueEntry
from app.services.fhir_service import FHIRService

router = APIRouter()  # Remove prefix - it's added in main.py
logger = logging.getLogger(__name__)

# Initialize FHIR service
fhir_service = FHIRService()

# FHIR Resource Endpoints

@router.get("/Patient", summary="Search Patients")
async def search_patients(
    family: Optional[str] = Query(None, description="Patient family name"),
    given: Optional[str] = Query(None, description="Patient given name"),
    identifier: Optional[str] = Query(None, description="Patient identifier"),
    birthdate: Optional[str] = Query(None, description="Patient birth date"),
    gender: Optional[str] = Query(None, description="Patient gender"),
    _count: int = Query(20, description="Number of results to return"),
    _offset: int = Query(0, description="Starting offset for results"),
    db: Session = Depends(get_db)
):
    """
    Search for patients using FHIR Patient resource parameters.
    """
    try:
        search_params = {
            "family": family,
            "given": given,
            "identifier": identifier,
            "birthdate": birthdate,
            "gender": gender
        }

        bundle = await fhir_service.search_patients(search_params, _count, _offset, db)

        return bundle

    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search patients: {str(e)}")

@router.get("/Patient/{patient_id}", summary="Get Patient by ID")
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific patient by FHIR ID.
    """
    try:
        patient_resource = await fhir_service.get_patient_by_id(patient_id, db)

        if not patient_resource:
            raise HTTPException(status_code=404, detail="Patient not found")

        return patient_resource

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get patient: {str(e)}")

@router.post("/Patient", summary="Create Patient")
async def create_patient(
    patient_resource: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new patient using FHIR Patient resource.
    """
    try:
        result = await fhir_service.create_patient(patient_resource, db)

        return result

    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create patient: {str(e)}")

@router.put("/Patient/{patient_id}", summary="Update Patient")
async def update_patient(
    patient_id: str,
    patient_resource: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update an existing patient using FHIR Patient resource.
    """
    try:
        result = await fhir_service.update_patient(patient_id, patient_resource, db)

        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update patient: {str(e)}")

@router.get("/Appointment", summary="Search Appointments")
async def search_appointments(
    patient: Optional[str] = Query(None, description="Patient reference"),
    practitioner: Optional[str] = Query(None, description="Practitioner reference"),
    status: Optional[str] = Query(None, description="Appointment status"),
    date: Optional[str] = Query(None, description="Appointment date"),
    _count: int = Query(20, description="Number of results to return"),
    _offset: int = Query(0, description="Starting offset for results"),
    db: Session = Depends(get_db)
):
    """
    Search for appointments using FHIR Appointment resource parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "practitioner": practitioner,
            "status": status,
            "date": date
        }

        bundle = await fhir_service.search_appointments(search_params, _count, _offset, db)

        return bundle

    except Exception as e:
        logger.error(f"Error searching appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search appointments: {str(e)}")

@router.get("/Appointment/{appointment_id}", summary="Get Appointment by ID")
async def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific appointment by FHIR ID.
    """
    try:
        appointment_resource = await fhir_service.get_appointment_by_id(appointment_id, db)

        if not appointment_resource:
            raise HTTPException(status_code=404, detail="Appointment not found")

        return appointment_resource

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment {appointment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get appointment: {str(e)}")

@router.post("/Appointment", summary="Create Appointment")
async def create_appointment(
    appointment_resource: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new appointment using FHIR Appointment resource.
    """
    try:
        result = await fhir_service.create_appointment(appointment_resource, db)

        return result

    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create appointment: {str(e)}")

@router.get("/Encounter", summary="Search Encounters")
async def search_encounters(
    patient: Optional[str] = Query(None, description="Patient reference"),
    status: Optional[str] = Query(None, description="Encounter status"),
    date: Optional[str] = Query(None, description="Encounter date"),
    _count: int = Query(20, description="Number of results to return"),
    _offset: int = Query(0, description="Starting offset for results"),
    db: Session = Depends(get_db)
):
    """
    Search for encounters using FHIR Encounter resource parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "status": status,
            "date": date
        }

        bundle = await fhir_service.search_encounters(search_params, _count, _offset, db)

        return bundle

    except Exception as e:
        logger.error(f"Error searching encounters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search encounters: {str(e)}")

@router.get("/Observation", summary="Search Observations")
async def search_observations(
    patient: Optional[str] = Query(None, description="Patient reference"),
    category: Optional[str] = Query(None, description="Observation category"),
    code: Optional[str] = Query(None, description="Observation code"),
    date: Optional[str] = Query(None, description="Observation date"),
    _count: int = Query(20, description="Number of results to return"),
    _offset: int = Query(0, description="Starting offset for results"),
    db: Session = Depends(get_db)
):
    """
    Search for observations using FHIR Observation resource parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "category": category,
            "code": code,
            "date": date
        }

        bundle = await fhir_service.search_observations(search_params, _count, _offset, db)

        return bundle

    except Exception as e:
        logger.error(f"Error searching observations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search observations: {str(e)}")

# Capability Statement
@router.get("/metadata", summary="Get FHIR Capability Statement")
async def get_capability_statement():
    """
    Return the FHIR server's capability statement describing supported resources and operations.
    """
    try:
        capability_statement = {
            "resourceType": "CapabilityStatement",
            "status": "active",
            "date": datetime.utcnow().isoformat(),
            "publisher": "Healthcare Queue Management System",
            "kind": "instance",
            "software": {
                "name": "QMS FHIR Server",
                "version": "1.0.0"
            },
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [
                {
                    "mode": "server",
                    "resource": [
                        {
                            "type": "Patient",
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"},
                                {"code": "create"},
                                {"code": "update"}
                            ],
                            "searchParam": [
                                {"name": "family", "type": "string"},
                                {"name": "given", "type": "string"},
                                {"name": "identifier", "type": "token"},
                                {"name": "birthdate", "type": "date"},
                                {"name": "gender", "type": "token"}
                            ]
                        },
                        {
                            "type": "Appointment",
                            "interaction": [
                                {"code": "read"},
                                {"code": "search-type"},
                                {"code": "create"}
                            ],
                            "searchParam": [
                                {"name": "patient", "type": "reference"},
                                {"name": "practitioner", "type": "reference"},
                                {"name": "status", "type": "token"},
                                {"name": "date", "type": "date"}
                            ]
                        },
                        {
                            "type": "Encounter",
                            "interaction": [
                                {"code": "search-type"}
                            ],
                            "searchParam": [
                                {"name": "patient", "type": "reference"},
                                {"name": "status", "type": "token"},
                                {"name": "date", "type": "date"}
                            ]
                        },
                        {
                            "type": "Observation",
                            "interaction": [
                                {"code": "search-type"}
                            ],
                            "searchParam": [
                                {"name": "patient", "type": "reference"},
                                {"name": "category", "type": "token"},
                                {"name": "code", "type": "token"},
                                {"name": "date", "type": "date"}
                            ]
                        }
                    ]
                }
            ]
        }

        return capability_statement

    except Exception as e:
        logger.error(f"Error getting capability statement: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capability statement")

# FHIR Operations
@router.post("/$convert", summary="Convert between FHIR versions")
async def convert_fhir_version(
    resource: Dict[str, Any],
    from_version: str = Query("4.0.1", description="Source FHIR version"),
    to_version: str = Query("4.0.1", description="Target FHIR version")
):
    """
    Convert FHIR resources between different FHIR versions.
    """
    try:
        converted_resource = await fhir_service.convert_fhir_version(
            resource, from_version, to_version
        )

        return converted_resource

    except Exception as e:
        logger.error(f"Error converting FHIR version: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to convert FHIR version: {str(e)}")

@router.post("/Patient/{patient_id}/$everything", summary="Patient Everything Operation")
async def patient_everything(
    patient_id: str,
    _since: Optional[str] = Query(None, description="Only include resources modified after this date"),
    _count: int = Query(50, description="Number of resources to return"),
    db: Session = Depends(get_db)
):
    """
    Return all resources related to a patient (Patient $everything operation).
    """
    try:
        bundle = await fhir_service.patient_everything(patient_id, _since, _count, db)

        return bundle

    except Exception as e:
        logger.error(f"Error getting patient everything for {patient_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get patient everything: {str(e)}")

# Integration Status and Configuration
@router.get("/status", summary="Get FHIR Integration Status")
async def get_fhir_status():
    """
    Get the current status of FHIR integration.
    """
    try:
        status = await fhir_service.get_integration_status()

        return {
            "status": "healthy" if status["connected"] else "disconnected",
            "endpoints": status,
            "last_check": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting FHIR status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get FHIR integration status")

@router.post("/test-connection", summary="Test FHIR Connection")
async def test_fhir_connection():
    """
    Test connection to FHIR interfaces and validate configuration.
    """
    try:
        test_result = await fhir_service.test_connection()

        return {
            "status": "success" if test_result["success"] else "failed",
            "test_results": test_result,
            "tested_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error testing FHIR connection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FHIR connection test failed: {str(e)}")

@router.get("/config", summary="Get FHIR Configuration")
async def get_fhir_config():
    """
    Get current FHIR configuration settings.
    """
    try:
        config = fhir_service.get_configuration()

        return {
            "configuration": config,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting FHIR config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get FHIR configuration")

@router.put("/config", summary="Update FHIR Configuration")
async def update_fhir_config(config: Dict[str, Any]):
    """
    Update FHIR configuration settings.
    """
    try:
        updated_config = fhir_service.update_configuration(config)

        return {
            "status": "success",
            "message": "FHIR configuration updated",
            "configuration": updated_config,
            "updated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error updating FHIR config: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update FHIR configuration: {str(e)}")