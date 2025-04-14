"""
Logging configuration for the TikTok scraper.
"""

import sys
from loguru import logger
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import LOG_LEVEL, LOG_FILE

# Configure logger
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