"""
HL7 Integration Module for Healthcare Queue Management System

This module provides HL7 message parsing, generation, and integration capabilities
for interoperability with hospital information systems.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from app.database import get_db
from app.models.models import Patient, QueueEntry, Appointment
from app.services.hl7_service import HL7Service

router = APIRouter()  # Remove prefix - it's added in main.py
logger = logging.getLogger(__name__)

# Initialize HL7 service
hl7_service = HL7Service()

@router.post("/adt", summary="Process HL7 ADT Messages")
async def process_adt_message(
    message: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process HL7 ADT (Admission, Discharge, Transfer) messages.

    Supported message types:
    - ADT^A01: Patient Admit
    - ADT^A02: Patient Transfer
    - ADT^A03: Patient Discharge
    - ADT^A04: Patient Registration
    - ADT^A08: Patient Information Update
    """
    try:
        result = await hl7_service.process_adt_message(message, db)

        # Add background task for additional processing if needed
        if result.get("requires_followup"):
            background_tasks.add_task(
                hl7_service.process_followup_actions,
                result["patient_id"],
                result["message_type"],
                db
            )

        return {
            "status": "success",
            "message": f"Processed {result['message_type']} message",
            "patient_id": result.get("patient_id"),
            "processed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing ADT message: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process ADT message: {str(e)}")

@router.post("/orm", summary="Process HL7 ORM Messages")
async def process_orm_message(
    message: str,
    db: Session = Depends(get_db)
):
    """
    Process HL7 ORM (Order) messages for appointment and service requests.

    Supported message types:
    - ORM^O01: Order Message
    """
    try:
        result = await hl7_service.process_orm_message(message, db)

        return {
            "status": "success",
            "message": f"Processed {result['message_type']} message",
            "appointment_id": result.get("appointment_id"),
            "processed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing ORM message: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process ORM message: {str(e)}")

@router.post("/oru", summary="Process HL7 ORU Messages")
async def process_oru_message(
    message: str,
    db: Session = Depends(get_db)
):
    """
    Process HL7 ORU (Observation Result) messages for lab results and diagnostics.
    """
    try:
        result = await hl7_service.process_oru_message(message, db)

        return {
            "status": "success",
            "message": f"Processed {result['message_type']} message",
            "patient_id": result.get("patient_id"),
            "processed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing ORU message: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process ORU message: {str(e)}")

@router.get("/messages", summary="Get HL7 Message History")
async def get_hl7_messages(
    limit: int = 50,
    offset: int = 0,
    message_type: Optional[str] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve HL7 message processing history with filtering options.
    """
    try:
        messages = await hl7_service.get_message_history(
            db, limit, offset, message_type, patient_id
        )

        return {
            "messages": messages,
            "total": len(messages),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving HL7 messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve HL7 messages")

@router.post("/generate/{message_type}", summary="Generate HL7 Messages")
async def generate_hl7_message(
    message_type: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Generate HL7 messages for export to other systems.

    Supported types: ADT, ORM, ORU
    """
    try:
        message = await hl7_service.generate_message(message_type, data, db)

        return {
            "status": "success",
            "message_type": message_type,
            "hl7_message": message,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating HL7 message: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to generate HL7 message: {str(e)}")

@router.get("/status", summary="Get HL7 Integration Status")
async def get_hl7_status():
    """
    Get the current status of HL7 integration and connection health.
    """
    try:
        status = await hl7_service.get_integration_status()

        return {
            "status": "healthy" if status["connected"] else "disconnected",
            "connection": status,
            "last_check": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting HL7 status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get HL7 integration status")

@router.post("/test-connection", summary="Test HL7 Connection")
async def test_hl7_connection():
    """
    Test connection to HL7 interfaces and validate configuration.
    """
    try:
        test_result = await hl7_service.test_connection()

        return {
            "status": "success" if test_result["success"] else "failed",
            "test_results": test_result,
            "tested_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error testing HL7 connection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HL7 connection test failed: {str(e)}")

@router.get("/config", summary="Get HL7 Configuration")
async def get_hl7_config():
    """
    Get current HL7 configuration settings.
    """
    try:
        config = hl7_service.get_configuration()

        return {
            "configuration": config,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting HL7 config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get HL7 configuration")

@router.put("/config", summary="Update HL7 Configuration")
async def update_hl7_config(config: Dict[str, Any]):
    """
    Update HL7 configuration settings.
    """
    try:
        updated_config = hl7_service.update_configuration(config)

        return {
            "status": "success",
            "message": "HL7 configuration updated",
            "configuration": updated_config,
            "updated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error updating HL7 config: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update HL7 configuration: {str(e)}")