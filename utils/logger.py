"""Logging configuration and utilities."""
import sys
from pathlib import Path
from loguru import logger
from config.settings import LOG_LEVEL, LOGS_DIR


def setup_logger():
    """Configure logger for the application."""
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # File handler - general log
    logger.add(
        LOGS_DIR / "capivara_bet.log",
        level=LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )
    
    # File handler - errors only
    logger.add(
        LOGS_DIR / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
    )
    
    return logger


# Initialize logger
log = setup_logger()
