"""
Service Recommendation API Routes
AI suggests appropriate department based on symptoms using ML and medical knowledge
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import joblib
import os
from app.database import get_db
from app.models.models import Service

router = APIRouter()

class ServiceRecommendationRequest(BaseModel):
    """Request model for service recommendation"""
    symptoms: str
    age_group: Optional[str] = None
    urgency_level: Optional[str] = None
    patient_history: Optional[str] = None
    current_department: Optional[str] = None

class ServiceRecommendationResponse(BaseModel):
    """Response model for service recommendation"""
    recommended_department: str
    confidence: float
    reasoning: str
    alternative_departments: List[Dict]
    urgency_level: str
    symptoms_analyzed: str
    age_group: Optional[str]
    recommendation_method: str
    timestamp: str

class DepartmentInfoResponse(BaseModel):
    """Response model for department information"""
    department: str
    specialties: List[str]
    common_symptoms: List[str]
    priority_level: str
    description: str

class IntelligentServiceRecommender:
    """AI-powered service recommendation based on symptoms and patient data"""
    
    def __init__(self):
        self.symptom_classifier = None
        self.tfidf_vectorizer = None
        self.department_encoder = None
        self.medical_knowledge_base = {}
        self.symptom_keywords = {}
        self.department_specialties = {}
        self.confidence_threshold = 0.6
        self._load_model()
        self._build_medical_knowledge_base()
    
    def _load_model(self):
        """Load the trained model and components"""
        try:
            model_path = 'models/symptom_classifier.pkl'
            vectorizer_path = 'models/symptom_tfidf_vectorizer.pkl'
            encoder_path = 'models/department_encoder.pkl'
            
            if all(os.path.exists(path) for path in [model_path, vectorizer_path, encoder_path]):
                self.symptom_classifier = joblib.load(model_path)
                self.tfidf_vectorizer = joblib.load(vectorizer_path)
                self.department_encoder = joblib.load(encoder_path)
                print("✅ Service recommendation model loaded successfully")
            else:
                print("⚠️ Service recommendation model not found. Using rule-based fallback.")
        except Exception as e:
            print(f"❌ Error loading service recommendation model: {e}")
    
    def _build_medical_knowledge_base(self):
        """Build comprehensive medical knowledge base for symptom-department mapping"""
        
        # Department specialties and keywords
        self.department_specialties = {
            'Emergency': {
                'keywords': ['emergency', 'urgent', 'trauma', 'accident', 'injury', 'bleeding', 'unconscious', 'severe', 'critical', 'life-threatening'],
                'symptoms': ['chest pain', 'difficulty breathing', 'severe bleeding', 'unconsciousness', 'stroke symptoms', 'heart attack', 'severe allergic reaction'],
                'priority': 'high'
            },
            'Cardiology': {
                'keywords': ['heart', 'cardiac', 'chest', 'cardio', 'blood pressure', 'hypertension', 'arrhythmia', 'angina'],
                'symptoms': ['chest pain', 'heart palpitations', 'shortness of breath', 'chest pressure', 'irregular heartbeat', 'high blood pressure'],
                'priority': 'high'
            },
            'Neurology': {
                'keywords': ['brain', 'head', 'neurological', 'seizure', 'stroke', 'headache', 'migraine', 'dizziness', 'memory'],
                'symptoms': ['severe headache', 'seizures', 'stroke symptoms', 'dizziness', 'memory problems', 'numbness', 'tingling'],
                'priority': 'high'
            },
            'Orthopedics': {
                'keywords': ['bone', 'joint', 'fracture', 'sprain', 'muscle', 'skeletal', 'spine', 'knee', 'hip', 'shoulder'],
                'symptoms': ['bone pain', 'joint pain', 'fracture', 'sprain', 'muscle pain', 'back pain', 'knee pain'],
                'priority': 'medium'
            },
            'General Surgery': {
                'keywords': ['surgery', 'surgical', 'operation', 'appendicitis', 'hernia', 'gallbladder', 'tumor'],
                'symptoms': ['abdominal pain', 'appendicitis', 'hernia', 'gallbladder pain', 'surgical consultation'],
                'priority': 'medium'
            },
            'Internal Medicine': {
                'keywords': ['general', 'internal', 'medicine', 'consultation', 'checkup', 'routine', 'chronic'],
                'symptoms': ['general consultation', 'routine checkup', 'chronic condition', 'general symptoms'],
                'priority': 'low'
            },
            'Pediatrics': {
                'keywords': ['child', 'pediatric', 'infant', 'baby', 'toddler', 'adolescent', 'kids'],
                'symptoms': ['child illness', 'pediatric consultation', 'infant care', 'child development'],
                'priority': 'medium'
            },
            'Obstetrics': {
                'keywords': ['pregnancy', 'prenatal', 'maternity', 'obstetric', 'gynecological', 'women'],
                'symptoms': ['pregnancy care', 'prenatal checkup', 'gynecological issues', 'maternity care'],
                'priority': 'medium'
            },
            'Radiology': {
                'keywords': ['imaging', 'x-ray', 'scan', 'mri', 'ct', 'ultrasound', 'radiological'],
                'symptoms': ['imaging needed', 'x-ray required', 'scan consultation', 'radiological examination'],
                'priority': 'low'
            },
            'Oncology': {
                'keywords': ['cancer', 'oncology', 'tumor', 'malignancy', 'chemotherapy', 'radiation'],
                'symptoms': ['cancer consultation', 'tumor evaluation', 'oncology care', 'cancer treatment'],
                'priority': 'high'
            }
        }
        
        # Build symptom keyword mapping
        self.symptom_keywords = {}
        for dept, info in self.department_specialties.items():
            for keyword in info['keywords']:
                if keyword not in self.symptom_keywords:
                    self.symptom_keywords[keyword] = []
                self.symptom_keywords[keyword].append(dept)
    
    def recommend_service(self, request: ServiceRecommendationRequest) -> ServiceRecommendationResponse:
        """Recommend appropriate department based on symptoms"""
        
        # Clean and preprocess symptoms
        symptoms_clean = request.symptoms.lower().strip()
        
        # Get ML prediction if model is available
        if self.symptom_classifier is not None:
            ml_recommendation = self._get_ml_recommendation(symptoms_clean)
        else:
            ml_recommendation = None
        
        # Apply medical knowledge base rules
        knowledge_recommendation = self._apply_medical_rules(
            symptoms_clean, 
            request.age_group, 
            request.urgency_level
        )
        
        # Combine ML and rule-based recommendations
        final_recommendation = self._combine_recommendations(
            ml_recommendation, 
            knowledge_recommendation, 
            symptoms_clean
        )
        
        # Get confidence and reasoning
        confidence = final_recommendation['confidence']
        reasoning = self._generate_reasoning(symptoms_clean, final_recommendation['department'])
        
        # Get alternative departments
        alternatives = self._get_alternative_departments(symptoms_clean, final_recommendation['department'])
        
        return ServiceRecommendationResponse(
            recommended_department=final_recommendation['department'],
            confidence=round(confidence, 3),
            reasoning=reasoning,
            alternative_departments=alternatives,
            urgency_level=request.urgency_level or 'medium',
            symptoms_analyzed=symptoms_clean,
            age_group=request.age_group,
            recommendation_method=final_recommendation.get('method', 'rule_based'),
            timestamp=datetime.now().isoformat()
        )
    
    def _get_ml_recommendation(self, symptoms: str) -> Optional[Dict]:
        """Get ML-based recommendation"""
        try:
            symptoms_tfidf = self.tfidf_vectorizer.transform([symptoms])
            prediction_proba = self.symptom_classifier.predict_proba(symptoms_tfidf)[0]
            
            # Get top prediction
            department_names = self.department_encoder.classes_
            predictions = list(zip(department_names, prediction_proba))
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            top_dept, top_conf = predictions[0]
            return {'department': top_dept, 'confidence': top_conf, 'method': 'ml'}
        except:
            return None
    
    def _apply_medical_rules(self, symptoms: str, age_group: str = None, urgency_level: str = None) -> Dict:
        """Apply medical knowledge base rules for department recommendation"""
        
        # Emergency cases
        emergency_keywords = ['emergency', 'urgent', 'trauma', 'accident', 'severe', 'critical', 'life-threatening']
        if any(keyword in symptoms for keyword in emergency_keywords):
            return {'department': 'Emergency', 'confidence': 0.95, 'method': 'emergency_rule'}
        
        # Age-specific rules
        if age_group and ('pediatric' in age_group.lower() or 'child' in age_group.lower()):
            if any(keyword in symptoms for keyword in ['fever', 'cough', 'cold', 'vaccination']):
                return {'department': 'Pediatrics', 'confidence': 0.90, 'method': 'age_specific'}
        
        # Symptom-based rules
        for dept, info in self.department_specialties.items():
            keyword_matches = sum(1 for keyword in info['keywords'] if keyword in symptoms)
            symptom_matches = sum(1 for symptom in info['symptoms'] if symptom in symptoms)
            
            if keyword_matches > 0 or symptom_matches > 0:
                confidence = min(0.9, 0.5 + (keyword_matches * 0.1) + (symptom_matches * 0.2))
                return {'department': dept, 'confidence': confidence, 'method': 'symptom_matching'}
        
        # Default to Internal Medicine
        return {'department': 'Internal Medicine', 'confidence': 0.3, 'method': 'default'}
    
    def _combine_recommendations(self, ml_recommendation: Optional[Dict], knowledge_recommendation: Dict, symptoms: str) -> Dict:
        """Combine ML and rule-based recommendations"""
        
        # If knowledge base has high confidence, use it
        if knowledge_recommendation['confidence'] > 0.8:
            return knowledge_recommendation
        
        # If ML recommendation is available, check for agreement
        if ml_recommendation:
            ml_dept = ml_recommendation['department']
            ml_conf = ml_recommendation['confidence']
            
            if ml_dept == knowledge_recommendation['department']:
                # Boost confidence when both methods agree
                combined_confidence = min(0.95, ml_conf + 0.1)
                return {'department': ml_dept, 'confidence': combined_confidence, 'method': 'combined'}
            
            # Use ML recommendation if it has higher confidence
            if ml_conf > knowledge_recommendation['confidence']:
                return {'department': ml_dept, 'confidence': ml_conf, 'method': 'ml'}
        
        # Use knowledge base recommendation
        return knowledge_recommendation
    
    def _generate_reasoning(self, symptoms: str, department: str) -> str:
        """Generate human-readable reasoning for the recommendation"""
        
        dept_info = self.department_specialties.get(department, {})
        keywords = dept_info.get('keywords', [])
        
        # Find matching keywords
        matching_keywords = [kw for kw in keywords if kw in symptoms]
        
        if matching_keywords:
            return f"Recommended {department} based on symptoms: {', '.join(matching_keywords[:3])}"
        else:
            return f"Recommended {department} based on general medical assessment and historical patterns"
    
    def _get_alternative_departments(self, symptoms: str, primary_dept: str) -> List[Dict]:
        """Get alternative department recommendations"""
        
        alternatives = []
        
        # Get ML alternatives if available
        if self.symptom_classifier is not None:
            try:
                symptoms_tfidf = self.tfidf_vectorizer.transform([symptoms])
                prediction_proba = self.symptom_classifier.predict_proba(symptoms_tfidf)[0]
                
                department_names = self.department_encoder.classes_
                predictions = list(zip(department_names, prediction_proba))
                predictions.sort(key=lambda x: x[1], reverse=True)
                
                # Get top 3 alternatives (excluding primary)
                for dept, conf in predictions[1:4]:
                    if dept != primary_dept:
                        alternatives.append({'department': dept, 'confidence': round(conf, 3)})
            except:
                pass
        
        # Add rule-based alternatives if needed
        if len(alternatives) < 2:
            for dept, info in self.department_specialties.items():
                if dept != primary_dept and len(alternatives) < 3:
                    keyword_matches = sum(1 for keyword in info['keywords'] if keyword in symptoms)
                    if keyword_matches > 0:
                        confidence = min(0.7, 0.3 + (keyword_matches * 0.1))
                        alternatives.append({'department': dept, 'confidence': round(confidence, 3)})
        
        return alternatives[:3]  # Return max 3 alternatives
    
    def get_department_info(self, department: str) -> DepartmentInfoResponse:
        """Get detailed information about a department"""
        
        dept_info = self.department_specialties.get(department, {})
        
        return DepartmentInfoResponse(
            department=department,
            specialties=dept_info.get('keywords', []),
            common_symptoms=dept_info.get('symptoms', []),
            priority_level=dept_info.get('priority', 'medium'),
            description=f"{department} department handles {', '.join(dept_info.get('keywords', [])[:5])} related conditions"
        )
    
    def get_all_departments(self) -> List[Dict]:
        """Get information about all available departments"""
        
        departments = []
        for dept_name, dept_info in self.department_specialties.items():
            departments.append({
                'name': dept_name,
                'specialties': dept_info['keywords'],
                'common_symptoms': dept_info['symptoms'],
                'priority_level': dept_info['priority']
            })
        
        return departments

# Initialize recommender
recommender = IntelligentServiceRecommender()

@router.post("/recommend", response_model=ServiceRecommendationResponse)
async def recommend_service(
    request: ServiceRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Recommend appropriate department based on symptoms using AI and medical knowledge
    
    - **symptoms**: Patient symptoms description
    - **age_group**: Patient age group (optional)
    - **urgency_level**: Urgency level (optional)
    - **patient_history**: Patient medical history (optional)
    - **current_department**: Current department (optional)
    """
    try:
        recommendation = recommender.recommend_service(request)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service recommendation failed: {str(e)}")

