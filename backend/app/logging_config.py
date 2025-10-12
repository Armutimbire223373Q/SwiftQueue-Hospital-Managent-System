"""
Logging configuration for Healthcare Queue Management System
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from app.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Use settings if not provided
    if log_level is None:
        log_level = settings.log_level

    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / "swiftqueue.log")

    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    # Create error file handler (only ERROR and above)
    error_log_file = str(Path(log_file).parent / "swiftqueue_error.log")
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # Configure specific loggers
    _configure_specific_loggers()

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")


def _configure_specific_loggers() -> None:
    """Configure specific loggers for different components."""
    # SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

    # FastAPI logging
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

    # AI service logging
    logging.getLogger('app.services.openrouter_service').setLevel(logging.INFO)
    logging.getLogger('app.services.ollama_service').setLevel(logging.INFO)

    # Emergency service logging (more verbose)
    logging.getLogger('app.services.emergency_service').setLevel(logging.DEBUG)

    # Database logging
    logging.getLogger('app.database').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class HealthCheckFilter(logging.Filter):
    """Filter to exclude health check logs from access logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out health check requests."""
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            return '/health' not in message and '/docs' not in message
        return True


class SecurityFilter(logging.Filter):
    """Filter for security-related log entries."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Only allow security-related messages."""
        security_keywords = [
            'authentication', 'authorization', 'security',
            'login', 'logout', 'password', 'token',
            'unauthorized', 'forbidden', 'suspicious'
        ]

        if hasattr(record, 'getMessage'):
            message = record.getMessage().lower()
            return any(keyword in message for keyword in security_keywords)
        return False


def setup_security_logging() -> None:
    """Set up separate security logging."""
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)

    # Create security log file
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    security_file = str(log_dir / "security.log")

    # Security file handler
    security_handler = logging.handlers.RotatingFileHandler(
        filename=security_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )

    formatter = logging.Formatter(
        fmt='%(asctime)s - SECURITY - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    security_handler.setFormatter(formatter)
    security_handler.addFilter(SecurityFilter())

    security_logger.addHandler(security_handler)
    security_logger.propagate = False  # Don't propagate to root logger


# Initialize logging when module is imported
if settings.env.lower() == "production":
    setup_logging()
    setup_security_logging()