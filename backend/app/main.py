from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import queue, users, services, analytics, auth, ai, appointments, notifications, checkin, scheduling, navigation, emergency, patient_history, uploads, payments, staff, admin, staff_communication
from app.database import create_tables
from app import ws
import os

app = FastAPI(title="Queue Management System API")

# Mount static files for the frontend (after API routes for precedence)
dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dist")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server default
        "http://localhost:5174",  # React dev server alternate
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(patient_history.router, prefix="/api/patient-history", tags=["patient-history"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(checkin.router, prefix="/api/checkin", tags=["checkin"])
app.include_router(scheduling.router, prefix="/api/scheduling", tags=["scheduling"])
app.include_router(navigation.router, prefix="/api/navigation", tags=["navigation"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(staff_communication.router, prefix="/api/staff-communication", tags=["staff-communication"])
app.include_router(ws.router)  # WebSocket router

# Mount static files for the frontend (after API routes for precedence)
app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

@app.on_event("startup")
async def startup_event():
    create_tables()
