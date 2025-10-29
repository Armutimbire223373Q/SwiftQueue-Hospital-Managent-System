from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import queue, users, services, analytics, auth, ai, appointments, notifications, checkin, scheduling, navigation, emergency, patient_history, uploads, payments, staff, admin, file_uploads, reports, websocket_enhanced, analytics_dashboard, prescriptions, inventory, patient_portal, enhanced_ai
# Temporarily disabled integration routes that reference missing models
# from app.routes import hl7_integration, fhir_integration, ehr_integration
from app.database import create_tables
from app import ws
import os

# Import security middleware
from app.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    AuditLogMiddleware
)
from app.middleware.cors_config import CORSConfig
from app.config.security_config import SecurityConfig
from app.services.session_service import SessionService

app = FastAPI(
    title="Queue Management System API",
    description="Hospital Queue Management System with AI-powered features",
    version="1.0.0"
)

# Mount static files for the frontend (after API routes for precedence)
dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dist")

# Configure CORS using centralized configuration
CORSConfig.apply_cors(app)

# Add security middleware (order matters - applied in reverse order)
# 1. Audit logging (outermost - logs everything)
if SecurityConfig.AUDIT_LOG_ENABLED:
    app.add_middleware(AuditLogMiddleware)

# 2. Request validation (check for malicious patterns)
if SecurityConfig.REQUEST_VALIDATION_ENABLED:
    app.add_middleware(RequestValidationMiddleware)

# 3. Security headers (add security headers to responses)
if SecurityConfig.SECURITY_HEADERS_ENABLED:
    app.add_middleware(SecurityHeadersMiddleware)

# 4. Rate limiting (innermost - closest to routes)
if SecurityConfig.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=SecurityConfig.RATE_LIMIT_PER_MINUTE
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(enhanced_ai.router, prefix="/api/enhanced-ai", tags=["enhanced-ai"])
app.include_router(patient_history.router, prefix="/api/patient-history", tags=["patient-history"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(file_uploads.router, prefix="/api/files", tags=["file-management"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(checkin.router, prefix="/api/checkin", tags=["checkin"])
app.include_router(scheduling.router, prefix="/api/scheduling", tags=["scheduling"])
app.include_router(navigation.router, prefix="/api/navigation", tags=["navigation"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(analytics_dashboard.router)  # Analytics Dashboard API

# New Feature Routes
app.include_router(prescriptions.router, prefix="/api", tags=["prescriptions"])
app.include_router(inventory.router, prefix="/api", tags=["inventory"])
app.include_router(patient_portal.router, prefix="/api", tags=["patient-portal"])

# Temporarily disabled integration routes that reference missing models
# app.include_router(hl7_integration.router, prefix="/api/hl7", tags=["hl7-integration"])
# app.include_router(fhir_integration.router, prefix="/api/fhir", tags=["fhir-integration"])
# app.include_router(ehr_integration.router, prefix="/api/ehr", tags=["ehr-integration"])
app.include_router(ws.router)  # WebSocket router (legacy)
app.include_router(websocket_enhanced.router)  # Enhanced WebSocket router

# Mount static files for the frontend (after API routes for precedence)
app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

@app.on_event("startup")
async def startup_event():
    """Application startup: initialize database and security"""
    # Validate critical environment variables
    import os
    required_vars = {
        "SECRET_KEY": "JWT secret key for authentication (generate with: openssl rand -hex 32)"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  ❌ {var}: {description}")
    
    if missing_vars:
        print("\n" + "=" * 70)
        print("🚨 CRITICAL: Missing Required Environment Variables")
        print("=" * 70)
        for msg in missing_vars:
            print(msg)
        print("\n💡 Create a .env file based on .env.example and set these variables")
        print("=" * 70 + "\n")
        raise ValueError("Required environment variables not set. See error above.")
    
    create_tables()
    
    # Print security configuration
    print("\n" + "=" * 60)
    print("🚀 Starting Hospital Queue Management System")
    print("=" * 60)
    
    SecurityConfig.print_config()
    
    # Print active routes
    print("\n📍 REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            print(f"  {methods:20} {route.path}")
    
    print("\n✅ Application started successfully!\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: cleanup sessions"""
    print("\n🛑 Shutting down application...")
    
    # Get session stats before cleanup
    stats = SessionService.get_session_stats()
    print(f"📊 Active sessions: {stats['active_sessions']}")
    print(f"   - Patients: {stats['sessions_by_role']['patient']}")
    print(f"   - Staff: {stats['sessions_by_role']['staff']}")
    print(f"   - Admin: {stats['sessions_by_role']['admin']}")
    
    print("✅ Shutdown complete\n")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": SecurityConfig.ENVIRONMENT,
        "security": {
            "rate_limiting": SecurityConfig.RATE_LIMIT_ENABLED,
            "audit_logging": SecurityConfig.AUDIT_LOG_ENABLED,
            "request_validation": SecurityConfig.REQUEST_VALIDATION_ENABLED,
        }
    }

@app.get("/api/session/stats")
async def session_stats():
    """Get session statistics (admin only in production)"""
    return SessionService.get_session_stats()
