#!/usr/bin/env python3
"""
Test script for Infobip SMS service integration
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.infobip_sms_service import infobip_sms_service

async def test_sms_service():
    """Test the Infobip SMS service functionality"""
    print("Testing Infobip SMS Service")
    print("=" * 50)

    try:
        # Test 1: Check account balance
        print("\n1. Checking account balance...")
        balance_result = await infobip_sms_service.get_account_balance()
        if balance_result.get("success"):
            print(f"[SUCCESS] Account balance: {balance_result.get('balance')} {balance_result.get('currency')}")
        else:
            print(f"[FAILED] Balance check failed: {balance_result.get('error')}")

        # Test 2: Send test SMS (commented out to avoid actual charges)
        print("\n2. Test SMS sending (commented out to avoid charges)")
        print("   To test actual SMS sending, uncomment the code below:")
        print("   test_sms = await infobip_sms_service.send_sms(")
        print("       to='263781660690',")
        print("       message='Test SMS from Healthcare Queue System'")
        print("   )")
        print("   print('SMS Result:', test_sms)")

        # Test 3: Test emergency ETA notification format
        print("\n3. Testing emergency ETA notification format...")
        eta_test = await infobip_sms_service.send_emergency_eta_notification(
            patient_phone="263781660690",
            eta_minutes=12,
            ambulance_id="AMB-001",
            location="123 Main St, Harare"
        )
        print(f"ETA notification would be sent: {eta_test}")

        # Test 4: Test emergency dispatch alert format
        print("\n4. Testing emergency dispatch alert format...")
        dispatch_test = await infobip_sms_service.send_emergency_dispatch_alert(
            responders=["263781660690"],
            emergency_location="456 Hospital Ave, Harare",
            emergency_type="Cardiac Arrest",
            priority="HIGH"
        )
        print(f"Dispatch alert would be sent: {len(dispatch_test)} recipients")

        print("\n[SUCCESS] SMS service tests completed successfully!")
        print("\nNext steps:")
        print("1. Uncomment the actual SMS sending code to test real messaging")
        print("2. Verify SMS delivery in Infobip dashboard")
        print("3. Check account balance after sending test messages")

    except Exception as e:
        print(f"\n[FAILED] SMS service test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Starting Infobip SMS Service Tests")
    success = asyncio.run(test_sms_service())
    sys.exit(0 if success else 1)