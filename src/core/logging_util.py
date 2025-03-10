import os
import logging
from logging.handlers import RotatingFileHandler
import sys


def setup_logging():
    """Setup base logging configuration."""
    # Create logs directory in the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                os.path.join(logs_dir, "hardware_analyzer.log"),
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )


def get_logger(name, filename):
    """Get a logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, filename),
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)

    return logger
