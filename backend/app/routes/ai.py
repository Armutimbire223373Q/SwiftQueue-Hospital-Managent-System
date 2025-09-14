from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from app.database import get_db
from app.ai.predictors import QueueAnalyzer
from app.ai.utils import get_ai_service_suggestion, calculate_efficiency_metrics
from app.models.models import Service, QueueEntry
import asyncio

router = APIRouter()
queue_analyzer = QueueAnalyzer()

@router.post("/train")
async def train_ai_models(db: Session = Depends(get_db)):
    """Train or retrain AI models with current data"""
    try:
        queue_analyzer.train_models(db)
        return {"message": "AI models successfully trained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wait-prediction/{service_id}")
async def predict_wait_time(service_id: int, db: Session = Depends(get_db)):
    """Get AI-predicted wait time for a service"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    predicted_wait = queue_analyzer.predict_service_wait(service_id, db)
    return {
        "service_id": service_id,
        "service_name": service.name,
        "predicted_wait_minutes": round(predicted_wait, 1)
    }

@router.get("/anomalies")
async def detect_anomalies(db: Session = Depends(get_db)):
    """Detect anomalies in current system state"""
    anomalies = queue_analyzer.detect_system_anomalies(db)
    return {
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies
    }

@router.post("/service-suggestion")
async def get_service_suggestion(symptoms: str, db: Session = Depends(get_db)):
    """Get AI-powered service suggestion based on symptoms"""
    suggestion = await get_ai_service_suggestion(symptoms)
    
    if suggestion.get("error"):
        raise HTTPException(status_code=500, detail=suggestion["error"])
        
    # Get current wait times for suggested service
    if suggestion["service"]:
        service = db.query(Service).filter(
            Service.name.ilike(f"%{suggestion['service']}%")
        ).first()
        
        if service:
            predicted_wait = queue_analyzer.predict_service_wait(service.id, db)
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
