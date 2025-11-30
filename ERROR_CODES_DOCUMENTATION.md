# Error Code System Documentation - Psi API

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Status**: ✅ Implemented

---

## Overview

The Psi API uses a standardized error code system to provide consistent, machine-readable error identification across all endpoints. This allows clients to programmatically handle specific error conditions without parsing error messages.

### Error Code Format

```
PSI-{CATEGORY}-{NUMBER}
```

- **PSI**: Project identifier
- **CATEGORY**: 3-5 letter category code (e.g., AUTH, VAL, RES)
- **NUMBER**: Unique 3-4 digit number within category

**Examples**:
- `PSI-AUTH-1001` - Authentication failed
- `PSI-RES-3012` - Recipe not found
- `PSI-RATE-4002` - Daily limit exceeded

---

## Error Response Structure

All API errors follow this standardized JSON structure:

```json
{
  "error": {
    "message": "Technical error message for developers",
    "type": "ExceptionClassName",
    "code": "PSI-CATEGORY-NUMBER",
    "user_message": "Friendly message for end users",
    "details": {
      "field": "field_name",
      "retryable": true,
      "action": "upgrade_subscription",
      ...additional context
    }
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Technical error description for developers |
| `type` | string | Exception class name (e.g., "ResourceNotFoundError") |
| `code` | string | Standardized error code (e.g., "PSI-RES-3012") |
| `user_message` | string | User-friendly error message for display |
| `details` | object | Additional error context and metadata |
| `details.retryable` | boolean | Whether the request can be retried |
| `details.action` | string | Suggested action (e.g., "upgrade_subscription") |

---

## Error Categories

### 1. Authentication Errors (AUTH: 1000-1499)

Errors related to user authentication and identity verification.

| Code | HTTP | Description | User Message | Retryable |
|------|------|-------------|--------------|-----------|
| **PSI-AUTH-1001** | 401 | Missing authentication credentials | Please provide your login credentials | No |
| **PSI-AUTH-1002** | 401 | Invalid email or password | The email or password is incorrect | Yes |
| **PSI-AUTH-1003** | 401 | Missing access token | Authentication token required | No |
| **PSI-AUTH-1004** | 401 | Invalid access token | Your session is invalid | No |
| **PSI-AUTH-1005** | 401 | Access token expired | Your session has expired. Please log in again | Yes |
| **PSI-AUTH-1006** | 401 | Token has been revoked | This token has been revoked | No |
| **PSI-AUTH-1010** | 423 | Account temporarily locked | Account locked due to failed login attempts | Yes |
| **PSI-AUTH-1011** | 403 | Account disabled by admin | Your account has been disabled | No |
| **PSI-AUTH-1012** | 403 | Account not verified | Please verify your account | Yes |
| **PSI-AUTH-1013** | 403 | Email not verified | Please verify your email address | Yes |
| **PSI-AUTH-1020** | 409 | User already exists | An account with this email already exists | No |
| **PSI-AUTH-1021** | 409 | Email already registered | This email is already registered | No |
| **PSI-AUTH-1022** | 400 | Password too weak | Password does not meet security requirements | Yes |
| **PSI-AUTH-1023** | 400 | Invalid email format | Please enter a valid email address | Yes |
| **PSI-AUTH-1030** | 400 | Invalid password reset token | Password reset link is invalid | No |
| **PSI-AUTH-1031** | 400 | Password reset token expired | Password reset link has expired | Yes |

**Example Response**:
```json
{
  "error": {
    "message": "Invalid email or password",
    "type": "AuthenticationError",
    "code": "PSI-AUTH-1002",
    "user_message": "The email or password you entered is incorrect. Please try again.",
    "details": {
      "retryable": true
    }
  }
}
```

---

### 2. Authorization Errors (AUTHZ: 1500-1599)

Errors related to permissions and access control.

| Code | HTTP | Description | User Message | Action |
|------|------|-------------|--------------|--------|
| **PSI-AUTHZ-1500** | 403 | Insufficient permissions | You don't have permission to perform this action | - |
| **PSI-AUTHZ-1501** | 403 | Feature not available for your tier | This feature is not available on your plan | upgrade |
| **PSI-AUTHZ-1502** | 403 | Subscription required | Subscription required for this feature | upgrade |
| **PSI-AUTHZ-1503** | 403 | Premium subscription required | Upgrade to Premium to access this feature | upgrade |
| **PSI-AUTHZ-1504** | 403 | Admin access required | Only administrators can perform this action | - |
| **PSI-AUTHZ-1505** | 403 | Cannot access this resource | You don't have access to this resource | - |

**Example Response**:
```json
{
  "error": {
    "message": "This feature is only available for premium subscribers",
    "type": "AuthorizationError",
    "code": "PSI-AUTHZ-1503",
    "user_message": "Upgrade to Premium to access unlimited analyses and advanced features!",
    "details": {
      "retryable": false,
      "action": "upgrade_subscription"
    }
  }
}
```

---

### 3. Validation Errors (VAL: 2000-2999)

Errors related to input validation and data format.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-VAL-2001** | 422 | Invalid input data | Please check your input and try again |
| **PSI-VAL-2002** | 422 | Required field missing | Please provide all required fields |
| **PSI-VAL-2003** | 422 | Invalid data format | Data format is invalid |
| **PSI-VAL-2004** | 422 | Value out of valid range | Value must be within valid range |
| **PSI-VAL-2005** | 422 | Invalid data type | Invalid data type provided |
| **PSI-VAL-2010** | 422 | HRV out of range | HRV must be between 10.0 and 200.0 ms |
| **PSI-VAL-2011** | 422 | Heart rate out of range | Heart rate must be between 30 and 220 bpm |
| **PSI-VAL-2012** | 422 | Coherence value out of range | Coherence must be between 0.0 and 1.0 |
| **PSI-VAL-2013** | 422 | Invalid biometric data | Biometric data validation failed |
| **PSI-VAL-2020** | 413 | File too large | Image file is too large. Maximum size is 10MB |
| **PSI-VAL-2021** | 415 | Unsupported file type | Please upload a JPEG or PNG image file |
| **PSI-VAL-2022** | 400 | File corrupted or unreadable | The file appears to be corrupted |
| **PSI-VAL-2023** | 400 | Invalid image dimensions | Image dimensions are invalid |
| **PSI-VAL-2024** | 400 | Too many files uploaded | Maximum 5 files can be uploaded at once |
| **PSI-VAL-2030** | 400 | Invalid page number | Page number must be positive |
| **PSI-VAL-2031** | 400 | Invalid limit parameter | Limit must be between 1 and 100 |
| **PSI-VAL-2032** | 400 | Invalid date range | Date range is invalid |
| **PSI-VAL-2040** | 400 | Insufficient data for analysis | More data needed for analysis |

---

### 4. Resource Errors (RES: 3000-3999)

Errors when requested resources don't exist.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-RES-3001** | 404 | Resource not found | The requested resource was not found |
| **PSI-RES-3002** | 409 | Resource already exists | This resource already exists |
| **PSI-RES-3003** | 410 | Resource deleted | This resource has been deleted |
| **PSI-RES-3010** | 404 | User not found | User account not found |
| **PSI-RES-3011** | 404 | Food item not found | Food item not found in database |
| **PSI-RES-3012** | 404 | Recipe not found | Recipe doesn't exist or has been removed |
| **PSI-RES-3013** | 404 | Emotion record not found | Emotion record not found |
| **PSI-RES-3014** | 404 | Analysis not found | Analysis record not found |
| **PSI-RES-3015** | 404 | Ingredient not found | Ingredient not found in database |

**Example Response**:
```json
{
  "error": {
    "message": "Recipe not found: abc-123",
    "type": "ResourceNotFoundError",
    "code": "PSI-RES-3012",
    "user_message": "The recipe you're looking for doesn't exist or has been removed.",
    "details": {
      "resource": "Recipe",
      "identifier": "abc-123",
      "retryable": false
    }
  }
}
```

---

### 5. Rate Limiting Errors (RATE: 4000-4999)

Errors when usage limits are exceeded.

| Code | HTTP | Description | User Message | Action |
|------|------|-------------|--------------|--------|
| **PSI-RATE-4001** | 429 | General rate limit exceeded | Too many requests. Please wait before trying again | - |
| **PSI-RATE-4002** | 429 | Daily limit exceeded | You've reached your daily limit of {limit} analyses | upgrade |
| **PSI-RATE-4003** | 429 | Hourly limit exceeded | Hourly rate limit exceeded | - |
| **PSI-RATE-4004** | 429 | Too many concurrent requests | Too many concurrent requests | - |
| **PSI-RATE-4005** | 429 | Free tier limit exceeded | Free tier daily limit exceeded | upgrade |
| **PSI-RATE-4006** | 429 | API quota exceeded | Monthly API quota exceeded | upgrade |

**Example Response**:
```json
{
  "error": {
    "message": "Daily API limit exceeded",
    "type": "RateLimitError",
    "code": "PSI-RATE-4002",
    "user_message": "You've reached your daily limit of 3 analyses. Upgrade to Premium for unlimited access!",
    "details": {
      "limit": 3,
      "window": "day",
      "reset_at": "2025-11-11T00:00:00Z",
      "retryable": true,
      "action": "upgrade_subscription"
    }
  }
}
```

---

### 6. Service Errors (SVC: 5000-5999)

Errors from system services and infrastructure.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-SVC-5001** | 500 | Internal server error | Something went wrong. We're working on it! |
| **PSI-SVC-5002** | 503 | Service unavailable | Service temporarily unavailable |
| **PSI-SVC-5003** | 504 | Service timeout | Request timed out. Please try again |
| **PSI-SVC-5004** | 503 | System under maintenance | System is under maintenance |
| **PSI-SVC-5010** | 503 | YOLO model not loaded | AI model temporarily unavailable |
| **PSI-SVC-5011** | 500 | YOLO inference failed | Image analysis failed |
| **PSI-SVC-5012** | 500 | S3 upload failed | Image upload failed |
| **PSI-SVC-5013** | 503 | Redis unavailable | Caching service unavailable |
| **PSI-SVC-5014** | 500 | Email service failed | Failed to send email |

---

### 7. Database Errors (DB: 6000-6999)

Errors from database operations.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-DB-6001** | 503 | Database connection failed | Database temporarily unavailable |
| **PSI-DB-6002** | 503 | Database query failed | Database query failed |
| **PSI-DB-6003** | 503 | Transaction failed | Database transaction failed |
| **PSI-DB-6004** | 409 | Constraint violation | Database constraint violation |
| **PSI-DB-6010** | 503 | PostgreSQL unavailable | PostgreSQL database unavailable |
| **PSI-DB-6011** | 503 | MongoDB unavailable | MongoDB database unavailable |
| **PSI-DB-6012** | 409 | Duplicate key error | Record already exists |

---

### 8. Image Processing Errors (IMG: 7000-7999)

Errors from image analysis and processing.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-IMG-7001** | 400 | Image processing failed | Failed to process image |
| **PSI-IMG-7002** | 400 | No food detected | We couldn't detect any food in your image |
| **PSI-IMG-7003** | 400 | Poor image quality | Image quality is too low |
| **PSI-IMG-7004** | 400 | Image too dark | Image is too dark. Please use better lighting |
| **PSI-IMG-7005** | 400 | Image too blurry | Image is too blurry. Please upload a clearer photo |
| **PSI-IMG-7006** | 415 | Invalid image format | Invalid image format |
| **PSI-IMG-7007** | 400 | Failed to decode image | Failed to read image file |
| **PSI-IMG-7008** | 500 | Image resize failed | Failed to process image |
| **PSI-IMG-7009** | 400 | Low detection confidence | Food detection confidence too low |

---

### 9. External Service Errors (EXT: 8000-8999)

Errors from external APIs and services.

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-EXT-8001** | 503 | External service unavailable | External service temporarily unavailable |
| **PSI-EXT-8002** | 504 | External service timeout | External service timed out |
| **PSI-EXT-8003** | 500 | Invalid external response | Received invalid response from external service |
| **PSI-EXT-8004** | 500 | External API key invalid | External API authentication failed |
| **PSI-EXT-8010** | 503 | USDA API unavailable | Nutrition database temporarily unavailable |
| **PSI-EXT-8011** | 503 | Claude API unavailable | AI service temporarily unavailable |

---

### 10. Domain-Specific Errors

#### Nutrition Errors (NUT: 9000-9099)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-NUT-9001** | 404 | Nutrition data not found | We don't have nutrition data for this food item yet |
| **PSI-NUT-9002** | 500 | Nutrition calculation failed | Failed to calculate nutrition information |
| **PSI-NUT-9003** | 400 | Invalid portion size | Invalid portion size specified |
| **PSI-NUT-9004** | 503 | Nutrition database unavailable | Nutrition database temporarily unavailable |

#### Emotion Analysis Errors (EMO: 9100-9199)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-EMO-9101** | 500 | Emotion analysis failed | Failed to analyze emotional state |
| **PSI-EMO-9102** | 400 | Insufficient biometric data | More biometric data needed for analysis |
| **PSI-EMO-9103** | 422 | Invalid biometric readings | Biometric readings are invalid |
| **PSI-EMO-9104** | 500 | Emotion model error | Emotion analysis model error |

#### Recipe Matching Errors (RCP: 9200-9299)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| **PSI-RCP-9201** | 404 | No matching recipes found | No recipes match your available ingredients |
| **PSI-RCP-9202** | 500 | Recipe matching failed | Failed to find matching recipes |
| **PSI-RCP-9203** | 400 | Insufficient ingredients | More ingredients needed for recipe matching |
| **PSI-RCP-9204** | 422 | Invalid dietary preferences | Dietary preferences are invalid |

---

## Client Implementation Guide

### Handling Error Responses

```python
import requests

