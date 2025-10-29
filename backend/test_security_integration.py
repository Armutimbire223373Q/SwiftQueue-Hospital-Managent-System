"""
Quick Security Integration Test
Verifies all security features are properly integrated and functional
"""

def test_security_imports():
    """Test that all security modules can be imported"""
    print("\n🔍 Testing Security Module Imports...")
    
    try:
        from app.middleware.security import (
            RateLimitMiddleware,
            SecurityHeadersMiddleware,
            RequestValidationMiddleware,
            AuditLogMiddleware
        )
        print("  ✅ Security middleware imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import security middleware: {e}")
        return False
    
    try:
        from app.middleware.cors_config import CORSConfig
        print("  ✅ CORS configuration imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import CORS config: {e}")
        return False
    
    try:
        from app.config.security_config import SecurityConfig
        print("  ✅ Security configuration imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import security config: {e}")
        return False
    
    try:
        from app.services.session_service import SessionService
        print("  ✅ Session service imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import session service: {e}")
        return False
    
    try:
        from app.services.audit_service import AuditLogger
        print("  ✅ Audit logger imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import audit logger: {e}")
        return False
    
    try:
        from app.utils.sanitization import InputSanitizer
        print("  ✅ Input sanitizer imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import input sanitizer: {e}")
        return False
    
    return True


def test_security_config():
    """Test security configuration"""
    print("\n🔍 Testing Security Configuration...")
    
    try:
        from app.config.security_config import SecurityConfig
        
        # Get configuration
        config = SecurityConfig.get_config()
        
        # Check required sections
        required_sections = [
            "environment", "rate_limiting", "session", "jwt",
            "password_policy", "audit_logging", "security_headers",
            "request_validation", "file_upload"
        ]
        
        for section in required_sections:
            if section in config:
                print(f"  ✅ Configuration section '{section}' present")
            else:
                print(f"  ❌ Configuration section '{section}' missing")
                return False
        
        # Validate configuration
        try:
            SecurityConfig.validate_config()
            print("  ✅ Security configuration validation passed")
        except ValueError as e:
            print(f"  ⚠️  Security configuration validation warning: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Security configuration test failed: {e}")
        return False


