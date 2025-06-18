"""
Professional logging configuration for PME Calculator backend.
Replaces print statements with structured logging.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime

from .utils.time import UTC
from pathlib import Path


class UTCFormatter(logging.Formatter):
    """Custom formatter with UTC timestamps and module names."""

    def formatTime(self, record, datefmt=None):
        """Override to use UTC time."""
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

    def format(self, record):
        """Custom formatting with module names."""
        # Add module name for better debugging
        record.module = (
            record.name.split(".")[-1] if "." in record.name else record.name
        )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def formatTime(self, record, datefmt=None):
        """Override to use UTC time."""
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.isoformat()

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "file_name"):
            log_entry["file_name"] = record.file_name
        if hasattr(record, "analysis_type"):
            log_entry["analysis_type"] = record.analysis_type

        return json.dumps(log_entry)


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    enable_console: bool = True,
    enable_json: bool = False,
) -> logging.Logger:
    """
    Set up logging configuration for the PME Calculator.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to log to console
        enable_json: Whether to use JSON formatting

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger("pme_calculator")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = UTCFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with UTC timestamps and module names.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Configure basic logging with UTC timestamps
        handler = logging.StreamHandler(sys.stdout)
        formatter = UTCFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


# Create default logger instance
logger = setup_logging(
    log_level="INFO",
    log_file="logs/pme_calculator.log",
    enable_console=True,
    enable_json=False,
)


class PMELogger:
    """
    Specialized logger for PME Calculator operations.
    Provides context-aware logging methods.
    """

    def __init__(self, logger_instance: logging.Logger = None):
        self.logger = logger_instance or logger

    def info_file_operation(self, operation: str, file_path: str, details: str = ""):
        """Log file operation with context."""
        self.logger.info(
            f"File {operation}: {file_path} - {details}",
            extra={"file_name": file_path, "operation": operation},
        )

    def info_analysis_start(self, analysis_type: str, data_points: int):
        """Log analysis start with context."""
        self.logger.info(
            f"Starting {analysis_type} analysis with {data_points} data points",
            extra={"analysis_type": analysis_type, "data_points": data_points},
        )

    def info_analysis_complete(self, analysis_type: str, metrics: dict):
        """Log analysis completion with key metrics."""
        key_metrics = {
            "IRR": metrics.get("Fund IRR", "N/A"),
            "TVPI": metrics.get("TVPI", "N/A"),
            "DPI": metrics.get("DPI", "N/A"),
        }
        self.logger.info(
            f"Analysis complete: {analysis_type} - Key metrics: {key_metrics}",
            extra={"analysis_type": analysis_type, "metrics": key_metrics},
        )

    def warning_data_quality(self, issue: str, file_path: str = "", details: str = ""):
        """Log data quality warnings."""
        self.logger.warning(
            f"Data quality issue: {issue} - {details}",
            extra={"file_name": file_path, "data_quality_issue": issue},
        )

    def error_calculation(
        self, calculation_type: str, error: Exception, context: dict = None
    ):
        """Log calculation errors with context."""
        self.logger.error(
            f"Calculation error in {calculation_type}: {str(error)}",
            extra={
                "calculation_type": calculation_type,
                "error_type": type(error).__name__,
                "context": context or {},
            },
            exc_info=True,
        )

    def error_file_processing(self, file_path: str, error: Exception):
        """Log file processing errors."""
        self.logger.error(
            f"File processing error: {file_path} - {str(error)}",
            extra={"file_name": file_path, "error_type": type(error).__name__},
            exc_info=True,
        )

    def debug_performance(
        self, operation: str, duration_ms: float, details: dict = None
    ):
        """Log performance metrics."""
        self.logger.debug(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "performance_details": details or {},
            },
        )


# Create default PME logger instance
pme_logger = PMELogger(logger)


# Convenience functions for backward compatibility
def log_info(message: str, **kwargs):
    """Log info message."""
    logger.info(message, extra=kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message."""
    logger.warning(message, extra=kwargs)


def log_error(message: str, error: Exception = None, **kwargs):
    """Log error message."""
    if error:
        logger.error(message, extra=kwargs, exc_info=True)
    else:
        logger.error(message, extra=kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message."""
    logger.debug(message, extra=kwargs)


# Export main components
__all__ = [
    "setup_logging",
    "get_logger",
    "logger",
    "PMELogger",
    "pme_logger",
    "log_info",
    "log_warning",
    "log_error",
    "log_debug",
]
