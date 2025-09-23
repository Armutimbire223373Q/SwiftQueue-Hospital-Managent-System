"""
Advanced AI-Powered Triage System
Based on insights from the hospital dataset analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
from .openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

class TriageCategory(Enum):
    EMERGENCY = "Emergency"
    URGENT = "Urgent"
    SEMI_URGENT = "Semi-urgent"
    NON_URGENT = "Non-urgent"

class TriageSystem:
    """AI-powered triage system with priority scoring and resource allocation"""
    
    def __init__(self):
        self.triage_rules = self._initialize_triage_rules()
        self.department_capacities = self._initialize_department_capacities()
        self.resource_requirements = self._initialize_resource_requirements()
        
    def _initialize_triage_rules(self) -> Dict:
        """Initialize triage rules based on dataset analysis"""
        return {
            "symptoms": {
                "chest_pain": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "difficulty_breathing": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "severe_bleeding": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "unconscious": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "severe_head_injury": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "stroke_symptoms": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "heart_attack": {"priority": 4, "category": TriageCategory.EMERGENCY},
                "severe_allergic_reaction": {"priority": 4, "category": TriageCategory.EMERGENCY},
                
                "moderate_pain": {"priority": 3, "category": TriageCategory.URGENT},
                "fever_high": {"priority": 3, "category": TriageCategory.URGENT},
                "injury_moderate": {"priority": 3, "category": TriageCategory.URGENT},
                "abdominal_pain_severe": {"priority": 3, "category": TriageCategory.URGENT},
                "mental_health_crisis": {"priority": 3, "category": TriageCategory.URGENT},
                
                "chronic_condition": {"priority": 2, "category": TriageCategory.SEMI_URGENT},
                "follow_up": {"priority": 2, "category": TriageCategory.SEMI_URGENT},
                "routine_checkup": {"priority": 2, "category": TriageCategory.SEMI_URGENT},
                "prescription_renewal": {"priority": 2, "category": TriageCategory.SEMI_URGENT},
                
                "vaccination": {"priority": 1, "category": TriageCategory.NON_URGENT},
                "consultation": {"priority": 1, "category": TriageCategory.NON_URGENT},
                "routine_exam": {"priority": 1, "category": TriageCategory.NON_URGENT}
            },
            "age_factors": {
                "pediatric": {"multiplier": 1.2},  # Higher priority for children
                "senior": {"multiplier": 1.1},    # Higher priority for seniors
                "adult": {"multiplier": 1.0}
            },
            "insurance_factors": {
                "medicaid": {"multiplier": 1.0},
                "medicare": {"multiplier": 1.0},
                "private": {"multiplier": 1.0},
                "self_pay": {"multiplier": 1.0}
            },
            "time_factors": {
                "peak_hours": {"multiplier": 1.1},  # 8-10 AM, 12-2 PM, 5-7 PM
                "off_peak": {"multiplier": 1.0},
                "weekend": {"multiplier": 1.05}
            }
        }
    
    def _initialize_department_capacities(self) -> Dict:
        """Initialize department capacity based on dataset analysis"""
        return {
            "Emergency": {"max_patients": 20, "avg_time": 122.2, "priority": 4},
            "Cardiology": {"max_patients": 15, "avg_time": 165.8, "priority": 3},
            "Orthopedics": {"max_patients": 12, "avg_time": 162.7, "priority": 2},
            "Neurology": {"max_patients": 10, "avg_time": 175.9, "priority": 3},
            "Oncology": {"max_patients": 8, "avg_time": 170.2, "priority": 3},
            "Pediatrics": {"max_patients": 15, "avg_time": 160.5, "priority": 3},
            "Internal Medicine": {"max_patients": 18, "avg_time": 173.5, "priority": 2},
            "General Surgery": {"max_patients": 12, "avg_time": 173.4, "priority": 3},
            "Radiology": {"max_patients": 10, "avg_time": 155.3, "priority": 2},
            "Obstetrics": {"max_patients": 8, "avg_time": 168.7, "priority": 3}
        }
    
    def _initialize_resource_requirements(self) -> Dict:
        """Initialize resource requirements for different triage categories"""
        return {
            TriageCategory.EMERGENCY: {
                "providers": 2,
                "nurses": 3,
                "rooms": 1,
                "equipment": ["defibrillator", "oxygen", "monitoring"],
                "max_wait_time": 0  # Immediate
            },
            TriageCategory.URGENT: {
                "providers": 1,
                "nurses": 2,
                "rooms": 1,
                "equipment": ["monitoring", "basic"],
                "max_wait_time": 30  # 30 minutes
            },
            TriageCategory.SEMI_URGENT: {
                "providers": 1,
                "nurses": 1,
                "rooms": 1,
                "equipment": ["basic"],
                "max_wait_time": 60  # 1 hour
            },
            TriageCategory.NON_URGENT: {
                "providers": 1,
                "nurses": 1,
                "rooms": 1,
                "equipment": ["basic"],
                "max_wait_time": 120  # 2 hours
            }
        }
    
    async def calculate_triage_score_with_ai(self, 
                                           symptoms: str,
                                           age_group: str,
                                           insurance_type: str,
                                           arrival_time: datetime,
                                           department: str = None,
                                           medical_history: str = None,
                                           additional_context: str = None) -> Dict:
        """
        Calculate triage score using local LLM for advanced symptom analysis
            
            Args:
                symptoms: Patient symptoms/reason for visit
                age_group: Patient age group
                insurance_type: Insurance type
                arrival_time: Time of arrival
                department: Requested department
                medical_history: Patient's medical history (optional)
                additional_context: Additional context (optional)
                
            Returns:
                Dict with AI-enhanced triage score, category, and recommendations
        """
        try:
            # Get AI analysis from local LLM
            ai_analysis = await openrouter_service.analyze_symptoms(
                symptoms=symptoms,
                patient_age=age_group,
                medical_history=medical_history,
                additional_context=additional_context,
                model=openrouter_service.triage_model
            )
            
            if ai_analysis.get("error"):
                logger.warning(f"AI analysis failed: {ai_analysis['error']}, falling back to rule-based triage")
                return self.calculate_triage_score(symptoms, age_group, insurance_type, arrival_time, department)
            
            # Extract AI results
            ai_emergency_level = ai_analysis.get("emergency_level", "moderate")
            ai_confidence = ai_analysis.get("confidence", 0.7)
            ai_triage_category = ai_analysis.get("triage_category", "Semi-urgent")
            ai_wait_time = ai_analysis.get("estimated_wait_time", 90)
            ai_department = ai_analysis.get("department_recommendation", "Internal Medicine")
            ai_actions = ai_analysis.get("recommended_actions", [])
            ai_reasoning = ai_analysis.get("ai_reasoning", "")
            ai_risk_factors = ai_analysis.get("risk_factors", [])
            
            # Convert AI emergency level to priority score
            emergency_to_priority = {
                "critical": 4,
                "high": 3,
                "moderate": 2,
                "low": 1
            }
            ai_priority = emergency_to_priority.get(ai_emergency_level, 2)
            
            # Apply traditional factors with AI enhancement
            age_multiplier = self.triage_rules["age_factors"].get(age_group.lower(), {"multiplier": 1.0})["multiplier"]
            insurance_multiplier = self.triage_rules["insurance_factors"].get(insurance_type.lower(), {"multiplier": 1.0})["multiplier"]
            
            # Time factor
            hour = arrival_time.hour
            is_weekend = arrival_time.weekday() >= 5
            
            time_multiplier = 1.0
            if is_weekend:
                time_multiplier *= self.triage_rules["time_factors"]["weekend"]["multiplier"]
            
            if (8 <= hour <= 10) or (12 <= hour <= 14) or (17 <= hour <= 19):
                time_multiplier *= self.triage_rules["time_factors"]["peak_hours"]["multiplier"]
            
            # Calculate final score with AI confidence weighting
            ai_weighted_priority = ai_priority * ai_confidence
            traditional_factors = age_multiplier * insurance_multiplier * time_multiplier
            
            # Blend AI and traditional scoring
            final_score = (ai_weighted_priority * 0.7) + (ai_priority * traditional_factors * 0.3)
            
            # Determine final category (AI takes precedence if confidence is high)
            if ai_confidence > 0.8:
                final_category = ai_triage_category
                final_wait_time = ai_wait_time
                final_department = ai_department
            else:
                # Blend AI and traditional recommendations
                final_category = ai_triage_category if ai_confidence > 0.6 else "Semi-urgent"
                final_wait_time = ai_wait_time if ai_confidence > 0.6 else 90
                final_department = ai_department if ai_confidence > 0.6 else self._recommend_department(symptoms, TriageCategory.SEMI_URGENT, department)
            
            # Get resource requirements
            category_enum = TriageCategory(final_category) if final_category in [e.value for e in TriageCategory] else TriageCategory.SEMI_URGENT
            resource_req = self.resource_requirements[category_enum]
            
            return {
                "triage_score": round(final_score, 2),
                "category": final_category,
                "priority_level": ai_priority,
                "estimated_wait_time": final_wait_time,
                "resource_requirements": resource_req,
                "recommended_department": final_department,
                "ai_analysis": {
                    "emergency_level": ai_emergency_level,
                    "confidence": ai_confidence,
                    "reasoning": ai_reasoning,
                    "recommended_actions": ai_actions,
                    "risk_factors": ai_risk_factors
                },
                "factors": {
                    "ai_priority": ai_priority,
                    "ai_confidence": ai_confidence,
                    "age_multiplier": age_multiplier,
                    "insurance_multiplier": insurance_multiplier,
                    "time_multiplier": time_multiplier,
                    "ai_weighted_score": ai_weighted_priority,
                    "traditional_score": ai_priority * traditional_factors
                },
                "analysis_method": "ai_enhanced"
            }
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced triage calculation: {e}")
            # Fallback to traditional triage
            return self.calculate_triage_score(symptoms, age_group, insurance_type, arrival_time, department)

    def calculate_triage_score(self, 
                             symptoms: str,
                             age_group: str,
                             insurance_type: str,
                             arrival_time: datetime,
                             department: str = None) -> Dict:
        """
        Calculate triage score and determine priority category
        
        Args:
            symptoms: Patient symptoms/reason for visit
            age_group: Patient age group
            insurance_type: Insurance type
            arrival_time: Time of arrival
            department: Requested department
            
        Returns:
            Dict with triage score, category, and recommendations
        """
        try:
            # Base priority from symptoms
            base_priority = 1
            category = TriageCategory.NON_URGENT
            
            # Check symptoms against triage rules
            symptoms_lower = symptoms.lower()
            for symptom_key, rule in self.triage_rules["symptoms"].items():
                if symptom_key.replace("_", " ") in symptoms_lower:
                    base_priority = rule["priority"]
                    category = rule["category"]
                    break
            
            # Apply age factor
            age_multiplier = self.triage_rules["age_factors"].get(age_group.lower(), {"multiplier": 1.0})["multiplier"]
            
            # Apply insurance factor
            insurance_multiplier = self.triage_rules["insurance_factors"].get(insurance_type.lower(), {"multiplier": 1.0})["multiplier"]
            
            # Apply time factor
            hour = arrival_time.hour
            is_weekend = arrival_time.weekday() >= 5
            
            time_multiplier = 1.0
            if is_weekend:
                time_multiplier *= self.triage_rules["time_factors"]["weekend"]["multiplier"]
            
            if (8 <= hour <= 10) or (12 <= hour <= 14) or (17 <= hour <= 19):
                time_multiplier *= self.triage_rules["time_factors"]["peak_hours"]["multiplier"]
            
            # Calculate final score
            final_score = base_priority * age_multiplier * insurance_multiplier * time_multiplier
            
            # Get resource requirements
            resource_req = self.resource_requirements[category]
            
            # Determine recommended department
            recommended_dept = self._recommend_department(symptoms, category, department)
            
            return {
                "triage_score": round(final_score, 2),
                "category": category.value,
                "priority_level": base_priority,
                "estimated_wait_time": self._estimate_wait_time(category, arrival_time),
                "resource_requirements": resource_req,
                "recommended_department": recommended_dept,
                "factors": {
                    "symptoms_priority": base_priority,
                    "age_multiplier": age_multiplier,
                    "insurance_multiplier": insurance_multiplier,
                    "time_multiplier": time_multiplier
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating triage score: {e}")
            return {
                "triage_score": 1.0,
                "category": TriageCategory.NON_URGENT.value,
                "priority_level": 1,
                "estimated_wait_time": 120,
                "resource_requirements": self.resource_requirements[TriageCategory.NON_URGENT],
                "recommended_department": "Internal Medicine",
                "error": str(e)
            }
    
    def _recommend_department(self, symptoms: str, category: TriageCategory, requested_dept: str = None) -> str:
        """Recommend the most appropriate department based on symptoms and triage category"""
        
        # Emergency cases go to Emergency department
        if category == TriageCategory.EMERGENCY:
            return "Emergency"
        
        # Department mapping based on symptoms
        dept_mapping = {
            "chest_pain": "Cardiology",
            "heart": "Cardiology",
            "cardiac": "Cardiology",
            "bone": "Orthopedics",
            "fracture": "Orthopedics",
            "joint": "Orthopedics",
            "head": "Neurology",
            "brain": "Neurology",
            "seizure": "Neurology",
            "cancer": "Oncology",
            "tumor": "Oncology",
            "child": "Pediatrics",
            "pediatric": "Pediatrics",
            "baby": "Pediatrics",
            "pregnancy": "Obstetrics",
            "pregnant": "Obstetrics",
            "surgery": "General Surgery",
            "operation": "General Surgery",
            "x-ray": "Radiology",
            "scan": "Radiology",
            "imaging": "Radiology"
        }
        
        symptoms_lower = symptoms.lower()
        for keyword, dept in dept_mapping.items():
            if keyword in symptoms_lower:
                return dept
        
        # If no specific match, use requested department or default
        if requested_dept and requested_dept in self.department_capacities:
            return requested_dept
        
        return "Internal Medicine"  # Default department
    
    def _estimate_wait_time(self, category: TriageCategory, arrival_time: datetime) -> int:
        """Estimate wait time based on triage category and current conditions"""
        
        base_wait_times = {
            TriageCategory.EMERGENCY: 0,
            TriageCategory.URGENT: 30,
            TriageCategory.SEMI_URGENT: 60,
            TriageCategory.NON_URGENT: 120
        }
        
        base_time = base_wait_times[category]
        
        # Adjust for peak hours
        hour = arrival_time.hour
        if (8 <= hour <= 10) or (12 <= hour <= 14) or (17 <= hour <= 19):
            base_time = int(base_time * 1.3)  # 30% increase during peak hours
        
        # Adjust for weekends
        if arrival_time.weekday() >= 5:
            base_time = int(base_time * 1.1)  # 10% increase on weekends
        
        return base_time
    
    def optimize_resource_allocation(self, 
                                  current_patients: List[Dict],
                                  available_resources: Dict) -> Dict:
        """
        Optimize resource allocation based on current patient load and triage priorities
        
        Args:
            current_patients: List of current patients with triage scores
            available_resources: Available providers, nurses, rooms
            
        Returns:
            Optimized resource allocation plan
        """
        try:
            # Sort patients by triage score (highest priority first)
            sorted_patients = sorted(current_patients, 
                                   key=lambda x: x.get('triage_score', 1), 
                                   reverse=True)
            
            allocation_plan = {
                "emergency_patients": [],
                "urgent_patients": [],
                "semi_urgent_patients": [],
                "non_urgent_patients": [],
                "resource_assignments": {},
                "recommendations": []
            }
            
            # Categorize patients
            for patient in sorted_patients:
                category = patient.get('category', 'Non-urgent')
                if category == 'Emergency':
                    allocation_plan["emergency_patients"].append(patient)
                elif category == 'Urgent':
                    allocation_plan["urgent_patients"].append(patient)
                elif category == 'Semi-urgent':
                    allocation_plan["semi_urgent_patients"].append(patient)
                else:
                    allocation_plan["non_urgent_patients"].append(patient)
            
            # Generate recommendations
            emergency_count = len(allocation_plan["emergency_patients"])
            urgent_count = len(allocation_plan["urgent_patients"])
            
            if emergency_count > 0:
                allocation_plan["recommendations"].append(
                    f"🚨 {emergency_count} emergency patients require immediate attention"
                )
            
            if urgent_count > 5:
                allocation_plan["recommendations"].append(
                    f"⚠️ High urgent patient load ({urgent_count}). Consider additional staff."
                )
            
            # Resource optimization recommendations
            total_patients = len(current_patients)
            if total_patients > available_resources.get('providers', 0) * 3:
                allocation_plan["recommendations"].append(
                    "👥 Consider increasing provider count - high patient-to-provider ratio"
                )
            
            return allocation_plan
            
        except Exception as e:
            logger.error(f"Error optimizing resource allocation: {e}")
            return {"error": str(e)}
    
    def predict_bottlenecks(self, 
                          current_workflow: List[Dict],
                          historical_data: pd.DataFrame = None) -> Dict:
        """
        Predict potential bottlenecks in the workflow
        
        Args:
            current_workflow: Current patient workflow data
            historical_data: Historical performance data
            
        Returns:
            Bottleneck predictions and recommendations
        """
        try:
            bottlenecks = {
                "predicted_bottlenecks": [],
                "recommendations": [],
                "risk_level": "Low"
            }
            
            # Analyze current stage distribution
            stage_counts = {}
            for patient in current_workflow:
                stage = patient.get('current_stage', 'Unknown')
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Identify potential bottlenecks
            total_patients = sum(stage_counts.values())
            
            for stage, count in stage_counts.items():
                percentage = (count / total_patients) * 100 if total_patients > 0 else 0
                
                if percentage > 40:  # More than 40% in one stage
                    bottlenecks["predicted_bottlenecks"].append({
                        "stage": stage,
                        "patient_count": count,
                        "percentage": round(percentage, 1),
                        "risk_level": "High" if percentage > 60 else "Medium"
                    })
            
            # Set overall risk level
            high_risk_bottlenecks = [b for b in bottlenecks["predicted_bottlenecks"] if b["risk_level"] == "High"]
            if high_risk_bottlenecks:
                bottlenecks["risk_level"] = "High"
            elif bottlenecks["predicted_bottlenecks"]:
                bottlenecks["risk_level"] = "Medium"
            
            # Generate recommendations
            if bottlenecks["predicted_bottlenecks"]:
                bottlenecks["recommendations"].append(
                    "📊 Consider redistributing staff to address bottlenecks"
                )
                bottlenecks["recommendations"].append(
                    "⏰ Monitor wait times in identified bottleneck stages"
                )
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error predicting bottlenecks: {e}")
            return {"error": str(e)}

# Global triage system instance
triage_system = TriageSystem()
