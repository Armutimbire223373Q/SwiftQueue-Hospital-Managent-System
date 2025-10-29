"""
Enhanced Session Management Service
Handles JWT token creation, validation, refresh, and revocation
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config.security_config import SecurityConfig
from app.services.audit_service import AuditLogger
import secrets


class SessionService:
    """
    Enhanced session management with JWT tokens, refresh tokens, and session tracking
    """
    
    # Store active sessions (in production, use Redis)
    _active_sessions: Dict[str, Dict[str, Any]] = {}
    _revoked_tokens: set = set()
    
    @staticmethod
    def create_access_token(user_id: int, email: str, role: str, user_agent: str = None, ip_address: str = None) -> Dict[str, Any]:
        """
        Create a new access token with embedded user information
        
        Args:
            user_id: User ID
            email: User email
            role: User role (patient, staff, admin)
            user_agent: User agent string (optional)
            ip_address: IP address (optional)
        
        Returns:
            Dict with access_token, refresh_token, expires_at, token_type
        """
        # Create access token
        access_token_expires = timedelta(minutes=SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "exp": datetime.utcnow() + access_token_expires,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
        }
        access_token = jwt.encode(
            access_token_data,
            SecurityConfig.JWT_SECRET_KEY,
            algorithm=SecurityConfig.JWT_ALGORITHM
        )
        
        # Create refresh token
        refresh_token_expires = timedelta(days=SecurityConfig.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_data = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": datetime.utcnow() + refresh_token_expires,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),
        }
        refresh_token = jwt.encode(
            refresh_token_data,
            SecurityConfig.JWT_SECRET_KEY,
            algorithm=SecurityConfig.JWT_ALGORITHM
        )
        
        # Store session information
        session_id = access_token_data["jti"]
        SessionService._active_sessions[session_id] = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "user_agent": user_agent,
            "ip_address": ip_address,
            "refresh_token_jti": refresh_token_data["jti"],
        }
        
        # Log session creation
        AuditLogger.log(
            event_type="session.created",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"session_id": session_id, "role": role},
            severity="info"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
            "expires_at": (datetime.utcnow() + access_token_expires).isoformat(),
        }
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            token_type: Token type (access or refresh)
        
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.JWT_SECRET_KEY,
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check if token is revoked
            if payload.get("jti") in SessionService._revoked_tokens:
                return None
            
            # Check session validity for access tokens
            if token_type == "access":
                session_id = payload.get("jti")
                if session_id not in SessionService._active_sessions:
                    return None
                
                # Update last activity
                SessionService._active_sessions[session_id]["last_activity"] = datetime.utcnow()
            
            return payload
        
        except JWTError:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str, user_agent: str = None, ip_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new access token using a refresh token
        
        Args:
            refresh_token: Refresh token
            user_agent: User agent string (optional)
            ip_address: IP address (optional)
        
        Returns:
            New token data or None if refresh token is invalid
        """
        # Verify refresh token
        payload = SessionService.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None
        
        user_id = int(payload["sub"])
        
        # Get user information from original session
        # In production, fetch from database
        original_session = None
        for session in SessionService._active_sessions.values():
            if session["user_id"] == user_id and session["refresh_token_jti"] == payload["jti"]:
                original_session = session
                break
        
        if not original_session:
            return None
        
        # Create new access token
        new_tokens = SessionService.create_access_token(
            user_id=user_id,
            email=original_session["email"],
            role=original_session["role"],
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Log token refresh
        AuditLogger.log(
            event_type="session.refreshed",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"old_jti": payload["jti"]},
            severity="info"
        )
        
        return new_tokens
    
    @staticmethod
    def revoke_token(token: str, reason: str = "logout", user_id: int = None, ip_address: str = None):
        """
        Revoke a token (logout)
        
        Args:
            token: Access token to revoke
            reason: Reason for revocation
            user_id: User ID (optional)
            ip_address: IP address (optional)
        """
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.JWT_SECRET_KEY,
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            
            jti = payload.get("jti")
            user_id = user_id or int(payload.get("sub"))
            
            # Add to revoked tokens
            SessionService._revoked_tokens.add(jti)
            
            # Remove from active sessions
            if jti in SessionService._active_sessions:
                session = SessionService._active_sessions[jti]
                
                # Also revoke refresh token
                refresh_jti = session.get("refresh_token_jti")
                if refresh_jti:
                    SessionService._revoked_tokens.add(refresh_jti)
                
                del SessionService._active_sessions[jti]
            
            # Log token revocation
            AuditLogger.log(
                event_type="session.revoked",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=None,
                details={"jti": jti, "reason": reason},
                severity="info"
            )
        
        except JWTError:
            pass
    
    @staticmethod
    def revoke_all_user_sessions(user_id: int, reason: str = "security", ip_address: str = None):
        """
        Revoke all active sessions for a user
        
        Args:
            user_id: User ID
            reason: Reason for revocation
            ip_address: IP address (optional)
        """
        revoked_count = 0
        sessions_to_remove = []
        
        for session_id, session in SessionService._active_sessions.items():
            if session["user_id"] == user_id:
                # Add to revoked tokens
                SessionService._revoked_tokens.add(session_id)
                if session.get("refresh_token_jti"):
                    SessionService._revoked_tokens.add(session["refresh_token_jti"])
                
                sessions_to_remove.append(session_id)
                revoked_count += 1
        
        # Remove sessions
        for session_id in sessions_to_remove:
            del SessionService._active_sessions[session_id]
        
        # Log bulk revocation
        AuditLogger.log(
            event_type="session.revoked_all",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=None,
            details={"count": revoked_count, "reason": reason},
            severity="warning"
        )
    
    @staticmethod
    def get_active_sessions(user_id: int) -> list:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of active session information
        """
        sessions = []
        for session_id, session in SessionService._active_sessions.items():
            if session["user_id"] == user_id:
                sessions.append({
                    "session_id": session_id,
                    "created_at": session["created_at"].isoformat(),
                    "last_activity": session["last_activity"].isoformat(),
                    "user_agent": session["user_agent"],
                    "ip_address": session["ip_address"],
                })
        
        return sessions
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up expired sessions (run periodically)
        """
        current_time = datetime.utcnow()
        timeout = timedelta(minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES)
        
        expired_sessions = []
        for session_id, session in SessionService._active_sessions.items():
            if current_time - session["last_activity"] > timeout:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            session = SessionService._active_sessions[session_id]
            SessionService._revoked_tokens.add(session_id)
            if session.get("refresh_token_jti"):
                SessionService._revoked_tokens.add(session["refresh_token_jti"])
            del SessionService._active_sessions[session_id]
        
        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    @staticmethod
    def should_refresh_token(token: str) -> bool:
        """
        Check if a token should be refreshed (approaching expiration)
        
        Args:
            token: Access token
        
        Returns:
            True if token should be refreshed
        """
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.JWT_SECRET_KEY,
                algorithms=[SecurityConfig.JWT_ALGORITHM],
                options={"verify_exp": False}  # Don't fail on expired
            )
            
            exp = datetime.fromtimestamp(payload["exp"])
            remaining = exp - datetime.utcnow()
            threshold = timedelta(minutes=SecurityConfig.SESSION_REFRESH_THRESHOLD_MINUTES)
            
            return remaining < threshold
        
        except JWTError:
            return False
    
    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            Session statistics
        """
        return {
            "active_sessions": len(SessionService._active_sessions),
            "revoked_tokens": len(SessionService._revoked_tokens),
            "sessions_by_role": {
                "patient": sum(1 for s in SessionService._active_sessions.values() if s["role"] == "patient"),
                "staff": sum(1 for s in SessionService._active_sessions.values() if s["role"] == "staff"),
                "admin": sum(1 for s in SessionService._active_sessions.values() if s["role"] == "admin"),
            }
        }
