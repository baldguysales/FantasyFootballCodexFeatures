import logging
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseSettings


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_FILE: Optional[Path] = None
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "zip"

    class Config:
        env_prefix = "LOG_"


def setup_logging():
    """Configure logging for the application."""
    settings = LoggingSettings()
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        colorize=True,
    )
    
    # Add file handler if LOG_FILE is set
    if settings.LOG_FILE:
        settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(settings.LOG_FILE),
            level=settings.LOG_LEVEL,
            format=settings.LOG_FORMAT,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            compression=settings.LOG_COMPRESSION,
            enqueue=True,  # For async support
        )
    
    # Configure uvicorn logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    # Set log level for specific loggers
    for name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
    
    return logger


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect them to loguru."""
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where the logged message originated
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Initialize logger
logger = setup_logging()
