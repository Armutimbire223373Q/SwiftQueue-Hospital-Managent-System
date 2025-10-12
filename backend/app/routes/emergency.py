from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.models import User, EmergencyDispatch
from app.routes.auth import get_current_active_user
from app.services.emergency_service import (
    dispatch_ambulance,
    get_dispatch_status,
    get_patient_dispatches,
    EmergencyServiceError
)
from app.services.infobip_sms_service import infobip_sms_service

router = APIRouter()

# Pydantic models
class DispatchAmbulanceRequest(BaseModel):
    patient_id: int
    emergency_details: str

class DispatchResponse(BaseModel):
    id: int
    patient_id: int
    emergency_details: str
    dispatch_address: str
    dispatch_status: str
    dispatched_at: Optional[datetime]
    response_time: Optional[int]
    ambulance_id: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DispatchStatusResponse(BaseModel):
    id: int
    patient_id: int
    emergency_details: str
    dispatch_address: str
    dispatch_status: str
    dispatched_at: Optional[datetime]
    response_time: Optional[int]
    ambulance_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    patient_name: Optional[str]

    class Config:
        from_attributes = True

class PatientDispatchesResponse(BaseModel):
    id: int
    patient_id: int
    emergency_details: str
    dispatch_address: str
    dispatch_status: str
    dispatched_at: Optional[datetime]
    response_time: Optional[int]
    ambulance_id: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SMSNotificationRequest(BaseModel):
    phone_number: str
    message: str
    priority: Optional[str] = "normal"

class EmergencyETANotificationRequest(BaseModel):
    dispatch_id: int
    eta_minutes: int
    custom_message: Optional[str] = None

class EmergencyDispatchAlertRequest(BaseModel):
    dispatch_id: int
    responder_phones: List[str]

@router.post("/dispatch-ambulance", response_model=DispatchResponse)
async def dispatch_ambulance_endpoint(
    request: DispatchAmbulanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Dispatch an ambulance for a patient emergency.

    Args:
        request: Dispatch request containing patient_id and emergency_details
        db: Database session
        current_user: Authenticated user

    Returns:
        DispatchResponse: Created dispatch information

    Raises:
        HTTPException: If dispatch fails or user lacks permissions
    """
    try:
        # Check permissions - only staff and admin can dispatch ambulances
        if current_user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff and administrators can dispatch ambulances"
            )

        # Dispatch ambulance using service
        dispatch = dispatch_ambulance(
            db=db,
            patient_id=request.patient_id,
            emergency_details=request.emergency_details
        )

        # Get patient information for SMS notifications
        patient = db.query(User).filter(User.id == request.patient_id).first()

        # Send initial dispatch SMS if patient has phone number
        if patient and patient.phone:
            try:
                sms_result = await infobip_sms_service.send_sms(
                    to=patient.phone,
                    message=f"🚨 EMERGENCY: Ambulance dispatched to your location. Emergency details: {request.emergency_details}. Help is on the way!"
                )
                # Log SMS result but don't fail the dispatch if SMS fails
                if sms_result.get("success"):
                    print(f"SMS notification sent to patient {patient.phone}")
                else:
                    print(f"Failed to send SMS to patient: {sms_result.get('error')}")
            except Exception as sms_error:
                print(f"SMS notification error: {sms_error}")
                # Continue with dispatch even if SMS fails

        return dispatch

    except EmergencyServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during ambulance dispatch: {str(e)}"
        )

@router.get("/dispatch/{dispatch_id}", response_model=DispatchStatusResponse)
async def get_dispatch_status_endpoint(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the status of a specific emergency dispatch.

    Args:
        dispatch_id: ID of the dispatch to check
        db: Database session
        current_user: Authenticated user

    Returns:
        DispatchStatusResponse: Dispatch status information

    Raises:
        HTTPException: If dispatch not found or access denied
    """
    try:
        # Get dispatch status using service
        dispatch = get_dispatch_status(db=db, dispatch_id=dispatch_id)

        if not dispatch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency dispatch not found"
            )

        # Check permissions - users can only see their own dispatches unless they're staff/admin
        if (current_user.role not in ["admin", "staff"] and
            dispatch.patient_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this dispatch"
            )

        # Build response with patient name
        response_data = DispatchStatusResponse.from_orm(dispatch)
        response_data.patient_name = dispatch.patient.name if dispatch.patient else None

        return response_data

    except EmergencyServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving dispatch status: {str(e)}"
        )

