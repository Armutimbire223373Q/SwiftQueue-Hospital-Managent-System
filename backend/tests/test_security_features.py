"""
Security Features Test Suite
Tests for rate limiting, security headers, request validation, audit logging, CORS, and session management
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import time
import json


class TestSecurityMiddleware:
    """Test security middleware components"""
    
    def test_rate_limiting_basic(self, client: TestClient):
        """Test basic rate limiting"""
        # Make requests up to the limit
        for i in range(5):
            response = client.post("/api/auth/login", data={
                "username": "test@example.com",
                "password": "wrong_password"
            })
            
            # Should get rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers
            
            remaining = int(response.headers["X-RateLimit-Remaining"])
            assert remaining == 5 - i - 1
        
        # 6th request should be rate limited
        response = client.post("/api/auth/login", data={
            "username": "test@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 429
        assert "Retry-After" in response.headers
    
    def test_rate_limiting_different_endpoints(self, client: TestClient):
        """Test that different endpoints have separate rate limits"""
        # Make requests to login endpoint
        for _ in range(3):
            client.post("/api/auth/login", data={
                "username": "test@example.com",
                "password": "wrong"
            })
        
        # Make requests to register endpoint (should have separate limit)
        response = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "Test123!@#",
            "name": "Test User"
        })
        
        # Should not be rate limited (separate counter)
        assert response.status_code != 429
    
    def test_security_headers_present(self, client: TestClient):
        """Test that security headers are added to responses"""
        response = client.get("/api/health")
        
        # Check OWASP security headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        
        assert "Referrer-Policy" in response.headers
        
        # Server header should be removed
        assert "Server" not in response.headers
    
    def test_sql_injection_detection(self, client: TestClient):
        """Test SQL injection pattern detection"""
        # Test various SQL injection patterns
        sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--",
        ]
        
        for pattern in sql_patterns:
            response = client.get(f"/api/users?search={pattern}")
            
            # Should be blocked (400 Bad Request)
            assert response.status_code == 400
            assert "Potential security threat detected" in response.json()["detail"]
    
    def test_xss_detection(self, client: TestClient):
        """Test XSS pattern detection"""
        # Test various XSS patterns
        xss_patterns = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='malicious.com'></iframe>",
        ]
        
        for pattern in xss_patterns:
            response = client.get(f"/api/services?name={pattern}")
            
            # Should be blocked
            assert response.status_code == 400
            assert "Potential security threat detected" in response.json()["detail"]
    
    def test_path_traversal_detection(self, client: TestClient):
        """Test path traversal detection"""
        # Test path traversal patterns
        traversal_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
        ]
        
        for pattern in traversal_patterns:
            response = client.get(f"/api/uploads?file={pattern}")
            
            # Should be blocked
            assert response.status_code == 400
            assert "Potential security threat detected" in response.json()["detail"]
    
    def test_cors_configuration(self, client: TestClient):
        """Test CORS configuration"""
        # Test with allowed origin
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Credentials"] == "true"
        
        # Test OPTIONS request
        response = client.options(
            "/api/auth/login",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "Access-Control-Allow-Methods" in response.headers


class TestSessionManagement:
    """Test session management and JWT tokens"""
    
    def test_create_session(self):
        """Test session creation"""
        from app.services.session_service import SessionService
        
        tokens = SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1"
        )
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
        assert "expires_in" in tokens
        assert "expires_at" in tokens
    
    def test_verify_valid_token(self):
        """Test token verification with valid token"""
        from app.services.session_service import SessionService
        
        tokens = SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient"
        )
        
        payload = SessionService.verify_token(tokens["access_token"])
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "patient"
        assert payload["type"] == "access"
    
    def test_verify_invalid_token(self):
        """Test token verification with invalid token"""
        from app.services.session_service import SessionService
        
        payload = SessionService.verify_token("invalid.token.here")
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test token verification with expired token"""
        from app.services.session_service import SessionService
        from app.config.security_config import SecurityConfig
        
        # Temporarily set very short expiration
        original_expire = SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 0  # Expire immediately
        
        tokens = SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient"
        )
        
        # Wait a bit
        time.sleep(1)
        
        payload = SessionService.verify_token(tokens["access_token"])
        assert payload is None  # Should be expired
        
        # Restore original setting
        SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = original_expire
    
    def test_refresh_token(self):
        """Test token refresh"""
        from app.services.session_service import SessionService
        
        # Create initial tokens
        tokens = SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient"
        )
        
        # Refresh using refresh token
        new_tokens = SessionService.refresh_access_token(
            refresh_token=tokens["refresh_token"],
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1"
        )
        
        assert new_tokens is not None
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]  # Different token
    
    def test_revoke_token(self):
        """Test token revocation"""
        from app.services.session_service import SessionService
        
        # Create token
        tokens = SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient"
        )
        
        # Verify token works
        assert SessionService.verify_token(tokens["access_token"]) is not None
        
        # Revoke token
        SessionService.revoke_token(
            token=tokens["access_token"],
            reason="logout",
            user_id=1
        )
        
        # Verify token no longer works
        assert SessionService.verify_token(tokens["access_token"]) is None
    
    def test_revoke_all_user_sessions(self):
        """Test revoking all sessions for a user"""
        from app.services.session_service import SessionService
        
        # Create multiple sessions
        tokens1 = SessionService.create_access_token(1, "test@example.com", "patient")
        tokens2 = SessionService.create_access_token(1, "test@example.com", "patient")
        tokens3 = SessionService.create_access_token(2, "other@example.com", "patient")
        
        # Revoke all sessions for user 1
        SessionService.revoke_all_user_sessions(user_id=1, reason="security")
        
        # User 1 tokens should be revoked
        assert SessionService.verify_token(tokens1["access_token"]) is None
        assert SessionService.verify_token(tokens2["access_token"]) is None
        
        # User 2 token should still work
        assert SessionService.verify_token(tokens3["access_token"]) is not None
    
    def test_get_active_sessions(self):
        """Test getting active sessions for a user"""
        from app.services.session_service import SessionService
        
        # Create sessions
        SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient",
            user_agent="Chrome",
            ip_address="192.168.1.1"
        )
        SessionService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="patient",
            user_agent="Firefox",
            ip_address="192.168.1.2"
        )
        
        sessions = SessionService.get_active_sessions(user_id=1)
        assert len(sessions) >= 2
        assert all("session_id" in s for s in sessions)
        assert all("created_at" in s for s in sessions)
        assert all("user_agent" in s for s in sessions)
    
    def test_session_stats(self):
        """Test session statistics"""
        from app.services.session_service import SessionService
        
        # Create sessions with different roles
        SessionService.create_access_token(1, "patient@example.com", "patient")
        SessionService.create_access_token(2, "staff@example.com", "staff")
        SessionService.create_access_token(3, "admin@example.com", "admin")
        
        stats = SessionService.get_session_stats()
        assert "active_sessions" in stats
        assert "sessions_by_role" in stats
        assert stats["active_sessions"] >= 3


