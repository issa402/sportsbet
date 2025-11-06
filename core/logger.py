"""
Logging configuration for the application.
Provides structured logging with file and console output.
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("sports_betting")
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "sports_betting.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logging()