@router.get("/departments", response_model=List[Dict])
async def get_all_departments():
    """
    Get information about all available departments
    """
    try:
        departments = recommender.get_all_departments()
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get departments: {str(e)}")

@router.get("/departments/{department}", response_model=DepartmentInfoResponse)
async def get_department_info(department: str):
    """
    Get detailed information about a specific department
    """
    try:
        dept_info = recommender.get_department_info(department)
        return dept_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get department info: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """
    Get the status of the service recommendation model
    """
    try:
        model_path = 'models/symptom_classifier.pkl'
        vectorizer_path = 'models/symptom_tfidf_vectorizer.pkl'
        encoder_path = 'models/department_encoder.pkl'
        
        model_exists = os.path.exists(model_path)
        vectorizer_exists = os.path.exists(vectorizer_path)
        encoder_exists = os.path.exists(encoder_path)
        
        status = {
            "model_available": model_exists and vectorizer_exists and encoder_exists,
            "model_loaded": recommender.symptom_classifier is not None,
            "vectorizer_loaded": recommender.tfidf_vectorizer is not None,
            "encoder_loaded": recommender.department_encoder is not None,
            "knowledge_base_size": len(recommender.department_specialties),
            "departments_available": list(recommender.department_specialties.keys()),
            "last_checked": datetime.now().isoformat()
        }
        
        if model_exists and vectorizer_exists and encoder_exists:
            # Get model performance metrics
            results_path = 'models/service_recommendation_results.pkl'
            if os.path.exists(results_path):
                results = joblib.load(results_path)
                performance = results.get('model_performance', {})
                status.update({
                    "accuracy": performance.get('accuracy', 'N/A'),
                    "training_date": results.get('training_date', 'N/A'),
                    "dataset_size": results.get('dataset_size', 'N/A')
                })
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.post("/train-model")
async def train_service_recommendation_model():
    """
    Train the service recommendation model (admin endpoint)
    """
    try:
        # This would trigger the training process
        # For now, return a message indicating training should be done via script
        return {
            "message": "Model training should be performed using the intelligent_service_recommender.py script",
            "command": "python intelligent_service_recommender.py",
            "status": "training_required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/symptoms/keywords")
