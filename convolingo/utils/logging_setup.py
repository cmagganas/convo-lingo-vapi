import logging
import os
from pathlib import Path
from typing import Optional


def configure_logging(log_level: int = logging.INFO,
                     log_to_file: bool = False,
                     log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to a file
        log_file: Path to log file (default: convolingo.log in logs directory)
    """
    # Create formatter
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if requested
    if log_to_file:
        if not log_file:
            # Get the repository root
            repo_root = Path(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
            
            # Create logs directory if it doesn't exist
            logs_dir = repo_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Default log file
            log_file = str(logs_dir / "convolingo.log")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress overly verbose loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 