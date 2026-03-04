"""Logging configuration for IM Repeater."""

import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_level: str = "INFO", log_dir: str = "data/logs") -> None:
    """Setup logging with file rotation.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # File handler with rotation (daily, keep 7 days)
    file_handler = TimedRotatingFileHandler(
        filename=log_path / "im-repeater.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
