from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import queue, users, services, analytics, auth
from app.database import create_tables
from app import ws

app = FastAPI(title="Queue Management System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
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
app.include_router(ws.router)  # WebSocket router

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Queue Management System API"}
