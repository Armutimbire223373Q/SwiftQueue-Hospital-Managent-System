import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.routes import queue, users, services, analytics, ai
from app.database import create_tables
from app import ws

# Environment configuration
ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV == "production"

# Comma-separated list of allowed origins for CORS
# e.g., "http://localhost:5173,http://127.0.0.1:5173,https://app.example.com"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context.

    - Runs blocking DB table creation in a thread to avoid blocking the event loop.
    - Add teardown logic if/when needed.
    """
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, create_tables)
    except Exception as exc:
        # Replace with proper structured logging if available
        print(f"[startup] Database initialization failed: {exc}")
        raise
    yield
    # Teardown logic could go here


app = FastAPI(
    title="Queue Management System API",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    lifespan=lifespan,
)

# Compression middleware to reduce payload sizes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Production hardening: enforce trusted hosts and HTTPS
if IS_PROD:
    allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "").split(",")
    allowed_hosts = [h.strip() for h in allowed_hosts_env if h.strip()]
    if allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    app.add_middleware(HTTPSRedirectMiddleware)

# CORS configuration (environment-driven)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,  # cache preflight for 24h
)

# Include routers
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])  # AI features router
app.include_router(ws.router)  # WebSocket router


@app.get("/", tags=["health"])
async def root() -> dict:
    return {"message": "Queue Management System API"}
