#!/usr/bin/env python3
"""
Simple test to verify Ollama models are working
"""

import requests
import json

def test_ollama_direct():
    """Test Ollama API directly"""
    print("🤖 Testing Ollama Models Directly")
    print("=" * 40)
    
    # Test 1: Check if Ollama is running
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
    
    # Test 2: Test a simple medical prompt
    print("\n🧠 Testing Medical Symptom Analysis")
    print("-" * 40)
    
    prompt = """MEDICAL TRIAGE ANALYSIS

Patient: I have severe chest pain that started this morning, accompanied by shortness of breath and dizziness
Age: 45
History: High blood pressure
Context: Pain is 8/10 on scale

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
{
    "emergency_level": "critical|high|moderate|low",
    "confidence": 0.0-1.0,
    "triage_category": "Emergency|Urgent|Semi-urgent|Non-urgent",
    "estimated_wait_time": 0|15|30|60|90|120,
    "department_recommendation": "Emergency|Cardiology|Orthopedics|Neurology|Pediatrics|Internal Medicine|General Surgery|Radiology|Obstetrics",
    "recommended_actions": ["action1", "action2"],
    "risk_factors": ["factor1"],
    "ai_reasoning": "Brief explanation"
}

Analyze and respond with JSON only."""

    payload = {
        "model": "phi3:3.8b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print("   Sending request to phi3:3.8b...")
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, 
                               timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', '')
            print("✅ Model responded successfully!")
            print(f"   Response length: {len(content)} characters")
            print(f"   Response preview: {content[:200]}...")
            
            # Try to parse JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed_data = json.loads(json_str)
                    print("✅ JSON parsing successful!")
                    print(f"   Emergency Level: {parsed_data.get('emergency_level', 'unknown')}")
                    print(f"   Confidence: {parsed_data.get('confidence', 0)}")
                    print(f"   Triage Category: {parsed_data.get('triage_category', 'unknown')}")
                    print(f"   Estimated Wait: {parsed_data.get('estimated_wait_time', 0)} min")
                    print(f"   Department: {parsed_data.get('department_recommendation', 'unknown')}")
                else:
                    print("⚠️ No JSON found in response")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}")
        else:
            print(f"❌ Model request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Test Mistral model
    print("\n🧠 Testing Mistral Model")
    print("-" * 40)
    
    simple_prompt = "Analyze this symptom: 'I have a mild headache and feel tired'. Respond with just the emergency level: critical, high, moderate, or low."
    
    payload = {
        "model": "mistral:latest",
        "prompt": simple_prompt,
        "stream": False
    }
    
    try:
        print("   Sending request to mistral:latest...")
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, 
                               timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', '')
            print("✅ Mistral responded successfully!")
            print(f"   Response: {content.strip()}")
        else:
            print(f"❌ Mistral request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Mistral request failed: {e}")

if __name__ == "__main__":
    test_ollama_direct()
    print("\n✨ Ollama test completed!")
