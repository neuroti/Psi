"""
Error Code System - Psi API
Standardized error codes for consistent API error handling

Error Code Format: PSI-{CATEGORY}-{NUMBER}
- PSI: Project identifier
- CATEGORY: Error category (3 letters)
- NUMBER: Unique 3-digit number within category

Example: PSI-AUTH-1001 (Authentication failed - invalid credentials)
"""
from enum import Enum
from typing import Dict, Optional


class ErrorCategory(str, Enum):
    """Error categories for organizing error codes"""
    AUTHENTICATION = "AUTH"  # Authentication errors (1000-1999)
    AUTHORIZATION = "AUTHZ"  # Authorization/Permission errors (1500-1599)
    VALIDATION = "VAL"       # Input validation errors (2000-2999)
    RESOURCE = "RES"         # Resource not found errors (3000-3999)
    RATE_LIMIT = "RATE"      # Rate limiting errors (4000-4999)
    SERVICE = "SVC"          # Service/Infrastructure errors (5000-5999)
    DATABASE = "DB"          # Database errors (6000-6999)
    IMAGE = "IMG"            # Image processing errors (7000-7999)
    EXTERNAL = "EXT"         # External service errors (8000-8999)
    NUTRITION = "NUT"        # Nutrition data errors (9000-9099)
    EMOTION = "EMO"          # Emotion analysis errors (9100-9199)
    RECIPE = "RCP"           # Recipe matching errors (9200-9299)


class ErrorCode(str, Enum):
    """
    Standardized error codes for Psi API

    Each error code includes:
    - Unique identifier
    - Human-readable description
    - Suggested HTTP status code
    - User-friendly message template
    """

    # ============================================================================
    # AUTHENTICATION ERRORS (1000-1499)
    # ============================================================================

    # Basic Authentication
    AUTH_MISSING_CREDENTIALS = "PSI-AUTH-1001"
    AUTH_INVALID_CREDENTIALS = "PSI-AUTH-1002"
    AUTH_TOKEN_MISSING = "PSI-AUTH-1003"
    AUTH_TOKEN_INVALID = "PSI-AUTH-1004"
    AUTH_TOKEN_EXPIRED = "PSI-AUTH-1005"
    AUTH_TOKEN_REVOKED = "PSI-AUTH-1006"

    # Account Status
    AUTH_ACCOUNT_LOCKED = "PSI-AUTH-1010"
    AUTH_ACCOUNT_DISABLED = "PSI-AUTH-1011"
    AUTH_ACCOUNT_NOT_VERIFIED = "PSI-AUTH-1012"
    AUTH_EMAIL_NOT_VERIFIED = "PSI-AUTH-1013"

    # Registration
    AUTH_USER_ALREADY_EXISTS = "PSI-AUTH-1020"
    AUTH_EMAIL_ALREADY_EXISTS = "PSI-AUTH-1021"
    AUTH_WEAK_PASSWORD = "PSI-AUTH-1022"
    AUTH_INVALID_EMAIL_FORMAT = "PSI-AUTH-1023"

    # Password Reset
    AUTH_RESET_TOKEN_INVALID = "PSI-AUTH-1030"
    AUTH_RESET_TOKEN_EXPIRED = "PSI-AUTH-1031"
    AUTH_PASSWORD_RESET_FAILED = "PSI-AUTH-1032"

    # Multi-Factor Authentication
    AUTH_MFA_REQUIRED = "PSI-AUTH-1040"
    AUTH_MFA_CODE_INVALID = "PSI-AUTH-1041"
    AUTH_MFA_CODE_EXPIRED = "PSI-AUTH-1042"
    AUTH_MFA_NOT_ENABLED = "PSI-AUTH-1043"

    # Session Management
    AUTH_SESSION_EXPIRED = "PSI-AUTH-1050"
    AUTH_SESSION_INVALID = "PSI-AUTH-1051"
    AUTH_CONCURRENT_SESSION_LIMIT = "PSI-AUTH-1052"

    # ============================================================================
    # AUTHORIZATION ERRORS (1500-1599)
    # ============================================================================

    AUTHZ_INSUFFICIENT_PERMISSIONS = "PSI-AUTHZ-1500"
    AUTHZ_FEATURE_NOT_AVAILABLE = "PSI-AUTHZ-1501"
    AUTHZ_SUBSCRIPTION_REQUIRED = "PSI-AUTHZ-1502"
    AUTHZ_PREMIUM_ONLY = "PSI-AUTHZ-1503"
    AUTHZ_ADMIN_ONLY = "PSI-AUTHZ-1504"
    AUTHZ_RESOURCE_ACCESS_DENIED = "PSI-AUTHZ-1505"

    # ============================================================================
    # VALIDATION ERRORS (2000-2999)
    # ============================================================================

    # General Validation
    VAL_INVALID_INPUT = "PSI-VAL-2001"
    VAL_MISSING_REQUIRED_FIELD = "PSI-VAL-2002"
    VAL_INVALID_FORMAT = "PSI-VAL-2003"
    VAL_OUT_OF_RANGE = "PSI-VAL-2004"
    VAL_INVALID_TYPE = "PSI-VAL-2005"

    # Wearable Data Validation
    VAL_HRV_OUT_OF_RANGE = "PSI-VAL-2010"
    VAL_HEART_RATE_OUT_OF_RANGE = "PSI-VAL-2011"
    VAL_COHERENCE_OUT_OF_RANGE = "PSI-VAL-2012"
    VAL_INVALID_BIOMETRIC_DATA = "PSI-VAL-2013"

    # File Validation
    VAL_FILE_TOO_LARGE = "PSI-VAL-2020"
    VAL_FILE_TYPE_NOT_SUPPORTED = "PSI-VAL-2021"
    VAL_FILE_CORRUPTED = "PSI-VAL-2022"
    VAL_IMAGE_DIMENSIONS_INVALID = "PSI-VAL-2023"
    VAL_TOO_MANY_FILES = "PSI-VAL-2024"

    # Query Parameter Validation
    VAL_INVALID_PAGE_NUMBER = "PSI-VAL-2030"
    VAL_INVALID_LIMIT = "PSI-VAL-2031"
    VAL_INVALID_DATE_RANGE = "PSI-VAL-2032"
    VAL_INVALID_SORT_FIELD = "PSI-VAL-2033"

    # Business Logic Validation
    VAL_INSUFFICIENT_DATA = "PSI-VAL-2040"
    VAL_CONFLICTING_PARAMETERS = "PSI-VAL-2041"
    VAL_INVALID_STATE_TRANSITION = "PSI-VAL-2042"

    # ============================================================================
    # RESOURCE ERRORS (3000-3999)
    # ============================================================================

    # General Resources
    RES_NOT_FOUND = "PSI-RES-3001"
    RES_ALREADY_EXISTS = "PSI-RES-3002"
    RES_DELETED = "PSI-RES-3003"
    RES_EXPIRED = "PSI-RES-3004"

    # Specific Resources
    RES_USER_NOT_FOUND = "PSI-RES-3010"
    RES_FOOD_ITEM_NOT_FOUND = "PSI-RES-3011"
    RES_RECIPE_NOT_FOUND = "PSI-RES-3012"
    RES_EMOTION_RECORD_NOT_FOUND = "PSI-RES-3013"
    RES_ANALYSIS_NOT_FOUND = "PSI-RES-3014"
    RES_INGREDIENT_NOT_FOUND = "PSI-RES-3015"

    # ============================================================================
    # RATE LIMITING ERRORS (4000-4999)
    # ============================================================================

    RATE_LIMIT_EXCEEDED = "PSI-RATE-4001"
    RATE_DAILY_LIMIT_EXCEEDED = "PSI-RATE-4002"
    RATE_HOURLY_LIMIT_EXCEEDED = "PSI-RATE-4003"
    RATE_CONCURRENT_REQUEST_LIMIT = "PSI-RATE-4004"
    RATE_FREE_TIER_LIMIT_EXCEEDED = "PSI-RATE-4005"
    RATE_API_QUOTA_EXCEEDED = "PSI-RATE-4006"

    # ============================================================================
    # SERVICE ERRORS (5000-5999)
    # ============================================================================

    # General Service Errors
    SVC_INTERNAL_ERROR = "PSI-SVC-5001"
    SVC_UNAVAILABLE = "PSI-SVC-5002"
    SVC_TIMEOUT = "PSI-SVC-5003"
    SVC_MAINTENANCE = "PSI-SVC-5004"
    SVC_CONFIGURATION_ERROR = "PSI-SVC-5005"

    # Specific Service Errors
    SVC_YOLO_MODEL_NOT_LOADED = "PSI-SVC-5010"
    SVC_YOLO_INFERENCE_FAILED = "PSI-SVC-5011"
    SVC_S3_UPLOAD_FAILED = "PSI-SVC-5012"
    SVC_REDIS_UNAVAILABLE = "PSI-SVC-5013"
    SVC_EMAIL_SERVICE_FAILED = "PSI-SVC-5014"

    # ============================================================================
    # DATABASE ERRORS (6000-6999)
    # ============================================================================

    DB_CONNECTION_FAILED = "PSI-DB-6001"
    DB_QUERY_FAILED = "PSI-DB-6002"
    DB_TRANSACTION_FAILED = "PSI-DB-6003"
    DB_CONSTRAINT_VIOLATION = "PSI-DB-6004"
    DB_DEADLOCK = "PSI-DB-6005"
    DB_TIMEOUT = "PSI-DB-6006"

    # Specific Database Errors
    DB_POSTGRES_UNAVAILABLE = "PSI-DB-6010"
    DB_MONGODB_UNAVAILABLE = "PSI-DB-6011"
    DB_DUPLICATE_KEY = "PSI-DB-6012"
    DB_FOREIGN_KEY_VIOLATION = "PSI-DB-6013"

    # ============================================================================
    # IMAGE PROCESSING ERRORS (7000-7999)
    # ============================================================================

    IMG_PROCESSING_FAILED = "PSI-IMG-7001"
    IMG_NO_FOOD_DETECTED = "PSI-IMG-7002"
    IMG_POOR_QUALITY = "PSI-IMG-7003"
    IMG_TOO_DARK = "PSI-IMG-7004"
    IMG_TOO_BLURRY = "PSI-IMG-7005"
    IMG_INVALID_FORMAT = "PSI-IMG-7006"
    IMG_DECODE_FAILED = "PSI-IMG-7007"
    IMG_RESIZE_FAILED = "PSI-IMG-7008"
    IMG_LOW_CONFIDENCE = "PSI-IMG-7009"

    # ============================================================================
    # EXTERNAL SERVICE ERRORS (8000-8999)
    # ============================================================================

    EXT_SERVICE_UNAVAILABLE = "PSI-EXT-8001"
    EXT_SERVICE_TIMEOUT = "PSI-EXT-8002"
    EXT_INVALID_RESPONSE = "PSI-EXT-8003"
    EXT_API_KEY_INVALID = "PSI-EXT-8004"
    EXT_QUOTA_EXCEEDED = "PSI-EXT-8005"

    # Specific External Services
    EXT_USDA_API_FAILED = "PSI-EXT-8010"
    EXT_CLAUDE_API_FAILED = "PSI-EXT-8011"
    EXT_PAYMENT_GATEWAY_FAILED = "PSI-EXT-8012"

    # ============================================================================
    # NUTRITION ERRORS (9000-9099)
    # ============================================================================

    NUT_DATA_NOT_FOUND = "PSI-NUT-9001"
    NUT_CALCULATION_FAILED = "PSI-NUT-9002"
    NUT_INVALID_PORTION_SIZE = "PSI-NUT-9003"
    NUT_DATABASE_UNAVAILABLE = "PSI-NUT-9004"

    # ============================================================================
    # EMOTION ANALYSIS ERRORS (9100-9199)
    # ============================================================================

    EMO_ANALYSIS_FAILED = "PSI-EMO-9101"
    EMO_INSUFFICIENT_DATA = "PSI-EMO-9102"
    EMO_INVALID_BIOMETRICS = "PSI-EMO-9103"
    EMO_MODEL_ERROR = "PSI-EMO-9104"

    # ============================================================================
    # RECIPE MATCHING ERRORS (9200-9299)
    # ============================================================================

    RCP_NO_MATCHES_FOUND = "PSI-RCP-9201"
    RCP_MATCHING_FAILED = "PSI-RCP-9202"
    RCP_INSUFFICIENT_INGREDIENTS = "PSI-RCP-9203"
    RCP_INVALID_DIETARY_PREFERENCES = "PSI-RCP-9204"