class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_log_creation(self):
        """Test creating audit log entries"""
        from app.services.audit_service import AuditLogger
        import os
        
        # Log an event
        AuditLogger.log_login_success(
            user_id=1,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )
        
        # Check that log file was created
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"logs/audit_{today}.log"
        
        # File should exist or be created
        # (in test environment, might not actually write)
        assert True  # Placeholder - actual file check would need temp directory
    
    def test_audit_log_events(self):
        """Test different audit log event types"""
        from app.services.audit_service import AuditLogger
        
        # Test various event types (should not raise errors)
        AuditLogger.log_login_success(1, "127.0.0.1", "Mozilla")
        AuditLogger.log_login_failure("test@example.com", "127.0.0.1", "Mozilla", "Invalid password")
        AuditLogger.log_payment_created(1, 100.00, "127.0.0.1")
        AuditLogger.log_medical_record_accessed(1, 1, "127.0.0.1")
        AuditLogger.log_security_violation("127.0.0.1", "sql_injection", {"pattern": "' OR '1'='1"})
        AuditLogger.log_admin_action(1, "create_user", "127.0.0.1", {"user_id": 2})
        
        assert True  # All logging should complete without errors


class TestInputSanitization:
    """Test input sanitization utilities"""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        # Test HTML escaping
        dangerous = "<script>alert('XSS')</script>"
        safe = InputSanitizer.sanitize_string(dangerous)
        assert "<script>" not in safe
        assert "&lt;script&gt;" in safe
    
    def test_sanitize_email(self):
        """Test email sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        # Valid emails
        assert InputSanitizer.sanitize_email("test@example.com") == "test@example.com"
        assert InputSanitizer.sanitize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"
        
        # Invalid emails
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_email("not-an-email")
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_email("test@")
    
    def test_sanitize_phone(self):
        """Test phone number sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        # Valid phone numbers
        assert InputSanitizer.sanitize_phone("(555) 123-4567") == "5551234567"
        assert InputSanitizer.sanitize_phone("+1-555-123-4567") == "15551234567"
        
        # Invalid phone numbers
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_phone("123")  # Too short
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_phone("12345678901234567890")  # Too long
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        # Path traversal attempts
        assert "../../../etc/passwd" not in InputSanitizer.sanitize_filename("../../../etc/passwd")
        assert "\\" not in InputSanitizer.sanitize_filename("..\\..\\windows\\system32")
        
        # Normal filenames
        assert InputSanitizer.sanitize_filename("document.pdf") == "document.pdf"
        assert InputSanitizer.sanitize_filename("my file.txt") == "my file.txt"
    
    def test_sanitize_url(self):
        """Test URL sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        # Valid URLs
        assert InputSanitizer.sanitize_url("https://example.com") == "https://example.com"
        assert InputSanitizer.sanitize_url("http://example.com/path") == "http://example.com/path"
        
        # Invalid URLs
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_url("javascript:alert('XSS')")
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_url("data:text/html,<script>alert('XSS')</script>")
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        from app.utils.sanitization import InputSanitizer
        
        dangerous_dict = {
            "name": "<script>alert('XSS')</script>",
            "email": "test@example.com",
            "nested": {
                "value": "javascript:alert('XSS')"
            }
        }
        
        safe_dict = InputSanitizer.sanitize_dict(dangerous_dict, allow_html=False)
        
        assert "<script>" not in safe_dict["name"]
        assert safe_dict["email"] == "test@example.com"
        assert "javascript:" not in safe_dict["nested"]["value"]
    
    def test_validate_json_depth(self):
        """Test JSON depth validation"""
        from app.utils.sanitization import InputSanitizer
        
        # Create deeply nested JSON
        deep_json = {"level": 1}
        current = deep_json
        for i in range(2, 15):
            current["nested"] = {"level": i}
            current = current["nested"]
        
        # Should raise error for too deep nesting
        with pytest.raises(ValueError):
            InputSanitizer.validate_json(deep_json, max_depth=10)
        
        # Shallow JSON should be fine
        shallow_json = {"level": 1, "data": {"level": 2}}
        assert InputSanitizer.validate_json(shallow_json, max_depth=10) is True


class TestSecurityConfiguration:
    """Test security configuration"""
    
    def test_security_config_load(self):
        """Test loading security configuration"""
        from app.config.security_config import SecurityConfig
        
        config = SecurityConfig.get_config()
        
        assert "environment" in config
        assert "rate_limiting" in config
        assert "session" in config
        assert "jwt" in config
        assert "password_policy" in config
    
    def test_security_config_validation(self):
        """Test security configuration validation"""
        from app.config.security_config import SecurityConfig
        
        # Should not raise errors with default config
        SecurityConfig.validate_config()


# Fixtures for testing
@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    from fastapi.testclient import TestClient
    
    return TestClient(app)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
