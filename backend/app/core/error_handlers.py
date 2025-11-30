"""
Global Error Handlers
Centralized error handling and formatting for FastAPI with standardized error codes
"""
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
import logging

from app.core.exceptions import PsiException
from app.core.error_codes import ErrorCode, get_error_metadata

logger = logging.getLogger(__name__)


async def psi_exception_handler(request: Request, exc: PsiException) -> JSONResponse:
    """
    Handle custom Psi exceptions with standardized error codes

    Args:
        request: FastAPI request
        exc: PsiException instance

    Returns:
        JSONResponse with error details including error code
    """
    # Get error code metadata if available
    error_code_value = exc.details.get("error_code") if exc.details else None

    logger.warning(
        f"PsiException: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": error_code_value,
            "details": exc.details
        }
    )

    # Build error response with error code
    error_response = {
        "error": {
            "message": exc.message,
            "type": exc.__class__.__name__,
            "code": error_code_value,  # Standardized error code (e.g., "PSI-RES-3012")
            "details": exc.details
        }
    }

    # Add user-friendly message if error code has metadata
    if exc.error_code:
        metadata = get_error_metadata(exc.error_code)
        user_message = metadata.get("user_message")
        if user_message:
            error_response["error"]["user_message"] = user_message

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSONResponse with validation error details
    """
    errors = []

    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
    else:
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed",
                "type": "ValidationError",
                "code": ErrorCode.VAL_INVALID_INPUT.value,  # Standardized error code
                "user_message": "The data you provided is invalid. Please check the highlighted fields.",
                "details": {
                    "errors": errors
                }
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions

    Args:
        request: FastAPI request
        exc: Any unhandled exception

    Returns:
        JSONResponse with generic error message
    """
    # Log the full exception with traceback
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__
        }
    )

    # Don't expose internal error details to clients
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An internal error occurred. Please try again later.",
                "type": "InternalServerError",
                "code": ErrorCode.SVC_INTERNAL_ERROR.value,  # Standardized error code
                "user_message": "Something went wrong on our end. We've been notified and are working on it!",
                "details": {
                    "request_id": None,  # TODO: Add request ID tracking
                    "retryable": True
                }
            }
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app

    Args:
        app: FastAPI application instance
    """
    # Custom Psi exceptions
    app.add_exception_handler(PsiException, psi_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)

    # Generic catch-all for unexpected errors
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Registered global exception handlers")
