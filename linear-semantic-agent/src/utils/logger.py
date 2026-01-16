"""
Structured logging configuration.
"""

import logging
import structlog
from typing import Any, Dict
from src.config.settings import settings


def configure_logging():
    """Configure structured logging for the application."""

    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.structured_logging:
        # Configure structlog for structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Standard logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Set level for root logger
    logging.getLogger().setLevel(log_level)


def get_logger(name: str):
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    if settings.structured_logging:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to a class."""

    @property
    def logger(self):
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger

    def log_event(self, event: str, **kwargs):
        """Log an event with structured data."""
        self.logger.info(event, **kwargs)

    def log_error(self, error: str, exc_info: Any = None, **kwargs):
        """Log an error with structured data."""
        self.logger.error(error, exc_info=exc_info, **kwargs)

    def log_decision(self, decision: str, confidence: float, **kwargs):
        """Log an agent decision."""
        self.logger.info(
            "agent_decision",
            decision=decision,
            confidence=confidence,
            **kwargs
        )


# Initialize logging on module import
configure_logging()