async def get_symptom_keywords():
    """
    Get common symptom keywords for each department
    """
    try:
        keywords_by_department = {}
        for dept, info in recommender.department_specialties.items():
            keywords_by_department[dept] = {
                'keywords': info['keywords'],
                'common_symptoms': info['symptoms'],
                'priority': info['priority']
            }
        
        return {
            "keywords_by_department": keywords_by_department,
            "total_departments": len(keywords_by_department)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get symptom keywords: {str(e)}")

@router.post("/validate-symptoms")
async def validate_symptoms(symptoms: str):
    """
    Validate symptoms and get preliminary department suggestions
    """
    try:
        symptoms_clean = symptoms.lower().strip()
        
        # Find matching departments
        matching_departments = []
        for dept, info in recommender.department_specialties.items():
            keyword_matches = [kw for kw in info['keywords'] if kw in symptoms_clean]
            symptom_matches = [symptom for symptom in info['symptoms'] if symptom in symptoms_clean]
            
            if keyword_matches or symptom_matches:
                confidence = min(0.9, 0.3 + (len(keyword_matches) * 0.1) + (len(symptom_matches) * 0.2))
                matching_departments.append({
                    'department': dept,
                    'confidence': round(confidence, 3),
                    'matched_keywords': keyword_matches,
                    'matched_symptoms': symptom_matches
                })
        
        # Sort by confidence
        matching_departments.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "symptoms": symptoms_clean,
            "matching_departments": matching_departments[:5],  # Top 5
            "total_matches": len(matching_departments),
            "validation_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate symptoms: {str(e)}")
