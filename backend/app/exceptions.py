"""
Custom exceptions for the Customer Bot application.
Provides structured error handling with proper HTTP status codes.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class CustomerBotException(Exception):
    """Base exception for Customer Bot application."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "CUSTOMER_BOT_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class LLMServiceException(CustomerBotException):
    """Exception raised when LLM service fails."""
    
    def __init__(self, message: str, model: str = None, details: Dict[str, Any] = None):
        self.model = model
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details={"model": model, **(details or {})}
        )


class VectorStoreException(CustomerBotException):
    """Exception raised when vector store operations fail."""
    
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        self.operation = operation
        super().__init__(
            message=message,
            error_code="VECTOR_STORE_ERROR",
            details={"operation": operation, **(details or {})}
        )


class EmbeddingException(CustomerBotException):
    """Exception raised when embedding operations fail."""
    
    def __init__(self, message: str, model: str = None, details: Dict[str, Any] = None):
        self.model = model
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            details={"model": model, **(details or {})}
        )


class SessionException(CustomerBotException):
    """Exception raised when session operations fail."""
    
    def __init__(self, message: str, session_id: str = None, details: Dict[str, Any] = None):
        self.session_id = session_id
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            details={"session_id": session_id, **(details or {})}
        )


class ConfigurationException(CustomerBotException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        self.config_key = config_key
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key, **(details or {})}
        )


class ValidationException(CustomerBotException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        self.field = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, **(details or {})}
        )


# HTTP Exception mappings
def to_http_exception(exception: CustomerBotException) -> HTTPException:
    """Convert CustomerBotException to HTTPException with appropriate status code."""
    
    status_code_mapping = {
        "LLM_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "VECTOR_STORE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "EMBEDDING_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "SESSION_ERROR": status.HTTP_400_BAD_REQUEST,
        "CONFIGURATION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "CUSTOMER_BOT_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    status_code = status_code_mapping.get(exception.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exception.error_code,
            "message": exception.message,
            "details": exception.details
        }
    )

