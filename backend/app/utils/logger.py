"""
Comprehensive logging configuration for the Customer Bot application.
Provides structured logging with different levels and formatters.
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path
import json
from app.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = record.session_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'response_time'):
            log_entry["response_time"] = record.response_time
        if hasattr(record, 'confidence_score'):
            log_entry["confidence_score"] = record.confidence_score
        
        return json.dumps(log_entry)


class Logger:
    """Centralized logger configuration."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup the main application logger."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger("customer_bot")
        self._logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Console handler with simple format
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # File handler with structured JSON format
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self._logger.addHandler(error_handler)
        
        # Performance log handler
        perf_handler = logging.FileHandler(log_dir / "performance.log")
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        self._logger.addHandler(perf_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        if name:
            return self._logger.getChild(name)
        return self._logger
    
    def log_chat_interaction(self, session_id: str, message: str, response: str, 
                           response_time: float, confidence_score: float, 
                           response_type: str, escalated: bool = False):
        """Log chat interactions with structured data."""
        logger = self.get_logger("chat")
        logger.info(
            "Chat interaction completed",
            extra={
                "session_id": session_id,
                "message_length": len(message),
                "response_length": len(response),
                "response_time": response_time,
                "confidence_score": confidence_score,
                "response_type": response_type,
                "escalated": escalated
            }
        )
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        perf_logger = logging.getLogger("customer_bot.performance")
        perf_logger.info(f"{operation}: {duration:.3f}s", extra=kwargs)
    
    def log_error(self, error: Exception, context: dict = None):
        """Log errors with context."""
        logger = self.get_logger("error")
        logger.error(
            f"Error occurred: {str(error)}",
            exc_info=True,
            extra=context or {}
        )



logger = Logger() 
app_logger= logger.get_logger("app")

