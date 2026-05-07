# app/core/logger.py
# ─────────────────────────────────────────────────────────────────
# Centralized structured logging for the ClimaSync agent.
# ─────────────────────────────────────────────────────────────────

import logging
import sys
from app.core.config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.
    Usage: logger = setup_logger(__name__)
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if the logger already has them
    if logger.handlers:
        return logger

    # Set log level from application settings
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Configure stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Define log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger
