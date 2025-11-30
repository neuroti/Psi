"""
Unit Tests for Error Code System
Tests standardized error codes, exceptions, and error responses
"""
import pytest
from app.core.error_codes import (
    ErrorCode,
    ErrorCategory,
    get_error_metadata,
    format_error_message,
    is_retryable,
    get_http_status
)
from app.core.exceptions import (
    PsiException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServiceUnavailableError,
    InvalidInputError,
    DatabaseError,
    ExternalServiceError,
    ImageProcessingError,
    NutritionDataNotFoundError,
    InsufficientDataError
)


class TestErrorCodes:
    """Test error code constants and format"""

    def test_error_code_format_authentication(self):
        """Test authentication error codes follow format"""
        assert ErrorCode.AUTH_INVALID_CREDENTIALS.value == "PSI-AUTH-1002"
        assert ErrorCode.AUTH_TOKEN_EXPIRED.value == "PSI-AUTH-1005"
        assert ErrorCode.AUTH_ACCOUNT_LOCKED.value == "PSI-AUTH-1010"

    def test_error_code_format_authorization(self):
        """Test authorization error codes follow format"""
        assert ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS.value == "PSI-AUTHZ-1500"
        assert ErrorCode.AUTHZ_PREMIUM_ONLY.value == "PSI-AUTHZ-1503"

    def test_error_code_format_validation(self):
        """Test validation error codes follow format"""
        assert ErrorCode.VAL_INVALID_INPUT.value == "PSI-VAL-2001"
        assert ErrorCode.VAL_HRV_OUT_OF_RANGE.value == "PSI-VAL-2010"
        assert ErrorCode.VAL_FILE_TOO_LARGE.value == "PSI-VAL-2020"

    def test_error_code_format_resources(self):
        """Test resource error codes follow format"""
        assert ErrorCode.RES_NOT_FOUND.value == "PSI-RES-3001"
        assert ErrorCode.RES_RECIPE_NOT_FOUND.value == "PSI-RES-3012"
        assert ErrorCode.RES_USER_NOT_FOUND.value == "PSI-RES-3010"

    def test_error_code_format_rate_limiting(self):
        """Test rate limiting error codes follow format"""
        assert ErrorCode.RATE_LIMIT_EXCEEDED.value == "PSI-RATE-4001"
        assert ErrorCode.RATE_DAILY_LIMIT_EXCEEDED.value == "PSI-RATE-4002"

    def test_error_code_format_services(self):
        """Test service error codes follow format"""
        assert ErrorCode.SVC_UNAVAILABLE.value == "PSI-SVC-5002"
        assert ErrorCode.SVC_INTERNAL_ERROR.value == "PSI-SVC-5001"

    def test_error_code_format_database(self):
        """Test database error codes follow format"""
        assert ErrorCode.DB_CONNECTION_FAILED.value == "PSI-DB-6001"
        assert ErrorCode.DB_QUERY_FAILED.value == "PSI-DB-6002"

    def test_error_code_format_image_processing(self):
        """Test image processing error codes follow format"""
        assert ErrorCode.IMG_PROCESSING_FAILED.value == "PSI-IMG-7001"
        assert ErrorCode.IMG_NO_FOOD_DETECTED.value == "PSI-IMG-7002"

    def test_error_code_format_domain_specific(self):
        """Test domain-specific error codes follow format"""
        assert ErrorCode.NUT_DATA_NOT_FOUND.value == "PSI-NUT-9001"
        assert ErrorCode.EMO_ANALYSIS_FAILED.value == "PSI-EMO-9101"
        assert ErrorCode.RCP_NO_MATCHES_FOUND.value == "PSI-RCP-9201"


class TestErrorMetadata:
    """Test error code metadata retrieval"""

    def test_get_metadata_authentication_error(self):
        """Test metadata for authentication errors"""
        metadata = get_error_metadata(ErrorCode.AUTH_INVALID_CREDENTIALS)
        assert metadata["status_code"] == 401
        assert metadata["retryable"] == True
        assert "email" in metadata["user_message"].lower() or "password" in metadata["user_message"].lower()

    def test_get_metadata_rate_limit_error(self):
        """Test metadata for rate limit errors"""
        metadata = get_error_metadata(ErrorCode.RATE_DAILY_LIMIT_EXCEEDED)
        assert metadata["status_code"] == 429
        assert metadata["retryable"] == True
        assert metadata["action"] == "upgrade_subscription"

    def test_get_metadata_premium_only_error(self):
        """Test metadata for premium feature errors"""
        metadata = get_error_metadata(ErrorCode.AUTHZ_PREMIUM_ONLY)
        assert metadata["status_code"] == 403
        assert metadata["retryable"] == False
        assert metadata["action"] == "upgrade_subscription"

    def test_get_metadata_resource_not_found(self):
        """Test metadata for resource not found errors"""
        metadata = get_error_metadata(ErrorCode.RES_RECIPE_NOT_FOUND)
        assert metadata["status_code"] == 404
        assert metadata["retryable"] == False

    def test_get_metadata_service_error(self):
        """Test metadata for service errors"""
        metadata = get_error_metadata(ErrorCode.SVC_UNAVAILABLE)
        assert metadata["status_code"] == 503
        assert metadata["retryable"] == True

    def test_get_metadata_unknown_error(self):
        """Test metadata for codes without explicit metadata"""
        # Create a mock error code (this would be a new code without metadata)
        metadata = get_error_metadata(ErrorCode.RES_EXPIRED)
        # Should return defaults
        assert "status_code" in metadata
        assert "message" in metadata


class TestErrorMessageFormatting:
    """Test error message formatting with placeholders"""

    def test_format_message_with_placeholders(self):
        """Test formatting message with placeholders"""
        message = format_error_message(
            ErrorCode.RATE_DAILY_LIMIT_EXCEEDED,
            limit=3
        )
        assert "3" in message
        assert "daily" in message.lower()

    def test_format_message_without_placeholders(self):
        """Test formatting message without placeholders"""
        message = format_error_message(ErrorCode.AUTH_INVALID_CREDENTIALS)
        assert len(message) > 0
        assert "password" in message.lower() or "credentials" in message.lower()

    def test_format_message_missing_placeholder(self):
        """Test formatting with missing placeholder values"""
        # Should not crash, just return unformatted message
        message = format_error_message(ErrorCode.RATE_DAILY_LIMIT_EXCEEDED)
        assert len(message) > 0


class TestErrorCodeHelpers:
    """Test helper functions"""

    def test_is_retryable_true(self):
        """Test retryable errors"""
        assert is_retryable(ErrorCode.AUTH_INVALID_CREDENTIALS) == True
        assert is_retryable(ErrorCode.SVC_UNAVAILABLE) == True
        assert is_retryable(ErrorCode.RATE_DAILY_LIMIT_EXCEEDED) == True

    def test_is_retryable_false(self):
        """Test non-retryable errors"""
        assert is_retryable(ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS) == False
        assert is_retryable(ErrorCode.RES_RECIPE_NOT_FOUND) == False

    def test_get_http_status(self):
        """Test HTTP status code retrieval"""
        assert get_http_status(ErrorCode.AUTH_INVALID_CREDENTIALS) == 401
        assert get_http_status(ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS) == 403
        assert get_http_status(ErrorCode.RES_NOT_FOUND) == 404
        assert get_http_status(ErrorCode.RATE_LIMIT_EXCEEDED) == 429
        assert get_http_status(ErrorCode.SVC_UNAVAILABLE) == 503


class TestExceptions:
    """Test custom exception classes with error codes"""

    def test_authentication_error_includes_code(self):
        """Test AuthenticationError includes error code"""
        error = AuthenticationError()
        assert error.error_code == ErrorCode.AUTH_INVALID_CREDENTIALS
        assert error.details["error_code"] == "PSI-AUTH-1002"
        assert error.status_code == 401

    def test_authentication_error_custom_code(self):
        """Test AuthenticationError with custom error code"""
        error = AuthenticationError(
            message="Token expired",
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED
        )
        assert error.error_code == ErrorCode.AUTH_TOKEN_EXPIRED
        assert error.details["error_code"] == "PSI-AUTH-1005"

    def test_authorization_error_includes_code(self):
        """Test AuthorizationError includes error code"""
        error = AuthorizationError()
        assert error.error_code == ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS
        assert error.details["error_code"] == "PSI-AUTHZ-1500"
        assert error.status_code == 403

    def test_resource_not_found_auto_code(self):
        """Test ResourceNotFoundError automatically selects code by resource type"""
        # Test recipe
        error = ResourceNotFoundError("Recipe", "abc-123")
        assert error.error_code == ErrorCode.RES_RECIPE_NOT_FOUND
        assert error.details["error_code"] == "PSI-RES-3012"

        # Test user
        error = ResourceNotFoundError("User", "user-456")
        assert error.error_code == ErrorCode.RES_USER_NOT_FOUND
        assert error.details["error_code"] == "PSI-RES-3010"

        # Test unknown resource type
        error = ResourceNotFoundError("UnknownType", "xyz-789")
        assert error.error_code == ErrorCode.RES_NOT_FOUND
        assert error.details["error_code"] == "PSI-RES-3001"

    def test_validation_error_includes_code(self):
        """Test ValidationError includes error code"""
        error = ValidationError("Invalid input", field="email")
        assert error.error_code == ErrorCode.VAL_INVALID_INPUT
        assert error.details["error_code"] == "PSI-VAL-2001"
        assert error.status_code == 422

    def test_rate_limit_error_daily(self):
        """Test RateLimitError with daily window"""
        error = RateLimitError(limit=3, window="day")
        assert error.error_code == ErrorCode.RATE_DAILY_LIMIT_EXCEEDED
        assert error.details["error_code"] == "PSI-RATE-4002"
        assert error.details["limit"] == 3
        assert error.details["window"] == "day"

    def test_rate_limit_error_hourly(self):
        """Test RateLimitError with hourly window"""
        error = RateLimitError(limit=100, window="hour")
        assert error.error_code == ErrorCode.RATE_HOURLY_LIMIT_EXCEEDED
        assert error.details["error_code"] == "PSI-RATE-4003"

    def test_service_unavailable_error_includes_code(self):
        """Test ServiceUnavailableError includes error code"""
        error = ServiceUnavailableError("database", retry_after=60)
        assert error.error_code == ErrorCode.SVC_UNAVAILABLE
        assert error.details["error_code"] == "PSI-SVC-5002"
        assert error.details["retry_after"] == 60

    def test_database_error_includes_code(self):
        """Test DatabaseError includes error code"""
        error = DatabaseError("select_query")
        assert error.error_code == ErrorCode.DB_QUERY_FAILED
        assert error.details["error_code"] == "PSI-DB-6002"
        assert error.status_code == 503

    def test_image_processing_error_includes_code(self):
        """Test ImageProcessingError includes error code"""
        error = ImageProcessingError(
            message="No food detected",
            error_code=ErrorCode.IMG_NO_FOOD_DETECTED
        )
        assert error.error_code == ErrorCode.IMG_NO_FOOD_DETECTED
        assert error.details["error_code"] == "PSI-IMG-7002"

    def test_nutrition_data_not_found_error(self):
        """Test NutritionDataNotFoundError includes error code"""
        error = NutritionDataNotFoundError("unknown_food")
        assert error.error_code == ErrorCode.NUT_DATA_NOT_FOUND
        assert error.details["error_code"] == "PSI-NUT-9001"
        assert error.details["food"] == "unknown_food"

    def test_insufficient_data_error(self):
        """Test InsufficientDataError includes error code"""
        error = InsufficientDataError("More data points needed")
        assert error.error_code == ErrorCode.VAL_INSUFFICIENT_DATA
        assert error.details["error_code"] == "PSI-VAL-2040"

    def test_exception_retryable_flag(self):
        """Test exceptions include retryable flag in details"""
        # Retryable error
        error = AuthenticationError()
        assert error.details["retryable"] == True

        # Non-retryable error
        error = AuthorizationError()
        assert error.details["retryable"] == False

    def test_exception_action_flag(self):
        """Test exceptions include action flag when applicable"""
        error = RateLimitError(limit=3, window="day")
        assert "action" in error.details
        assert error.details["action"] == "upgrade_subscription"