# Error code metadata for detailed error information
ERROR_CODE_METADATA: Dict[ErrorCode, Dict[str, any]] = {
    # Authentication Errors
    ErrorCode.AUTH_MISSING_CREDENTIALS: {
        "status_code": 401,
        "message": "Authentication credentials are required",
        "user_message": "Please provide your login credentials to access this resource.",
        "category": ErrorCategory.AUTHENTICATION,
        "retryable": False,
    },
    ErrorCode.AUTH_INVALID_CREDENTIALS: {
        "status_code": 401,
        "message": "Invalid email or password",
        "user_message": "The email or password you entered is incorrect. Please try again.",
        "category": ErrorCategory.AUTHENTICATION,
        "retryable": True,
    },
    ErrorCode.AUTH_TOKEN_EXPIRED: {
        "status_code": 401,
        "message": "Access token has expired",
        "user_message": "Your session has expired. Please log in again.",
        "category": ErrorCategory.AUTHENTICATION,
        "retryable": True,
        "action": "refresh_token",
    },
    ErrorCode.AUTH_TOKEN_INVALID: {
        "status_code": 401,
        "message": "Invalid access token",
        "user_message": "Your session is invalid. Please log in again.",
        "category": ErrorCategory.AUTHENTICATION,
        "retryable": False,
    },
    ErrorCode.AUTH_ACCOUNT_LOCKED: {
        "status_code": 423,
        "message": "Account is locked due to too many failed login attempts",
        "user_message": "Your account has been temporarily locked for security. Please try again in {lockout_duration} minutes.",
        "category": ErrorCategory.AUTHENTICATION,
        "retryable": True,
    },

    # Authorization Errors
    ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS: {
        "status_code": 403,
        "message": "Insufficient permissions to access this resource",
        "user_message": "You don't have permission to perform this action.",
        "category": ErrorCategory.AUTHORIZATION,
        "retryable": False,
    },
    ErrorCode.AUTHZ_PREMIUM_ONLY: {
        "status_code": 403,
        "message": "This feature is only available for premium subscribers",
        "user_message": "Upgrade to Premium to access unlimited analyses and advanced features!",
        "category": ErrorCategory.AUTHORIZATION,
        "retryable": False,
        "action": "upgrade_subscription",
    },

    # Validation Errors
    ErrorCode.VAL_HRV_OUT_OF_RANGE: {
        "status_code": 422,
        "message": "Heart Rate Variability (HRV) value is out of valid range",
        "user_message": "HRV must be between 10.0 and 200.0 ms. Please check your wearable device.",
        "category": ErrorCategory.VALIDATION,
        "retryable": True,
    },
    ErrorCode.VAL_FILE_TOO_LARGE: {
        "status_code": 413,
        "message": "Uploaded file exceeds maximum size limit",
        "user_message": "Image file is too large. Maximum size is 10MB.",
        "category": ErrorCategory.VALIDATION,
        "retryable": True,
    },
    ErrorCode.VAL_FILE_TYPE_NOT_SUPPORTED: {
        "status_code": 415,
        "message": "File type not supported",
        "user_message": "Please upload a JPEG or PNG image file.",
        "category": ErrorCategory.VALIDATION,
        "retryable": True,
    },

    # Resource Errors
    ErrorCode.RES_NOT_FOUND: {
        "status_code": 404,
        "message": "Resource not found",
        "user_message": "The requested resource was not found.",
        "category": ErrorCategory.RESOURCE,
        "retryable": False,
    },
    ErrorCode.RES_RECIPE_NOT_FOUND: {
        "status_code": 404,
        "message": "Recipe not found",
        "user_message": "The recipe you're looking for doesn't exist or has been removed.",
        "category": ErrorCategory.RESOURCE,
        "retryable": False,
    },
    ErrorCode.RES_USER_NOT_FOUND: {
        "status_code": 404,
        "message": "User not found",
        "user_message": "User account not found.",
        "category": ErrorCategory.RESOURCE,
        "retryable": False,
    },

    # Rate Limiting Errors
    ErrorCode.RATE_DAILY_LIMIT_EXCEEDED: {
        "status_code": 429,
        "message": "Daily API limit exceeded",
        "user_message": "You've reached your daily limit of {limit} analyses. Upgrade to Premium for unlimited access!",
        "category": ErrorCategory.RATE_LIMIT,
        "retryable": True,
        "action": "upgrade_subscription",
    },
    ErrorCode.RATE_LIMIT_EXCEEDED: {
        "status_code": 429,
        "message": "Rate limit exceeded",
        "user_message": "Too many requests. Please wait {retry_after} seconds before trying again.",
        "category": ErrorCategory.RATE_LIMIT,
        "retryable": True,
    },

    # Service Errors
    ErrorCode.SVC_UNAVAILABLE: {
        "status_code": 503,
        "message": "Service temporarily unavailable",
        "user_message": "Our service is temporarily unavailable. Please try again in a few moments.",
        "category": ErrorCategory.SERVICE,
        "retryable": True,
    },
    ErrorCode.DB_CONNECTION_FAILED: {
        "status_code": 503,
        "message": "Database connection failed",
        "user_message": "We're experiencing technical difficulties. Please try again later.",
        "category": ErrorCategory.DATABASE,
        "retryable": True,
    },

    # Image Processing Errors
    ErrorCode.IMG_NO_FOOD_DETECTED: {
        "status_code": 400,
        "message": "No food items detected in image",
        "user_message": "We couldn't detect any food in your image. Please upload a clearer photo of your meal.",
        "category": ErrorCategory.IMAGE,
        "retryable": True,
    },
    ErrorCode.IMG_POOR_QUALITY: {
        "status_code": 400,
        "message": "Image quality too poor for analysis",
        "user_message": "Image quality is too low. Please upload a clearer, well-lit photo.",
        "category": ErrorCategory.IMAGE,
        "retryable": True,
    },

    # Nutrition Errors
    ErrorCode.NUT_DATA_NOT_FOUND: {
        "status_code": 404,
        "message": "Nutrition data not found for detected food item",
        "user_message": "We don't have nutrition data for this food item yet. Our team is working on expanding our database!",
        "category": ErrorCategory.NUTRITION,
        "retryable": False,
    },
}


