"""
CORS Configuration - Production-ready Cross-Origin Resource Sharing setup
"""
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os


class CORSConfig:
    """
    CORS configuration for different environments
    """
    
    @staticmethod
    def get_allowed_origins() -> List[str]:
        """
        Get allowed origins based on environment
        In production, restrict to specific domains
        """
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            # Production - restrict to specific domains
            return [
                "https://hospital.example.com",
                "https://www.hospital.example.com",
                "https://admin.hospital.example.com",
                # Add your production domains here
            ]
        
        elif env == "staging":
            # Staging - allow staging domains
            return [
                "https://staging.hospital.example.com",
                "http://localhost:3000",
                "http://localhost:5173",  # Vite dev server
            ]
        
        else:
            # Development - allow local development
            return [
                "http://localhost:3000",
                "http://localhost:5173",  # Vite
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8080",
            ]
    
    @staticmethod
    def get_cors_config() -> dict:
        """
        Get complete CORS configuration
        """
        env = os.getenv("ENVIRONMENT", "development")
        
        return {
            "allow_origins": CORSConfig.get_allowed_origins(),
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "Accept",
                "Origin",
                "User-Agent",
                "DNT",
                "Cache-Control",
                "X-Requested-With",
                "X-CSRF-Token",
            ],
            "expose_headers": [
                "Content-Length",
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset",
            ],
            "max_age": 600 if env == "production" else 3600,  # Preflight cache time
        }
    
    @staticmethod
    def apply_cors(app) -> None:
        """
        Apply CORS middleware to FastAPI app
        """
        config = CORSConfig.get_cors_config()
        
        app.add_middleware(
            CORSMiddleware,
            **config
        )
        
        print(f"[CORS] Configured for environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"[CORS] Allowed origins: {len(config['allow_origins'])} domains")


# Additional CORS utilities

def is_origin_allowed(origin: str) -> bool:
    """Check if origin is allowed"""
    allowed = CORSConfig.get_allowed_origins()
    return origin in allowed


def get_cors_headers(origin: str = None) -> dict:
    """Get CORS headers for manual responses"""
    headers = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
        "Access-Control-Max-Age": "3600",
    }
    
    if origin and is_origin_allowed(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    
    return headers
