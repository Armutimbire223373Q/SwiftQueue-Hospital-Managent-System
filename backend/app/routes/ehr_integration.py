"""
EHR Integration Module for Healthcare Queue Management System

This module provides integration capabilities with Electronic Health Record (EHR)
systems for comprehensive patient data synchronization and interoperability.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models.models import Patient, Appointment, QueueEntry, User
from app.services.ehr_service import EHRService

router = APIRouter()  # Remove prefix - it's added in main.py
logger = logging.getLogger(__name__)

# Initialize EHR service
ehr_service = EHRService()

@router.post("/sync-patient", summary="Sync Patient Data with EHR")
async def sync_patient_with_ehr(
    patient_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Synchronize patient data with connected EHR systems.

    This endpoint triggers a full patient data sync including:
    - Demographics
    - Medical history
    - Allergies and medications
    - Recent encounters
    - Insurance information
    """
    try:
        # Check if patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Start background sync
        background_tasks.add_task(
            ehr_service.sync_patient_data,
            patient_id,
            db
        )

        return {
            "status": "sync_started",
            "message": f"Patient data synchronization started for patient {patient_id}",
            "patient_id": patient_id,
            "started_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting patient sync for {patient_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start patient synchronization: {str(e)}")

@router.post("/sync-appointment", summary="Sync Appointment with EHR")
async def sync_appointment_with_ehr(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Synchronize appointment data with EHR systems.
    """
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        background_tasks.add_task(
            ehr_service.sync_appointment_data,
            appointment_id,
            db
        )

        return {
            "status": "sync_started",
            "message": f"Appointment synchronization started for appointment {appointment_id}",
            "appointment_id": appointment_id,
            "started_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting appointment sync for {appointment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start appointment synchronization: {str(e)}")

@router.get("/patient/{patient_id}/medical-record", summary="Get Patient Medical Record from EHR")
async def get_patient_medical_record(
    patient_id: int,
    include_history: bool = Query(True, description="Include medical history"),
    include_medications: bool = Query(True, description="Include current medications"),
    include_allergies: bool = Query(True, description="Include allergies"),
    db: Session = Depends(get_db)
):
    """
    Retrieve comprehensive medical record from connected EHR systems.
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        medical_record = await ehr_service.get_patient_medical_record(
            patient_id,
            include_history=include_history,
            include_medications=include_medications,
            include_allergies=include_allergies,
            db=db
        )

        return {
            "patient_id": patient_id,
            "patient_name": patient.name,
            "medical_record": medical_record,
            "retrieved_at": datetime.utcnow().isoformat(),
            "source": "EHR_SYSTEM"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medical record for patient {patient_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve medical record: {str(e)}")

@router.post("/patient/{patient_id}/update-record", summary="Update Patient Record in EHR")
async def update_patient_record_in_ehr(
    patient_id: int,
    update_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Update patient medical record in connected EHR systems.
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        background_tasks.add_task(
            ehr_service.update_patient_record,
            patient_id,
            update_data,
            db
        )

        return {
            "status": "update_started",
            "message": f"Patient record update started for patient {patient_id}",
            "patient_id": patient_id,
            "update_data": update_data,
            "started_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting record update for patient {patient_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start record update: {str(e)}")

@router.get("/sync-status", summary="Get EHR Synchronization Status")
async def get_ehr_sync_status(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Starting offset"),
    db: Session = Depends(get_db)
):
    """
    Get the status of EHR synchronization operations.
    """
    try:
        sync_status = await ehr_service.get_sync_status(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            db=db
        )

        return {
            "sync_operations": sync_status,
            "total": len(sync_status),
            "limit": limit,
            "offset": offset,
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving sync status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sync status: {str(e)}")

@router.post("/bulk-sync", summary="Bulk Synchronize Data with EHR")
async def bulk_sync_with_ehr(
    background_tasks: BackgroundTasks,
    sync_type: str = Query(..., description="Type of data to sync: patients, appointments, or all"),
    db: Session = Depends(get_db)
):
    """
    Perform bulk synchronization of data with EHR systems.

    Supported sync types:
    - patients: Sync all patient data
    - appointments: Sync all appointment data
    - all: Sync all data types
    """
    try:
        if sync_type not in ["patients", "appointments", "all"]:
            raise HTTPException(status_code=400, detail="Invalid sync_type. Must be: patients, appointments, or all")

        background_tasks.add_task(
            ehr_service.bulk_sync_data,
            sync_type,
            db
        )

        return {
            "status": "bulk_sync_started",
            "message": f"Bulk synchronization started for {sync_type}",
            "sync_type": sync_type,
            "started_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk sync for {sync_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start bulk synchronization: {str(e)}")

@router.get("/connected-systems", summary="Get Connected EHR Systems")
async def get_connected_ehr_systems():
    """
    Get information about connected EHR systems and their status.
    """
    try:
        connected_systems = await ehr_service.get_connected_systems()

        return {
            "connected_systems": connected_systems,
            "total_connected": len([s for s in connected_systems if s.get("status") == "connected"]),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving connected systems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve connected systems: {str(e)}")

@router.post("/test-connection", summary="Test EHR System Connection")
async def test_ehr_connection(
    system_id: Optional[str] = Query(None, description="Specific system to test")
):
    """
    Test connection to EHR systems.
    """
    try:
        test_results = await ehr_service.test_connection(system_id)

        return {
            "status": "success" if all(r.get("success", False) for r in test_results) else "partial_failure",
            "test_results": test_results,
            "tested_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error testing EHR connection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"EHR connection test failed: {str(e)}")

@router.get("/config", summary="Get EHR Integration Configuration")
async def get_ehr_config():
    """
    Get current EHR integration configuration.
    """
    try:
        config = ehr_service.get_configuration()

        return {
            "configuration": config,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting EHR config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get EHR configuration")

@router.put("/config", summary="Update EHR Integration Configuration")
async def update_ehr_config(config: Dict[str, Any]):
    """
    Update EHR integration configuration settings.
    """
    try:
        updated_config = ehr_service.update_configuration(config)

        return {
            "status": "success",
            "message": "EHR configuration updated",
            "configuration": updated_config,
            "updated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error updating EHR config: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update EHR configuration: {str(e)}")

@router.post("/webhook/{system_id}", summary="EHR System Webhook Endpoint")
async def ehr_webhook(
    system_id: str,
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive webhooks from EHR systems for real-time data updates.
    """
    try:
        # Process webhook in background
        background_tasks.add_task(
            ehr_service.process_webhook,
            system_id,
            webhook_data,
            db
        )

        return {
            "status": "webhook_received",
            "system_id": system_id,
            "message": "Webhook processed successfully",
            "received_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing webhook from {system_id}: {str(e)}")
        # Don't raise exception for webhooks - just log and return success
        return {
            "status": "webhook_received_with_errors",
            "system_id": system_id,
            "error": str(e),
            "received_at": datetime.utcnow().isoformat()
        }

@router.get("/audit-log", summary="Get EHR Integration Audit Log")
async def get_ehr_audit_log(
    start_date: Optional[str] = Query(None, description="Start date for audit log (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date for audit log (ISO format)"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, description="Number of results to return"),
    offset: int = Query(0, description="Starting offset"),
    db: Session = Depends(get_db)
):
    """
    Get audit log for EHR integration activities.
    """
    try:
        audit_log = await ehr_service.get_audit_log(
            start_date=start_date,
            end_date=end_date,
            action_type=action_type,
            limit=limit,
            offset=offset,
            db=db
        )

        return {
            "audit_entries": audit_log,
            "total": len(audit_log),
            "limit": limit,
            "offset": offset,
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving audit log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit log: {str(e)}")