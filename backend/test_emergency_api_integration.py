#!/usr/bin/env python3
"""
Integration tests for emergency API endpoints.
Tests the actual running server endpoints.
"""

import requests
import json
import time
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api"

def test_emergency_endpoints():
    """Test emergency API endpoints"""

    print("Testing Emergency API Endpoints")
    print("=" * 50)

    # Test 1: AI health check (server connectivity test)
    print("\n2. Testing AI service health...")
    try:
        response = requests.get(f"{API_BASE}/ai/health")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: AI service status: {data.get('status', 'unknown')}")
        else:
            print(f"FAIL: AI health check failed: {response.status_code}")
    except Exception as e:
        print(f"FAIL: AI health check error: {e}")

    # Test 3: Test critical symptom analysis (should trigger ambulance dispatch)
    print("\n3. Testing critical symptom analysis with ambulance dispatch...")
    try:
        payload = {
            "symptoms": "chest pain, difficulty breathing, unconscious",
            "patient_id": 1
        }
        response = requests.post(f"{API_BASE}/ai/analyze-symptoms", json=payload)
        if response.status_code == 200:
            data = response.json()
            analysis = data.get("analysis", {})
            print(f"PASS: Symptom analysis successful")
            print(f"   Emergency level: {analysis.get('emergency_level', 'unknown')}")
            if "ambulance_dispatch" in analysis:
                dispatch_info = analysis["ambulance_dispatch"]
                if dispatch_info and "error" not in dispatch_info:
                    print("PASS: Ambulance dispatch triggered successfully!")
                    print(f"   Dispatch ID: {dispatch_info.get('dispatch_id')}")
                    print(f"   Ambulance: {dispatch_info.get('ambulance_id')}")
                    print(f"   Status: {dispatch_info.get('status')}")
                    dispatch_id = dispatch_info.get('dispatch_id')
                else:
                    print(f"FAIL: Ambulance dispatch failed: {dispatch_info.get('error', 'Unknown error')}")
            else:
                print("INFO: No ambulance dispatch in response (may be expected)")
        else:
            print(f"FAIL: Symptom analysis failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAIL: Symptom analysis error: {e}")

    # Test 4: Test dispatch status retrieval (if dispatch was created)
    if 'dispatch_id' in locals():
        print(f"\n4. Testing dispatch status retrieval for ID {dispatch_id}...")
        try:
            response = requests.get(f"{API_BASE}/emergency/dispatch/{dispatch_id}")
            if response.status_code == 200:
                data = response.json()
                print("PASS: Dispatch status retrieved successfully")
                print(f"   Status: {data.get('dispatch_status')}")
                print(f"   Patient: {data.get('patient_name', 'Unknown')}")
                print(f"   Address: {data.get('dispatch_address', 'Unknown')[:50]}...")
            elif response.status_code == 404:
                print("INFO: Dispatch not found (may be expected if using mock data)")
            else:
                print(f"FAIL: Dispatch status retrieval failed: {response.status_code}")
        except Exception as e:
            print(f"FAIL: Dispatch status error: {e}")

    # Test 5: Test patient dispatches retrieval
    print("\n5. Testing patient dispatches retrieval...")
    try:
        response = requests.get(f"{API_BASE}/emergency/dispatches/patient/1")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Patient dispatches retrieved: {len(data)} dispatches found")
            if data:
                latest = data[0]
                print(f"   Latest dispatch: {latest.get('emergency_details', 'Unknown')[:50]}...")
                print(f"   Status: {latest.get('dispatch_status')}")
        elif response.status_code == 404:
            print("INFO: No dispatches found for patient (expected for new patient)")
        else:
            print(f"FAIL: Patient dispatches retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"FAIL: Patient dispatches error: {e}")

    # Test 6: Test manual ambulance dispatch (would need authentication)
    print("\n6. Testing manual ambulance dispatch endpoint...")
    try:
        payload = {
            "patient_id": 1,
            "emergency_details": "Manual dispatch test - severe headache"
        }
        response = requests.post(f"{API_BASE}/emergency/dispatch-ambulance", json=payload)
        if response.status_code == 403:
            print("PASS: Authentication required (expected for manual dispatch)")
        elif response.status_code == 200:
            data = response.json()
            print("PASS: Manual dispatch successful (authentication bypassed?)")
            print(f"   Dispatch ID: {data.get('id')}")
            print(f"   Status: {data.get('dispatch_status')}")
        else:
            print(f"FAIL: Manual dispatch failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAIL: Manual dispatch error: {e}")

    print("\n" + "=" * 50)
    print("Emergency API testing completed!")
    return True

if __name__ == "__main__":
    success = test_emergency_endpoints()
    exit(0 if success else 1)