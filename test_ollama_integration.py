#!/usr/bin/env python3
"""
Test script to verify Ollama model integration with the hospital queue system
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_ollama_models():
    """Test the Ollama models through the backend API"""
    
    base_url = "http://localhost:8000"
    
    # Test cases for symptom analysis
    test_cases = [
        {
            "symptoms": "I have severe chest pain that started this morning, accompanied by shortness of breath and dizziness",
            "patient_age": "45",
            "medical_history": "High blood pressure",
            "additional_context": "Pain is 8/10 on scale"
        },
        {
            "symptoms": "I have a mild headache and feel tired",
            "patient_age": "25",
            "medical_history": "None",
            "additional_context": "Started yesterday"
        },
        {
            "symptoms": "I have difficulty breathing and my lips are turning blue",
            "patient_age": "60",
            "medical_history": "Asthma",
            "additional_context": "Symptoms getting worse"
        }
    ]
    
    print("🤖 Testing Ollama Model Integration")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check if server is running
        try:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    print("✅ Backend server is running")
                else:
                    print("❌ Backend server not responding properly")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to backend server: {e}")
            return
        
        # Test 2: Test symptom analysis with Ollama models
        print("\n🧠 Testing Symptom Analysis with Ollama Models")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['symptoms'][:50]}...")
            
            try:
                async with session.post(
                    f"{base_url}/api/enhanced-ai/symptoms/analyze",
                    json=test_case,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Analysis successful!")
                        print(f"   Emergency Level: {result.get('analysis', {}).get('emergency_level', 'unknown')}")
                        print(f"   Confidence: {result.get('analysis', {}).get('confidence', 0):.2f}")
                        print(f"   Triage Category: {result.get('analysis', {}).get('triage_category', 'unknown')}")
                        print(f"   Estimated Wait: {result.get('analysis', {}).get('estimated_wait_time', 0)} min")
                        print(f"   Department: {result.get('analysis', {}).get('department_recommendation', 'unknown')}")
                        
                        if result.get('analysis', {}).get('ai_reasoning'):
                            print(f"   AI Reasoning: {result.get('analysis', {}).get('ai_reasoning', '')[:100]}...")
                        
                        # Check if recommendations are provided
                        recommendations = result.get('recommendations', [])
                        if recommendations:
                            print(f"   Recommendations: {len(recommendations)} provided")
                            for rec in recommendations[:2]:  # Show first 2 recommendations
                                print(f"     • {rec}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Analysis failed: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        # Test 3: Test AI-enhanced triage
        print("\n🎯 Testing AI-Enhanced Triage")
        print("-" * 50)
        
        triage_test = {
            "symptoms": "Severe abdominal pain with nausea and vomiting",
            "age_group": "adult",
            "insurance_type": "private",
            "department": "Emergency",
            "medical_history": "Previous appendectomy",
            "additional_context": "Pain started 2 hours ago"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/enhanced-ai/triage/ai-enhanced",
                json=triage_test,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ AI-Enhanced Triage successful!")
                    
                    triage_result = result.get('triage_result', {})
                    print(f"   Triage Score: {triage_result.get('triage_score', 'unknown')}/10")
                    print(f"   Category: {triage_result.get('category', 'unknown')}")
                    print(f"   Priority Level: {triage_result.get('priority_level', 'unknown')}/5")
                    print(f"   Estimated Wait: {triage_result.get('estimated_wait_time', 0)} min")
                    
                    ai_analysis = triage_result.get('ai_analysis', {})
                    if ai_analysis:
                        print(f"   AI Emergency Level: {ai_analysis.get('emergency_level', 'unknown')}")
                        print(f"   AI Confidence: {ai_analysis.get('confidence', 0):.2f}")
                        print(f"   AI Reasoning: {ai_analysis.get('reasoning', '')[:100]}...")
                    
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        print(f"   Recommendations: {len(recommendations)} provided")
                        for rec in recommendations[:2]:
                            print(f"     • {rec}")
                else:
                    error_text = await response.text()
                    print(f"❌ AI-Enhanced Triage failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Triage request failed: {e}")
        
        # Test 4: Test Ollama model directly
        print("\n🔧 Testing Direct Ollama Model Access")
        print("-" * 50)
        
        try:
            # Test if Ollama is running
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    models = await response.json()
                    print("✅ Ollama is running")
                    print(f"   Available models: {len(models.get('models', []))}")
                    for model in models.get('models', []):
                        print(f"     • {model.get('name', 'unknown')} ({model.get('size', 0) / 1024**3:.1f} GB)")
                else:
                    print("❌ Ollama not responding")
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
        
        # Test 5: Test cache functionality
        print("\n💾 Testing AI Response Cache")
        print("-" * 50)
        
        try:
            async with session.get(f"{base_url}/api/enhanced-ai/cache/stats") as response:
                if response.status == 200:
                    cache_stats = await response.json()
                    stats = cache_stats.get('cache_stats', {})
                    print("✅ Cache stats retrieved")
                    print(f"   Total cached entries: {stats.get('total_cached_entries', 0)}")
                    print(f"   Active entries: {stats.get('active_entries', 0)}")
                    print(f"   Cache TTL: {stats.get('cache_ttl_hours', 0)} hours")
                else:
                    print("❌ Cache stats failed")
        except Exception as e:
            print(f"❌ Cache stats request failed: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Ollama Integration Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(test_ollama_models())
    print("\n✨ Test completed!")
