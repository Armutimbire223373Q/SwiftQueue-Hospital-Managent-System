"""
Monitoring and metrics for Healthcare Queue Management System
"""
import time
import psutil
from typing import Dict, Any, Optional
from functools import wraps
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and expose application metrics."""

    def __init__(self):
        self._metrics = {
            "requests_total": 0,
            "requests_duration": 0.0,
            "errors_total": 0,
            "active_connections": 0,
            "queue_operations": 0,
            "ai_requests": 0,
            "emergency_dispatches": 0,
        }
        self._start_time = time.time()

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        if name in self._metrics:
            self._metrics[name] += value

    def record_duration(self, name: str, duration: float) -> None:
        """Record a duration metric."""
        if name in self._metrics:
            self._metrics[name] += duration

    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        # Add system metrics
        system_metrics = self._get_system_metrics()

        return {
            **self._metrics,
            **system_metrics,
            "uptime_seconds": time.time() - self._start_time,
        }

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            }
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            return {}


# Global metrics collector
metrics = MetricsCollector()


def monitor_request(func):
    """Decorator to monitor FastAPI endpoint requests."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            # Extract request from args if it's a FastAPI endpoint
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Increment request counter
            metrics.increment_counter("requests_total")

            # Call the original function
            result = await func(*args, **kwargs)

            # Record duration
            duration = time.time() - start_time
            metrics.record_duration("requests_duration", duration)

            # Log slow requests
            if duration > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow request: {request.url.path if request else 'unknown'} "
                    ".2f"
                )

            return result

        except Exception as e:
            # Increment error counter
            metrics.increment_counter("errors_total")
            logger.error(f"Request error: {e}")
            raise

    return wrapper


def monitor_queue_operation(operation_type: str):
    """Decorator to monitor queue operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Record successful operation
                metrics.increment_counter("queue_operations")
                duration = time.time() - start_time

                logger.info(
                    f"Queue operation '{operation_type}' completed in {duration:.3f}s"
                )

                return result

            except Exception as e:
                logger.error(f"Queue operation '{operation_type}' failed: {e}")
                raise

        return wrapper
    return decorator


def monitor_ai_request(model_type: str = "unknown"):
    """Decorator to monitor AI service requests."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Record successful AI request
                metrics.increment_counter("ai_requests")
                duration = time.time() - start_time

                logger.info(
                    f"AI request ({model_type}) completed in {duration:.3f}s"
                )

                return result

            except Exception as e:
                logger.error(f"AI request ({model_type}) failed: {e}")
                raise

        return wrapper
    return decorator


def monitor_emergency_dispatch(func):
    """Decorator to monitor emergency dispatches."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # Record successful dispatch
            metrics.increment_counter("emergency_dispatches")
            duration = time.time() - start_time

            logger.info(
                f"Emergency dispatch completed in {duration:.3f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Emergency dispatch failed: {e}")
            raise

    return wrapper


async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    try:
        # Basic health check
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "environment": settings.env,
        }

        # Add metrics
        health_data.update(metrics.get_metrics())

        # Check critical services
        services_status = await _check_services_health()
        health_data["services"] = services_status

        # Determine overall health
        if any(not service["healthy"] for service in services_status.values()):
            health_data["status"] = "degraded"
        elif health_data["errors_total"] > 100:  # High error rate
            health_data["status"] = "warning"

        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time(),
        }


async def _check_services_health() -> Dict[str, Dict[str, Any]]:
    """Check health of critical services."""
    services = {}

    # Database health check
    try:
        from app.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        services["database"] = {"healthy": True, "response_time": 0.001}
    except Exception as e:
        services["database"] = {"healthy": False, "error": str(e)}

    # Redis health check (if configured)
    if settings.redis_url:
        try:
            import redis
            r = redis.from_url(settings.redis_url)
            r.ping()
            services["redis"] = {"healthy": True, "response_time": 0.001}
        except Exception as e:
            services["redis"] = {"healthy": False, "error": str(e)}
    else:
        services["redis"] = {"healthy": True, "status": "not_configured"}

    # AI services health check
    try:
        from app.services.openrouter_service import OpenRouterService
        ai_service = OpenRouterService()
        # Simple health check - just verify service is initialized
        services["ai_service"] = {"healthy": True, "status": "initialized"}
    except Exception as e:
        services["ai_service"] = {"healthy": False, "error": str(e)}

    return services


async def metrics_endpoint() -> JSONResponse:
    """Prometheus-compatible metrics endpoint."""
    metrics_data = metrics.get_metrics()

    # Format for Prometheus
    prometheus_output = "# Healthcare Queue Management System Metrics\n"

    for key, value in metrics_data.items():
        if isinstance(value, (int, float)):
            prometheus_output += f"swiftqueue_{key} {value}\n"

    return JSONResponse(
        content={"metrics": prometheus_output},
        media_type="text/plain"
    )


# Middleware for request monitoring
async def monitoring_middleware(request: Request, call_next):
    """Middleware to monitor all requests."""
    start_time = time.time()

    # Increment active connections
    metrics.increment_counter("active_connections", 1)

    try:
        response = await call_next(request)

        # Record request metrics
        duration = time.time() - start_time
        metrics.record_duration("requests_duration", duration)
        metrics.increment_counter("requests_total")

        # Log slow requests
        if duration > 2.0:  # More than 2 seconds
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                ".2f"
            )

        return response

    except Exception as e:
        metrics.increment_counter("errors_total")
        raise
    finally:
        # Decrement active connections
        metrics.increment_counter("active_connections", -1)