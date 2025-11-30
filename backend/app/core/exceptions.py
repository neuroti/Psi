"""
Custom Exception Classes
Provides domain-specific exceptions for better error handling with standardized error codes
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.core.error_codes import ErrorCode, get_error_metadata, format_error_message


class PsiException(Exception):
    """Base exception for all Psi-specific errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

        # Add error code metadata if provided
        if error_code:
            metadata = get_error_metadata(error_code)
            self.details["error_code"] = error_code.value
            self.details["retryable"] = metadata.get("retryable", False)
            if "action" in metadata:
                self.details["action"] = metadata["action"]

        super().__init__(self.message)


class AuthenticationError(PsiException):
    """Raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            details=details
        )


class AuthorizationError(PsiException):
    """Raised when user lacks permission"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: ErrorCode = ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            details=details
        )


class ResourceNotFoundError(PsiException):
    """Raised when a resource is not found"""

    def __init__(
        self,
        resource: str,
        identifier: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} not found: {identifier}"
        error_details = details.copy() if details else {}
        error_details.update({"resource": resource, "identifier": identifier})

        # Map resource types to specific error codes
        if error_code is None:
            resource_code_map = {
                "Recipe": ErrorCode.RES_RECIPE_NOT_FOUND,
                "User": ErrorCode.RES_USER_NOT_FOUND,
                "Food": ErrorCode.RES_FOOD_ITEM_NOT_FOUND,
                "Emotion": ErrorCode.RES_EMOTION_RECORD_NOT_FOUND,
                "Ingredient": ErrorCode.RES_INGREDIENT_NOT_FOUND,
            }
            error_code = resource_code_map.get(resource, ErrorCode.RES_NOT_FOUND)

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            details=error_details
        )


class ValidationError(PsiException):
    """Raised when input validation fails"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.VAL_INVALID_INPUT,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details.copy() if details else {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code,
            details=error_details
        )


class RateLimitError(PsiException):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[str] = None,
        reset_at: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.RATE_LIMIT_EXCEEDED,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details.copy() if details else {}
        error_details.update({
            "limit": limit,
            "window": window,
            "reset_at": reset_at
        })

        # Use specific error code based on window
        if error_code == ErrorCode.RATE_LIMIT_EXCEEDED and window:
            if window == "day":
                error_code = ErrorCode.RATE_DAILY_LIMIT_EXCEEDED
            elif window == "hour":
                error_code = ErrorCode.RATE_HOURLY_LIMIT_EXCEEDED

        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code,
            details=error_details
        )


class ServiceUnavailableError(PsiException):
    """Raised when a service is temporarily unavailable"""

    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        retry_after: Optional[int] = None,
        error_code: ErrorCode = ErrorCode.SVC_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"{service} service is temporarily unavailable"
        error_details = details.copy() if details else {}
        error_details.update({
            "service": service,
            "retry_after": retry_after
        })
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code,
            details=error_details
        )


class InvalidInputError(PsiException):
    """Raised when input data is invalid"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.VAL_INVALID_INPUT,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details.copy() if details else {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=error_details
        )


class DatabaseError(PsiException):
    """Raised when database operation fails"""

    def __init__(
        self,
        operation: str,
        message: Optional[str] = None,
        original_error: Optional[Exception] = None,
        error_code: ErrorCode = ErrorCode.DB_QUERY_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"Database operation failed: {operation}"
        error_details = details.copy() if details else {}
        error_details.update({
            "operation": operation,
            "error": str(original_error) if original_error else None
        })
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code,
            details=error_details
        )


class ExternalServiceError(PsiException):
    """Raised when external service call fails"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        original_error: Optional[Exception] = None,
        error_code: ErrorCode = ErrorCode.EXT_SERVICE_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"External service error: {service_name}"
        error_details = details.copy() if details else {}
        error_details.update({
            "service": service_name,
            "error": str(original_error) if original_error else None
        })
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code,
            details=error_details
        )


class ImageProcessingError(PsiException):
    """Raised when image processing fails"""

    def __init__(
        self,
        message: str = "Image processing failed",
        reason: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.IMG_PROCESSING_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details.copy() if details else {}
        error_details["reason"] = reason
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=error_details
        )


class NutritionDataNotFoundError(PsiException):
    """Raised when nutrition data is not available"""

    def __init__(
        self,
        food_name: str,
        error_code: ErrorCode = ErrorCode.NUT_DATA_NOT_FOUND,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Nutrition data not found for: {food_name}"
        error_details = details.copy() if details else {}
        error_details["food"] = food_name
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            details=error_details
        )


class InsufficientDataError(PsiException):
    """Raised when insufficient data for analysis"""

    def __init__(
        self,
        required: str,
        message: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.VAL_INSUFFICIENT_DATA,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"Insufficient data: {required}"
        error_details = details.copy() if details else {}
        error_details["required"] = required
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=error_details
        )


def to_http_exception(exc: PsiException) -> HTTPException:
    """
    Convert PsiException to FastAPI HTTPException

    Args:
        exc: PsiException instance

    Returns:
        HTTPException with proper status code and detail
    """
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )
