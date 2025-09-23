#!/usr/bin/env python3
"""
Example usage of the OpenRouter AI integration for medical triage
This demonstrates how the system analyzes symptoms and determines emergency levels
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def demonstrate_triage_analysis():
    """Demonstrate the medical triage analysis with various symptoms"""
    print("🏥 Medical Triage Analysis Demo")
    print("=" * 50)
    
    try:
        from backend.app.ai.openrouter_service import openrouter_service
        from backend.app.ai.triage_system import triage_system
        
        # Test cases with different emergency levels
        test_cases = [
            {
                "symptoms": "Chest pain and shortness of breath",
                "expected_level": "Level 1",
                "description": "Life-threatening cardiac symptoms"
            },
            {
                "symptoms": "Severe headache with nausea and vomiting",
                "expected_level": "Level 2", 
                "description": "Serious neurological symptoms"
            },
            {
                "symptoms": "Fever and cough for 3 days",
                "expected_level": "Level 3",
                "description": "Moderate respiratory infection"
            },
            {
                "symptoms": "Minor cut on finger",
                "expected_level": "Level 4",
                "description": "Minor injury"
            },
            {
                "symptoms": "Unconsciousness and difficulty breathing",
                "expected_level": "Level 1",
                "description": "Critical emergency symptoms"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {case['description']}")
            print(f"Symptoms: {case['symptoms']}")
            print(f"Expected: {case['expected_level']}")
            
            # Analyze symptoms
            analysis = await openrouter_service.analyze_symptoms(
                symptoms=case['symptoms']
            )
            
            if analysis.get("error"):
                print(f"❌ Analysis failed: {analysis['error']}")
                continue
            
            # Display results
            emergency_level = analysis.get('emergency_level', 'unknown')
            triage_category = analysis.get('triage_category', 'unknown')
            wait_time = analysis.get('estimated_wait_time', 0)
            confidence = analysis.get('confidence', 0)
            
            print(f"✅ AI Analysis:")
            print(f"   Emergency Level: {emergency_level}")
            print(f"   Triage Category: {triage_category}")
            print(f"   Wait Time: {wait_time} minutes")
            print(f"   Confidence: {confidence:.2f}")
            
            # Show AI reasoning
            reasoning = analysis.get('ai_reasoning', 'No reasoning provided')
            print(f"   AI Reasoning: {reasoning}")
            
            # Show recommended actions
            actions = analysis.get('recommended_actions', [])
            if actions:
                print(f"   Recommended Actions:")
                for action in actions:
                    print(f"     • {action}")
            
            print("-" * 40)
        
        # Demonstrate AI-enhanced triage
        print(f"\n🔄 AI-Enhanced Triage Example")
        print("=" * 30)
        
        triage_result = await triage_system.calculate_triage_score_with_ai(
            symptoms="Chest pain and shortness of breath",
            age_group="adult",
            insurance_type="private",
            arrival_time=datetime.now(),
            department="Emergency"
        )
        
        if not triage_result.get("error"):
            print("✅ AI-Enhanced Triage Results:")
            print(f"   Triage Score: {triage_result.get('triage_score', 0):.2f}")
            print(f"   Category: {triage_result.get('category', 'unknown')}")
            print(f"   Wait Time: {triage_result.get('estimated_wait_time', 0)} minutes")
            print(f"   Department: {triage_result.get('recommended_department', 'unknown')}")
            print(f"   Analysis Method: {triage_result.get('analysis_method', 'unknown')}")
            
            # Show AI analysis details
            ai_analysis = triage_result.get('ai_analysis', {})
            if ai_analysis:
                print(f"   AI Emergency Level: {ai_analysis.get('emergency_level', 'unknown')}")
                print(f"   AI Confidence: {ai_analysis.get('confidence', 0):.2f}")
                print(f"   AI Reasoning: {ai_analysis.get('reasoning', 'No reasoning')}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\nThe system is now ready to analyze patient symptoms and determine emergency levels.")
        print(f"Key features:")
        print(f"• Uses your specific medical triage prompt")
        print(f"• Returns Level 1-4 emergency classifications")
        print(f"• Provides structured analysis with confidence scores")
        print(f"• Integrates with existing triage system")
        print(f"• Supports batch processing for multiple patients")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demonstrate_triage_analysis())
