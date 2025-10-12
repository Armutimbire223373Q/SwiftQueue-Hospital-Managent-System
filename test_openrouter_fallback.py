#!/usr/bin/env python3
"""
Test script for OpenRouter fallback AI service
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.openrouter_fallback_service import openrouter_fallback_service

async def test_openrouter_service():
    """Test the OpenRouter fallback service functionality"""
    print("Testing OpenRouter Fallback Service")
    print("=" * 50)

    try:
        # Test 1: Health check
        print("\n1. Checking service health...")
        health_result = await openrouter_fallback_service.health_check()
        if health_result.get("success"):
            print(f"[SUCCESS] OpenRouter service is available")
            print(f"   Model: {health_result.get('model')}")
        else:
            print(f"[FAILED] Service health check failed: {health_result.get('error')}")
            return False

        # Test 2: Emergency first aid analysis
        print("\n2. Testing emergency first aid analysis...")
        first_aid_result = await openrouter_fallback_service.analyze_emergency_first_aid(
            emergency_type="cardiac_arrest",
            symptoms="person collapsed, not breathing, no pulse",
            patient_age="adult",
            available_resources=["phone", "hands"],
            location="office building"
        )

        if first_aid_result.get("success"):
            print(f"[SUCCESS] First aid analysis completed")
            print(f"   Service used: {first_aid_result.get('service_used', 'unknown')}")
            print(f"   Severity: {first_aid_result.get('severity', 'unknown')}")
            print(f"   Immediate actions: {len(first_aid_result.get('immediate_actions', []))}")
        else:
            print(f"[FAILED] First aid analysis failed: {first_aid_result.get('error')}")

        # Test 3: Symptom analysis
        print("\n3. Testing symptom analysis...")
        symptom_result = await openrouter_fallback_service.analyze_symptoms(
            symptoms="severe chest pain, shortness of breath, left arm numbness",
            medical_history="high blood pressure",
            patient_age="55"
        )

        if symptom_result.get("success"):
            print(f"[SUCCESS] Symptom analysis completed")
            print(f"   Analysis length: {len(symptom_result.get('analysis', ''))}")
        else:
            print(f"[FAILED] Symptom analysis failed: {symptom_result.get('error')}")

        # Test 4: Chat completion directly
        print("\n4. Testing direct chat completion...")
        chat_result = await openrouter_fallback_service.chat_completion([
            {"role": "user", "content": "What is the most important first aid step for burns?"}
        ], max_tokens=100)

        if chat_result.get("success"):
            response = chat_result["response"]["choices"][0]["message"]["content"]
            print(f"[SUCCESS] Chat completion worked")
            print(f"   Response preview: {response[:100]}...")
        else:
            print(f"[FAILED] Chat completion failed: {chat_result.get('error')}")

        print("\n[SUCCESS] OpenRouter fallback service tests completed!")
        print("\nBenefits of OpenRouter fallback:")
        print("- Works when local Ollama is unavailable")
        print("- Provides real-time AI analysis for emergencies")
        print("- Uses free DeepSeek model for cost-effective AI")
        print("- Faster response times for critical situations")

    except Exception as e:
        print(f"\n[FAILED] OpenRouter service test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Starting OpenRouter Fallback Service Tests")
    success = asyncio.run(test_openrouter_service())
    sys.exit(0 if success else 1)