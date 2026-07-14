"""Structured logging configuration for CiteReady.

Every log entry is JSON-formatted with automatic trace_id injection,
timestamps, and log level — making the system fully auditable.
"""

import logging
import structlog
from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the entire application."""

    # Set the root logger level
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )

    # Configure structlog processors
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()
            if settings.LOG_LEVEL == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance bound with a module name.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        A bound structured logger.
    """
    return structlog.get_logger(name)
