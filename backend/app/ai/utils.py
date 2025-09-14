"""
AI utility functions for the Queue Management System.
Includes service suggestion, efficiency calculations, and other AI-powered features.
"""

import asyncio
import random
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import QueueEntry, Service, Analytics

async def get_ai_service_suggestion(symptoms: str) -> Dict:
    """
    AI-powered service suggestion based on patient symptoms.
    In a real implementation, this would use NLP and medical knowledge bases.
    For now, using keyword matching and heuristics.
    """
    try:
        symptoms_lower = symptoms.lower()
        
        # Medical keyword mapping to services
        service_keywords = {
            "Emergency Care": [
                "chest pain", "heart attack", "stroke", "severe pain", "bleeding", 
                "unconscious", "difficulty breathing", "emergency", "urgent", "accident",
                "trauma", "severe", "critical", "life threatening"
            ],
            "Cardiology": [
                "heart", "cardiac", "chest pain", "palpitations", "blood pressure",
                "hypertension", "arrhythmia", "cardiovascular", "heart rate"
            ],
            "General Medicine": [
                "fever", "cold", "flu", "headache", "general", "checkup", "consultation",
                "tired", "fatigue", "general pain", "routine", "physical exam"
            ],
            "Laboratory Services": [
                "blood test", "lab work", "blood", "urine", "test", "screening",
                "cholesterol", "diabetes", "lab", "analysis", "sample"
            ],
            "Radiology": [
                "x-ray", "scan", "ct", "mri", "imaging", "fracture", "bone",
                "radiology", "picture", "image"
            ],
            "Pediatrics": [
                "child", "baby", "infant", "pediatric", "kid", "children",
                "vaccination", "vaccine", "growth", "development"
            ]
        }
        
        # Score each service based on keyword matches
        service_scores = {}
        for service, keywords in service_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in symptoms_lower:
                    score += 1
                    # Give higher weight to exact matches
                    if keyword == symptoms_lower.strip():
                        score += 2
            service_scores[service] = score
        
        # Find the best matching service
        best_service = max(service_scores, key=service_scores.get) if service_scores else None
        confidence = service_scores.get(best_service, 0) / len(symptoms.split()) if best_service else 0
        
        # If no good match, default to General Medicine
        if confidence < 0.3:
            best_service = "General Medicine"
            confidence = 0.5
        
        # Generate urgency level based on keywords
        urgent_keywords = ["severe", "emergency", "urgent", "critical", "chest pain", "bleeding"]
        urgency = "high" if any(keyword in symptoms_lower for keyword in urgent_keywords) else "medium"
        
        return {
            "service": best_service,
            "confidence": min(confidence, 1.0),
            "urgency": urgency,
            "reasoning": f"Based on symptoms analysis, {best_service} is recommended",
            "alternative_services": [
                service for service, score in sorted(service_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
                if score > 0
            ]
        }
        
    except Exception as e:
        return {
            "error": f"AI service suggestion failed: {str(e)}",
            "service": "General Medicine",  # Safe fallback
            "confidence": 0.0
        }

def calculate_efficiency_metrics(db: Session, service_id: int) -> Dict:
    """
    Calculate efficiency metrics for a specific service.
    """
    try:
        # Get current queue metrics
        current_queue_length = db.query(func.count(QueueEntry.id)).filter(
            QueueEntry.service_id == service_id,
            QueueEntry.status == "waiting"
        ).scalar() or 0
        
        # Get average wait time for waiting patients
        avg_wait_time = db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
            QueueEntry.service_id == service_id,
            QueueEntry.status == "waiting"
        ).scalar() or 0
        
        # Get service information
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return {"error": "Service not found"}
        
        # Get recent analytics (last 24 hours)
        recent_analytics = db.query(Analytics).filter(
            Analytics.service_id == service_id,
            Analytics.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(Analytics.timestamp.desc()).first()
        
        # Calculate efficiency score
        # Based on: queue length, wait time, staff utilization, and historical performance
        queue_efficiency = max(0, 1 - (current_queue_length / 20))  # Assume 20+ queue is very inefficient
        wait_time_efficiency = max(0, 1 - (avg_wait_time / 60))  # Assume 60+ min wait is very inefficient
        
        # Use historical data if available
        if recent_analytics:
            historical_efficiency = recent_analytics.efficiency_score
            staff_utilization = recent_analytics.staff_utilization
        else:
            historical_efficiency = 0.8  # Default assumption
            staff_utilization = 0.7  # Default assumption
        
        # Weighted efficiency score
        efficiency_score = (
            queue_efficiency * 0.3 +
            wait_time_efficiency * 0.3 +
            historical_efficiency * 0.2 +
            staff_utilization * 0.2
        )
        
        # Calculate throughput (patients per hour)
        throughput = service.service_rate * service.staff_count if service.service_rate else 2.0
        
        # Calculate capacity utilization
        capacity_utilization = min(1.0, current_queue_length / (throughput * 2))  # Assume 2-hour capacity
        
        return {
            "efficiency_score": round(efficiency_score, 3),
            "current_queue_length": current_queue_length,
            "avg_wait_time": round(avg_wait_time, 1),
            "staff_count": service.staff_count,
            "staff_utilization": round(staff_utilization, 3) if recent_analytics else 0.7,
            "throughput_per_hour": round(throughput, 1),
            "capacity_utilization": round(capacity_utilization, 3),
            "service_rate": service.service_rate,
            "recommendations": generate_efficiency_recommendations(
                efficiency_score, current_queue_length, avg_wait_time, service.staff_count
            )
        }
        
    except Exception as e:
        return {
            "error": f"Failed to calculate efficiency metrics: {str(e)}",
            "efficiency_score": 0.0
        }

def generate_efficiency_recommendations(
    efficiency_score: float, 
    queue_length: int, 
    avg_wait_time: float, 
    staff_count: int
) -> List[str]:
    """
    Generate actionable recommendations based on efficiency metrics.
    """
    recommendations = []
    
    if efficiency_score < 0.6:
        recommendations.append("Critical: Service efficiency is below acceptable levels")
    
    if queue_length > 10:
        recommendations.append(f"High queue length ({queue_length}): Consider adding more staff or service counters")
    
    if avg_wait_time > 45:
        recommendations.append(f"Long wait times ({avg_wait_time:.1f} min): Review service processes for optimization")
    
    if queue_length > staff_count * 8:
        recommendations.append("Staff overload detected: Immediate staff reinforcement recommended")
    
    if efficiency_score > 0.9 and queue_length < 3:
        recommendations.append("Excellent efficiency: Consider reallocating excess resources to other services")
    
    if not recommendations:
        recommendations.append("Service operating within normal parameters")
    
    return recommendations

def predict_peak_times(db: Session, service_id: int) -> Dict:
    """
    Predict peak times for a service based on historical data.
    """
    try:
        # Get historical analytics for the past week
        week_ago = datetime.utcnow() - timedelta(days=7)
        analytics = db.query(Analytics).filter(
            Analytics.service_id == service_id,
            Analytics.timestamp >= week_ago
        ).all()
        
        if not analytics:
            return {"error": "Insufficient historical data"}
        
        # Analyze peak hours
        hour_loads = {}
        for record in analytics:
            hour = record.peak_hour
            if hour not in hour_loads:
                hour_loads[hour] = []
            hour_loads[hour].append(record.peak_load)
        
        # Calculate average load per hour
        avg_hourly_loads = {
            hour: sum(loads) / len(loads) 
            for hour, loads in hour_loads.items()
        }
        
        # Find peak hours
        sorted_hours = sorted(avg_hourly_loads.items(), key=lambda x: x[1], reverse=True)
        peak_hours = sorted_hours[:3]  # Top 3 peak hours
        
        # Predict next peak
        current_hour = datetime.utcnow().hour
        next_peaks = [hour for hour, _ in peak_hours if hour > current_hour]
        next_peak = next_peaks[0] if next_peaks else peak_hours[0][0]
        
        return {
            "peak_hours": [{"hour": hour, "avg_load": round(load, 1)} for hour, load in peak_hours],
            "next_predicted_peak": {
                "hour": next_peak,
                "expected_load": round(avg_hourly_loads.get(next_peak, 0), 1)
            },
            "current_trend": "increasing" if current_hour in [h for h, _ in peak_hours[:2]] else "stable"
        }
        
    except Exception as e:
        return {"error": f"Peak time prediction failed: {str(e)}"}

def calculate_optimal_staffing(db: Session, service_id: int) -> Dict:
    """
    Calculate optimal staffing levels based on current and predicted demand.
    """
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return {"error": "Service not found"}
        
        # Get current queue metrics
        current_queue = db.query(func.count(QueueEntry.id)).filter(
            QueueEntry.service_id == service_id,
            QueueEntry.status == "waiting"
        ).scalar() or 0
        
        # Calculate optimal staff based on queue length and service rate
        service_rate = service.service_rate or 2.0  # Default 2 patients per hour per staff
        target_wait_time = 30  # Target max 30 minutes wait
        
        # Calculate required throughput to clear queue in target time
        required_throughput = current_queue / (target_wait_time / 60)  # patients per hour
        optimal_staff = max(1, round(required_throughput / service_rate))
        
        # Consider peak time predictions
        peak_prediction = predict_peak_times(db, service_id)
        if not peak_prediction.get("error"):
            next_peak_load = peak_prediction.get("next_predicted_peak", {}).get("expected_load", 0)
            peak_optimal_staff = max(1, round(next_peak_load / service_rate))
            optimal_staff = max(optimal_staff, peak_optimal_staff)
        
        return {
            "current_staff": service.staff_count,
            "optimal_staff": optimal_staff,
            "staff_adjustment": optimal_staff - service.staff_count,
            "reasoning": f"Based on current queue ({current_queue}) and service rate ({service_rate} patients/hour/staff)",
            "expected_improvement": {
                "wait_time_reduction": max(0, round((current_queue / service.staff_count - current_queue / optimal_staff) * 60 / service_rate, 1)),
                "efficiency_gain": round(min(0.3, (optimal_staff - service.staff_count) * 0.1), 2)
            }
        }
        
    except Exception as e:
        return {"error": f"Optimal staffing calculation failed: {str(e)}"}