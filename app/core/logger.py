import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logger(name: str = "fin-track-api"):
    """
    Configures a structured logger with:
    - File rotation (10 MB per file, max 5 backups)
    - Console output
    - JSON formatting in production
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Clear existing handlers
    logger.handlers.clear()

    # Formatting
    if settings.ENV == "prod":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", '
            '"function": "%(funcName)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s"
        )

    # File Handler (Rotating)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    file_handler = RotatingFileHandler(
        filename=logs_dir / "fin-track.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()