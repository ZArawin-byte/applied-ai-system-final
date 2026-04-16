"""
Logging configuration for the Music Recommender AI system.
"""

import logging
import os
from datetime import datetime


def setup_logging() -> None:
    """Configure logging to both console and a log file."""
    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/recommender_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger(__name__).info("Logging initialized. Log file: %s", log_filename)
