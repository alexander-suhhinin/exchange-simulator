"""
Logging utilities for BingX Emulator
"""
import logging
import sys
from typing import Optional
from src.config.settings import settings

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Setup logger with consistent formatting

    Args:
        name: Logger name
        level: Log level (optional, uses settings default if not provided)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger