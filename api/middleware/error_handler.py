from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_error_handlers(app: FastAPI):
    """Setup error handlers for the FastAPI application"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions"""
        logger.warning(f"Starlette HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.warning(f"Validation error: {exc.errors()}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "validation_error",
                    "status_code": 422,
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors"""
        logger.error(f"Value error: {str(exc)}")
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "value_error",
                    "status_code": 400,
                    "message": str(exc),
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        """Handle key errors"""
        logger.error(f"Key error: {str(exc)}")
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "key_error",
                    "status_code": 400,
                    "message": f"Missing required field: {str(exc)}",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        """Handle file not found errors"""
        logger.error(f"File not found: {str(exc)}")
        
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "type": "file_not_found",
                    "status_code": 404,
                    "message": "Requested file not found",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle permission errors"""
        logger.error(f"Permission error: {str(exc)}")
        
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "type": "permission_error",
                    "status_code": 403,
                    "message": "Insufficient permissions",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(ConnectionError)
    async def connection_error_handler(request: Request, exc: ConnectionError):
        """Handle connection errors"""
        logger.error(f"Connection error: {str(exc)}")
        
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "type": "connection_error",
                    "status_code": 503,
                    "message": "Service temporarily unavailable",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        """Handle timeout errors"""
        logger.error(f"Timeout error: {str(exc)}")
        
        return JSONResponse(
            status_code=408,
            content={
                "error": {
                    "type": "timeout_error",
                    "status_code": 408,
                    "message": "Request timeout",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_server_error",
                    "status_code": 500,
                    "message": "An internal server error occurred",
                    "path": str(request.url),
                    "method": request.method
                }
            }
        )

class ErrorResponse:
    """Standardized error response class"""
    
    @staticmethod
    def create_error_response(
        error_type: str,
        status_code: int,
        message: str,
        details: Dict[str, Any] = None,
        path: str = None,
        method: str = None
    ) -> JSONResponse:
        """Create a standardized error response"""
        
        error_content = {
            "error": {
                "type": error_type,
                "status_code": status_code,
                "message": message
            }
        }
        
        if details:
            error_content["error"]["details"] = details
        
        if path:
            error_content["error"]["path"] = path
        
        if method:
            error_content["error"]["method"] = method
        
        return JSONResponse(
            status_code=status_code,
            content=error_content
        )
    
    @staticmethod
    def validation_error(errors: list, path: str = None, method: str = None) -> JSONResponse:
        """Create validation error response"""
        return ErrorResponse.create_error_response(
            error_type="validation_error",
            status_code=422,
            message="Request validation failed",
            details={"validation_errors": errors},
            path=path,
            method=method
        )
    
    @staticmethod
    def not_found(resource: str, path: str = None, method: str = None) -> JSONResponse:
        """Create not found error response"""
        return ErrorResponse.create_error_response(
            error_type="not_found",
            status_code=404,
            message=f"{resource} not found",
            path=path,
            method=method
        )
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized", path: str = None, method: str = None) -> JSONResponse:
        """Create unauthorized error response"""
        return ErrorResponse.create_error_response(
            error_type="unauthorized",
            status_code=401,
            message=message,
            path=path,
            method=method
        )
    
    @staticmethod
    def forbidden(message: str = "Forbidden", path: str = None, method: str = None) -> JSONResponse:
        """Create forbidden error response"""
        return ErrorResponse.create_error_response(
            error_type="forbidden",
            status_code=403,
            message=message,
            path=path,
            method=method
        )
    
    @staticmethod
    def rate_limit_exceeded(path: str = None, method: str = None) -> JSONResponse:
        """Create rate limit exceeded error response"""
        return ErrorResponse.create_error_response(
            error_type="rate_limit_exceeded",
            status_code=429,
            message="Rate limit exceeded",
            path=path,
            method=method
        )
    
    @staticmethod
    def service_unavailable(message: str = "Service temporarily unavailable", path: str = None, method: str = None) -> JSONResponse:
        """Create service unavailable error response"""
        return ErrorResponse.create_error_response(
            error_type="service_unavailable",
            status_code=503,
            message=message,
            path=path,
            method=method
        )
