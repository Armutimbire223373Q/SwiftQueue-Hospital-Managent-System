from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import re
import logging
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.emergency_service import dispatch_ambulance, EmergencyServiceError

router = APIRouter()
logger = logging.getLogger(__name__)

class SymptomAnalysisRequest(BaseModel):
    symptoms: str
    patient_age: Optional[str] = None
    medical_history: Optional[str] = None
    additional_context: Optional[str] = None
    patient_id: Optional[int] = None

@router.post("/analyze-symptoms")
async def analyze_symptoms(request: SymptomAnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze patient symptoms to determine emergency level and priority
    Uses rule-based analysis until Ollama integration is set up
    Automatically dispatches ambulance for critical emergencies
    """
    try:
        logger.info(f"Analyzing symptoms: {request.symptoms[:50]}...")

        # Rule-based analysis (fallback until Ollama is integrated)
        analysis = _analyze_symptoms_rule_based(request.symptoms, request.patient_age, request.patient_id, db)

        return {
            "success": True,
            "analysis": analysis,
            "recommendations": analysis["recommended_actions"]
        }

    except Exception as e:
        logger.error(f"Error in symptom analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def ai_health_check():
    """
    Check AI service health
    """
    return {
        "status": "healthy",
        "models_available": False,
        "service_type": "rule_based",
        "note": "Using rule-based analysis. Ollama integration pending."
    }

def _analyze_symptoms_rule_based(symptoms: str, age: Optional[str] = None, patient_id: Optional[int] = None, db: Optional[Session] = None) -> dict:
    """
    Rule-based symptom analysis for priority determination
    """
    symptoms_lower = symptoms.lower()
    
    # Critical symptoms (Emergency - Level 1)
    critical_keywords = [
        'chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding',
        'stroke', 'heart attack', 'cardiac arrest', 'anaphylaxis', 'not breathing',
        'severe allergic reaction', 'major trauma', 'overdose', 'severe burns'
    ]
    
    # High priority symptoms (Urgent - Level 2)  
    high_keywords = [
        'severe pain', 'high fever', 'broken bone', 'mental crisis', 'suicidal',
        'seizure', 'dehydration', 'vomiting blood', 'severe headache', 'fainting',
        'allergic reaction', 'severe injury', 'can\'t walk', 'intense pain'
    ]
    
    # Moderate symptoms (Semi-urgent - Level 3)
    moderate_keywords = [
        'pain', 'fever', 'nausea', 'headache', 'infection', 'sprain', 'cut',
        'burn', 'rash', 'dizziness', 'cough', 'sore throat', 'stomach ache'
    ]
    
    # Low priority symptoms (Non-urgent - Level 4)
    low_keywords = [
        'checkup', 'routine', 'vaccination', 'cold', 'minor', 'consultation',
        'follow up', 'medication refill', 'physical exam'
    ]
    
    # Age-based risk factors
    age_risk = 0
    if age:
        age_num = _extract_age_number(age)
        if age_num:
            if age_num >= 65 or age_num <= 2:
                age_risk = 1  # Higher risk for elderly and very young
            elif age_num <= 18:
                age_risk = 0.5  # Moderate risk for children
    
    # Check for critical symptoms
    if any(keyword in symptoms_lower for keyword in critical_keywords):
        logger.warning("🚨 CRITICAL EMERGENCY DETECTED")

        # Initialize dispatch information
        dispatch_info = None

        # Attempt ambulance dispatch if patient_id and db are available
        if patient_id and db:
            try:
                logger.info(f"Attempting ambulance dispatch for patient {patient_id}")
                dispatch = dispatch_ambulance(
                    db=db,
                    patient_id=patient_id,
                    emergency_details=f"Critical symptoms detected: {symptoms}"
                )
                dispatch_info = {
                    "dispatch_id": dispatch.id,
                    "ambulance_id": dispatch.ambulance_id,
                    "status": dispatch.dispatch_status,
                    "estimated_response_time": dispatch.response_time,
                    "dispatched_at": dispatch.dispatched_at.isoformat() if dispatch.dispatched_at else None
                }
                logger.info(f"🚨 Ambulance dispatched successfully: {dispatch_info}")
            except EmergencyServiceError as e:
                logger.error(f"Ambulance dispatch failed: {e}")
                dispatch_info = {
                    "error": str(e),
                    "status": "failed"
                }
            except Exception as e:
                logger.error(f"Unexpected error during ambulance dispatch: {e}")
                dispatch_info = {
                    "error": f"Unexpected dispatch error: {str(e)}",
                    "status": "failed"
                }
        else:
            logger.warning("Cannot dispatch ambulance: missing patient_id or database session")
            if not patient_id:
                logger.warning("Patient ID not provided in request")
            if not db:
                logger.warning("Database session not available")

        return {
            "emergency_level": "critical",
            "confidence": min(0.95, 0.85 + age_risk * 0.1),
            "triage_category": "Emergency",
            "estimated_wait_time": 0,
            "department_recommendation": "Emergency",
            "recommended_actions": [
                "🚨 SEEK IMMEDIATE EMERGENCY CARE",
                "Call 911 if condition is life-threatening",
                "Go to nearest emergency department"
            ],
            "risk_factors": ["High-risk condition detected", "Immediate medical attention required"],
            "ai_reasoning": "Critical symptoms detected requiring immediate emergency care",
            "timestamp": "2024-01-01T00:00:00Z",
            "ambulance_dispatch": dispatch_info
        }
    
    # Check for high priority symptoms
    elif any(keyword in symptoms_lower for keyword in high_keywords):
        return {
            "emergency_level": "high",
            "confidence": min(0.85, 0.75 + age_risk * 0.1),
            "triage_category": "Urgent",
            "estimated_wait_time": 30,
            "department_recommendation": "Urgent Care" if "mental" not in symptoms_lower else "Emergency",
            "recommended_actions": [
                "⚠️ Seek prompt medical attention",
                "Go to urgent care or emergency department",
                "Do not delay treatment"
            ],
            "risk_factors": ["Urgent condition requiring prompt care"],
            "ai_reasoning": "High priority symptoms requiring urgent medical attention",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    # Check for moderate symptoms
    elif any(keyword in symptoms_lower for keyword in moderate_keywords):
        return {
            "emergency_level": "moderate",
            "confidence": min(0.75, 0.65 + age_risk * 0.1),
            "triage_category": "Semi-urgent",
            "estimated_wait_time": 90,
            "department_recommendation": "General Medicine",
            "recommended_actions": [
                "📋 Schedule appointment within 24-48 hours",
                "Monitor symptoms for changes",
                "Seek care if symptoms worsen"
            ],
            "risk_factors": ["Monitor for symptom progression"],
            "ai_reasoning": "Moderate symptoms requiring medical evaluation within 1-2 days",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    # Low priority or routine care
    else:
        return {
            "emergency_level": "low",
            "confidence": 0.6,
            "triage_category": "Non-urgent",
            "estimated_wait_time": 120,
            "department_recommendation": "General Medicine",
            "recommended_actions": [
                "📅 Schedule routine appointment",
                "Non-urgent medical care",
                "Can wait several days if needed"
            ],
            "risk_factors": [],
            "ai_reasoning": "Routine or low-priority symptoms, standard appointment recommended",
            "timestamp": "2024-01-01T00:00:00Z"
        }

def _extract_age_number(age_str: str) -> Optional[int]:
    """Extract numeric age from age string"""
    try:
        # Try to extract number from string
        numbers = re.findall(r'\d+', age_str)
        if numbers:
            return int(numbers[0])
    except:
        pass
    return None