class TestPsiExceptionBase:
    """Test PsiException base class"""

    def test_psi_exception_without_error_code(self):
        """Test PsiException can be created without error code"""
        error = PsiException("Test error", status_code=400)
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.error_code is None

    def test_psi_exception_with_error_code(self):
        """Test PsiException with error code"""
        error = PsiException(
            "Test error",
            status_code=404,
            error_code=ErrorCode.RES_NOT_FOUND
        )
        assert error.error_code == ErrorCode.RES_NOT_FOUND
        assert error.details["error_code"] == "PSI-RES-3001"
        assert error.details["retryable"] == False

    def test_psi_exception_inherits_from_exception(self):
        """Test PsiException inherits from Exception"""
        error = PsiException("Test")
        assert isinstance(error, Exception)

    def test_psi_exception_string_representation(self):
        """Test PsiException string representation"""
        error = PsiException("Test error message")
        assert str(error) == "Test error message"


class TestErrorCodeCoverage:
    """Test that all error codes have proper metadata"""

    def test_all_auth_codes_have_metadata(self):
        """Test all authentication error codes have metadata"""
        auth_codes = [
            ErrorCode.AUTH_INVALID_CREDENTIALS,
            ErrorCode.AUTH_TOKEN_EXPIRED,
            ErrorCode.AUTH_TOKEN_INVALID,
            ErrorCode.AUTH_ACCOUNT_LOCKED,
        ]
        for code in auth_codes:
            metadata = get_error_metadata(code)
            assert "status_code" in metadata
            assert "message" in metadata
            assert "user_message" in metadata

    def test_all_rate_limit_codes_have_metadata(self):
        """Test all rate limit error codes have metadata"""
        rate_codes = [
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.RATE_DAILY_LIMIT_EXCEEDED,
        ]
        for code in rate_codes:
            metadata = get_error_metadata(code)
            assert metadata["status_code"] == 429
            assert metadata["retryable"] == True

    def test_all_resource_codes_have_metadata(self):
        """Test all resource error codes have metadata"""
        resource_codes = [
            ErrorCode.RES_RECIPE_NOT_FOUND,
            ErrorCode.RES_USER_NOT_FOUND,
        ]
        for code in resource_codes:
            metadata = get_error_metadata(code)
            assert metadata["status_code"] == 404
            assert metadata["retryable"] == False


class TestErrorCodeCategories:
    """Test error code categories"""

    def test_error_categories_exist(self):
        """Test all error categories are defined"""
        assert ErrorCategory.AUTHENTICATION == "AUTH"
        assert ErrorCategory.AUTHORIZATION == "AUTHZ"
        assert ErrorCategory.VALIDATION == "VAL"
        assert ErrorCategory.RESOURCE == "RES"
        assert ErrorCategory.RATE_LIMIT == "RATE"
        assert ErrorCategory.SERVICE == "SVC"
        assert ErrorCategory.DATABASE == "DB"
        assert ErrorCategory.IMAGE == "IMG"
        assert ErrorCategory.EXTERNAL == "EXT"
        assert ErrorCategory.NUTRITION == "NUT"
        assert ErrorCategory.EMOTION == "EMO"
        assert ErrorCategory.RECIPE == "RCP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
