"""
Centralized logging configuration for the trading bot.

Provides structured logging with both file and console output.
Supports different log levels and formats.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

from scalping_bot.config.settings import Settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TradingLogger:
    """Centralized logger for trading bot."""

    _instance: Optional["TradingLogger"] = None
    _loggers: dict = {}

    def __new__(cls) -> "TradingLogger":
        if cls._instance is None:
            cls._instance = super(TradingLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger."""
        if not hasattr(self, "_initialized"):
            self._setup_logging()
            self._initialized = True

    @staticmethod
    def _setup_logging() -> None:
        """Setup logging configuration."""
        settings = Settings()

        # Create logs directory
        log_dir = Path(settings.logging.file.path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.logging.level))

        # Remove existing handlers
        root_logger.handlers.clear()

        # File handler with rotation
        if settings.logging.file.enabled:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=settings.logging.file.path,
                maxBytes=settings.logging.file.max_size_bytes,
                backupCount=settings.logging.file.backup_count,
            )
            file_handler.setLevel(getattr(logging, settings.logging.level))

            # JSON formatter for file
            file_formatter = JSONFormatter()
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, settings.logging.level))

        # Standard formatter for console
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get logger instance for a module.

        Args:
            name: Logger name (typically __name__)

        Returns:
            Configured logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]


def setup_logging() -> None:
    """Initialize logging system."""
    TradingLogger()


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Trading bot started")
    """
    return TradingLogger.get_logger(name)
