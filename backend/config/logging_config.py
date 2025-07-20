import logging
import logging.handlers
import os
from typing import Optional
from .settings import get_settings

settings = get_settings()

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure logging for the application
    """
    
    # Use settings defaults if not provided
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    log_format = log_format or settings.log_format
    
    # Create logs directory if needed
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = None
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
    
    # Get root logger and add handlers
    logger = logging.getLogger()
    logger.handlers.clear()  # Clear any existing handlers
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)
    
    # Configure specific loggers
    
    # SQLAlchemy logging
    if settings.database_echo:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # HTTP client logging (for FHIR calls)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # FastAPI/Uvicorn logging
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    
    # DiagnoAssist specific loggers
    logging.getLogger('diagnoassist.ai').setLevel(logging.INFO)
    logging.getLogger('diagnoassist.fhir').setLevel(logging.INFO)
    logging.getLogger('diagnoassist.api').setLevel(logging.INFO)
    
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")