response = requests.post(
    "https://api.psi.com/api/v1/food/upload",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": image_file}
)

if response.status_code != 200:
    error = response.json()["error"]
    error_code = error["code"]
    user_message = error.get("user_message", error["message"])

    # Handle specific error codes
    if error_code == "PSI-RATE-4002":
        # Daily limit exceeded - show upgrade prompt
        show_upgrade_dialog(error["details"]["limit"])
    elif error_code == "PSI-IMG-7002":
        # No food detected - ask user to retake photo
        show_retake_photo_prompt()
    elif error_code == "PSI-AUTH-1005":
        # Token expired - refresh token
        refresh_auth_token()
        retry_request()
    elif error["details"].get("retryable"):
        # Error is retryable - retry with exponential backoff
        retry_with_backoff()
    else:
        # Show generic error
        show_error_message(user_message)
```

### TypeScript/JavaScript Example

```typescript
interface ApiError {
  error: {
    message: string;
    type: string;
    code: string;
    user_message?: string;
    details: {
      retryable?: boolean;
      action?: string;
      [key: string]: any;
    };
  };
}

async function uploadFoodImage(file: File): Promise<void> {
  try {
    const response = await fetch("/api/v1/food/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      handleApiError(error);
    }
  } catch (error) {
    // Network error
    showErrorToast("Connection error. Please check your internet.");
  }
}

function handleApiError(error: ApiError): void {
  const { code, user_message, details } = error.error;

  switch (code) {
    case "PSI-RATE-4002":
      showUpgradeModal(details.limit);
      break;
    case "PSI-AUTH-1005":
      refreshToken().then(() => retryRequest());
      break;
    case "PSI-IMG-7002":
      showRetakePhotoPrompt();
      break;
    default:
      showErrorToast(user_message || error.error.message);
  }
}
```

---

## Error Code Categories Quick Reference

| Prefix | Range | Category | Description |
|--------|-------|----------|-------------|
| **AUTH** | 1000-1499 | Authentication | Login, tokens, passwords |
| **AUTHZ** | 1500-1599 | Authorization | Permissions, subscriptions |
| **VAL** | 2000-2999 | Validation | Input validation, data format |
| **RES** | 3000-3999 | Resources | Not found, deleted |
| **RATE** | 4000-4999 | Rate Limiting | Usage limits, quotas |
| **SVC** | 5000-5999 | Services | System services |
| **DB** | 6000-6999 | Database | Database operations |
| **IMG** | 7000-7999 | Images | Image processing |
| **EXT** | 8000-8999 | External | External APIs |
| **NUT** | 9000-9099 | Nutrition | Nutrition data |
| **EMO** | 9100-9199 | Emotion | Emotion analysis |
| **RCP** | 9200-9299 | Recipes | Recipe matching |

---

## Testing Error Codes

### Unit Tests

```python
# tests/test_error_codes.py
import pytest
from app.core.error_codes import ErrorCode, get_error_metadata, format_error_message
from app.core.exceptions import RateLimitError

