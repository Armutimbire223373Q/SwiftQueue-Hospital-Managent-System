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


# First Aid Guidance Endpoint
class FirstAidRequest(BaseModel):
    emergency_type: str
    location: Optional[str] = None
    available_equipment: Optional[List[str]] = None
    patient_conscious: Optional[bool] = True

@router.post("/first-aid")
async def get_first_aid_instructions(request: FirstAidRequest):
    """
    Provide first aid instructions based on emergency type.
    
    Args:
        request: First aid request with emergency type and context
        
    Returns:
        First aid instructions and steps
    """
    emergency_type = request.emergency_type.lower()
    
    # First aid instructions database
    first_aid_guide = {
        "bleeding": {
            "priority": "HIGH",
            "steps": [
                "Apply direct pressure to the wound with a clean cloth",
                "Elevate the injured area above heart level if possible",
                "Maintain pressure for at least 10 minutes",
                "If bleeding persists, apply additional cloth without removing the first",
                "Call emergency services if bleeding is severe"
            ],
            "warnings": ["Do not remove embedded objects", "Watch for signs of shock"],
            "equipment": ["Clean cloth", "Bandages", "Gloves"]
        },
        "choking": {
            "priority": "CRITICAL",
            "steps": [
                "Ask 'Are you choking?' to confirm",
                "Encourage coughing if person can still cough",
                "Perform 5 back blows between shoulder blades",
                "Perform 5 abdominal thrusts (Heimlich maneuver)",
                "Alternate between back blows and abdominal thrusts",
                "Call emergency services immediately if unsuccessful"
            ],
            "warnings": ["Do not perform on infants under 1 year", "Do not slap on back if person can cough"],
            "equipment": []
        },
        "burns": {
            "priority": "MEDIUM",
            "steps": [
                "Remove person from heat source",
                "Cool the burn with cool (not cold) running water for 10-20 minutes",
                "Remove any clothing or jewelry near the burn (unless stuck)",
                "Cover with sterile, non-stick dressing",
                "Do not apply ice, butter, or ointments",
                "Seek medical attention for severe burns"
            ],
            "warnings": ["Do not break blisters", "Do not use ice directly on burns"],
            "equipment": ["Cool water", "Sterile dressing", "Clean cloth"]
        },
        "cardiac_arrest": {
            "priority": "CRITICAL",
            "steps": [
                "Check for responsiveness - tap shoulders and shout",
                "Call 911 immediately or have someone else call",
                "Check for breathing - look for chest movement",
                "Begin CPR immediately if not breathing normally",
                "Place person on firm, flat surface",
                "Position hands on center of chest, interlocked",
                "Compress chest 2 inches deep at 100-120/minute",
                "Give 30 compressions followed by 2 rescue breaths",
                "Use AED (Automated External Defibrillator) if available",
                "Continue CPR until emergency services arrive"
            ],
            "warnings": ["Do not delay CPR", "Push hard and fast", "Minimize interruptions"],
            "equipment": ["AED if available", "CPR barrier mask"]
        },
        "cpr": {
            "priority": "CRITICAL",
            "steps": [
                "Check for responsiveness - tap and shout",
                "Call emergency services immediately",
                "Place person on firm, flat surface",
                "Position hands on center of chest",
                "Perform 30 chest compressions (2 inches deep, 100-120/min)",
                "Give 2 rescue breaths (if trained)",
                "Continue cycles of 30 compressions and 2 breaths",
                "Continue until help arrives or person recovers"
            ],
            "warnings": ["Do not stop CPR unless person shows signs of life", "Push hard and fast"],
            "equipment": ["AED if available", "CPR barrier device"]
        },
        "fracture": {
            "priority": "MEDIUM",
            "steps": [
                "Do not move the injured area",
                "Immobilize the injured limb",
                "Apply ice packs wrapped in cloth to reduce swelling",
                "Elevate if possible without causing pain",
                "Seek medical attention immediately",
                "Monitor for shock symptoms"
            ],
            "warnings": ["Do not try to realign the bone", "Do not apply ice directly to skin"],
            "equipment": ["Splint materials", "Ice pack", "Cloth"]
        },
        "heart_attack": {
            "priority": "CRITICAL",
            "steps": [
                "Call emergency services immediately",
                "Have person sit or lie down in comfortable position",
                "Loosen any tight clothing",
                "Give aspirin if available and person not allergic (chew, don't swallow)",
                "Stay with person and monitor condition",
                "Be prepared to perform CPR if person becomes unconscious"
            ],
            "warnings": ["Do not leave person alone", "Do not give anything by mouth if unconscious"],
            "equipment": ["Aspirin", "AED if available"]
        },
        "stroke": {
            "priority": "CRITICAL",
            "steps": [
                "Remember F.A.S.T.: Face drooping, Arm weakness, Speech difficulty, Time to call 911",
                "Call emergency services immediately",
                "Note the time symptoms started",
                "Have person lie down with head and shoulders elevated",
                "Do not give food or drink",
                "Monitor breathing and consciousness"
            ],
            "warnings": ["Time is critical - every minute counts", "Do not give aspirin"],
            "equipment": []
        },
        "shock": {
            "priority": "HIGH",
            "steps": [
                "Call emergency services",
                "Lay person down and elevate legs 12 inches (unless head, neck, or back injury)",
                "Keep person warm with blanket",
                "Do not give food or drink",
                "Turn head to side if vomiting",
                "Monitor breathing and pulse"
            ],
            "warnings": ["Do not move person if spinal injury suspected", "Do not elevate legs if uncomfortable"],
            "equipment": ["Blanket", "Pillows for elevation"]
        },
        "allergic_reaction": {
            "priority": "HIGH",
            "steps": [
                "Check if person has epinephrine auto-injector (EpiPen)",
                "Help administer EpiPen if available (inject into outer thigh)",
                "Call emergency services immediately",
                "Have person lie down and elevate legs",
                "Monitor breathing and consciousness",
                "Be prepared to perform CPR if needed",
                "Give second dose after 5-15 minutes if no improvement"
            ],
            "warnings": ["Anaphylaxis can be life-threatening", "Always call 911 even after EpiPen"],
            "equipment": ["EpiPen", "Antihistamines"]
        },
        "seizure": {
            "priority": "MEDIUM",
            "steps": [
                "Stay calm and time the seizure",
                "Clear area of dangerous objects",
                "Cushion head with something soft",
                "Turn person on their side after seizure",
                "Do not restrain or hold person down",
                "Do not put anything in mouth",
                "Stay with person until fully conscious",
                "Call 911 if seizure lasts more than 5 minutes"
            ],
            "warnings": ["Never put objects in mouth", "Do not give food/drink until fully alert"],
            "equipment": ["Soft cushion", "Blanket"]
        }
    }
    
    # Get instructions for the emergency type
    instructions = first_aid_guide.get(emergency_type)
    
    if not instructions:
        # Return general emergency response for unknown types
        return {
            "emergency_type": request.emergency_type,
            "priority": "UNKNOWN",
            "message": "Specific instructions not available for this emergency type",
            "general_advice": [
                "Call emergency services (911) immediately",
                "Ensure scene safety",
                "Do not move injured person unless necessary",
                "Monitor vital signs",
                "Provide comfort and reassurance"
            ],
            "warning": "When in doubt, always call emergency services"
        }
    
    # Enhance response based on available equipment
    available_equipment = request.available_equipment or []
    equipment_status = {}
    for item in instructions["equipment"]:
        equipment_status[item] = item.lower() in [e.lower() for e in available_equipment]
    
    # Estimate response time based on priority
    response_time_map = {
        "CRITICAL": 5,  # 5 minutes
        "HIGH": 15,     # 15 minutes
        "MEDIUM": 30,   # 30 minutes
        "LOW": 60       # 60 minutes
    }
    
    return {
        "emergency_type": request.emergency_type,
        "priority_level": instructions["priority"],
        "recommendations": instructions["steps"],
        "warnings": instructions["warnings"],
        "required_equipment": instructions["equipment"],
        "equipment_availability": equipment_status,
        "location_context": request.location or "Not specified",
        "patient_conscious": request.patient_conscious,
        "estimated_response_time": response_time_map.get(instructions["priority"], 30),
        "critical_note": "Always call emergency services for serious emergencies" if instructions["priority"] in ["CRITICAL", "HIGH"] else None
    }