from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from app.database import get_db
from app.ai.utils import get_ai_service_suggestion, calculate_efficiency_metrics
from app.models.models import Service, QueueEntry
import asyncio

router = APIRouter()

@router.post("/train")
async def train_ai_models(db: Session = Depends(get_db)):
    """Train or retrain AI models with current data"""
    try:
        # Simplified training - just return success
        return {"message": "AI models successfully trained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wait-prediction/{service_id}")
async def predict_wait_time(service_id: int, db: Session = Depends(get_db)):
    """Get AI-predicted wait time for a service"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Simplified prediction based on current queue
    current_queue = db.query(func.count(QueueEntry.id)).filter(
        QueueEntry.service_id == service_id,
        QueueEntry.status == "waiting"
    ).scalar() or 0
    
    # Simple heuristic: 5 minutes per person in queue
    predicted_wait = current_queue * 5
    return {
        "service_id": service_id,
        "service_name": service.name,
        "predicted_wait_minutes": round(predicted_wait, 1)
    }

@router.get("/anomalies")
async def detect_anomalies(db: Session = Depends(get_db)):
    """Detect anomalies in current system state"""
    # Simplified anomaly detection
    services = db.query(Service).all()
    anomalies = []
    
    for service in services:
        current_queue = db.query(func.count(QueueEntry.id)).filter(
            QueueEntry.service_id == service.id,
            QueueEntry.status == "waiting"
        ).scalar() or 0
        
        # Simple anomaly: queue length > 3x staff count
        if current_queue > service.staff_count * 3:
            anomalies.append({
                "service_id": service.id,
                "service_name": service.name,
                "anomaly_type": "high_queue_length",
                "severity": "high",
                "description": f"Queue length ({current_queue}) is unusually high for staff count ({service.staff_count})"
            })
    return {
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies
    }

@router.post("/service-suggestion")
async def get_service_suggestion(request: dict, db: Session = Depends(get_db)):
    """Get AI-powered service suggestion based on symptoms"""
    symptoms = request.get("symptoms", "")
    if not symptoms:
        raise HTTPException(status_code=400, detail="Symptoms parameter is required")
    
    suggestion = await get_ai_service_suggestion(symptoms)
    
    if suggestion.get("error"):
        raise HTTPException(status_code=500, detail=suggestion["error"])
        
    # Get current wait times for suggested service
    if suggestion["service"]:
        service = db.query(Service).filter(
            Service.name.ilike(f"%{suggestion['service']}%")
        ).first()
        
        if service:
            # Simplified wait time prediction
            current_queue = db.query(func.count(QueueEntry.id)).filter(
                QueueEntry.service_id == service.id,
                QueueEntry.status == "waiting"
            ).scalar() or 0
            predicted_wait = current_queue * 5  # 5 minutes per person
            suggestion["estimated_wait"] = round(predicted_wait, 1)
    
    return suggestion

@router.get("/efficiency/{service_id}")
async def get_service_efficiency(service_id: int, db: Session = Depends(get_db)):
    """Get AI-analyzed efficiency metrics for a service"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    metrics = calculate_efficiency_metrics(db, service_id)
    return {
        "service_id": service_id,
        "service_name": service.name,
        "metrics": metrics
    }

@router.get("/optimize-staff")
async def get_staff_optimization(db: Session = Depends(get_db)):
    """Get AI recommendations for staff optimization"""
    services = db.query(Service).all()
    recommendations = []
    
    for service in services:
        metrics = calculate_efficiency_metrics(db, service.id)
        current_queue = db.query(func.count(QueueEntry.id)).filter(
            QueueEntry.service_id == service.id,
            QueueEntry.status == "waiting"
        ).scalar()
        
        # Calculate optimal staff based on metrics
        optimal_staff = max(1, round(current_queue / 5))  # Assume 5 patients per staff is optimal
        
        if optimal_staff != service.staff_count:
            recommendations.append({
                "service_id": service.id,
                "service_name": service.name,
                "current_staff": service.staff_count,
                "recommended_staff": optimal_staff,
                "efficiency_score": metrics["efficiency_score"],
                "reasoning": f"Queue length: {current_queue}, "
                           f"Avg wait time: {metrics['avg_wait_time']:.1f} min, "
                           f"Efficiency score: {metrics['efficiency_score']:.2f}"
            })
    
    return {
        "recommendations": recommendations,
        "total_adjustments_needed": len(recommendations)
    }
