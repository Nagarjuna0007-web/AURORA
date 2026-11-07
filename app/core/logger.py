import logging
import sys
from pathlib import Path


# --------------------------------------------------
# Log Directory
# --------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "aurora.log"


# --------------------------------------------------
# Formatter
# --------------------------------------------------

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s"
)


# --------------------------------------------------
# Console Handler
# --------------------------------------------------

console_handler = logging.StreamHandler(sys.stdout)

console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)


# --------------------------------------------------
# File Handler
# --------------------------------------------------

file_handler = logging.FileHandler(
    LOG_FILE,
    encoding="utf-8"
)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


# --------------------------------------------------
# Aurora Logger
# --------------------------------------------------

logger = logging.getLogger("AURORA")

logger.setLevel(logging.DEBUG)

logger.handlers.clear()

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.propagate = False