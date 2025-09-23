#!/usr/bin/env python3
"""
Quick and simple Ollama test
"""

import requests
import json

def quick_test():
    print("🚀 Quick Ollama Test")
    print("=" * 30)
    
    # Test with a very simple prompt
    simple_tests = [
        {"model": "phi3:3.8b", "prompt": "Say hello"},
        {"model": "mistral:latest", "prompt": "Say hello"}
    ]
    
    for test in simple_tests:
        print(f"\n🧪 Testing {test['model']}")
        print("-" * 30)
        
        payload = {
            "model": test["model"],
            "prompt": test["prompt"],
            "stream": False
        }
        
        try:
            print(f"   Sending: '{test['prompt']}'")
            response = requests.post("http://localhost:11434/api/generate", 
                                   json=payload, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                print(f"✅ Response: {content}")
                print(f"   Model loaded and working!")
            else:
                print(f"❌ Failed with status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout - model might be loading for the first time")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
    print("\n✨ Quick test completed!")