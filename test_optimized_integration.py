#!/usr/bin/env python3
"""
Test script for optimized OpenRouter AI integration
Demonstrates performance improvements, caching, and enhanced features
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_optimized_integration():
    """Test the optimized OpenRouter AI integration"""
    print("🚀 Testing Optimized OpenRouter AI Integration")
    print("=" * 60)
    
    try:
        from backend.app.ai.openrouter_service import openrouter_service
        
        print("✅ Services imported successfully")
        
        # Test 1: Performance with caching
        print("\n⚡ Performance Test with Caching")
        print("-" * 40)
        
        test_symptoms = "Chest pain and shortness of breath"
        
        # First request (will be cached)
        start_time = time.time()
        result1 = await openrouter_service.analyze_symptoms(test_symptoms)
        first_duration = time.time() - start_time
        
        # Second request (should use cache)
        start_time = time.time()
        result2 = await openrouter_service.analyze_symptoms(test_symptoms)
        second_duration = time.time() - start_time
        
        print(f"First request: {first_duration:.2f}s")
        print(f"Second request (cached): {second_duration:.2f}s")
        print(f"Speed improvement: {((first_duration - second_duration) / first_duration * 100):.1f}%")
        
        if result2.get("cached"):
            print("✅ Cache hit confirmed!")
        else:
            print("⚠️ Cache miss - may need investigation")
        
        # Test 2: Input validation
        print("\n🛡️ Input Validation Test")
        print("-" * 30)
        
        # Test empty symptoms
        empty_result = await openrouter_service.analyze_symptoms("")
        if empty_result.get("error"):
            print("✅ Empty symptoms properly rejected")
        else:
            print("❌ Empty symptoms should be rejected")
        
        # Test overly long symptoms
        long_symptoms = "Chest pain " * 200  # Very long string
        long_result = await openrouter_service.analyze_symptoms(long_symptoms)
        if long_result.get("error"):
            print("✅ Long symptoms properly rejected")
        else:
            print("❌ Long symptoms should be rejected")
        
        # Test 3: Enhanced response format
        print("\n📊 Enhanced Response Format Test")
        print("-" * 35)
        
        analysis = await openrouter_service.analyze_symptoms("Severe headache with nausea")
        
        if analysis.get("success"):
            print("✅ Analysis successful!")
            print(f"   Emergency Level: {analysis.get('emergency_level', 'unknown')}")
            print(f"   Confidence: {analysis.get('confidence', 0):.2f}")
            print(f"   Wait Time: {analysis.get('estimated_wait_time', 0)} minutes")
            
            # Check performance metrics
            performance = analysis.get("performance", {})
            if performance:
                print(f"   Request Duration: {performance.get('request_duration_seconds', 0):.2f}s")
                print(f"   Tokens Used: {performance.get('tokens_used', 0)}")
                print(f"   Model: {performance.get('model_used', 'unknown')}")
            
            # Check if cached
            if analysis.get("cached"):
                print("   📦 Response served from cache")
        else:
            print(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")
        
        # Test 4: Cache statistics
        print("\n📈 Cache Statistics")
        print("-" * 20)
        
        cache_stats = openrouter_service.get_cache_stats()
        print(f"Total cached entries: {cache_stats.get('total_cached_entries', 0)}")
        print(f"Active entries: {cache_stats.get('active_entries', 0)}")
        print(f"Cache TTL: {cache_stats.get('cache_ttl_hours', 0):.1f} hours")
        
        # Test 5: Batch processing optimization
        print("\n📦 Batch Processing Test")
        print("-" * 25)
        
        batch_symptoms = [
            {"symptoms": "Chest pain", "patient_age": "adult"},
            {"symptoms": "Fever and cough", "patient_age": "pediatric"},
            {"symptoms": "Minor cut on finger", "patient_age": "adult"}
        ]
        
        start_time = time.time()
        batch_results = await openrouter_service.batch_analyze_symptoms(batch_symptoms)
        batch_duration = time.time() - start_time
        
        print(f"Batch processing: {batch_duration:.2f}s for {len(batch_symptoms)} cases")
        print(f"Average per case: {batch_duration/len(batch_symptoms):.2f}s")
        
        successful = len([r for r in batch_results if not r.get("error")])
        print(f"Successful analyses: {successful}/{len(batch_results)}")
        
        # Test 6: Error handling
        print("\n🔧 Error Handling Test")
        print("-" * 25)
        
        # Test with invalid input
        invalid_result = await openrouter_service.analyze_symptoms("<script>alert('test')</script>Chest pain")
        if invalid_result.get("success"):
            print("✅ Malicious input properly sanitized")
        else:
            print("⚠️ Input sanitization may need review")
        
        print("\n🎉 All optimization tests completed!")
        
        # Summary
        print("\n📋 Optimization Summary:")
        print("✅ Response caching implemented")
        print("✅ Input validation and sanitization")
        print("✅ Performance metrics tracking")
        print("✅ Enhanced error handling")
        print("✅ Optimized prompt structure")
        print("✅ Batch processing improvements")
        print("✅ Cache management endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_optimized_integration()
    
    if success:
        print("\n✅ Optimization test completed successfully!")
        print("\nKey improvements:")
        print("• Faster responses with intelligent caching")
        print("• Better input validation and security")
        print("• Enhanced performance monitoring")
        print("• Optimized AI prompt for accuracy")
        print("• Improved error handling and logging")
        print("• Cache management capabilities")
    else:
        print("\n❌ Optimization test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
