#!/usr/bin/env python3
"""
Analyze the current Ollama implementation and model configuration
"""

import os
import json
import requests
from typing import Dict, List

def analyze_ollama_implementation():
    """Analyze the current Ollama implementation"""
    print("🔍 Analyzing Ollama Implementation")
    print("=" * 50)
    
    # 1. Check Ollama models
    print("\n📋 Available Ollama Models:")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running")
            print(f"   Total models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                size_gb = model.get('size', 0) / 1024**3
                print(f"   • {model.get('name', 'unknown')} ({size_gb:.1f} GB)")
                print(f"     ID: {model.get('id', 'unknown')}")
                print(f"     Modified: {model.get('modified_at', 'unknown')}")
        else:
            print("❌ Ollama not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return
    
    # 2. Analyze configuration
    print("\n⚙️ Configuration Analysis:")
    print("-" * 30)
    
    # Check environment variables
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
    ollama_model = os.getenv("OLLAMA_MODEL", "phi3:3.8b")
    ollama_triage_model = os.getenv("OLLAMA_MODEL_TRIAGE", "mistral:latest")
    ollama_timeout = os.getenv("OLLAMA_TIMEOUT", "60")
    
    print(f"   Base URL: {ollama_base_url}")
    print(f"   Default Model: {ollama_model}")
    print(f"   Triage Model: {ollama_triage_model}")
    print(f"   Timeout: {ollama_timeout}s")
    
    # 3. Test model responses
    print("\n🧠 Testing Model Responses:")
    print("-" * 30)
    
    test_prompts = [
        {
            "model": "phi3:3.8b",
            "prompt": "What is your name and what can you help with?",
            "description": "Basic capability test"
        },
        {
            "model": "mistral:latest", 
            "prompt": "Analyze this symptom: 'chest pain'. Respond with just: critical, high, moderate, or low",
            "description": "Medical analysis test"
        }
    ]
    
    for test in test_prompts:
        print(f"\n   Testing {test['model']} - {test['description']}")
        try:
            payload = {
                "model": test["model"],
                "prompt": test["prompt"],
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                print(f"   ✅ Response received ({len(content)} chars)")
                print(f"   Preview: {content[:100]}...")
                
                # Check if it's a medical response
                if any(word in content.lower() for word in ['critical', 'high', 'moderate', 'low']):
                    print("   🏥 Medical analysis detected!")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out - model may need to load")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 4. Analyze the implementation structure
    print("\n🏗️ Implementation Structure:")
    print("-" * 35)
    
    implementation_details = {
        "Service Class": "OpenRouterService (misleading name - actually uses Ollama)",
        "Base URL": "http://localhost:11434/api/generate",
        "Default Model": "phi3:3.8b",
        "Triage Model": "mistral:latest", 
        "Timeout": "60 seconds",
        "Caching": "Yes - 1 hour TTL",
        "Error Handling": "Yes - fallback parsing",
        "JSON Parsing": "Yes - with regex extraction",
        "Batch Processing": "Yes - async gather"
    }
    
    for key, value in implementation_details.items():
        print(f"   {key}: {value}")
    
    # 5. Check API endpoints
    print("\n🔗 API Endpoints:")
    print("-" * 20)
    
    endpoints = [
        "/api/enhanced-ai/symptoms/analyze",
        "/api/enhanced-ai/triage/ai-enhanced", 
        "/api/enhanced-ai/symptoms/batch-analyze",
        "/api/enhanced-ai/cache/stats",
        "/api/enhanced-ai/cache/clear"
    ]
    
    for endpoint in endpoints:
        print(f"   • {endpoint}")
    
    # 6. Model usage analysis
    print("\n🎯 Model Usage Analysis:")
    print("-" * 30)
    
    usage_patterns = {
        "phi3:3.8b": {
            "Primary Use": "General symptom analysis",
            "Size": "2.2 GB",
            "Speed": "Faster loading",
            "Capability": "Good for structured responses"
        },
        "mistral:latest": {
            "Primary Use": "Advanced triage analysis", 
            "Size": "4.4 GB",
            "Speed": "Slower loading",
            "Capability": "Better reasoning and analysis"
        }
    }
    
    for model, details in usage_patterns.items():
        print(f"\n   {model}:")
        for key, value in details.items():
            print(f"     {key}: {value}")
    
    # 7. Recommendations
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    recommendations = [
        "✅ Current setup is well-configured with two complementary models",
        "✅ phi3:3.8b is good for quick symptom analysis",
        "✅ mistral:latest provides better reasoning for complex cases",
        "⚠️ First requests may be slow as models load into memory",
        "💡 Consider pre-loading models for faster response times",
        "💡 Monitor memory usage with both models loaded",
        "💡 Consider adding model health checks"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # 8. Test the actual implementation
    print("\n🧪 Testing Implementation:")
    print("-" * 30)
    
    # Test the medical prompt format
    medical_prompt = """MEDICAL TRIAGE ANALYSIS

Patient: I have severe chest pain that started this morning
Age: 45
History: High blood pressure
Context: Pain is 8/10 on scale

RESPONSE FORMAT (JSON only):
{
    "emergency_level": "critical|high|moderate|low",
    "confidence": 0.0-1.0,
    "triage_category": "Emergency|Urgent|Semi-urgent|Non-urgent",
    "estimated_wait_time": 0|15|30|60|90|120,
    "department_recommendation": "Emergency|Cardiology|Internal Medicine",
    "recommended_actions": ["action1", "action2"],
    "risk_factors": ["factor1"],
    "ai_reasoning": "Brief explanation"
}

Analyze and respond with JSON only."""
    
    try:
        payload = {
            "model": "phi3:3.8b",
            "prompt": medical_prompt,
            "stream": False
        }
        
        print("   Testing medical prompt with phi3:3.8b...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', '')
            print(f"   ✅ Medical analysis response received")
            print(f"   Response length: {len(content)} characters")
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    parsed_data = json.loads(json_str)
                    print("   ✅ JSON parsing successful!")
                    print(f"   Emergency Level: {parsed_data.get('emergency_level', 'unknown')}")
                    print(f"   Confidence: {parsed_data.get('confidence', 0)}")
                    print(f"   Triage Category: {parsed_data.get('triage_category', 'unknown')}")
                    print(f"   Department: {parsed_data.get('department_recommendation', 'unknown')}")
                except json.JSONDecodeError:
                    print("   ⚠️ JSON parsing failed - response may not be properly formatted")
            else:
                print("   ⚠️ No JSON found in response")
                
        else:
            print(f"   ❌ Medical test failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Medical test timed out - model may need more time to load")
    except Exception as e:
        print(f"   ❌ Medical test error: {e}")

if __name__ == "__main__":
    analyze_ollama_implementation()
    print("\n✨ Analysis complete!")
