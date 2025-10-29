"""
Security Middleware - Rate limiting, security headers, and request validation
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import hashlib
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse
    Implements token bucket algorithm with different limits per endpoint
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
        
        # Endpoint-specific rate limits (requests per minute)
        self.endpoint_limits = {
            "/api/auth/login": 5,           # Prevent brute force
            "/api/auth/register": 3,        # Prevent spam registrations
            "/api/payments/create": 20,     # Prevent payment spam
            "/api/payments/process": 30,    # Payment processing
            "/api/ai/chat": 10,             # AI rate limiting
            "/api/queue/join": 10,          # Queue spam prevention
        }
        
        # IP whitelist (add trusted IPs here)
        self.whitelist = set([
            "127.0.0.1",
            "::1",
        ])
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier (IP + User-Agent hash)"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Combine IP and user agent for more accurate tracking
        identifier = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier
    
    def _get_rate_limit(self, path: str) -> int:
        """Get rate limit for specific endpoint"""
        # Check if path matches any specific endpoint limit
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        
        # Default rate limit
        return self.requests_per_minute
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove requests older than 1 minute"""
        cutoff_time = current_time - 60
        self.request_counts[client_id] = [
            req_time for req_time in self.request_counts[client_id]
            if req_time > cutoff_time
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for whitelisted IPs
        client_ip = request.client.host if request.client else "unknown"
        if client_ip in self.whitelist:
            return await call_next(request)
        
        # Get client identifier and current time
        client_id = self._get_client_identifier(request)
        current_time = time.time()
        path = request.url.path
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit(path)
        
        # Check if rate limit exceeded
        request_count = len(self.request_counts[client_id])
        if request_count >= rate_limit:
            # Calculate retry-after time
            oldest_request = min(self.request_counts[client_id])
            retry_after = int(60 - (current_time - oldest_request))
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit": rate_limit,
                    "requests_made": request_count
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(oldest_request + 60))
                }
            )
        
        # Add current request to tracking
        self.request_counts[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_limit - len(self.request_counts[client_id]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    Implements OWASP security best practices
    """
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (HSTS)
        # Enable only in production with HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        # Remove server header (security through obscurity)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize incoming requests
    Detect common attack patterns
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # SQL injection patterns
        self.sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE",
            "UNION SELECT",
            "' OR 1=1--",
            "'; --",
            "' AND '1'='1",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            "<script",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe",
            "eval(",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            "../",
            "..\\",
            "%2e%2e%2f",
            "%2e%2e\\",
        ]
    
    def _check_malicious_patterns(self, value: str) -> Tuple[bool, str]:
        """Check if value contains malicious patterns"""
        value_lower = value.lower()
        
        # Check SQL injection
        for pattern in self.sql_patterns:
            if pattern.lower() in value_lower:
                return True, f"Potential SQL injection detected: {pattern}"
        
        # Check XSS
        for pattern in self.xss_patterns:
            if pattern.lower() in value_lower:
                return True, f"Potential XSS detected: {pattern}"
        
        # Check path traversal
        for pattern in self.path_traversal_patterns:
            if pattern in value_lower:
                return True, f"Potential path traversal detected: {pattern}"
        
        return False, ""
    
    async def dispatch(self, request: Request, call_next):
        """Validate request for malicious content"""
        
        # Check query parameters
        for key, value in request.query_params.items():
            is_malicious, reason = self._check_malicious_patterns(str(value))
            if is_malicious:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Invalid request",
                        "message": "Request contains potentially malicious content",
                        "detail": reason
                    }
                )
        
        # Check headers for suspicious values
        suspicious_headers = ["x-forwarded-for", "referer", "user-agent"]
        for header in suspicious_headers:
            value = request.headers.get(header, "")
            if value:
                is_malicious, reason = self._check_malicious_patterns(value)
                if is_malicious:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": "Invalid request",
                            "message": "Request headers contain potentially malicious content"
                        }
                    )
        
        # Process request
        response = await call_next(request)
        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for security auditing
    Track authentication attempts, sensitive operations
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Sensitive endpoints to always log
        self.sensitive_endpoints = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/payments/",
            "/api/admin/",
            "/api/staff/",
        ]
    
    def _should_log(self, path: str, method: str) -> bool:
        """Determine if request should be logged"""
        # Always log POST, PUT, DELETE, PATCH
        if method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True
        
        # Always log sensitive endpoints
        for endpoint in self.sensitive_endpoints:
            if path.startswith(endpoint):
                return True
        
        return False
    
    def _get_client_info(self, request: Request) -> dict:
        """Extract client information for logging"""
        return {
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer", ""),
            "forwarded_for": request.headers.get("x-forwarded-for", ""),
        }
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response"""
        start_time = time.time()
        
        # Check if should log this request
        should_log = self._should_log(request.url.path, request.method)
        
        if should_log:
            client_info = self._get_client_info(request)
            
            # Log request (in production, send to logging service)
            print(f"[AUDIT] {request.method} {request.url.path} from {client_info['ip']}")
        
        # Process request
        response = await call_next(request)
        
        if should_log:
            duration = time.time() - start_time
            
            # Log response
            print(f"[AUDIT] Response: {response.status_code} ({duration:.3f}s)")
            
            # Log failed authentication attempts
            if request.url.path.startswith("/api/auth/login") and response.status_code == 401:
                print(f"[SECURITY] Failed login attempt from {client_info['ip']}")
            
            # Log successful authentications
            if request.url.path.startswith("/api/auth/login") and response.status_code == 200:
                print(f"[SECURITY] Successful login from {client_info['ip']}")
        
        return response


# Export middleware classes
__all__ = [
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware", 
    "RequestValidationMiddleware",
    "AuditLogMiddleware"
]
