"""
Enhanced AI Routes with Multi-Stage Workflow and Advanced Triage
Based on insights from the comprehensive hospital dataset analysis
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.database import get_db
from app.ai.triage_system import triage_system
from app.ai.predictions import prediction_service
from app.ai.openrouter_service import openrouter_service
from app.models.workflow_models import PatientVisit, WorkflowStage, Department
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class TriageRequest(BaseModel):
    symptoms: str
    age_group: str
    insurance_type: str
    department: Optional[str] = None
    arrival_time: Optional[datetime] = None

class AITriageRequest(BaseModel):
    symptoms: str
    age_group: str
    insurance_type: str
    department: Optional[str] = None
    arrival_time: Optional[datetime] = None
    medical_history: Optional[str] = None
    additional_context: Optional[str] = None

class SymptomAnalysisRequest(BaseModel):
    symptoms: str
    patient_age: Optional[str] = None
    medical_history: Optional[str] = None
    additional_context: Optional[str] = None

class WorkflowStageUpdate(BaseModel):
    visit_id: int
    stage_name: str
    stage_data: Optional[Dict] = None

class PatientWorkflowRequest(BaseModel):
    patient_id: str
    department: str
    appointment_type: str
    symptoms: str
    age_group: str
    insurance_type: str
    booking_type: str = "Online"

class ResourceOptimizationRequest(BaseModel):
    current_patients: List[Dict]
    available_resources: Dict

@router.post("/triage/calculate")
async def calculate_triage_score(request: TriageRequest):
    """Calculate AI-powered triage score and recommendations"""
    try:
        arrival_time = request.arrival_time or datetime.now()
        
        result = triage_system.calculate_triage_score(
            symptoms=request.symptoms,
            age_group=request.age_group,
            insurance_type=request.insurance_type,
            arrival_time=arrival_time,
            department=request.department
        )
        
        return {
            "success": True,
            "triage_result": result,
            "recommendations": _generate_triage_recommendations(result)
        }
        
    except Exception as e:
        logger.error(f"Error calculating triage score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triage/ai-enhanced")
async def calculate_ai_enhanced_triage(request: AITriageRequest):
    """Calculate AI-enhanced triage score using local LLM"""
    try:
        arrival_time = request.arrival_time or datetime.now()
        
        result = await triage_system.calculate_triage_score_with_ai(
            symptoms=request.symptoms,
            age_group=request.age_group,
            insurance_type=request.insurance_type,
            arrival_time=arrival_time,
            department=request.department,
            medical_history=request.medical_history,
            additional_context=request.additional_context
        )
        
        return {
            "success": True,
            "triage_result": result,
            "recommendations": _generate_ai_triage_recommendations(result)
        }
        
    except Exception as e:
        logger.error(f"Error calculating AI-enhanced triage score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symptoms/analyze")
async def analyze_symptoms_with_ai(request: SymptomAnalysisRequest):
    """Analyze patient symptoms using local LLM"""
    try:
        analysis_result = await openrouter_service.analyze_symptoms(
            symptoms=request.symptoms,
            patient_age=request.patient_age,
            medical_history=request.medical_history,
            additional_context=request.additional_context
        )
        
        if analysis_result.get("error"):
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        return {
            "success": True,
            "analysis": analysis_result,
            "recommendations": _generate_symptom_analysis_recommendations(analysis_result)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing symptoms with AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symptoms/batch-analyze")
async def batch_analyze_symptoms(symptom_batch: List[SymptomAnalysisRequest]):
    """Analyze multiple symptoms in batch using local LLM"""
    try:
        # Convert to the format expected by the service
        batch_data = []
        for request in symptom_batch:
            batch_data.append({
                "symptoms": request.symptoms,
                "patient_age": request.patient_age,
                "medical_history": request.medical_history,
                "additional_context": request.additional_context
            })
        
        results = await openrouter_service.batch_analyze_symptoms(batch_data)
        
        return {
            "success": True,
            "batch_results": results,
            "total_analyzed": len(results),
            "successful_analyses": len([r for r in results if not r.get("error")])
        }
        
    except Exception as e:
        logger.error(f"Error in batch symptom analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats():
    """Get AI cache statistics"""
    try:
        stats = openrouter_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache():
    """Clear AI response cache"""
    try:
        openrouter_service.clear_cache()
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/start-visit")
async def start_patient_visit(request: PatientWorkflowRequest, db: Session = Depends(get_db)):
    """Start a new patient visit with multi-stage workflow tracking"""
    try:
        # Calculate triage score
        triage_result = triage_system.calculate_triage_score(
            symptoms=request.symptoms,
            age_group=request.age_group,
            insurance_type=request.insurance_type,
            department=request.department
        )
        
        # Create patient visit record
        visit = PatientVisit(
            patient_id=request.patient_id,
            visit_id=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
            department=request.department,
            appointment_type=request.appointment_type,
            booking_type=request.booking_type,
            triage_category=triage_result['category'],
            reason_for_visit=request.symptoms,
            current_stage="Scheduled",
            appointment_time=datetime.now(),
            actual_arrival_time=datetime.now(),
            facility_occupancy_rate=0.5,  # Default, should be calculated
            providers_on_shift=5,  # Default, should be from actual data
            nurses_on_shift=8,  # Default, should be from actual data
            staff_to_patient_ratio=0.3  # Default, should be calculated
        )
        
        db.add(visit)
        db.flush()  # Get the ID
        
        # Create workflow stages
        stages = [
            "Registration", "Check-in", "Triage", "Provider", "Tests", "Discharge"
        ]
        
        for i, stage_name in enumerate(stages):
            workflow_stage = WorkflowStage(
                visit_id=visit.id,
                stage_name=stage_name,
                stage_order=i + 1,
                is_completed=False
            )
            db.add(workflow_stage)
        
        db.commit()
        
        return {
            "success": True,
            "visit_id": visit.id,
            "visit_number": visit.visit_id,
            "triage_result": triage_result,
            "estimated_total_time": triage_result['estimated_wait_time'],
            "workflow_stages": stages
        }
        
    except Exception as e:
        logger.error(f"Error starting patient visit: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/update-stage")
async def update_workflow_stage(request: WorkflowStageUpdate, db: Session = Depends(get_db)):
    """Update patient workflow stage"""
    try:
        # Find the workflow stage
        stage = db.query(WorkflowStage).filter(
            WorkflowStage.visit_id == request.visit_id,
            WorkflowStage.stage_name == request.stage_name
        ).first()
        
        if not stage:
            raise HTTPException(status_code=404, detail="Workflow stage not found")
        
        # Update stage
        if not stage.stage_start_time:
            stage.stage_start_time = datetime.now()
        
        stage.stage_end_time = datetime.now()
        stage.is_completed = True
        
        if stage.stage_start_time and stage.stage_end_time:
            stage.stage_duration = (stage.stage_end_time - stage.stage_start_time).total_seconds() / 60
        
        if request.stage_data:
            import json
            stage.stage_data = json.dumps(request.stage_data)
        
        # Update visit current stage
        visit = db.query(PatientVisit).filter(PatientVisit.id == request.visit_id).first()
        if visit:
            # Move to next stage
            next_stage = db.query(WorkflowStage).filter(
                WorkflowStage.visit_id == request.visit_id,
                WorkflowStage.stage_order == stage.stage_order + 1
            ).first()
            
            if next_stage:
                visit.current_stage = next_stage.stage_name
            else:
                visit.current_stage = "Discharged"
                visit.is_completed = True
        
        db.commit()
        
        return {
            "success": True,
            "stage_updated": request.stage_name,
            "duration_minutes": stage.stage_duration,
            "next_stage": visit.current_stage if visit else None
        }
        
    except Exception as e:
        logger.error(f"Error updating workflow stage: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/active-patients")
async def get_active_patients(db: Session = Depends(get_db)):
    """Get all active patients with their workflow status"""
    try:
        active_visits = db.query(PatientVisit).filter(
            PatientVisit.is_completed == False
        ).all()
        
        patients_data = []
        for visit in active_visits:
            # Get workflow stages
            stages = db.query(WorkflowStage).filter(
                WorkflowStage.visit_id == visit.id
            ).order_by(WorkflowStage.stage_order).all()
            
            # Calculate progress
            completed_stages = len([s for s in stages if s.is_completed])
            total_stages = len(stages)
            progress = (completed_stages / total_stages) * 100 if total_stages > 0 else 0
            
            # Calculate total time
            total_time = 0
            if visit.actual_arrival_time:
                total_time = (datetime.now() - visit.actual_arrival_time).total_seconds() / 60
            
            patients_data.append({
                "visit_id": visit.id,
                "patient_id": visit.patient_id,
                "department": visit.department,
                "triage_category": visit.triage_category,
                "current_stage": visit.current_stage,
                "progress_percentage": round(progress, 1),
                "total_time_minutes": round(total_time, 1),
                "stages": [
                    {
                        "name": stage.stage_name,
                        "order": stage.stage_order,
                        "is_completed": stage.is_completed,
                        "duration_minutes": stage.stage_duration,
                        "start_time": stage.stage_start_time,
                        "end_time": stage.stage_end_time
                    }
                    for stage in stages
                ]
            })
        
        return {
            "success": True,
            "active_patients": patients_data,
            "total_count": len(patients_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting active patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimization/resource-allocation")
async def optimize_resource_allocation(request: ResourceOptimizationRequest):
    """Optimize resource allocation based on current patient load"""
    try:
        optimization_result = triage_system.optimize_resource_allocation(
            current_patients=request.current_patients,
            available_resources=request.available_resources
        )
        
        return {
            "success": True,
            "optimization_result": optimization_result,
            "recommendations": _generate_optimization_recommendations(optimization_result)
        }
        
    except Exception as e:
        logger.error(f"Error optimizing resource allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/workflow-bottlenecks")
async def analyze_workflow_bottlenecks(db: Session = Depends(get_db)):
    """Analyze workflow bottlenecks and provide recommendations"""
    try:
        # Get recent workflow data
        recent_stages = db.query(WorkflowStage).filter(
            WorkflowStage.stage_start_time >= datetime.now() - timedelta(hours=24)
        ).all()
        
        # Analyze bottlenecks
        stage_analysis = {}
        for stage in recent_stages:
            stage_name = stage.stage_name
            if stage_name not in stage_analysis:
                stage_analysis[stage_name] = {
                    "total_patients": 0,
                    "total_duration": 0,
                    "avg_duration": 0,
                    "bottleneck_score": 0
                }
            
            stage_analysis[stage_name]["total_patients"] += 1
            if stage.stage_duration:
                stage_analysis[stage_name]["total_duration"] += stage.stage_duration
        
        # Calculate averages and bottleneck scores
        for stage_name, data in stage_analysis.items():
            if data["total_patients"] > 0:
                data["avg_duration"] = data["total_duration"] / data["total_patients"]
                # Bottleneck score based on average duration and patient count
                data["bottleneck_score"] = data["avg_duration"] * (data["total_patients"] / 10)
        
        # Identify bottlenecks
        bottlenecks = sorted(
            stage_analysis.items(),
            key=lambda x: x[1]["bottleneck_score"],
            reverse=True
        )[:3]
        
        return {
            "success": True,
            "bottleneck_analysis": {
                "stage_analysis": stage_analysis,
                "top_bottlenecks": [
                    {
                        "stage": stage_name,
                        "avg_duration": data["avg_duration"],
                        "patient_count": data["total_patients"],
                        "bottleneck_score": data["bottleneck_score"]
                    }
                    for stage_name, data in bottlenecks
                ],
                "recommendations": _generate_bottleneck_recommendations(bottlenecks)
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing workflow bottlenecks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/department-performance")
async def get_department_performance(db: Session = Depends(get_db)):
    """Get department performance metrics"""
    try:
        departments = db.query(Department).all()
        
        performance_data = []
        for dept in departments:
            # Get recent visits for this department
            recent_visits = db.query(PatientVisit).filter(
                PatientVisit.department == dept.name,
                PatientVisit.created_at >= datetime.now() - timedelta(days=7)
            ).all()
            
            if recent_visits:
                avg_wait_time = sum(v.estimated_wait_time or 0 for v in recent_visits) / len(recent_visits)
                avg_total_time = sum(v.total_time_in_hospital or 0 for v in recent_visits) / len(recent_visits)
                completion_rate = len([v for v in recent_visits if v.is_completed]) / len(recent_visits)
                
                performance_data.append({
                    "department": dept.name,
                    "total_patients": len(recent_visits),
                    "avg_wait_time": round(avg_wait_time, 1),
                    "avg_total_time": round(avg_total_time, 1),
                    "completion_rate": round(completion_rate * 100, 1),
                    "efficiency_score": round(completion_rate * (100 / max(avg_total_time, 1)), 2)
                })
        
        return {
            "success": True,
            "department_performance": performance_data,
            "recommendations": _generate_department_recommendations(performance_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting department performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_ai_triage_recommendations(triage_result: Dict) -> List[str]:
    """Generate recommendations based on AI-enhanced triage result"""
    recommendations = []
    
    category = triage_result.get('category', 'Non-urgent')
    estimated_wait = triage_result.get('estimated_wait_time', 120)
    ai_analysis = triage_result.get('ai_analysis', {})
    confidence = ai_analysis.get('confidence', 0.5)
    emergency_level = ai_analysis.get('emergency_level', 'moderate')
    ai_actions = ai_analysis.get('recommended_actions', [])
    risk_factors = ai_analysis.get('risk_factors', [])
    
    # AI-specific recommendations
    if confidence > 0.8:
        recommendations.append(f"🤖 High AI confidence ({confidence:.1%}) - AI analysis is reliable")
    elif confidence < 0.5:
        recommendations.append(f"⚠️ Low AI confidence ({confidence:.1%}) - Consider manual review")
    
    if emergency_level == "critical":
        recommendations.append("🚨 CRITICAL: AI detected life-threatening condition - immediate attention required")
        recommendations.append("📞 Alert emergency team and prepare critical care resources")
    elif emergency_level == "high":
        recommendations.append("⚠️ HIGH PRIORITY: AI detected serious condition - prompt attention needed")
        recommendations.append("👥 Ensure adequate staff coverage for urgent cases")
    
    # Add AI-recommended actions
    if ai_actions:
        recommendations.append("🎯 AI Recommended Actions:")
        for action in ai_actions[:3]:  # Limit to top 3 actions
            recommendations.append(f"   • {action}")
    
    # Add risk factors
    if risk_factors:
        recommendations.append("⚠️ Identified Risk Factors:")
        for factor in risk_factors[:3]:  # Limit to top 3 factors
            recommendations.append(f"   • {factor}")
    
    # Traditional recommendations
    if category == 'Emergency':
        recommendations.append("🚨 Patient requires immediate attention - prioritize resources")
    elif category == 'Urgent':
        recommendations.append("⚠️ Patient needs prompt attention - monitor closely")
    elif estimated_wait > 60:
        recommendations.append("⏰ Consider patient comfort during extended wait")
        recommendations.append("📱 Provide regular updates to patient")
    
    return recommendations

def _generate_symptom_analysis_recommendations(analysis_result: Dict) -> List[str]:
    """Generate recommendations based on symptom analysis result"""
    recommendations = []
    
    emergency_level = analysis_result.get('emergency_level', 'moderate')
    confidence = analysis_result.get('confidence', 0.5)
    triage_category = analysis_result.get('triage_category', 'Semi-urgent')
    estimated_wait = analysis_result.get('estimated_wait_time', 90)
    department = analysis_result.get('department_recommendation', 'Internal Medicine')
    ai_actions = analysis_result.get('recommended_actions', [])
    risk_factors = analysis_result.get('risk_factors', [])
    
    # Confidence-based recommendations
    if confidence > 0.8:
        recommendations.append(f"✅ High confidence analysis ({confidence:.1%})")
    elif confidence < 0.5:
        recommendations.append(f"⚠️ Low confidence analysis ({confidence:.1%}) - manual review recommended")
    
    # Emergency level recommendations
    if emergency_level == "critical":
        recommendations.append("🚨 CRITICAL EMERGENCY - Immediate medical attention required")
        recommendations.append("📞 Call emergency services immediately")
    elif emergency_level == "high":
        recommendations.append("⚠️ HIGH PRIORITY - Seek medical attention within 30 minutes")
    elif emergency_level == "moderate":
        recommendations.append("📋 MODERATE PRIORITY - Schedule appointment within 1-2 hours")
    else:
        recommendations.append("📅 LOW PRIORITY - Routine care appropriate")
    
    # Department-specific recommendations
    recommendations.append(f"🏥 Recommended Department: {department}")
    
    # Wait time recommendations
    if estimated_wait == 0:
        recommendations.append("⚡ Immediate attention - no wait time")
    elif estimated_wait <= 30:
        recommendations.append(f"⏰ Short wait expected: {estimated_wait} minutes")
    elif estimated_wait <= 60:
        recommendations.append(f"⏰ Moderate wait expected: {estimated_wait} minutes")
    else:
        recommendations.append(f"⏰ Extended wait expected: {estimated_wait} minutes")
    
    # AI-recommended actions
    if ai_actions:
        recommendations.append("🎯 Recommended Actions:")
        for action in ai_actions:
            recommendations.append(f"   • {action}")
    
    # Risk factors
    if risk_factors:
        recommendations.append("⚠️ Risk Factors Identified:")
        for factor in risk_factors:
            recommendations.append(f"   • {factor}")
    
    return recommendations

def _generate_triage_recommendations(triage_result: Dict) -> List[str]:
    """Generate recommendations based on triage result"""
    recommendations = []
    
    category = triage_result.get('category', 'Non-urgent')
    estimated_wait = triage_result.get('estimated_wait_time', 120)
    
    if category == 'Emergency':
        recommendations.append("🚨 Patient requires immediate attention - prioritize resources")
        recommendations.append("📞 Alert emergency team and prepare critical care resources")
    elif category == 'Urgent':
        recommendations.append("⚠️ Patient needs prompt attention - monitor closely")
        recommendations.append("👥 Ensure adequate staff coverage for urgent cases")
    elif estimated_wait > 60:
        recommendations.append("⏰ Consider patient comfort during extended wait")
        recommendations.append("📱 Provide regular updates to patient")
    
    return recommendations

def _generate_optimization_recommendations(optimization_result: Dict) -> List[str]:
    """Generate optimization recommendations"""
    recommendations = []
    
    emergency_count = len(optimization_result.get('emergency_patients', []))
    urgent_count = len(optimization_result.get('urgent_patients', []))
    
    if emergency_count > 0:
        recommendations.append(f"🚨 {emergency_count} emergency patients require immediate attention")
    
    if urgent_count > 5:
        recommendations.append(f"⚠️ High urgent patient load ({urgent_count}) - consider additional staff")
    
    recommendations.extend(optimization_result.get('recommendations', []))
    
    return recommendations

def _generate_bottleneck_recommendations(bottlenecks: List) -> List[str]:
    """Generate bottleneck recommendations"""
    recommendations = []
    
    if bottlenecks:
        top_bottleneck = bottlenecks[0]
        recommendations.append(f"🔍 Primary bottleneck: {top_bottleneck[0]} (avg {top_bottleneck[1]['avg_duration']:.1f} min)")
        recommendations.append("📊 Consider redistributing staff to address bottlenecks")
        recommendations.append("⏰ Monitor wait times in identified bottleneck stages")
    
    return recommendations

def _generate_department_recommendations(performance_data: List[Dict]) -> List[str]:
    """Generate department recommendations"""
    recommendations = []
    
    if performance_data:
        # Find slowest department
        slowest = max(performance_data, key=lambda x: x['avg_total_time'])
        recommendations.append(f"🐌 Slowest department: {slowest['department']} ({slowest['avg_total_time']:.1f} min avg)")
        
        # Find most efficient department
        most_efficient = max(performance_data, key=lambda x: x['efficiency_score'])
        recommendations.append(f"⚡ Most efficient: {most_efficient['department']} (score: {most_efficient['efficiency_score']:.2f})")
        
        recommendations.append("📈 Consider sharing best practices between departments")
    
    return recommendations