def test_error_code_format():
    """Test error code format is correct"""
    assert ErrorCode.AUTH_INVALID_CREDENTIALS.value == "PSI-AUTH-1002"
    assert ErrorCode.RES_RECIPE_NOT_FOUND.value == "PSI-RES-3012"
    assert ErrorCode.RATE_DAILY_LIMIT_EXCEEDED.value == "PSI-RATE-4002"

def test_error_metadata():
    """Test error metadata retrieval"""
    metadata = get_error_metadata(ErrorCode.RATE_DAILY_LIMIT_EXCEEDED)
    assert metadata["status_code"] == 429
    assert metadata["retryable"] == True
    assert metadata["action"] == "upgrade_subscription"

def test_format_error_message():
    """Test error message formatting"""
    message = format_error_message(
        ErrorCode.RATE_DAILY_LIMIT_EXCEEDED,
        limit=3
    )
    assert "3" in message
    assert "analyses" in message

def test_rate_limit_error_code():
    """Test RateLimitError includes error code"""
    error = RateLimitError(limit=3, window="day")
    assert error.error_code == ErrorCode.RATE_DAILY_LIMIT_EXCEEDED
    assert error.details["error_code"] == "PSI-RATE-4002"
```

---

## Migration Guide

If you're migrating from the old error system:

### Before (No Error Codes)
```json
{
  "detail": "Recipe not found"
}
```

### After (With Error Codes)
```json
{
  "error": {
    "message": "Recipe not found: abc-123",
    "type": "ResourceNotFoundError",
    "code": "PSI-RES-3012",
    "user_message": "The recipe you're looking for doesn't exist or has been removed.",
    "details": {
      "resource": "Recipe",
      "identifier": "abc-123",
      "retryable": false
    }
  }
}
```

### Client Code Updates

**Before**:
```python
if "not found" in error_message:
    handle_not_found()
```

**After**:
```python
if error_code == "PSI-RES-3012":
    handle_recipe_not_found()
```

---

## Best Practices

### 1. Always Check Error Codes
Don't parse error messages - use error codes for logic:
```python
# ❌ Bad
if "expired" in error["message"]:
    refresh_token()

# ✅ Good
if error["code"] == "PSI-AUTH-1005":
    refresh_token()
```

### 2. Display User Messages
Show `user_message` to end users, not `message`:
```python
# ❌ Bad - technical message
show_alert(error["message"])

# ✅ Good - user-friendly message
show_alert(error["user_message"] or error["message"])
```

### 3. Respect Retryable Flag
Check if error can be retried:
```python
if error["details"].get("retryable"):
    retry_with_exponential_backoff()
else:
    show_permanent_error()
```

### 4. Handle Suggested Actions
Execute suggested actions from error:
```python
action = error["details"].get("action")
if action == "upgrade_subscription":
    show_upgrade_modal()
elif action == "refresh_token":
    refresh_authentication()
```

---

## Support

For questions or issues with error codes:
- **Documentation**: https://docs.psi.com/errors
- **Support**: support@psi.com
- **GitHub Issues**: https://github.com/psi/api/issues

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
