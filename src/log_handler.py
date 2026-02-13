import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = Path(LOG_DIR) / "console-output.log"


def init_logger():
    logger = logging.getLogger("bestbuy-notifier-logger")
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",  # rotate at midnight
        interval=1,  # each day
        backupCount=3,  # keep last 3 days
        utc=False  # local time
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
