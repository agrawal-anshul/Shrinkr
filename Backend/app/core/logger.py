import logging
import sys
import os
from logging.handlers import RotatingFileHandler
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

# Configure logging
logger = logging.getLogger("shrinkr")
logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter(COLOR_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler
file_handler = RotatingFileHandler(
    LOG_FILE_PATH,
    maxBytes=1024 * 1024,  # 1MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter(PLAIN_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

logger.propagate = False