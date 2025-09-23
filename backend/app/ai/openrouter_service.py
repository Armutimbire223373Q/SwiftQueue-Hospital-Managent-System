"""
OpenRouter AI Service for Advanced Symptom Analysis
Integrates with DeepSeek model for emergency level determination
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Service for interacting with a local Ollama model"""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
        self.default_model = os.getenv("OLLAMA_MODEL", "phi3:3.8b")
        self.triage_model = os.getenv("OLLAMA_MODEL_TRIAGE", "mistral:7b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "60"))
        # Response cache for common symptoms
        self.response_cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    async def analyze_symptoms(self, 
                             symptoms: str, 
                             patient_age: Optional[str] = None,
                             medical_history: Optional[str] = None,
                             additional_context: Optional[str] = None,
                             model: Optional[str] = None) -> Dict:
        """
        Analyze patient symptoms using a local LLM to determine emergency level
            
            Args:
                symptoms: Patient's reported symptoms
                patient_age: Patient's age group (optional)
                medical_history: Relevant medical history (optional)
                additional_context: Any additional context (optional)
                
            Returns:
                Dict containing analysis results and emergency level
        """
        # Input validation and sanitization
        if not symptoms or not symptoms.strip():
            return {
                "error": "Symptoms cannot be empty",
                "emergency_level": "unknown",
                "confidence": 0.0
            }
        
        # Sanitize inputs
        symptoms = self._sanitize_input(symptoms)
        patient_age = self._sanitize_input(patient_age) if patient_age else None
        medical_history = self._sanitize_input(medical_history) if medical_history else None
        additional_context = self._sanitize_input(additional_context) if additional_context else None
        
        # Validate input lengths
        if len(symptoms) > 1000:
            return {
                "error": "Symptoms description too long (max 1000 characters)",
                "emergency_level": "unknown",
                "confidence": 0.0
            }
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(symptoms, patient_age, medical_history, additional_context)
            cached_result = self._get_cached_response(cache_key)
            if cached_result:
                logger.info(f"Using cached response for symptoms: {symptoms[:50]}...")
                return cached_result
            
            # Construct the prompt for symptom analysis
            prompt = self._construct_symptom_analysis_prompt(
                symptoms, patient_age, medical_history, additional_context
            )
            
            # Make API call to local Ollama model (choose model per request)
            start_time = datetime.now()
            model_to_use = model or self.default_model
            response = await self._make_ollama_request(prompt, model_to_use)
            request_duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Symptom analysis request completed in {request_duration:.2f}s for: {symptoms[:50]}...")
            
            if response.get("error"):
                logger.error(f"Ollama API error: {response['error']}")
                return response
            
            # Parse the AI response
            analysis_result = self._parse_ai_response(response.get("content", ""))
            result = {
                "success": True,
                "emergency_level": analysis_result["emergency_level"],
                "confidence": analysis_result["confidence"],
                "recommended_actions": analysis_result["recommended_actions"],
                "triage_category": analysis_result["triage_category"],
                "estimated_wait_time": analysis_result["estimated_wait_time"],
                "ai_reasoning": analysis_result["ai_reasoning"],
                "department_recommendation": analysis_result["department_recommendation"],
                "risk_factors": analysis_result["risk_factors"],
                "timestamp": datetime.now().isoformat(),
                "performance": {
                    "request_duration_seconds": round(request_duration, 2),
                    "model_used": model_to_use,
                    "tokens_used": response.get("usage", {}).get("total_tokens", 0)
                }
            }
            
            # Cache the result
            self._cache_response(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return {
                "error": str(e),
                "emergency_level": "unknown",
                "confidence": 0.0
            }
    
    def _construct_symptom_analysis_prompt(self, 
                                         symptoms: str, 
                                         patient_age: Optional[str] = None,
                                         medical_history: Optional[str] = None,
                                         additional_context: Optional[str] = None) -> str:
        """Construct a medical triage prompt using the specific format provided"""
        
        prompt = f"""MEDICAL TRIAGE ANALYSIS

Patient: {symptoms}
Age: {patient_age or 'Not specified'}
History: {medical_history or 'None'}
Context: {additional_context or 'None'}

CRITICAL SYMPTOMS (Level 1 - Emergency):
- Chest pain, severe chest pressure
- Unconsciousness, unresponsive
- Severe bleeding, major trauma
- Difficulty breathing, respiratory distress
- Stroke symptoms (facial droop, slurred speech, weakness)
- Severe allergic reaction, anaphylaxis
- Cardiac arrest, severe shock

URGENT SYMPTOMS (Level 2 - Urgent):
- Severe pain (8-10/10)
- High fever (>103°F) with concerning symptoms
- Moderate injuries, fractures
- Mental health crisis, suicidal ideation
- Severe dehydration, inability to keep fluids down

MODERATE SYMPTOMS (Level 3 - Semi-urgent):
- Chronic condition flare-ups
- Routine follow-ups
- Moderate pain (4-7/10)
- Non-severe infections

NON-URGENT SYMPTOMS (Level 4 - Non-urgent):
- Minor injuries, cuts
- Routine checkups
- Vaccinations
- Mild symptoms, colds

RESPONSE FORMAT (JSON only):
{{
    "emergency_level": "critical|high|moderate|low",
    "confidence": 0.0-1.0,
    "triage_category": "Emergency|Urgent|Semi-urgent|Non-urgent",
    "estimated_wait_time": 0|15|30|60|90|120,
    "department_recommendation": "Emergency|Cardiology|Orthopedics|Neurology|Pediatrics|Internal Medicine|General Surgery|Radiology|Obstetrics",
    "recommended_actions": ["action1", "action2"],
    "risk_factors": ["factor1"],
    "ai_reasoning": "Brief explanation"
}}

Analyze and respond with JSON only."""
        return prompt
    
    async def _make_ollama_request(self, prompt: str, model: Optional[str] = None) -> Dict:
        """Make API request to Ollama local model"""
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.base_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "content": data.get("response", ""),
                            "model": data.get("model", self.model)
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Ollama API request failed: {response.status} - {error_text}"}
        except Exception as e:
            return {"error": f"Ollama request failed: {str(e)}"}
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Parse the AI response and extract structured data"""
        try:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON block in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Validate and normalize the response
                return self._validate_and_normalize_response(parsed_data)
            else:
                # Fallback parsing if no JSON found
                return self._fallback_parsing(content)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return self._fallback_parsing(content)
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._create_default_response(content)
    
    def _generate_cache_key(self, symptoms: str, patient_age: Optional[str], 
                           medical_history: Optional[str], additional_context: Optional[str]) -> str:
        """Generate a cache key for the symptom analysis request"""
        # Normalize inputs for consistent caching
        normalized_symptoms = symptoms.lower().strip()
        normalized_age = (patient_age or "").lower().strip()
        normalized_history = (medical_history or "").lower().strip()
        normalized_context = (additional_context or "").lower().strip()
        
        # Create hash of normalized inputs
        cache_string = f"{normalized_symptoms}|{normalized_age}|{normalized_history}|{normalized_context}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            cache_time = cached_data.get("cache_time")
            
            if cache_time and datetime.now() - cache_time < self.cache_ttl:
                # Return cached result without timestamp
                result = cached_data["result"].copy()
                result["timestamp"] = datetime.now().isoformat()
                result["cached"] = True
                return result
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, result: Dict) -> None:
        """Cache the analysis result"""
        self.response_cache[cache_key] = {
            "result": result,
            "cache_time": datetime.now()
        }
        
        # Limit cache size to prevent memory issues
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]["cache_time"])
            del self.response_cache[oldest_key]
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize input text to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        import re
        # Remove script tags and other HTML/JS
        text = re.sub(r'<[^>]+>', '', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        total_entries = len(self.response_cache)
        expired_entries = 0
        
        for entry in self.response_cache.values():
            if datetime.now() - entry["cache_time"] >= self.cache_ttl:
                expired_entries += 1
        
        return {
            "total_cached_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "cache_hit_rate": "N/A"  # Would need to track hits/misses
        }
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def _convert_level_to_structured_response(self, level: int, content: str) -> Dict:
        """Convert Level X response to structured format"""
        
        # Map levels to emergency categories
        level_mapping = {
            1: {
                "emergency_level": "critical",
                "triage_category": "Emergency",
                "estimated_wait_time": 0,
                "confidence": 0.9
            },
            2: {
                "emergency_level": "high", 
                "triage_category": "Urgent",
                "estimated_wait_time": 30,
                "confidence": 0.8
            },
            3: {
                "emergency_level": "moderate",
                "triage_category": "Semi-urgent", 
                "estimated_wait_time": 90,
                "confidence": 0.7
            },
            4: {
                "emergency_level": "low",
                "triage_category": "Non-urgent",
                "estimated_wait_time": 120,
                "confidence": 0.6
            }
        }
        
        level_data = level_mapping.get(level, level_mapping[3])  # Default to level 3
        
        return {
            "emergency_level": level_data["emergency_level"],
            "confidence": level_data["confidence"],
            "triage_category": level_data["triage_category"],
            "estimated_wait_time": level_data["estimated_wait_time"],
            "department_recommendation": self._get_department_recommendation(level),
            "recommended_actions": self._get_recommended_actions(level),
            "risk_factors": self._get_risk_factors(level),
            "ai_reasoning": f"AI assigned Level {level} based on symptom analysis"
        }
    
    def _get_department_recommendation(self, level: int) -> str:
        """Get department recommendation based on level"""
        if level == 1:
            return "Emergency"
        elif level == 2:
            return "Emergency"  # Urgent cases often go to emergency
        else:
            return "Internal Medicine"  # Default for lower levels
    
    def _get_recommended_actions(self, level: int) -> List[str]:
        """Get recommended actions based on level"""
        if level == 1:
            return ["Immediate medical attention", "Call emergency services", "Prepare critical care resources"]
        elif level == 2:
            return ["Prompt medical attention", "Monitor vital signs", "Prepare urgent care resources"]
        elif level == 3:
            return ["Schedule same-day appointment", "Monitor symptoms", "Provide comfort measures"]
        else:
            return ["Schedule routine appointment", "Self-care instructions", "Follow-up as needed"]
    
    def _get_risk_factors(self, level: int) -> List[str]:
        """Get risk factors based on level"""
        if level == 1:
            return ["Life-threatening condition", "Immediate intervention required"]
        elif level == 2:
            return ["Serious condition", "Time-sensitive treatment needed"]
        elif level == 3:
            return ["Moderate condition", "Same-day care recommended"]
        else:
            return ["Minor condition", "Routine care appropriate"]
    
    def _validate_and_normalize_response(self, data: Dict) -> Dict:
        """Validate and normalize the parsed AI response"""
        
        # Normalize emergency level
        emergency_level = data.get("emergency_level", "moderate").lower()
        if emergency_level in ["critical", "high", "moderate", "low"]:
            normalized_level = emergency_level
        else:
            normalized_level = "moderate"
            logger.warning(f"Invalid emergency level: {emergency_level}, defaulting to moderate")
        
        # Normalize triage category
        triage_category = data.get("triage_category", "Semi-urgent")
        valid_categories = ["Emergency", "Urgent", "Semi-urgent", "Non-urgent"]
        if triage_category not in valid_categories:
            triage_category = "Semi-urgent"
            logger.warning(f"Invalid triage category: {triage_category}, defaulting to Semi-urgent")
        
        # Normalize wait time - handle both string and numeric values
        wait_time = data.get("estimated_wait_time", 90)
        if isinstance(wait_time, str):
            wait_time_mapping = {
                "immediate": 0,
                "0-30": 15,
                "30-60": 45,
                "60-120": 90,
                "120+": 150
            }
            estimated_minutes = wait_time_mapping.get(wait_time, 90)
        else:
            # Handle numeric values directly
            estimated_minutes = max(0, min(300, int(wait_time)))  # Clamp between 0-300 minutes
        
        # Normalize confidence
        try:
            confidence = float(data.get("confidence", 0.7))
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.7
            logger.warning(f"Invalid confidence value: {data.get('confidence')}, defaulting to 0.7")
        
        # Validate and normalize lists
        recommended_actions = data.get("recommended_actions", ["Monitor patient", "Schedule appointment"])
        if not isinstance(recommended_actions, list):
            recommended_actions = ["Monitor patient", "Schedule appointment"]
        
        risk_factors = data.get("risk_factors", [])
        if not isinstance(risk_factors, list):
            risk_factors = []
        
        # Validate department recommendation
        valid_departments = ["Emergency", "Cardiology", "Orthopedics", "Neurology", "Oncology", 
                           "Pediatrics", "Internal Medicine", "General Surgery", "Radiology", "Obstetrics"]
        department = data.get("department_recommendation", "Internal Medicine")
        if department not in valid_departments:
            department = "Internal Medicine"
            logger.warning(f"Invalid department: {department}, defaulting to Internal Medicine")
        
        return {
            "emergency_level": normalized_level,
            "confidence": confidence,
            "triage_category": triage_category,
            "estimated_wait_time": estimated_minutes,
            "department_recommendation": department,
            "recommended_actions": recommended_actions[:3],  # Limit to 3 actions
            "risk_factors": risk_factors[:3],  # Limit to 3 risk factors
            "ai_reasoning": data.get("ai_reasoning", "AI analysis completed")[:500]  # Limit reasoning length
        }
    
    def _fallback_parsing(self, content: str) -> Dict:
        """Fallback parsing when JSON extraction fails"""
        content_lower = content.lower()
        
        # Simple keyword-based emergency level detection
        if any(word in content_lower for word in ["critical", "emergency", "immediate", "urgent"]):
            emergency_level = "high"
            triage_category = "Emergency"
            estimated_minutes = 0
        elif any(word in content_lower for word in ["serious", "severe", "high priority"]):
            emergency_level = "high"
            triage_category = "Urgent"
            estimated_minutes = 30
        elif any(word in content_lower for word in ["moderate", "routine", "follow-up"]):
            emergency_level = "moderate"
            triage_category = "Semi-urgent"
            estimated_minutes = 90
        else:
            emergency_level = "low"
            triage_category = "Non-urgent"
            estimated_minutes = 120
        
        return {
            "emergency_level": emergency_level,
            "confidence": 0.6,  # Lower confidence for fallback parsing
            "triage_category": triage_category,
            "estimated_wait_time": estimated_minutes,
            "department_recommendation": "Internal Medicine",
            "recommended_actions": ["Monitor patient", "Schedule appointment"],
            "risk_factors": [],
            "ai_reasoning": f"Fallback analysis based on keyword detection: {content[:200]}..."
        }
    
    def _create_default_response(self, content: str) -> Dict:
        """Create a default response when parsing fails completely"""
        return {
            "emergency_level": "moderate",
            "confidence": 0.5,
            "triage_category": "Semi-urgent",
            "estimated_wait_time": 90,
            "department_recommendation": "Internal Medicine",
            "recommended_actions": ["Monitor patient", "Schedule appointment"],
            "risk_factors": [],
            "ai_reasoning": f"Default analysis - parsing failed: {content[:100]}..."
        }
    
    async def batch_analyze_symptoms(self, symptom_batch: List[Dict]) -> List[Dict]:
        """Analyze multiple symptoms in batch"""
        tasks = []
        for symptom_data in symptom_batch:
            if isinstance(symptom_data, dict):
                symptoms = symptom_data.get("symptoms", "")
                patient_age = symptom_data.get("patient_age")
                medical_history = symptom_data.get("medical_history")
                additional_context = symptom_data.get("additional_context")
            else:
                # If it's just a string, treat it as symptoms
                symptoms = symptom_data
                patient_age = None
                medical_history = None
                additional_context = None
            
            task = self.analyze_symptoms(
                symptoms=symptoms,
                patient_age=patient_age,
                medical_history=medical_history,
                additional_context=additional_context
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "emergency_level": "unknown",
                    "confidence": 0.0,
                    "index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results

# Global instance
openrouter_service = OpenRouterService()
