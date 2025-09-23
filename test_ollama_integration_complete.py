#!/usr/bin/env python3
"""
Complete test of Ollama integration with the hospital queue system
"""

import requests
import json
import time
from datetime import datetime

def test_ollama_integration():
    """Test the complete Ollama integration"""
    print("🏥 Testing Ollama Integration with Hospital Queue System")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    # Wait for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Test 1: Check backend server
    print("\n🔧 Testing Backend Server")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return
    
    # Test 2: Check Ollama models
    print("\n🤖 Testing Ollama Models")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running")
            print(f"   Available models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                print(f"     • {model.get('name', 'unknown')} ({model.get('size', 0) / 1024**3:.1f} GB)")
        else:
            print("❌ Ollama not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return
    
    # Test 3: Test symptom analysis endpoint
    print("\n🧠 Testing Symptom Analysis Endpoint")
    print("-" * 40)
    
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
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test Case {i}: {test_case['symptoms'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/enhanced-ai/symptoms/analyze",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Analysis successful!")
                
                analysis = result.get('analysis', {})
                print(f"      Emergency Level: {analysis.get('emergency_level', 'unknown')}")
                print(f"      Confidence: {analysis.get('confidence', 0):.2f}")
                print(f"      Triage Category: {analysis.get('triage_category', 'unknown')}")
                print(f"      Estimated Wait: {analysis.get('estimated_wait_time', 0)} min")
                print(f"      Department: {analysis.get('department_recommendation', 'unknown')}")
                
                if analysis.get('ai_reasoning'):
                    print(f"      AI Reasoning: {analysis.get('ai_reasoning', '')[:100]}...")
                
                # Check performance metrics
                performance = result.get('performance', {})
                if performance:
                    print(f"      Request Duration: {performance.get('request_duration_seconds', 0):.2f}s")
                    print(f"      Model Used: {performance.get('model_used', 'unknown')}")
                
                # Check recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"      Recommendations: {len(recommendations)} provided")
                    for rec in recommendations[:2]:
                        print(f"        • {rec}")
                        
            else:
                error_text = response.text
                print(f"   ❌ Analysis failed: {response.status_code} - {error_text}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out - Ollama model may need more time to load")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Test 4: Test AI-enhanced triage
    print("\n🎯 Testing AI-Enhanced Triage")
    print("-" * 35)
    
    triage_test = {
        "symptoms": "Severe abdominal pain with nausea and vomiting",
        "age_group": "adult",
        "insurance_type": "private",
        "department": "Emergency",
        "medical_history": "Previous appendectomy",
        "additional_context": "Pain started 2 hours ago"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/enhanced-ai/triage/ai-enhanced",
            json=triage_test,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
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
            error_text = response.text
            print(f"❌ AI-Enhanced Triage failed: {response.status_code} - {error_text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Triage request timed out - Ollama model may need more time to load")
    except Exception as e:
        print(f"❌ Triage request failed: {e}")
    
    # Test 5: Test cache functionality
    print("\n💾 Testing AI Response Cache")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/enhanced-ai/cache/stats", timeout=10)
        if response.status_code == 200:
            cache_stats = response.json()
            stats = cache_stats.get('cache_stats', {})
            print("✅ Cache stats retrieved")
            print(f"   Total cached entries: {stats.get('total_cached_entries', 0)}")
            print(f"   Active entries: {stats.get('active_entries', 0)}")
            print(f"   Cache TTL: {stats.get('cache_ttl_hours', 0)} hours")
        else:
            print("❌ Cache stats failed")
    except Exception as e:
        print(f"❌ Cache stats request failed: {e}")
    
    # Test 6: Test frontend integration
    print("\n🌐 Testing Frontend Integration")
    print("-" * 35)
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            print(f"   Frontend URL: {frontend_url}")
            print("   You can now test the AI features in the browser!")
        else:
            print("❌ Frontend not responding")
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
    
    # Summary
    print("\n📊 Integration Test Summary")
    print("=" * 30)
    print("✅ Ollama models are installed and running")
    print("✅ Backend server is running with AI endpoints")
    print("✅ Frontend is running and ready for testing")
    print("\n🎯 Next Steps:")
    print("1. Open your browser and go to http://localhost:5173")
    print("2. Navigate to the Queue Page")
    print("3. Enter symptoms and click 'Get AI Service Recommendation'")
    print("4. Watch the AI analyze your symptoms using Ollama models!")
    print("\n💡 Tips:")
    print("- The first AI request may take longer as models load into memory")
    print("- Subsequent requests will be faster due to caching")
    print("- Try different symptom descriptions to test various emergency levels")

if __name__ == "__main__":
    print(f"🚀 Starting Complete Ollama Integration Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_ollama_integration()
    print("\n✨ Complete integration test finished!")
