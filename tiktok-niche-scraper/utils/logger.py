"""
Logging configuration for the TikTok scraper.
"""

import sys
from loguru import logger
import os
from pathlib import Path

# Import config only if not called during configuration
try:
    sys.path.append(str(Path(__file__).parent.parent))
    from config import LOG_LEVEL, LOG_FILE
except ImportError:
    # Default values if config is not available
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"

def configure_logging(level=None, log_file=None):
    """
    Configure the logger with the specified settings.
    
    Args:
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to the log file
    """
    # Use provided values or defaults
    log_level = level or LOG_LEVEL
    file_path = log_file or LOG_FILE
    
    # Remove existing handlers
    logger.remove()
    
    # Add console handler
    logger.add(sys.stderr, level=log_level)
    
    # Add file handler
    logger.add(
        os.path.join(Path(__file__).parent.parent, file_path),
        rotation="500 MB",
        retention="10 days",
        level=log_level
    )
    
    logger.info(f"Logging configured with level: {log_level}")

# Initial configuration with default values
logger.remove()  # Remove default handler
logger.add(sys.stderr, level=LOG_LEVEL)  # Add stderr handler with configured level
logger.add(
    os.path.join(Path(__file__).parent.parent, LOG_FILE),
    rotation="500 MB",
    retention="10 days",
    level=LOG_LEVEL
)

def get_logger():
    """Return configured logger instance."""
    return logger 