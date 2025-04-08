import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from app.core.config import settings

# Color codes for terminal (reset-safe)
RESET = "\x1b[0m"
CYAN = "\x1b[36m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"

# Log format with colors for console
COLOR_FORMAT = (
    f"{CYAN}[%(asctime)s]{RESET} "
    f"{GREEN}[%(levelname)s]{RESET} "
    f"{YELLOW}[%(filename)s:%(funcName)s():%(lineno)d]{RESET} "
    "%(message)s"
)

# Plain format for file logs
PLAIN_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(funcName)s():%(lineno)d] %(message)s"
)

# Create logs directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "shrinkr.log")

# Daily Rotating File Handler
file_handler = TimedRotatingFileHandler(
    LOG_FILE_PATH, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.suffix = "%Y-%m-%d"

# Console Stream Handler
console_handler = logging.StreamHandler(sys.stdout)

# Formatters
console_formatter = logging.Formatter(COLOR_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
file_formatter = logging.Formatter(PLAIN_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# Set logging level from environment
log_level = logging.DEBUG if settings.environment == "development" else logging.INFO
console_handler.setLevel(log_level)
file_handler.setLevel(log_level)

# Configure logger
logger = logging.getLogger("shrinkr")
logger.setLevel(log_level)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False