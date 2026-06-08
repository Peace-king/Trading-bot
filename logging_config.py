"""
Logging configuration.
Sets up both a rotating file handler (trading_bot.log) and a coloured console handler.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path("trading_bot.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging(level: int = logging.DEBUG) -> None:
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(level)

    # File handler — keeps up to 5 × 1 MB files
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # Console handler — INFO and above only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    root.addHandler(file_handler)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
