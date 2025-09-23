"""
Intelligent Service Recommendation System
AI suggests appropriate department based on symptoms using ML and medical knowledge
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
import warnings
warnings.filterwarnings('ignore')

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
        
    def load_and_preprocess_data(self):
        """Load and preprocess hospital data for service recommendation"""
        print("📊 Loading hospital data for service recommendation...")
        
        # Load the comprehensive dataset
        self.df = pd.read_csv('../dataset/Hospital Wait  TIme Data.csv')
        print(f"   Loaded {len(self.df):,} records with {len(self.df.columns)} features")
        
        # Clean and preprocess
        self._clean_data()
        self._build_medical_knowledge_base()
        self._analyze_symptom_department_patterns()
        
        print(f"   Preprocessed data: {len(self.processed_df):,} records")
        return self.processed_df
    
    def _clean_data(self):
        """Clean and validate the dataset"""
        print("🧹 Cleaning service recommendation dataset...")
        
        self.processed_df = self.df.copy()
        
        # Handle missing values
        self.processed_df['ReasonForVisit'] = self.processed_df['ReasonForVisit'].fillna('Unknown')
        self.processed_df['Department'] = self.processed_df['Department'].fillna('Internal Medicine')
        
        # Clean symptom descriptions
        self.processed_df['ReasonForVisit'] = self.processed_df['ReasonForVisit'].str.lower()
        self.processed_df['ReasonForVisit'] = self.processed_df['ReasonForVisit'].str.strip()
        
        # Remove very short or generic descriptions
        self.processed_df = self.processed_df[
            self.processed_df['ReasonForVisit'].str.len() > 3
        ]
        
        print(f"   ✅ Data cleaned: {len(self.processed_df):,} records")
    
    def _build_medical_knowledge_base(self):
        """Build comprehensive medical knowledge base for symptom-department mapping"""
        print("🏥 Building medical knowledge base...")
        
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
        
        print(f"   ✅ Medical knowledge base built with {len(self.department_specialties)} departments")
    
    def _analyze_symptom_department_patterns(self):
        """Analyze historical patterns of symptoms to departments"""
        print("📈 Analyzing symptom-department patterns...")
        
        # Analyze actual patterns from data
        symptom_dept_patterns = self.processed_df.groupby(['ReasonForVisit', 'Department']).size().reset_index(name='count')
        
        # Get top patterns
        top_patterns = symptom_dept_patterns.sort_values('count', ascending=False).head(50)
        
        # Build pattern-based recommendations
        self.pattern_recommendations = {}
        for _, row in top_patterns.iterrows():
            symptom = row['ReasonForVisit']
            department = row['Department']
            count = row['count']
            
            if symptom not in self.pattern_recommendations:
                self.pattern_recommendations[symptom] = []
            
            self.pattern_recommendations[symptom].append({
                'department': department,
                'confidence': min(1.0, count / 100),  # Normalize confidence
                'frequency': count
            })
        
        print(f"   ✅ Analyzed {len(self.pattern_recommendations)} symptom patterns")
    
    def train_symptom_classifier(self):
        """Train ML model for symptom-based department classification"""
        print("🤖 Training symptom-based department classifier...")
        
        # Prepare training data
        X = self.processed_df['ReasonForVisit'].fillna('unknown')
        y = self.processed_df['Department']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Vectorize symptoms using TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        X_train_tfidf = self.tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = self.tfidf_vectorizer.transform(X_test)
        
        # Encode departments
        self.department_encoder = LabelEncoder()
        y_train_encoded = self.department_encoder.fit_transform(y_train)
        y_test_encoded = self.department_encoder.transform(y_test)
        
        # Train RandomForest classifier
        self.symptom_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        
        self.symptom_classifier.fit(X_train_tfidf, y_train_encoded)
        
        # Evaluate model
        y_pred = self.symptom_classifier.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test_encoded, y_pred)
        
        print(f"   ✅ Model trained successfully!")
        print(f"   Accuracy: {accuracy:.4f}")
        
        # Get feature importance (top symptoms)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        feature_importance = self.symptom_classifier.feature_importances_
        
        # Get top important features
        top_features = sorted(zip(feature_names, feature_importance), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"   📊 Top 10 most important symptoms:")
        for feature, importance in top_features:
            print(f"      {feature}: {importance:.4f}")
        
        # Save model and components
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.symptom_classifier, 'models/symptom_classifier.pkl')
        joblib.dump(self.tfidf_vectorizer, 'models/symptom_tfidf_vectorizer.pkl')
        joblib.dump(self.department_encoder, 'models/department_encoder.pkl')
        
        # Save comprehensive results
        results = {
            'model_performance': {
                'accuracy': accuracy,
                'classification_report': classification_report(y_test_encoded, y_pred, output_dict=True)
            },
            'feature_importance': dict(top_features),
            'department_specialties': self.department_specialties,
            'pattern_recommendations': self.pattern_recommendations,
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(self.processed_df)
        }
        
        joblib.dump(results, 'models/service_recommendation_results.pkl')
        
        return accuracy
    
    def recommend_service(self, 
                         symptoms: str,
                         age_group: str = None,
                         urgency_level: str = None,
                         patient_history: str = None) -> Dict:
        """Recommend appropriate department based on symptoms"""
        
        # Load model if not already loaded
        if self.symptom_classifier is None:
            try:
                self.symptom_classifier = joblib.load('models/symptom_classifier.pkl')
                self.tfidf_vectorizer = joblib.load('models/symptom_tfidf_vectorizer.pkl')
                self.department_encoder = joblib.load('models/department_encoder.pkl')
            except:
                return self._fallback_recommendation(symptoms)
        
        # Clean and preprocess symptoms
        symptoms_clean = symptoms.lower().strip()
        
        # Get ML prediction
        symptoms_tfidf = self.tfidf_vectorizer.transform([symptoms_clean])
        prediction_proba = self.symptom_classifier.predict_proba(symptoms_tfidf)[0]
        
        # Get top predictions
        department_names = self.department_encoder.classes_
        predictions = list(zip(department_names, prediction_proba))
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 3 recommendations
        top_recommendations = predictions[:3]
        
        # Apply medical knowledge base rules
        knowledge_recommendation = self._apply_medical_rules(symptoms_clean, age_group, urgency_level)
        
        # Combine ML and rule-based recommendations
        final_recommendation = self._combine_recommendations(
            top_recommendations, 
            knowledge_recommendation, 
            symptoms_clean
        )
        
        # Get confidence and reasoning
        confidence = final_recommendation['confidence']
        reasoning = self._generate_reasoning(symptoms_clean, final_recommendation['department'])
        
        return {
            'recommended_department': final_recommendation['department'],
            'confidence': round(confidence, 3),
            'reasoning': reasoning,
            'alternative_departments': [
                {'department': dept, 'confidence': round(conf, 3)} 
                for dept, conf in top_recommendations[1:3]
            ],
            'urgency_level': urgency_level or 'medium',
            'symptoms_analyzed': symptoms_clean,
            'age_group': age_group,
            'recommendation_method': 'ML + Medical Knowledge',
            'timestamp': datetime.now().isoformat()
        }
    
    def _apply_medical_rules(self, symptoms: str, age_group: str = None, urgency_level: str = None) -> Dict:
        """Apply medical knowledge base rules for department recommendation"""
        
        # Emergency cases
        emergency_keywords = ['emergency', 'urgent', 'trauma', 'accident', 'severe', 'critical', 'life-threatening']
        if any(keyword in symptoms for keyword in emergency_keywords):
            return {'department': 'Emergency', 'confidence': 0.95, 'method': 'emergency_rule'}
        
        # Age-specific rules
        if age_group and 'pediatric' in age_group.lower() or 'child' in age_group.lower():
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
    
    def _combine_recommendations(self, ml_recommendations: List, knowledge_recommendation: Dict, symptoms: str) -> Dict:
        """Combine ML and rule-based recommendations"""
        
        # If knowledge base has high confidence, use it
        if knowledge_recommendation['confidence'] > 0.8:
            return knowledge_recommendation
        
        # Check if ML top recommendation matches knowledge base
        ml_top_dept = ml_recommendations[0][0]
        ml_top_conf = ml_recommendations[0][1]
        
        if ml_top_dept == knowledge_recommendation['department']:
            # Boost confidence when both methods agree
            combined_confidence = min(0.95, ml_top_conf + 0.1)
            return {'department': ml_top_dept, 'confidence': combined_confidence, 'method': 'combined'}
        
        # Use ML recommendation if it has higher confidence
        if ml_top_conf > knowledge_recommendation['confidence']:
            return {'department': ml_top_dept, 'confidence': ml_top_conf, 'method': 'ml'}
        
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
    
    def _fallback_recommendation(self, symptoms: str) -> Dict:
        """Fallback recommendation when ML model is not available"""
        
        # Simple keyword-based fallback
        symptoms_lower = symptoms.lower()
        
        if any(keyword in symptoms_lower for keyword in ['heart', 'chest', 'cardiac']):
            return {
                'recommended_department': 'Cardiology',
                'confidence': 0.7,
                'reasoning': 'Symptoms suggest cardiac-related issues',
                'alternative_departments': [],
                'urgency_level': 'medium',
                'symptoms_analyzed': symptoms_lower,
                'recommendation_method': 'Keyword Fallback',
                'timestamp': datetime.now().isoformat()
            }
        elif any(keyword in symptoms_lower for keyword in ['bone', 'joint', 'fracture']):
            return {
                'recommended_department': 'Orthopedics',
                'confidence': 0.7,
                'reasoning': 'Symptoms suggest musculoskeletal issues',
                'alternative_departments': [],
                'urgency_level': 'medium',
                'symptoms_analyzed': symptoms_lower,
                'recommendation_method': 'Keyword Fallback',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'recommended_department': 'Internal Medicine',
                'confidence': 0.5,
                'reasoning': 'General consultation recommended',
                'alternative_departments': [],
                'urgency_level': 'low',
                'symptoms_analyzed': symptoms_lower,
                'recommendation_method': 'Default Fallback',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_department_info(self, department: str) -> Dict:
        """Get detailed information about a department"""
        
        dept_info = self.department_specialties.get(department, {})
        
        return {
            'department': department,
            'specialties': dept_info.get('keywords', []),
            'common_symptoms': dept_info.get('symptoms', []),
            'priority_level': dept_info.get('priority', 'medium'),
            'description': f"{department} department handles {', '.join(dept_info.get('keywords', [])[:5])} related conditions"
        }
    
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

if __name__ == "__main__":
    recommender = IntelligentServiceRecommender()
    
    # Load and preprocess data
    recommender.load_and_preprocess_data()
    
    # Train model
    accuracy = recommender.train_symptom_classifier()
    
    # Example recommendations
    print("\n🎯 Example Service Recommendations:")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ("chest pain and shortness of breath", "Adult (36-60)", "high"),
        ("severe headache with dizziness", "Adult (36-60)", "high"),
        ("bone fracture in arm", "Young Adult (18-35)", "medium"),
        ("routine checkup", "Senior (61+)", "low"),
        ("child with fever and cough", "Pediatric", "medium"),
        ("pregnancy consultation", "Adult (36-60)", "medium")
    ]
    
    for symptoms, age_group, urgency in test_cases:
        recommendation = recommender.recommend_service(symptoms, age_group, urgency)
        
        print(f"\n🩺 Symptoms: {symptoms}")
        print(f"   Age Group: {age_group}")
        print(f"   Urgency: {urgency}")
        print(f"   → Recommended: {recommendation['recommended_department']}")
        print(f"   → Confidence: {recommendation['confidence']}")
        print(f"   → Reasoning: {recommendation['reasoning']}")
        
        if recommendation['alternative_departments']:
            print(f"   → Alternatives: {[alt['department'] for alt in recommendation['alternative_departments']]}")
    
    # Get department information
    print(f"\n📋 Available Departments:")
    departments = recommender.get_all_departments()
    for dept in departments[:5]:  # Show first 5
        print(f"   {dept['name']}: {dept['priority_level']} priority")
