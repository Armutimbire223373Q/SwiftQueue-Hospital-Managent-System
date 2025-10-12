import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import User, EmergencyDispatch
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyServiceError(Exception):
    """Custom exception for emergency service errors."""
    pass

def get_patient_address(db: Session, patient_id: int) -> str:
    """
    Retrieve and format patient address from User model.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        Formatted address string

    Raises:
        EmergencyServiceError: If patient not found or address incomplete
    """
    try:
        patient = db.query(User).filter(User.id == patient_id).first()
        if not patient:
            raise EmergencyServiceError(f"Patient with ID {patient_id} not found")

        # Build address from available fields
        address_parts = []
        if patient.street_address:
            address_parts.append(patient.street_address)
        if patient.city:
            address_parts.append(patient.city)
        if patient.state:
            address_parts.append(patient.state)
        if patient.zip_code:
            address_parts.append(patient.zip_code)
        if patient.country:
            address_parts.append(patient.country)

        if not address_parts:
            raise EmergencyServiceError(f"No address information available for patient {patient_id}")

        return ", ".join(address_parts)

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving patient address: {e}")
        raise EmergencyServiceError("Failed to retrieve patient address")

def simulate_emergency_communication(emergency_details: str, address: str) -> Dict[str, Any]:
    """
    Simulate communication with emergency services.

    Args:
        emergency_details: Description of the emergency
        address: Patient address

    Returns:
        Dict containing simulated response with ambulance assignment
    """
    # Simulate processing time
    time.sleep(random.uniform(0.5, 2.0))

    # Simulate ambulance assignment
    ambulance_id = f"AMB-{random.randint(100, 999)}"

    # Simulate response time (5-15 minutes)
    response_time = random.randint(5, 15)

    logger.info(f"Emergency communication simulated: Ambulance {ambulance_id} assigned to {address}")

    return {
        "ambulance_id": ambulance_id,
        "estimated_response_time": response_time,
        "status": "dispatched"
    }

def dispatch_ambulance(db: Session, patient_id: int, emergency_details: str) -> EmergencyDispatch:
    """
    Dispatch an ambulance to a patient's location.

    Args:
        db: Database session
        patient_id: Patient ID
        emergency_details: Description of the emergency

    Returns:
        EmergencyDispatch object

    Raises:
        EmergencyServiceError: If dispatch fails
    """
    try:
        logger.info(f"Dispatching ambulance for patient {patient_id}")

        # Get patient address
        address = get_patient_address(db, patient_id)

        # Create dispatch record
        dispatch = EmergencyDispatch(
            patient_id=patient_id,
            emergency_details=emergency_details,
            dispatch_address=address,
            dispatch_status="pending"
        )

        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)

        # Simulate emergency services communication
        try:
            emergency_response = simulate_emergency_communication(emergency_details, address)

            # Update dispatch with ambulance info
            dispatch.ambulance_id = emergency_response["ambulance_id"]
            dispatch.response_time = emergency_response["estimated_response_time"]
            dispatch.dispatch_status = "dispatched"
            dispatch.dispatched_at = datetime.utcnow()

            db.commit()
            db.refresh(dispatch)

            logger.info(f"Ambulance {dispatch.ambulance_id} dispatched to patient {patient_id}")

        except Exception as e:
            logger.error(f"Emergency communication failed: {e}")
            # Still save the dispatch but mark as failed
            dispatch.dispatch_status = "pending"
            dispatch.notes = f"Emergency communication failed: {str(e)}"
            db.commit()

        return dispatch

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during ambulance dispatch: {e}")
        raise EmergencyServiceError("Failed to dispatch ambulance due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during ambulance dispatch: {e}")
        raise EmergencyServiceError(f"Failed to dispatch ambulance: {str(e)}")

def get_dispatch_status(db: Session, dispatch_id: int) -> Optional[EmergencyDispatch]:
    """
    Get the status of an emergency dispatch.

    Args:
        db: Database session
        dispatch_id: Dispatch ID

    Returns:
        EmergencyDispatch object or None if not found

    Raises:
        EmergencyServiceError: If database error occurs
    """
    try:
        dispatch = db.query(EmergencyDispatch).filter(EmergencyDispatch.id == dispatch_id).first()

        if dispatch:
            # Simulate status updates for dispatched ambulances
            if dispatch.dispatch_status == "dispatched" and dispatch.dispatched_at:
                elapsed_time = (datetime.utcnow() - dispatch.dispatched_at).total_seconds() / 60

                # Simulate status progression based on elapsed time
                if elapsed_time > dispatch.response_time + 5:  # Arrived + 5 minutes
                    dispatch.dispatch_status = "arrived"
                elif elapsed_time > dispatch.response_time:
                    dispatch.dispatch_status = "en_route"

                # Auto-commit status changes
                if dispatch.dispatch_status in ["en_route", "arrived"]:
                    db.commit()

            logger.info(f"Retrieved dispatch status for ID {dispatch_id}: {dispatch.dispatch_status}")

        return dispatch

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving dispatch status: {e}")
        raise EmergencyServiceError("Failed to retrieve dispatch status")

def update_dispatch_status(db: Session, dispatch_id: int, status: str, notes: Optional[str] = None) -> bool:
    """
    Update the status of an emergency dispatch.

    Args:
        db: Database session
        dispatch_id: Dispatch ID
        status: New status
        notes: Optional notes

    Returns:
        True if update successful

    Raises:
        EmergencyServiceError: If update fails
    """
    try:
        dispatch = db.query(EmergencyDispatch).filter(EmergencyDispatch.id == dispatch_id).first()

        if not dispatch:
            raise EmergencyServiceError(f"Dispatch with ID {dispatch_id} not found")

        valid_statuses = ["pending", "dispatched", "en_route", "arrived", "completed", "cancelled"]
        if status not in valid_statuses:
            raise EmergencyServiceError(f"Invalid status: {status}")

        dispatch.dispatch_status = status
        if notes:
            dispatch.notes = notes

        db.commit()

        logger.info(f"Updated dispatch {dispatch_id} status to {status}")
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating dispatch status: {e}")
        raise EmergencyServiceError("Failed to update dispatch status")

def get_patient_dispatches(db: Session, patient_id: int) -> list:
    """
    Get all emergency dispatches for a patient.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        List of EmergencyDispatch objects

    Raises:
        EmergencyServiceError: If database error occurs
    """
    try:
        dispatches = db.query(EmergencyDispatch).filter(
            EmergencyDispatch.patient_id == patient_id
        ).order_by(EmergencyDispatch.created_at.desc()).all()

        logger.info(f"Retrieved {len(dispatches)} dispatches for patient {patient_id}")
        return dispatches

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving patient dispatches: {e}")
        raise EmergencyServiceError("Failed to retrieve patient dispatches")