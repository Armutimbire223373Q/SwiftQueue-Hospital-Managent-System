import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class OpenRouterFallbackService:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3.1:free"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://healthcare-queue-system.com",
            "X-Title": "Healthcare Queue Management System",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Make a chat completion request to OpenRouter"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "response": result
                    }
                else:
                    error_data = response.json()
                    logger.error(f"OpenRouter API error: {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error"),
                        "status_code": response.status_code
                    }

        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def analyze_emergency_first_aid(
        self,
        emergency_type: str,
        symptoms: str,
        patient_age: Optional[str] = None,
        available_resources: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use OpenRouter to analyze emergency and provide first aid recommendations"""

        prompt = f"""You are an expert emergency medical responder. A patient is experiencing a medical emergency.

EMERGENCY DETAILS:
- Type: {emergency_type}
- Symptoms: {symptoms}
- Patient Age: {patient_age or 'Unknown'}
- Location: {location or 'Unknown'}
- Available Resources: {', '.join(available_resources) if available_resources else 'None specified'}

Provide immediate first aid instructions following this structure:
1. IMMEDIATE ACTIONS (most critical steps first)
2. WHAT TO AVOID (things that could make it worse)
3. WHEN TO CALL EMERGENCY (when to seek professional help)
4. ADDITIONAL CARE (ongoing care while waiting for help)

IMPORTANT: Always emphasize calling emergency services (911/112) immediately. Include age-specific considerations if relevant. Keep instructions clear and actionable."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert emergency medical responder providing life-saving first aid instructions. Always prioritize calling emergency services and be clear about when professional medical help is needed."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        result = await self.chat_completion(messages, temperature=0.1, max_tokens=1000)

        if result.get("success"):
            ai_response = result["response"]["choices"][0]["message"]["content"]

            # Parse the AI response into structured format
            result = self._parse_first_aid_response(ai_response, emergency_type)
            result["service_used"] = "openrouter"
            return result
        else:
            return {
                "success": False,
                "error": result.get("error", "AI analysis failed"),
                "fallback": self._get_basic_first_aid(emergency_type)
            }

    async def analyze_symptoms(self, symptoms: str, **kwargs) -> Dict[str, Any]:
        """Analyze patient symptoms using OpenRouter"""

        prompt = f"""Analyze these patient symptoms and provide medical insights:

SYMPTOMS: {symptoms}
ADDITIONAL INFO: {kwargs.get('medical_history', 'None provided')}

Provide:
1. Possible conditions (most likely first)
2. Urgency level (Critical/High/Moderate/Low)
3. Recommended department
4. Key questions to ask patient
5. Immediate recommendations"""

        messages = [
            {
                "role": "system",
                "content": "You are a medical triage assistant. Analyze symptoms and provide structured medical recommendations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        result = await self.chat_completion(messages, temperature=0.2, max_tokens=800)

        if result.get("success"):
            ai_response = result["response"]["choices"][0]["message"]["content"]
            return self._parse_symptom_analysis(ai_response)
        else:
            return {
                "success": False,
                "error": result.get("error", "Symptom analysis failed")
            }

    def _parse_first_aid_response(self, ai_response: str, emergency_type: str) -> Dict[str, Any]:
        """Parse AI first aid response into structured format"""
        try:
            # Extract sections from AI response
            sections = ai_response.split('\n')

            immediate_actions = []
            do_not = []
            when_to_call = []
            additional_care = []

            current_section = None

            for line in sections:
                line = line.strip()
                if not line:
                    continue

                lower_line = line.lower()
                if 'immediate' in lower_line and 'action' in lower_line:
                    current_section = 'immediate'
                elif 'avoid' in lower_line or 'do not' in lower_line:
                    current_section = 'avoid'
                elif 'call' in lower_line and 'emergency' in lower_line:
                    current_section = 'call'
                elif 'additional' in lower_line or 'ongoing' in lower_line:
                    current_section = 'additional'
                elif current_section and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                    clean_line = line.lstrip('-•0123456789. ').strip()
                    if current_section == 'immediate':
                        immediate_actions.append(clean_line)
                    elif current_section == 'avoid':
                        do_not.append(clean_line)
                    elif current_section == 'call':
                        when_to_call.append(clean_line)
                    elif current_section == 'additional':
                        additional_care.append(clean_line)

            return {
                "success": True,
                "emergency_type": emergency_type,
                "immediate_actions": immediate_actions[:5],  # Limit to top 5
                "do_not": do_not[:4],  # Limit to top 4
                "when_to_call_emergency": when_to_call[:3],  # Limit to top 3
                "additional_care": additional_care[:3],  # Limit to top 3
                "severity": self._determine_severity(emergency_type, immediate_actions),
                "estimated_response_time": "5-15 minutes",
                "ai_generated": True,
                "disclaimer": "AI-generated recommendations. Always call emergency services immediately."
            }

        except Exception as e:
            logger.error(f"Error parsing first aid response: {e}")
            return self._get_basic_first_aid(emergency_type)

    def _parse_symptom_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parse symptom analysis response"""
        try:
            return {
                "success": True,
                "analysis": ai_response,
                "triage_category": "Moderate",  # Default
                "department_recommendation": "Internal Medicine",  # Default
                "estimated_wait_time": 60,  # Default 1 hour
                "ai_generated": True
            }
        except Exception as e:
            logger.error(f"Error parsing symptom analysis: {e}")
            return {
                "success": False,
                "error": "Failed to parse AI response"
            }

    def _determine_severity(self, emergency_type: str, actions: List[str]) -> str:
        """Determine severity based on emergency type and actions"""
        critical_keywords = ['cpr', 'unconscious', 'not breathing', 'cardiac arrest', 'severe bleeding']
        high_keywords = ['chest pain', 'difficulty breathing', 'stroke', 'heart attack']

        emergency_lower = emergency_type.lower()
        actions_text = ' '.join(actions).lower()

        if any(keyword in emergency_lower or keyword in actions_text for keyword in critical_keywords):
            return "critical"
        elif any(keyword in emergency_lower or keyword in actions_text for keyword in high_keywords):
            return "high"
        else:
            return "moderate"

    def _get_basic_first_aid(self, emergency_type: str) -> Dict[str, Any]:
        """Fallback basic first aid for when AI fails"""
        return {
            "success": True,
            "emergency_type": emergency_type,
            "immediate_actions": [
                "Call emergency services immediately (911/112)",
                "Ensure safety of person and bystanders",
                "Keep person comfortable and monitor vital signs",
                "Do not give food, drink, or medication unless directed by professional"
            ],
            "do_not": [
                "Do not attempt complex medical procedures",
                "Do not move injured person unless necessary",
                "Do not leave seriously injured person alone"
            ],
            "when_to_call_emergency": [
                "Call immediately for any serious symptoms",
                "Call if symptoms worsen",
                "Call if person becomes unconscious"
            ],
            "additional_care": [
                "Monitor breathing and consciousness",
                "Keep person warm",
                "Reassure and comfort the person"
            ],
            "severity": "unknown",
            "estimated_response_time": "5-15 minutes",
            "fallback": True,
            "disclaimer": "Basic emergency protocol. Professional medical help required immediately."
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check if OpenRouter service is available"""
        try:
            test_messages = [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]

            result = await self.chat_completion(test_messages, max_tokens=10)

            return {
                "success": result.get("success", False),
                "service": "openrouter",
                "model": self.model,
                "response_time": "N/A"  # Could measure this
            }

        except Exception as e:
            return {
                "success": False,
                "service": "openrouter",
                "error": str(e)
            }

# Global instance
openrouter_fallback_service = OpenRouterFallbackService()