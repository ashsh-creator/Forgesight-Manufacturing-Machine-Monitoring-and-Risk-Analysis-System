"""
Centralized logging configuration for the Manufacturing Predictive Maintenance application.
"""
import logging
import sys
from datetime import datetime
import os

def setup_logging(log_level=logging.INFO, log_dir=None):
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (default: from LOG_LEVEL env var or INFO)
        log_dir: Optional log directory path (default: from LOG_DIR env var or None)
    """
    # Get configuration from environment variables
    if log_level is None:
        log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
    
   
    if log_dir is None:
        log_dir = os.environ.get('LOG_DIR')
        # Set default log file based on environment
        if not log_dir and is_docker_environment():
            log_dir = 'logs'
        elif not log_dir:
            log_dir = 'logs'
    
    log_file = log_dir + "/manufacturing_ai_" + datetime.now().strftime('%Y%m%d') + ".log"
    
    print(f"Setting up logging with log_level: {log_level} and log_file: {log_file}")    
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        print(f"Logs directory created: {os.path.dirname(log_file)}")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def is_docker_environment():
    """
    Check if the application is running in a Docker container.
    
    Returns:
        bool: True if running in Docker, False otherwise
    """
    return (
        os.path.exists("/.dockerenv") or
        os.environ.get("DOCKER_CONTAINER") == "true" or
        os.path.exists("/app")
    )

# Initialize logging on import with environment variables
setup_logging()
