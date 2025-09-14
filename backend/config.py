"""
Configuration settings for the SwiftQueue Hospital application.
"""

import os
from typing import List

class Settings:
    # Environment
    ENV: str = os.getenv("ENV", "development").lower()
    IS_PRODUCTION: bool = ENV == "production"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    
    # Production Settings
    ALLOWED_HOSTS: List[str] = [
        host.strip() 
        for host in os.getenv("ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./queue_management.db")
    
    # AI Model Settings
    AI_MODEL_UPDATE_INTERVAL: int = int(os.getenv("AI_MODEL_UPDATE_INTERVAL", "3600"))
    AI_PREDICTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_PREDICTION_CONFIDENCE_THRESHOLD", "0.7"))
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    WS_MAX_CONNECTIONS: int = int(os.getenv("WS_MAX_CONNECTIONS", "100"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-here")
    
    # Email Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # SMS Settings
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

# Global settings instance
settings = Settings()
