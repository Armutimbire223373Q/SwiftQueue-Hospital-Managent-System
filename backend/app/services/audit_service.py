"""
Audit Logging Service - Track security-sensitive operations
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import json
import os


class AuditLogger:
    """
    Centralized audit logging for security events
    In production, integrate with logging services (CloudWatch, Datadog, etc.)
    """
    
    # Event types
    EVENT_AUTH_LOGIN_SUCCESS = "auth.login.success"
    EVENT_AUTH_LOGIN_FAILURE = "auth.login.failure"
    EVENT_AUTH_LOGOUT = "auth.logout"
    EVENT_AUTH_REGISTER = "auth.register"
    EVENT_AUTH_PASSWORD_CHANGE = "auth.password.change"
    EVENT_AUTH_PASSWORD_RESET = "auth.password.reset"
    
    EVENT_PAYMENT_CREATE = "payment.create"
    EVENT_PAYMENT_PROCESS = "payment.process"
    EVENT_PAYMENT_REFUND = "payment.refund"
    EVENT_PAYMENT_VERIFY = "payment.verify"
    
    EVENT_PATIENT_VIEW = "patient.view"
    EVENT_PATIENT_CREATE = "patient.create"
    EVENT_PATIENT_UPDATE = "patient.update"
    EVENT_PATIENT_DELETE = "patient.delete"
    
    EVENT_MEDICAL_RECORD_VIEW = "medical_record.view"
    EVENT_MEDICAL_RECORD_CREATE = "medical_record.create"
    EVENT_MEDICAL_RECORD_UPDATE = "medical_record.update"
    
    EVENT_ADMIN_ACTION = "admin.action"
    EVENT_SECURITY_VIOLATION = "security.violation"
    EVENT_RATE_LIMIT_EXCEEDED = "security.rate_limit"
    
    @staticmethod
    def log(
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ):
        """
        Log an audit event
        
        Args:
            event_type: Type of event (use EVENT_* constants)
            user_id: User ID performing the action
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional event details
            severity: Severity level (info, warning, error, critical)
        """
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "severity": severity,
            "details": details or {}
        }
        
        # In production, send to logging service
        # For now, write to console and file
        AuditLogger._write_to_console(log_entry)
        AuditLogger._write_to_file(log_entry)
        
        # Store in database for queryable audit trail
        # AuditLogger._write_to_database(log_entry)
    
    @staticmethod
    def _write_to_console(log_entry: dict):
        """Write log entry to console"""
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        emoji = severity_emoji.get(log_entry["severity"], "📝")
        event = log_entry["event_type"]
        user = f"User:{log_entry['user_id']}" if log_entry['user_id'] else "Anonymous"
        ip = log_entry.get('ip_address', 'unknown')
        
        print(f"[AUDIT {emoji}] {event} | {user} | IP:{ip}")
        
        if log_entry.get('details'):
            print(f"         Details: {json.dumps(log_entry['details'], indent=2)}")
    
    @staticmethod
    def _write_to_file(log_entry: dict):
        """Write log entry to file"""
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create daily log file
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"audit_{date_str}.log")
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[AUDIT ERROR] Failed to write to file: {e}")
    
    @staticmethod
    def _write_to_database(log_entry: dict):
        """
        Write log entry to database
        Implement in production for queryable audit trail
        """
        # TODO: Implement database logging
        # from app.models.models import AuditLog
        # db_log = AuditLog(**log_entry)
        # db.add(db_log)
        # db.commit()
        pass
    
    # Convenience methods for common events
    
    @staticmethod
    def log_login_success(user_id: int, ip_address: str, user_agent: str):
        """Log successful login"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_AUTH_LOGIN_SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity="info"
        )
    
    @staticmethod
    def log_login_failure(email: str, ip_address: str, user_agent: str, reason: str):
        """Log failed login attempt"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_AUTH_LOGIN_FAILURE,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": email, "reason": reason},
            severity="warning"
        )
    
    @staticmethod
    def log_payment_created(user_id: int, payment_id: str, amount: float, ip_address: str):
        """Log payment creation"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_PAYMENT_CREATE,
            user_id=user_id,
            ip_address=ip_address,
            details={"payment_id": payment_id, "amount": amount},
            severity="info"
        )
    
    @staticmethod
    def log_medical_record_accessed(user_id: int, patient_id: int, ip_address: str):
        """Log medical record access (HIPAA compliance)"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_MEDICAL_RECORD_VIEW,
            user_id=user_id,
            ip_address=ip_address,
            details={"patient_id": patient_id},
            severity="info"
        )
    
    @staticmethod
    def log_security_violation(ip_address: str, violation_type: str, details: dict):
        """Log security violation"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_SECURITY_VIOLATION,
            ip_address=ip_address,
            details={"violation_type": violation_type, **details},
            severity="error"
        )
    
    @staticmethod
    def log_admin_action(user_id: int, action: str, target: str, ip_address: str):
        """Log administrative action"""
        AuditLogger.log(
            event_type=AuditLogger.EVENT_ADMIN_ACTION,
            user_id=user_id,
            ip_address=ip_address,
            details={"action": action, "target": target},
            severity="warning"
        )


# Singleton instance
audit_logger = AuditLogger()


# Decorator for automatic audit logging
def audit_log(event_type: str, severity: str = "info"):
    """
    Decorator to automatically log function calls
    
    Usage:
        @audit_log(AuditLogger.EVENT_PAYMENT_CREATE)
        def create_payment(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request context if available
            request = kwargs.get('request')
            current_user = kwargs.get('current_user')
            
            user_id = current_user.id if current_user and hasattr(current_user, 'id') else None
            ip_address = request.client.host if request and request.client else None
            user_agent = request.headers.get('user-agent') if request else None
            
            # Log before execution
            AuditLogger.log(
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                severity=severity
            )
            
            # Execute function
            result = await func(*args, **kwargs)
            return result
        
        return wrapper
    return decorator
