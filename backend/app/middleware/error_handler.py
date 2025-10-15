"""
Error handling middleware for the Customer Bot application.
Provides centralized error handling and logging.
"""

import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions import CustomerBotException, to_http_exception
from app.utils.logger import Logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and logging requests."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = Logger().get_logger("middleware")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            process_time = time.time() - start_time
            self.logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time": process_time,
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            return response
            
        except CustomerBotException as e:
            # Handle custom application exceptions
            self.logger.error(
                f"CustomerBotException: {e.error_code} - {e.message}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error_code": e.error_code,
                    "details": e.details
                }
            )
            
            http_exception = to_http_exception(e)
            return JSONResponse(
                status_code=http_exception.status_code,
                content=http_exception.detail
            )
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            self.logger.warning(
                f"HTTP Exception: {e.status_code} - {e.detail}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": e.status_code
                }
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "HTTP_ERROR", "message": e.detail}
            )
            
        except Exception as e:
            # Handle unexpected exceptions
            process_time = time.time() - start_time
            self.logger.error(
                f"Unexpected error: {str(e)}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "response_time": process_time
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later."
                }
            )


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring performance metrics."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = Logger().get_logger("performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log performance metrics for slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            self.logger.info(
                f"Slow request: {request.method} {request.url.path} - {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time": process_time
                }
            )
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