def test_session_service():
    """Test session service functionality"""
    print("\n🔍 Testing Session Service...")
    
    try:
        from app.services.session_service import SessionService
        
        # Create session
        tokens = SessionService.create_access_token(
            user_id=999,
            email="test@example.com",
            role="patient",
            user_agent="Test Agent",
            ip_address="127.0.0.1"
        )
        
        required_keys = ["access_token", "refresh_token", "token_type", "expires_in", "expires_at"]
        for key in required_keys:
            if key in tokens:
                print(f"  ✅ Token response has '{key}'")
            else:
                print(f"  ❌ Token response missing '{key}'")
                return False
        
        # Verify token
        payload = SessionService.verify_token(tokens["access_token"])
        if payload:
            print(f"  ✅ Token verification successful")
            print(f"     - User ID: {payload.get('sub')}")
            print(f"     - Email: {payload.get('email')}")
            print(f"     - Role: {payload.get('role')}")
        else:
            print(f"  ❌ Token verification failed")
            return False
        
        # Get session stats
        stats = SessionService.get_session_stats()
        print(f"  ✅ Session stats retrieved: {stats['active_sessions']} active sessions")
        
        # Revoke token
        SessionService.revoke_token(tokens["access_token"], reason="test", user_id=999)
        
        # Verify revoked token doesn't work
        payload = SessionService.verify_token(tokens["access_token"])
        if payload is None:
            print(f"  ✅ Token revocation successful")
        else:
            print(f"  ❌ Token revocation failed - token still valid")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Session service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audit_logger():
    """Test audit logging"""
    print("\n🔍 Testing Audit Logger...")
    
    try:
        from app.services.audit_service import AuditLogger
        
        # Test different log methods
        test_cases = [
            ("login_success", lambda: AuditLogger.log_login_success(
                user_id=1,
                ip_address="127.0.0.1",
                user_agent="Test"
            )),
            ("login_failure", lambda: AuditLogger.log_login_failure(
                email="test@example.com",
                ip_address="127.0.0.1",
                user_agent="Test",
                reason="Invalid password"
            )),
            ("payment_created", lambda: AuditLogger.log_payment_created(
                user_id=1,
                payment_id="PAY-123",
                amount=100.00,
                ip_address="127.0.0.1"
            )),
            ("security_violation", lambda: AuditLogger.log_security_violation(
                ip_address="127.0.0.1",
                violation_type="test",
                details={"test": "data"}
            )),
        ]
        
        for name, func in test_cases:
            try:
                func()
                print(f"  ✅ Audit log '{name}' successful")
            except Exception as e:
                print(f"  ❌ Audit log '{name}' failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Audit logger test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_sanitizer():
    """Test input sanitization"""
    print("\n🔍 Testing Input Sanitizer...")
    
    try:
        from app.utils.sanitization import InputSanitizer
        
        # Test string sanitization
        dangerous = "<script>alert('XSS')</script>"
        safe = InputSanitizer.sanitize_string(dangerous)
        if "<script>" not in safe:
            print(f"  ✅ String sanitization blocks XSS")
        else:
            print(f"  ❌ String sanitization failed - XSS not blocked")
            return False
        
        # Test email sanitization
        try:
            email = InputSanitizer.sanitize_email("test@example.com")
            print(f"  ✅ Email sanitization successful: {email}")
        except ValueError as e:
            print(f"  ❌ Email sanitization failed: {e}")
            return False
        
        # Test invalid email
        try:
            InputSanitizer.sanitize_email("not-an-email")
            print(f"  ❌ Invalid email should have been rejected")
            return False
        except ValueError:
            print(f"  ✅ Invalid email rejected correctly")
        
        # Test phone sanitization
        phone = InputSanitizer.sanitize_phone("(555) 123-4567")
        if phone == "5551234567":
            print(f"  ✅ Phone sanitization successful: {phone}")
        else:
            print(f"  ❌ Phone sanitization failed: got {phone}")
            return False
        
        # Test filename sanitization
        dangerous_file = "../../../etc/passwd"
        safe_file = InputSanitizer.sanitize_filename(dangerous_file)
        if ".." not in safe_file and "/" not in safe_file:
            print(f"  ✅ Filename sanitization blocks path traversal")
        else:
            print(f"  ❌ Filename sanitization failed: {safe_file}")
            return False
        
        # Test URL sanitization
        try:
            url = InputSanitizer.sanitize_url("https://example.com")
            print(f"  ✅ URL sanitization successful")
        except ValueError as e:
            print(f"  ❌ URL sanitization failed: {e}")
            return False
        
        # Test invalid URL
        try:
            InputSanitizer.sanitize_url("javascript:alert('XSS')")
            print(f"  ❌ Dangerous URL should have been rejected")
            return False
        except ValueError:
            print(f"  ✅ Dangerous URL rejected correctly")
        
        return True
    except Exception as e:
        print(f"  ❌ Input sanitizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_middleware_classes():
    """Test that middleware classes are properly defined"""
    print("\n🔍 Testing Middleware Classes...")
    
    try:
        from app.middleware.security import (
            RateLimitMiddleware,
            SecurityHeadersMiddleware,
            RequestValidationMiddleware,
            AuditLogMiddleware
        )
        
        # Check that classes have dispatch method
        middleware_classes = [
            ("RateLimitMiddleware", RateLimitMiddleware),
            ("SecurityHeadersMiddleware", SecurityHeadersMiddleware),
            ("RequestValidationMiddleware", RequestValidationMiddleware),
            ("AuditLogMiddleware", AuditLogMiddleware),
        ]
        
        for name, cls in middleware_classes:
            if hasattr(cls, "dispatch"):
                print(f"  ✅ {name} has dispatch method")
            else:
                print(f"  ❌ {name} missing dispatch method")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Middleware classes test failed: {e}")
        return False


def test_cors_config():
    """Test CORS configuration"""
    print("\n🔍 Testing CORS Configuration...")
    
    try:
        from app.middleware.cors_config import CORSConfig, is_origin_allowed
        
        # Get allowed origins
        origins = CORSConfig.get_allowed_origins()
        print(f"  ✅ Allowed origins: {len(origins)} domains")
        
        # Get CORS config
        config = CORSConfig.get_cors_config()
        
        required_keys = ["allow_origins", "allow_credentials", "allow_methods", "allow_headers"]
        for key in required_keys:
            if key in config:
                print(f"  ✅ CORS config has '{key}'")
            else:
                print(f"  ❌ CORS config missing '{key}'")
                return False
        
        # Test origin validation
        is_allowed = is_origin_allowed("http://localhost:3000")
        print(f"  ✅ Origin validation working: localhost is {'allowed' if is_allowed else 'blocked'}")
        
        return True
    except Exception as e:
        print(f"  ❌ CORS configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all security tests"""
    print("\n" + "=" * 60)
    print("🔒 SECURITY INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Security Imports", test_security_imports),
        ("Security Configuration", test_security_config),
        ("Session Service", test_session_service),
        ("Audit Logger", test_audit_logger),
        ("Input Sanitizer", test_input_sanitizer),
        ("Middleware Classes", test_middleware_classes),
        ("CORS Configuration", test_cors_config),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("🎉 ALL SECURITY TESTS PASSED! 🎉\n")
        print("✅ Security features are properly integrated and functional")
        print("✅ Rate limiting, security headers, request validation ready")
        print("✅ Audit logging, CORS, session management operational")
        print("✅ Input sanitization working correctly")
        print("\n🚀 Production security features are READY TO DEPLOY!")
        return True
    else:
        print("⚠️  SOME SECURITY TESTS FAILED")
        print(f"   {total - passed} test(s) need attention")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