def get_error_metadata(error_code: ErrorCode) -> Dict[str, any]:
    """
    Get metadata for an error code

    Args:
        error_code: ErrorCode enum value

    Returns:
        Dictionary containing error metadata
    """
    return ERROR_CODE_METADATA.get(error_code, {
        "status_code": 500,
        "message": "An unexpected error occurred",
        "user_message": "Something went wrong. Please try again later.",
        "category": ErrorCategory.SERVICE,
        "retryable": True,
    })


def format_error_message(error_code: ErrorCode, **kwargs) -> str:
    """
    Format user-friendly error message with placeholders

    Args:
        error_code: ErrorCode enum value
        **kwargs: Values to substitute in message template

    Returns:
        Formatted error message

    Example:
        >>> format_error_message(
        ...     ErrorCode.RATE_DAILY_LIMIT_EXCEEDED,
        ...     limit=3
        ... )
        "You've reached your daily limit of 3 analyses..."
    """
    metadata = get_error_metadata(error_code)
    user_message = metadata.get("user_message", "An error occurred")

    try:
        return user_message.format(**kwargs)
    except KeyError:
        return user_message


def is_retryable(error_code: ErrorCode) -> bool:
    """
    Check if an error is retryable

    Args:
        error_code: ErrorCode enum value

    Returns:
        True if error is retryable, False otherwise
    """
    metadata = get_error_metadata(error_code)
    return metadata.get("retryable", False)


def get_http_status(error_code: ErrorCode) -> int:
    """
    Get HTTP status code for an error code

    Args:
        error_code: ErrorCode enum value

    Returns:
        HTTP status code (e.g., 404, 500)
    """
    metadata = get_error_metadata(error_code)
    return metadata.get("status_code", 500)
