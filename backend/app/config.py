"""
Configuration management for Healthcare Queue Management System
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # ==========================================
    # SECURITY SETTINGS
    # ==========================================
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY",
        description="JWT secret key - CHANGE IN PRODUCTION"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="JWT token expiration time in minutes"
    )

    # ==========================================
    # DATABASE SETTINGS
    # ==========================================
    database_url: str = Field(
        default="sqlite:///./queue_management.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )

    # ==========================================
    # AI & ML SETTINGS
    # ==========================================
    openrouter_api_key: Optional[str] = Field(
        default=None,
        env="OPENROUTER_API_KEY",
        description="OpenRouter API key for AI services"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL",
        description="OpenRouter API base URL"
    )
    local_ai_model_path: str = Field(
        default="./models",
        env="LOCAL_AI_MODEL_PATH",
        description="Path to local AI models"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_BASE_URL",
        description="Ollama API base URL"
    )
    ai_cache_ttl_minutes: int = Field(
        default=60,
        env="AI_CACHE_TTL_MINUTES",
        description="AI response cache TTL in minutes"
    )
    ai_cache_max_size_mb: int = Field(
        default=100,
        env="AI_CACHE_MAX_SIZE_MB",
        description="Maximum AI cache size in MB"
    )

    # ==========================================
    # SMS & COMMUNICATION SETTINGS
    # ==========================================
    infobip_api_key: Optional[str] = Field(
        default=None,
        env="INFOBIP_API_KEY",
        description="Infobip SMS API key"
    )
    infobip_base_url: str = Field(
        default="https://api.infobip.com",
        env="INFOBIP_BASE_URL",
        description="Infobip API base URL"
    )
    infobip_sender_id: str = Field(
        default="HospitalAlert",
        env="INFOBIP_SENDER_ID",
        description="SMS sender ID"
    )

    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================
    env: str = Field(
        default="development",
        env="ENV",
        description="Environment (development/production)"
    )
    debug: bool = Field(
        default=True,
        env="DEBUG",
        description="Enable debug mode"
    )
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        env="PORT",
        description="Server port"
    )

    # ==========================================
    # CORS SETTINGS
    # ==========================================
    allowed_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        env="ALLOWED_ORIGINS",
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        env="CORS_ALLOW_CREDENTIALS",
        description="Allow CORS credentials"
    )

    # ==========================================
    # MONITORING & LOGGING
    # ==========================================
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    sentry_dsn: Optional[str] = Field(
        default=None,
        env="SENTRY_DSN",
        description="Sentry DSN for error tracking"
    )

    # ==========================================
    # QUEUE MANAGEMENT SETTINGS
    # ==========================================
    urgent_priority_weight: int = Field(
        default=10,
        env="URGENT_PRIORITY_WEIGHT",
        description="Priority weight for urgent cases"
    )
    high_priority_weight: int = Field(
        default=5,
        env="HIGH_PRIORITY_WEIGHT",
        description="Priority weight for high priority cases"
    )
    normal_priority_weight: int = Field(
        default=2,
        env="NORMAL_PRIORITY_WEIGHT",
        description="Priority weight for normal cases"
    )
    low_priority_weight: int = Field(
        default=1,
        env="LOW_PRIORITY_WEIGHT",
        description="Priority weight for low priority cases"
    )
    max_queue_size: int = Field(
        default=100,
        env="MAX_QUEUE_SIZE",
        description="Maximum queue size per service"
    )
    auto_call_delay_seconds: int = Field(
        default=30,
        env="AUTO_CALL_DELAY_SECONDS",
        description="Auto-call next patient delay"
    )

    # ==========================================
    # EMERGENCY SETTINGS
    # ==========================================
    emergency_response_timeout_minutes: int = Field(
        default=15,
        env="EMERGENCY_RESPONSE_TIMEOUT_MINUTES",
        description="Emergency response timeout"
    )
    ambulance_dispatch_timeout_minutes: int = Field(
        default=10,
        env="AMBULANCE_DISPATCH_TIMEOUT_MINUTES",
        description="Ambulance dispatch timeout"
    )

    # ==========================================
    # FILE UPLOAD SETTINGS
    # ==========================================
    max_upload_size_mb: int = Field(
        default=10,
        env="MAX_UPLOAD_SIZE_MB",
        description="Maximum upload file size in MB"
    )
    allowed_extensions: List[str] = Field(
        default=[".csv", ".xlsx", ".json"],
        env="ALLOWED_EXTENSIONS",
        description="Allowed file extensions"
    )
    upload_dir: str = Field(
        default="./uploads",
        env="UPLOAD_DIR",
        description="Upload directory path"
    )

    # ==========================================
    # CACHE SETTINGS
    # ==========================================
    redis_url: Optional[str] = Field(
        default=None,
        env="REDIS_URL",
        description="Redis connection URL"
    )
    redis_cache_ttl_seconds: int = Field(
        default=3600,
        env="REDIS_CACHE_TTL_SECONDS",
        description="Redis cache TTL"
    )

    # ==========================================
    # DEVELOPMENT SETTINGS
    # ==========================================
    enable_swagger_ui: bool = Field(
        default=True,
        env="ENABLE_SWAGGER_UI",
        description="Enable Swagger UI"
    )
    enable_debug_mode: bool = Field(
        default=True,
        env="ENABLE_DEBUG_MODE",
        description="Enable debug mode features"
    )

    # ==========================================
    # ANALYTICS SETTINGS
    # ==========================================
    analytics_retention_days: int = Field(
        default=365,
        env="ANALYTICS_RETENTION_DAYS",
        description="Analytics data retention period"
    )
    performance_monitor_interval: int = Field(
        default=60,
        env="PERFORMANCE_MONITOR_INTERVAL",
        description="Performance monitoring interval"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.env.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.env.lower() == "development"