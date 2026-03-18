"""
Logging utilities for BrookStream.Ai
Provides centralized logging configuration and utilities.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from config import config


class BrookStreamLogger:
    """Centralized logging configuration for BrookStream.Ai."""
    
    def __init__(self):
        self.log_dir = config.LOG_DIR
        self.log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for general logs
        log_file = self.log_dir / 'brookstream.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = self.log_dir / 'errors.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=5*1024*1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Security log handler
        security_log_file = self.log_dir / 'security.log'
        security_handler = logging.handlers.RotatingFileHandler(
            security_log_file, maxBytes=5*1024*1024, backupCount=3
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(detailed_formatter)
        
        # Create security logger
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.propagate = False
        
        # ML model performance logger
        ml_log_file = self.log_dir / 'ml_performance.log'
        ml_handler = logging.handlers.RotatingFileHandler(
            ml_log_file, maxBytes=5*1024*1024, backupCount=3
        )
        ml_handler.setLevel(logging.INFO)
        ml_handler.setFormatter(detailed_formatter)
        
        # Create ML logger
        ml_logger = logging.getLogger('ml_performance')
        ml_logger.addHandler(ml_handler)
        ml_logger.propagate = False
        
        # API request logger
        api_log_file = self.log_dir / 'api_requests.log'
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(detailed_formatter)
        
        # Create API logger
        api_logger = logging.getLogger('api_requests')
        api_logger.addHandler(api_handler)
        api_logger.propagate = False
        
        print(f"Logging configured. Log directory: {self.log_dir}")
    
    @staticmethod
    def log_api_request(logger: logging.Logger, method: str, endpoint: str, 
                       user: Optional[str] = None, status_code: int = 200, 
                       response_time: float = 0, error: Optional[str] = None):
        """Log API request details."""
        message = f"{method} {endpoint}"
        if user:
            message += f" - User: {user}"
        message += f" - Status: {status_code} - Time: {response_time:.3f}s"
        if error:
            message += f" - Error: {error}"
        
        if status_code >= 400:
            logger.error(message)
        else:
            logger.info(message)
    
    @staticmethod
    def log_ml_performance(logger: logging.Logger, model_name: str, accuracy: float,
                          metrics: dict, dataset_size: int, training_time: float = 0):
        """Log ML model performance metrics."""
        message = (f"Model: {model_name} - Accuracy: {accuracy:.4f} - "
                  f"Dataset: {dataset_size} - Training Time: {training_time:.2f}s")
        
        # Add additional metrics
        for key, value in metrics.items():
            if key != 'accuracy':
                message += f" - {key}: {value}"
        
        logger.info(message)
    
    @staticmethod
    def log_security_event(logger: logging.Logger, event_type: str, user: Optional[str] = None,
                           ip_address: Optional[str] = None, details: Optional[str] = None):
        """Log security-related events."""
        message = f"SECURITY: {event_type}"
        if user:
            message += f" - User: {user}"
        if ip_address:
            message += f" - IP: {ip_address}"
        if details:
            message += f" - Details: {details}"
        
        logger.warning(message)
    
    @staticmethod
    def log_data_processing(logger: logging.Logger, operation: str, records_processed: int,
                           errors: int = 0, processing_time: float = 0):
        """Log data processing operations."""
        message = (f"Data Processing: {operation} - Records: {records_processed} - "
                  f"Errors: {errors} - Time: {processing_time:.2f}s")
        
        if errors > 0:
            logger.warning(message)
        else:
            logger.info(message)
    
    @staticmethod
    def log_alert_event(logger: logging.Logger, alert_type: str, dam_name: str,
                       severity: str, message: str, user: Optional[str] = None):
        """Log alert-related events."""
        log_message = (f"ALERT: {alert_type} - Dam: {dam_name} - "
                      f"Severity: {severity} - {message}")
        if user:
            log_message += f" - User: {user}"
        
        if severity in ['HIGH', 'CRITICAL']:
            logger.error(log_message)
        else:
            logger.warning(log_message)


# Initialize logging
logger_setup = BrookStreamLogger()

# Get specific loggers
api_logger = logging.getLogger('api_requests')
ml_logger = logging.getLogger('ml_performance')
security_logger = logging.getLogger('security')
main_logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """Log exception with context information."""
    message = f"Exception in {context}: {str(exception)}"
    logger.error(message, exc_info=True)


class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str, **kwargs):
        self.logger = logger
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        message = f"Performance: {self.operation} completed in {duration:.3f}s"
        
        if self.kwargs:
            message += f" - Parameters: {self.kwargs}"
        
        if exc_type:
            message += f" - FAILED: {exc_val}"
            self.logger.error(message)
        else:
            self.logger.info(message)


def log_function_call(logger: logging.Logger):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceLogger(logger, f"{func.__module__}.{func.__name__}"):
                return func(*args, **kwargs)
        return wrapper
    return decorator
