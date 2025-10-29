"""
Security Configuration - Central security settings and integration
"""
import os
from typing import Dict, Any, List


class SecurityConfig:
    """
    Central security configuration
    """
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    IS_PRODUCTION = ENVIRONMENT == "production"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    SESSION_REFRESH_THRESHOLD_MINUTES = int(os.getenv("SESSION_REFRESH_THRESHOLD_MINUTES", "5"))
    
    # JWT Settings
    JWT_ALGORITHM = "HS256"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_DIGIT = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # Audit Logging
    AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
    AUDIT_LOG_TO_DATABASE = os.getenv("AUDIT_LOG_TO_DATABASE", "false").lower() == "true"
    
    # Security Headers
    SECURITY_HEADERS_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
    HSTS_ENABLED = IS_PRODUCTION  # Only enable HSTS in production with HTTPS
    HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
    
    # Request Validation
    REQUEST_VALIDATION_ENABLED = os.getenv("REQUEST_VALIDATION_ENABLED", "true").lower() == "true"
    MAX_REQUEST_SIZE_MB = int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))
    
    # IP Whitelist (comma-separated)
    IP_WHITELIST = os.getenv("IP_WHITELIST", "127.0.0.1,::1").split(",")
    
    # Blocked IPs (comma-separated)
    IP_BLACKLIST = os.getenv("IP_BLACKLIST", "").split(",") if os.getenv("IP_BLACKLIST") else []
    
    # File Upload Security
    ALLOWED_FILE_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'medical': ['.dcm', '.dicom'],  # DICOM medical images
    }
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    # Database Security
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # Encryption
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")  # For encrypting sensitive data
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all security configuration as dictionary"""
        return {
            "environment": cls.ENVIRONMENT,
            "is_production": cls.IS_PRODUCTION,
            "rate_limiting": {
                "enabled": cls.RATE_LIMIT_ENABLED,
                "per_minute": cls.RATE_LIMIT_PER_MINUTE,
            },
            "session": {
                "timeout_minutes": cls.SESSION_TIMEOUT_MINUTES,
                "refresh_threshold_minutes": cls.SESSION_REFRESH_THRESHOLD_MINUTES,
            },
            "jwt": {
                "algorithm": cls.JWT_ALGORITHM,
                "access_token_expire_minutes": cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_expire_days": cls.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
            },
            "password_policy": {
                "min_length": cls.PASSWORD_MIN_LENGTH,
                "require_uppercase": cls.PASSWORD_REQUIRE_UPPERCASE,
                "require_lowercase": cls.PASSWORD_REQUIRE_LOWERCASE,
                "require_digit": cls.PASSWORD_REQUIRE_DIGIT,
                "require_special": cls.PASSWORD_REQUIRE_SPECIAL,
            },
            "audit_logging": {
                "enabled": cls.AUDIT_LOG_ENABLED,
                "to_database": cls.AUDIT_LOG_TO_DATABASE,
            },
            "security_headers": {
                "enabled": cls.SECURITY_HEADERS_ENABLED,
                "hsts_enabled": cls.HSTS_ENABLED,
            },
            "request_validation": {
                "enabled": cls.REQUEST_VALIDATION_ENABLED,
                "max_size_mb": cls.MAX_REQUEST_SIZE_MB,
            },
            "file_upload": {
                "max_size_mb": cls.MAX_FILE_SIZE_MB,
                "allowed_extensions": cls.ALLOWED_FILE_EXTENSIONS,
            },
        }
    
    @classmethod
    def validate_config(cls):
        """Validate security configuration"""
        warnings = []
        errors = []
        
        # Check production settings
        if cls.IS_PRODUCTION:
            if cls.JWT_SECRET_KEY == "your-secret-key-change-in-production":
                errors.append("JWT_SECRET_KEY must be changed in production!")
            
            if not cls.ENCRYPTION_KEY:
                warnings.append("ENCRYPTION_KEY not set - sensitive data won't be encrypted")
            
            if not cls.HSTS_ENABLED:
                warnings.append("HSTS should be enabled in production")
        
        # Check password policy
        if cls.PASSWORD_MIN_LENGTH < 8:
            warnings.append("PASSWORD_MIN_LENGTH should be at least 8")
        
        # Print validation results
        if errors:
            print("❌ SECURITY CONFIGURATION ERRORS:")
            for error in errors:
                print(f"  - {error}")
            raise ValueError("Invalid security configuration")
        
        if warnings:
            print("⚠️  SECURITY CONFIGURATION WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        print("✅ Security configuration validated")
    
    @classmethod
    def print_config(cls):
        """Print security configuration (for debugging)"""
        print("\n" + "=" * 60)
        print("🔒 SECURITY CONFIGURATION")
        print("=" * 60)
        
        config = cls.get_config()
        
        for section, settings in config.items():
            print(f"\n{section.upper()}:")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    # Hide sensitive values
                    if 'key' in key.lower() or 'secret' in key.lower():
                        value = "***HIDDEN***"
                    print(f"  {key}: {value}")
            else:
                print(f"  {settings}")
        
        print("\n" + "=" * 60)


# Validate configuration on import
if __name__ != "__main__":
    try:
        SecurityConfig.validate_config()
    except ValueError as e:
        print(f"Security configuration error: {e}")
        if SecurityConfig.IS_PRODUCTION:
            raise
