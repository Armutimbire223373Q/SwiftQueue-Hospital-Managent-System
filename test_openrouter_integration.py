#!/usr/bin/env python3
"""
Test script for OpenRouter AI integration
Run this to verify the integration is working correctly
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_openrouter_integration():
    """Test the OpenRouter AI integration"""
    print("🧪 Testing OpenRouter AI Integration")
    print("=" * 50)
    
    # Check if API key is configured
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("   Using default API key from config...")
        api_key = "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"
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    try:
        # Import the services
        from backend.app.ai.openrouter_service import openrouter_service
        from backend.app.ai.triage_system import triage_system
        
        print("✅ Services imported successfully")
        
        # Test symptom analysis
        print("\n🔍 Testing symptom analysis...")
        analysis_result = await openrouter_service.analyze_symptoms(
            symptoms="Chest pain and shortness of breath",
            patient_age="adult",
            medical_history="Previous heart condition",
            additional_context="Patient is diabetic"
        )
        
        if analysis_result.get("error"):
            print(f"❌ Symptom analysis failed: {analysis_result['error']}")
            return False
        
        print("✅ Symptom analysis successful!")
        print(f"   Emergency Level: {analysis_result.get('emergency_level', 'unknown')}")
        print(f"   Confidence: {analysis_result.get('confidence', 0):.2f}")
        print(f"   Triage Category: {analysis_result.get('triage_category', 'unknown')}")
        print(f"   Department: {analysis_result.get('department_recommendation', 'unknown')}")
        print(f"   AI Reasoning: {analysis_result.get('ai_reasoning', 'unknown')}")
        
        # Test AI-enhanced triage
        print("\n🏥 Testing AI-enhanced triage...")
        triage_result = await triage_system.calculate_triage_score_with_ai(
            symptoms="Chest pain and shortness of breath",
            age_group="adult",
            insurance_type="private",
            arrival_time=datetime.now(),
            department="Emergency",
            medical_history="Previous heart condition",
            additional_context="Patient is diabetic"
        )
        
        if triage_result.get("error"):
            print(f"❌ AI-enhanced triage failed: {triage_result['error']}")
            return False
        
        print("✅ AI-enhanced triage successful!")
        print(f"   Triage Score: {triage_result.get('triage_score', 0):.2f}")
        print(f"   Category: {triage_result.get('category', 'unknown')}")
        print(f"   Wait Time: {triage_result.get('estimated_wait_time', 0)} minutes")
        print(f"   Analysis Method: {triage_result.get('analysis_method', 'unknown')}")
        
        # Test batch analysis
        print("\n📦 Testing batch analysis...")
        batch_data = [
            {
                "symptoms": "Chest pain",
                "patient_age": "senior"
            },
            {
                "symptoms": "Fever and cough",
                "patient_age": "pediatric"
            }
        ]
        
        batch_results = await openrouter_service.batch_analyze_symptoms(batch_data)
        
        if batch_results and len(batch_results) > 0:
            print("✅ Batch analysis successful!")
            print(f"   Analyzed {len(batch_results)} cases")
            successful = len([r for r in batch_results if not r.get("error")])
            print(f"   Successful analyses: {successful}/{len(batch_results)}")
        else:
            print("❌ Batch analysis failed")
            return False
        
        print("\n🎉 All tests passed! OpenRouter integration is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_openrouter_integration()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("\nNext steps:")
        print("1. Set your OPENROUTER_API_KEY environment variable")
        print("2. Start the backend server: python backend/run.py")
        print("3. Test the API endpoints using the frontend or API client")
        print("4. Check the OPENROUTER_INTEGRATION.md file for detailed usage")
    else:
        print("\n❌ Integration test failed!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