@router.get("/dispatches/patient/{patient_id}", response_model=List[PatientDispatchesResponse])
async def get_patient_dispatches_endpoint(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all emergency dispatches for a specific patient.

    Args:
        patient_id: ID of the patient
        db: Database session
        current_user: Authenticated user

    Returns:
        List[PatientDispatchesResponse]: List of patient's dispatches

    Raises:
        HTTPException: If access denied or database error
    """
    try:
        # Check permissions - users can only see their own dispatches unless they're staff/admin
        if (current_user.role not in ["admin", "staff"] and
            patient_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to patient dispatches"
            )

        # Get patient dispatches using service
        dispatches = get_patient_dispatches(db=db, patient_id=patient_id)

        return dispatches

    except EmergencyServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving patient dispatches: {str(e)}"
        )

@router.post("/sms/send")
async def send_emergency_sms(
    request: SMSNotificationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send an SMS notification for emergency purposes.

    Args:
        request: SMS request containing phone number and message
        current_user: Authenticated user

    Returns:
        SMS send result

    Raises:
        HTTPException: If SMS send fails or user lacks permissions
    """
    try:
        # Check permissions - only staff and admin can send emergency SMS
        if current_user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff and administrators can send emergency SMS notifications"
            )

        # Send SMS using Infobip service
        result = await infobip_sms_service.send_sms(
            to=request.phone_number,
            message=request.message
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMS send failed: {result.get('error', 'Unknown error')}"
            )

        return {
            "success": True,
            "message_id": result.get("message_id"),
            "status": result.get("status"),
            "recipient": request.phone_number
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error sending SMS: {str(e)}"
        )

@router.post("/sms/eta-notification")
async def send_emergency_eta_sms(
    request: EmergencyETANotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send ETA notification SMS to patient when ambulance is 10+ minutes away.

    Args:
        request: ETA notification request
        db: Database session
        current_user: Authenticated user

    Returns:
        SMS send result

    Raises:
        HTTPException: If dispatch not found or SMS send fails
    """
    try:
        # Check permissions
        if current_user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff and administrators can send ETA notifications"
            )

        # Get dispatch details
        dispatch = get_dispatch_status(db=db, dispatch_id=request.dispatch_id)
        if not dispatch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency dispatch not found"
            )

        # Get patient phone number
        patient = db.query(User).filter(User.id == dispatch.patient_id).first()
        if not patient or not patient.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient phone number not available"
            )

        # Send ETA notification
        result = await infobip_sms_service.send_emergency_eta_notification(
            patient_phone=patient.phone,
            eta_minutes=request.eta_minutes,
            ambulance_id=dispatch.ambulance_id or "Unknown",
            location=dispatch.dispatch_address
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ETA SMS send failed: {result.get('error', 'Unknown error')}"
            )

        return {
            "success": True,
            "message_id": result.get("message_id"),
            "patient_phone": patient.phone,
            "eta_minutes": request.eta_minutes,
            "ambulance_id": dispatch.ambulance_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error sending ETA notification: {str(e)}"
        )

@router.post("/sms/dispatch-alert")
async def send_emergency_dispatch_alert(
    request: EmergencyDispatchAlertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send emergency dispatch alerts to multiple responders.

    Args:
        request: Dispatch alert request with responder phones
        db: Database session
        current_user: Authenticated user

    Returns:
        Bulk SMS send results

    Raises:
        HTTPException: If dispatch not found or SMS send fails
    """
    try:
        # Check permissions
        if current_user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff and administrators can send dispatch alerts"
            )

        # Get dispatch details
        dispatch = get_dispatch_status(db=db, dispatch_id=request.dispatch_id)
        if not dispatch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency dispatch not found"
            )

        # Send dispatch alerts to all responders
        results = await infobip_sms_service.send_emergency_dispatch_alert(
            responders=request.responder_phones,
            emergency_location=dispatch.dispatch_address,
            emergency_type=dispatch.emergency_details,
            priority="HIGH"
        )

        successful_sends = len([r for r in results if r.get("success")])

        return {
            "success": True,
            "total_recipients": len(request.responder_phones),
            "successful_sends": successful_sends,
            "failed_sends": len(request.responder_phones) - successful_sends,
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error sending dispatch alerts: {str(e)}"
        )