"""
src/core/logging.py

Configures project-wide logging for FastAPI application.
Supports console output, proper log formatting, and log level configuration.
"""

import logging
import sys


def setup_logging(level: str = "INFO"):
    """
    Set up global logging configuration.

    Args:
        level (str): Logging level ("DEBUG", "INFO", "WARNING", etc.)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Optional: silence overly verbose loggers (like uvicorn.access)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
