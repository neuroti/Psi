# Psi API Documentation

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Base URL**: `https://api.psi.com`
**API Version**: `v1`

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
   - [Authentication & Users](#authentication--users)
   - [Mode 1: Food Analysis](#mode-1-food-analysis)
   - [Mode 2: Fridge & Recipes](#mode-2-fridge--recipes)
   - [Mode 3: Wellness Hub](#mode-3-wellness-hub)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Response Formats](#response-formats)
8. [Code Examples](#code-examples)
9. [Webhooks](#webhooks)
10. [Changelog](#changelog)

---

## Introduction

The Psi API is a comprehensive wellness platform that combines emotion analysis, nutrition tracking, and personalized recommendations. The API provides three core modes:

- **Mode 1: Food Analysis** - Real-time emotion-nutrition analysis using AI-powered food detection
- **Mode 2: Fridge & Recipes** - Emotion-based recipe recommendations from available ingredients
- **Mode 3: Wellness Hub** - Comprehensive emotion monitoring and wellness analytics

### Key Features

✅ **YOLO v8 Food Detection** - 96%+ accuracy on 100+ food types
✅ **62+ Nutrition Metrics** - Complete nutritional analysis
✅ **8 Emotion Types** - Advanced emotional state classification
✅ **Personalized Recommendations** - AI-powered suggestions based on emotional state
✅ **Comprehensive Analytics** - Track wellness trends over time
✅ **RESTful Design** - Clean, predictable API structure
✅ **Standardized Error Codes** - Machine-readable error handling

### API Principles

- **RESTful Architecture** - Resource-based URLs with standard HTTP methods
- **JSON Format** - All requests and responses use JSON
- **Stateless** - Each request contains all necessary information
- **Versioned** - API versioning for backward compatibility
- **Secure** - HTTPS only, JWT authentication
- **Rate Limited** - Fair usage policies (3 requests/day free tier)

---

## Getting Started

### Base URL

All API requests should be made to:

```
https://api.psi.com/api/v1
```

### Quick Start

1. **Register an account**
   ```bash
   POST /api/v1/auth/register
   ```

2. **Get authentication token**
   ```bash
   POST /api/v1/auth/login
   ```

3. **Make authenticated requests**
   ```bash
   GET /api/v1/auth/me
   Headers: Authorization: Bearer YOUR_TOKEN
   ```

### API Versioning

The API uses URL-based versioning:
- Current version: `v1`
- Example: `https://api.psi.com/api/v1/food/upload`

When breaking changes are introduced, a new version will be released (e.g., `v2`) while maintaining backward compatibility with `v1`.

### Content Type

All requests must include:
```http
Content-Type: application/json
```

For file uploads:
```http
Content-Type: multipart/form-data
```

---

## Authentication

The Psi API uses **JWT (JSON Web Token)** authentication for secure access to protected endpoints.

### Authentication Flow

```mermaid
sequenceDiagram
    Client->>API: POST /auth/register (email, password)
    API->>Client: 200 OK {token, user_id}
    Client->>API: GET /food/upload (Authorization: Bearer TOKEN)
    API->>Client: 200 OK {analysis_result}
```

### Register a New User

**Endpoint**: `POST /api/v1/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Response** (200 OK):
```json
{
  "user_id": "usr_abc123def456",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "User registered successfully"
}
```

**Error Codes**:
- `PSI-AUTH-1021` - Email already exists
- `PSI-AUTH-1022` - Password too weak
- `PSI-AUTH-1023` - Invalid email format

---

### Login

**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

**Error Codes**:
- `PSI-AUTH-1002` - Invalid email or password
- `PSI-AUTH-1010` - Account locked (too many failed attempts)
- `PSI-AUTH-1011` - Account disabled

---

### Using Authentication Tokens

Include the JWT token in the `Authorization` header of all protected requests:

```http
GET /api/v1/auth/me HTTP/1.1
Host: api.psi.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Token Expiration**:
- Access tokens expire after **24 hours**
- You'll receive a `401 Unauthorized` response with error code `PSI-AUTH-1005` when token expires
- Re-authenticate to get a new token

---

### Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Response** (200 OK):
```json
{
  "user_id": "usr_abc123def456",
  "email": "user@example.com",
  "subscription_type": "free"
}
```

---

## API Endpoints

### Authentication & Users

#### Register User
- **POST** `/api/v1/auth/register`
- **Public**
- Register a new user account
- Returns authentication token

#### Login
- **POST** `/api/v1/auth/login`
- **Public**
- Authenticate user and get token
- Returns JWT token valid for 24 hours

#### Get Current User
- **GET** `/api/v1/auth/me`
- **Protected**
- Get authenticated user's profile
- Returns user details and subscription info

#### Update Profile
- **PUT** `/api/v1/auth/profile`
- **Protected**
- Update user profile information

#### Delete Account
- **DELETE** `/api/v1/auth/account`
- **Protected**
- Delete user account permanently

---

## Mode 1: Food Analysis

Real-time emotion-nutrition analysis with AI-powered food detection.

### Upload Food Image

Analyze a food image and get comprehensive nutrition and emotion insights.

**Endpoint**: `POST /api/v1/food/upload`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data
```

**Request Body** (multipart/form-data):
```
file: [image file] (required)
hrv: 65.5 (optional, float, 10.0-200.0)
heart_rate: 72 (optional, int, 30-220)
```

**Image Requirements**:
- Format: JPEG or PNG
- Maximum size: 10 MB
- Minimum dimensions: 224x224 pixels
- Clear, well-lit photo of food

**Response** (200 OK):
```json
{
  "analysis_id": "anl_xyz789",
  "timestamp": "2025-11-10T14:30:00Z",
  "food_items": [
    {
      "name": "grilled_chicken",
      "confidence": 0.96,
      "grams": 150,
      "calories": 248,
      "nutrition": {
        "protein": 37.2,
        "carbs": 0.0,
        "fat": 9.3,
        "fiber": 0.0,
        "sugar": 0.0,
        "sodium": 89,
        "cholesterol": 96,
        "vitamins": {
          "vitamin_a": 45,
          "vitamin_c": 0,
          "vitamin_d": 3
        },
        "minerals": {
          "calcium": 15,
          "iron": 1.2,
          "potassium": 256
        }
      }
    },
    {
      "name": "brown_rice",
      "confidence": 0.92,
      "grams": 200,
      "calories": 218,
      "nutrition": {
        "protein": 4.5,
        "carbs": 45.8,
        "fat": 1.6,
        "fiber": 3.5,
        "sugar": 0.7
      }
    }
  ],
  "total_nutrition": {
    "calories": 466,
    "protein": 41.7,
    "carbs": 45.8,
    "fat": 10.9,
    "fiber": 3.5
  },
  "emotion": {
    "type": "calm",
    "score": 0.82,
    "hrv": 65.5,
    "heart_rate": 72
  },
  "recommendation": "Great choice! This balanced meal provides excellent protein for muscle recovery. Your calm state suggests good stress management.",
  "xp_gained": 10,
  "streak_days": 5
}
```

**Error Codes**:
- `PSI-VAL-2020` - File too large (>10MB)
- `PSI-VAL-2021` - Unsupported file type
- `PSI-IMG-7002` - No food detected in image
- `PSI-IMG-7003` - Image quality too poor
- `PSI-RATE-4002` - Daily limit exceeded (free tier)

**Rate Limit**: 3 requests/day (free tier), unlimited (premium)

---

### Get Food History

Retrieve user's food analysis history.

**Endpoint**: `GET /api/v1/food/history`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters**:
- `limit` (optional, default: 10, max: 100) - Number of records to return
- `offset` (optional, default: 0) - Pagination offset

**Example Request**:
```http
GET /api/v1/food/history?limit=5&offset=0
```

**Response** (200 OK):
```json
{
  "history": [
    {
      "analysis_id": "anl_xyz789",
      "timestamp": "2025-11-10T14:30:00Z",
      "food_items": ["grilled_chicken", "brown_rice"],
      "total_calories": 466,
      "emotion_type": "calm"
    },
    {
      "analysis_id": "anl_abc123",
      "timestamp": "2025-11-09T12:15:00Z",
      "food_items": ["salmon", "vegetables"],
      "total_calories": 385,
      "emotion_type": "happy"
    }
  ],
  "count": 2,
  "total": 47
}
```

---

### Get Food Statistics

Get aggregated statistics about user's food intake.

**Endpoint**: `GET /api/v1/food/stats`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters**:
- `period` (optional, default: "week") - "week", "month", or "year"

**Response** (200 OK):
```json
{
  "period": "week",
  "total_analyses": 12,
  "avg_calories": 1847,
  "avg_protein": 95,
  "avg_carbs": 230,
  "avg_fat": 68,
  "top_foods": [
    {"name": "chicken_breast", "count": 8},
    {"name": "brown_rice", "count": 6},
    {"name": "broccoli", "count": 5}
  ],
  "emotion_distribution": {
    "calm": 6,
    "happy": 4,
    "stressed": 2
  }
}
```

---

## Mode 2: Fridge & Recipes

Emotion-based recipe recommendations from available ingredients.

### Detect Fridge Contents

Upload images of your fridge to detect available ingredients.

**Endpoint**: `POST /api/v1/fridge/detect`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data
```

**Request Body** (multipart/form-data):
```
files: [array of image files] (required, max 5)
hrv: 65.5 (optional)
heart_rate: 72 (optional)
```

**Response** (200 OK):
```json
{
  "detection_id": "det_abc123",
  "timestamp": "2025-11-10T15:00:00Z",
  "ingredients": [
    {
      "name": "chicken_breast",
      "confidence": 0.94,
      "quantity": "2 pieces"
    },
    {
      "name": "broccoli",
      "confidence": 0.89,
      "quantity": "1 head"
    },
    {
      "name": "onion",
      "confidence": 0.92,
      "quantity": "3 units"
    },
    {
      "name": "garlic",
      "confidence": 0.87,
      "quantity": "1 bulb"
    }
  ],
  "emotion": {
    "type": "stressed",
    "score": 0.73
  },
  "recommended_recipes": [
    {
      "recipe_id": "rcp_xyz789",
      "name": "Comfort Chicken Stir-Fry",
      "match_score": 0.92,
      "emotion_match": "stressed",
      "cooking_time": 25,
      "difficulty": "easy",
      "ingredients_available": 4,
      "ingredients_total": 5,
      "missing_ingredients": ["soy_sauce"],
      "nutrition": {
        "calories": 385,
        "protein": 42,
        "carbs": 28,
        "fat": 12
      },
      "benefits": [
        "High protein for energy",
        "Quick preparation",
        "Comfort food properties"
      ]
    },
    {
      "recipe_id": "rcp_def456",
      "name": "Garlic Roasted Chicken & Broccoli",
      "match_score": 0.88,
      "emotion_match": "stressed",
      "cooking_time": 35,
      "difficulty": "easy"
    }
  ],
  "total_recipes": 8,
  "xp_gained": 15
}
```

**Error Codes**:
- `PSI-VAL-2024` - Too many files (max 5)
- `PSI-IMG-7002` - No ingredients detected
- `PSI-RATE-4002` - Daily limit exceeded

**Rate Limit**: 3 requests/day (free tier)

---

### Get Recipe Details

Get detailed information about a specific recipe.

**Endpoint**: `GET /api/v1/fridge/recipes/{recipe_id}`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Path Parameters**:
- `recipe_id` (required) - UUID of the recipe

**Example Request**:
```http
GET /api/v1/fridge/recipes/rcp_xyz789
```

**Response** (200 OK):
```json
{
  "recipe_id": "rcp_xyz789",
  "name": "Comfort Chicken Stir-Fry",
  "description": "A quick and comforting stir-fry perfect for busy evenings",
  "emotion_type": "stressed",
  "cooking_time": 25,
  "difficulty": "easy",
  "servings": 2,
  "ingredients": [
    {
      "name": "chicken_breast",
      "quantity": "300g",
      "available": true
    },
    {
      "name": "broccoli",
      "quantity": "200g",
      "available": true
    },
    {
      "name": "onion",
      "quantity": "1 medium",
      "available": true
    },
    {
      "name": "garlic",
      "quantity": "3 cloves",
      "available": true
    },
    {
      "name": "soy_sauce",
      "quantity": "2 tbsp",
      "available": false
    }
  ],
  "instructions": [
    "Cut chicken into bite-sized pieces",
    "Mince garlic and dice onion",
    "Cut broccoli into florets",
    "Heat oil in wok or large pan over high heat",
    "Stir-fry chicken until golden (5-6 min)",
    "Add garlic and onion, cook 2 min",
    "Add broccoli and soy sauce, stir-fry 3-4 min",
    "Serve hot over rice"
  ],
  "nutrition": {
    "calories": 385,
    "protein": 42,
    "carbs": 28,
    "fat": 12,
    "fiber": 5
  },
  "image_url": "https://cdn.psi.com/recipes/comfort-chicken-stirfry.jpg",
  "tags": ["quick", "high-protein", "comfort-food"],
  "created_at": "2025-10-15T10:00:00Z"
}
```

**Error Codes**:
- `PSI-RES-3012` - Recipe not found

---

### Rate Recipe

Submit a rating for a recipe you've tried.

**Endpoint**: `POST /api/v1/fridge/recipes/{recipe_id}/rate`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "rating": 5,
  "comment": "Delicious and easy to make!"
}
```

**Request Fields**:
- `rating` (required, int, 1-5) - Star rating
- `comment` (optional, string, max 500 chars) - Review text

**Response** (200 OK):
```json
{
  "message": "Rating submitted successfully",
  "recipe_id": "rcp_xyz789",
  "your_rating": 5,
  "average_rating": 4.7,
  "total_ratings": 142
}
```

---

## Mode 3: Wellness Hub

Comprehensive emotion monitoring and wellness analytics.

### Wellness Check

Perform a comprehensive wellness analysis based on biometric data.

**Endpoint**: `GET /api/v1/wellness/check`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters**:
- `hrv` (optional, float, 10.0-200.0) - Heart Rate Variability in ms
- `heart_rate` (optional, int, 30-220) - Heart rate in bpm

**Example Request**:
```http
GET /api/v1/wellness/check?hrv=58.3&heart_rate=82
```

**Response** (200 OK):
```json
{
  "timestamp": "2025-11-10T16:00:00Z",
  "current_emotion": {
    "type": "stressed",
    "score": 0.76,
    "confidence": 0.89
  },
  "wellness_score": 62,
  "biometrics": {
    "hrv": 58.3,
    "heart_rate": 82,
    "hrv_status": "below_optimal",
    "hr_status": "elevated"
  },
  "recommendations": [
    "Take 5-10 minute breathing exercise",
    "Consider a short walk to reduce stress",
    "Avoid caffeine for the next 2 hours",
    "Stay hydrated - aim for 2 glasses of water"
  ],
  "daily_tip": "Stress is normal, but chronic stress affects health. Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8.",
  "insights": {
    "trend": "increasing_stress",
    "compared_to_yesterday": -8,
    "weekly_average": 68
  }
}
```

**Error Codes**:
- `PSI-VAL-2010` - HRV out of valid range
- `PSI-VAL-2011` - Heart rate out of valid range

**Rate Limit**: Unlimited

---

### Get Wellness History

Retrieve historical wellness data.

**Endpoint**: `GET /api/v1/wellness/history`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters**:
- `days` (optional, default: 7, min: 1, max: 90) - Number of days to retrieve

**Example Request**:
```http
GET /api/v1/wellness/history?days=14
```

**Response** (200 OK):
```json
{
  "period_days": 14,
  "daily_summary": [
    {
      "date": "2025-11-10",
      "checks": 5,
      "emotions": {
        "calm": 2,
        "stressed": 2,
        "happy": 1
      },
      "avg_wellness_score": 64,
      "avg_biometrics": {
        "hrv": 62.4,
        "heart_rate": 76
      }
    },
    {
      "date": "2025-11-09",
      "checks": 6,
      "emotions": {
        "calm": 3,
        "happy": 2,
        "stressed": 1
      },
      "avg_wellness_score": 72,
      "avg_biometrics": {
        "hrv": 68.1,
        "heart_rate": 71
      }
    }
  ],
  "total_readings": 67
}
```

---

### Analyze Emotion Trends

Get emotion trends and patterns over time.

**Endpoint**: `GET /api/v1/wellness/trends`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters**:
- `period` (optional, default: "week") - "week", "month", or "year"

**Example Request**:
```http
GET /api/v1/wellness/trends?period=month
```

**Response** (200 OK):
```json
{
  "period": "month",
  "start_date": "2025-10-10",
  "end_date": "2025-11-10",
  "emotion_distribution": {
    "calm": 45,
    "happy": 32,
    "stressed": 18,
    "anxious": 12,
    "sad": 5,
    "energetic": 8,
    "tired": 10,
    "angry": 2
  },
  "wellness_trend": "improving",
  "avg_wellness_score": 68,
  "best_day": {
    "date": "2025-11-05",
    "score": 89,
    "emotion": "happy"
  },
  "worst_day": {
    "date": "2025-10-22",
    "score": 42,
    "emotion": "stressed"
  },
  "patterns": [
    {
      "pattern": "stress_peaks_monday",
      "confidence": 0.82,
      "description": "Stress levels tend to be higher on Mondays"
    },
    {
      "pattern": "evening_calmness",
      "confidence": 0.75,
      "description": "Emotional state improves in the evening"
    }
  ],
  "recommendations": [
    "Consider meditation on Monday mornings",
    "Maintain your evening routine - it's working well"
  ]
}
```

---

### Get Wellness Insights

Get personalized wellness insights and recommendations.

**Endpoint**: `GET /api/v1/wellness/insights`

**Headers**:
```http
Authorization: Bearer YOUR_TOKEN
```

**Response** (200 OK):
```json
{
  "insights": [
    {
      "type": "achievement",
      "title": "5-Day Calm Streak!",
      "description": "You've maintained a calm emotional state for 5 consecutive days",
      "xp_reward": 50
    },
    {
      "type": "warning",
      "title": "Stress Pattern Detected",
      "description": "Your stress levels increase on Mondays. Consider planning lighter mornings.",
      "severity": "medium"
    },
    {
      "type": "tip",
      "title": "HRV Improvement",
      "description": "Your HRV has improved 12% this month. Keep up the breathing exercises!"
    }
  ],
  "progress": {
    "current_level": 5,
    "xp": 1240,
    "xp_to_next_level": 260,
    "streak_days": 12,
    "total_checks": 156
  },
  "next_milestone": {
    "name": "Wellness Warrior",
    "requirement": "Complete 200 wellness checks",
    "progress": "78%",
    "reward": "Premium feature unlock"
  },
  "goals": [
    "Maintain wellness score above 70",
    "Reduce stress episodes",
    "Improve sleep quality",
    "Build consistent routines"
  ]
}
```

---

## Error Handling

The Psi API uses standardized error codes for consistent, machine-readable error handling.

### Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "message": "Technical error description for developers",
    "type": "ExceptionClassName",
    "code": "PSI-CATEGORY-NUMBER",
    "user_message": "User-friendly error message for display",
    "details": {
      "field": "field_name",
      "retryable": true,
      "action": "suggested_action",
      ...additional context
    }
  }
}
```

### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Technical error description for developers |
| `type` | string | Exception class name (e.g., "ResourceNotFoundError") |
| `code` | string | Standardized error code (e.g., "PSI-RES-3012") |
| `user_message` | string | User-friendly message safe to display to end users |
| `details` | object | Additional error context and metadata |
| `details.retryable` | boolean | Whether the request can be retried |
| `details.action` | string | Suggested action (e.g., "upgrade_subscription") |

---

### Error Categories

| Category | Code Range | Description | Examples |
|----------|------------|-------------|----------|
| **AUTH** | 1000-1499 | Authentication errors | Login failures, invalid tokens |
| **AUTHZ** | 1500-1599 | Authorization errors | Insufficient permissions, premium features |
| **VAL** | 2000-2999 | Validation errors | Invalid input, file size limits |
| **RES** | 3000-3999 | Resource errors | Not found, already exists |
| **RATE** | 4000-4999 | Rate limiting | Daily limits, quota exceeded |
| **SVC** | 5000-5999 | Service errors | System unavailable, timeouts |
| **DB** | 6000-6999 | Database errors | Connection failures, query errors |
| **IMG** | 7000-7999 | Image processing | No food detected, poor quality |
| **EXT** | 8000-8999 | External services | Third-party API failures |
| **NUT** | 9000-9099 | Nutrition data | Data not found, calculation errors |
| **EMO** | 9100-9199 | Emotion analysis | Analysis failures, invalid biometrics |
| **RCP** | 9200-9299 | Recipe matching | No matches, insufficient ingredients |

---

### Common Error Codes

#### Authentication Errors (1000-1499)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-AUTH-1002` | 401 | Invalid credentials | The email or password you entered is incorrect |
| `PSI-AUTH-1005` | 401 | Token expired | Your session has expired. Please log in again |
| `PSI-AUTH-1010` | 423 | Account locked | Account locked due to too many failed login attempts |
| `PSI-AUTH-1021` | 409 | Email exists | This email is already registered |
| `PSI-AUTH-1022` | 400 | Weak password | Password does not meet security requirements |

#### Authorization Errors (1500-1599)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-AUTHZ-1500` | 403 | Insufficient permissions | You don't have permission to perform this action |
| `PSI-AUTHZ-1503` | 403 | Premium only | Upgrade to Premium to access this feature |

#### Validation Errors (2000-2999)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-VAL-2010` | 422 | HRV out of range | HRV must be between 10.0 and 200.0 ms |
| `PSI-VAL-2011` | 422 | Heart rate out of range | Heart rate must be between 30 and 220 bpm |
| `PSI-VAL-2020` | 413 | File too large | Image file is too large. Maximum size is 10MB |
| `PSI-VAL-2021` | 415 | Unsupported file type | Please upload a JPEG or PNG image file |

#### Resource Errors (3000-3999)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-RES-3012` | 404 | Recipe not found | The recipe you're looking for doesn't exist |
| `PSI-RES-3010` | 404 | User not found | User account not found |

#### Rate Limiting Errors (4000-4999)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-RATE-4002` | 429 | Daily limit exceeded | You've reached your daily limit. Upgrade to Premium! |
| `PSI-RATE-4003` | 429 | Hourly limit exceeded | Hourly rate limit exceeded. Please try again later |

#### Service Errors (5000-5999)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-SVC-5001` | 500 | Internal error | Something went wrong. We're working on it! |
| `PSI-SVC-5002` | 503 | Service unavailable | Service temporarily unavailable. Please try again |

#### Image Processing Errors (7000-7999)

| Code | HTTP | Description | User Message |
|------|------|-------------|--------------|
| `PSI-IMG-7002` | 400 | No food detected | We couldn't detect any food in your image |
| `PSI-IMG-7003` | 400 | Poor quality | Image quality is too low. Please upload a clearer photo |
| `PSI-IMG-7004` | 400 | Too dark | Image is too dark. Please use better lighting |

---

### Error Handling Examples

#### Example 1: Daily Limit Exceeded

**Request**:
```bash
POST /api/v1/food/upload
```

**Response** (429 Too Many Requests):
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
      "error_code": "PSI-RATE-4002",
      "retryable": true,
      "action": "upgrade_subscription"
    }
  }
}
```

#### Example 2: Invalid Token

**Request**:
```bash
GET /api/v1/auth/me
Authorization: Bearer invalid_token_here
```

**Response** (401 Unauthorized):
```json
{
  "error": {
    "message": "Invalid access token",
    "type": "AuthenticationError",
    "code": "PSI-AUTH-1004",
    "user_message": "Your session is invalid. Please log in again.",
    "details": {
      "error_code": "PSI-AUTH-1004",
      "retryable": false
    }
  }
}
```

#### Example 3: Recipe Not Found

**Request**:
```bash
GET /api/v1/fridge/recipes/invalid-recipe-id
```

**Response** (404 Not Found):
```json
{
  "error": {
    "message": "Recipe not found: invalid-recipe-id",
    "type": "ResourceNotFoundError",
    "code": "PSI-RES-3012",
    "user_message": "The recipe you're looking for doesn't exist or has been removed.",
    "details": {
      "resource": "Recipe",
      "identifier": "invalid-recipe-id",
      "error_code": "PSI-RES-3012",
      "retryable": false
    }
  }
}
```

---

### Handling Errors in Your Client

#### Python Example

```python
import requests

def upload_food_image(token, image_file):
    response = requests.post(
        "https://api.psi.com/api/v1/food/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": image_file}
    )

    if response.status_code == 200:
        return response.json()

    # Handle errors
    error = response.json()["error"]
    error_code = error["code"]

    # Handle specific errors
    if error_code == "PSI-RATE-4002":
        # Daily limit exceeded - show upgrade prompt
        show_upgrade_dialog(error["details"]["limit"])
    elif error_code == "PSI-AUTH-1005":
        # Token expired - refresh authentication
        refresh_auth_token()
        return upload_food_image(token, image_file)  # Retry
    elif error_code == "PSI-IMG-7002":
        # No food detected - ask user to retake photo
        show_error("No food detected. Please retake the photo.")
    elif error["details"].get("retryable"):
        # Error is retryable - use exponential backoff
        retry_with_backoff(upload_food_image, token, image_file)
    else:
        # Show user-friendly message
        show_error(error["user_message"])
```

#### JavaScript/TypeScript Example

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

async function uploadFoodImage(token: string, file: File): Promise<any> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("https://api.psi.com/api/v1/food/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (response.ok) {
      return await response.json();
    }

    const error: ApiError = await response.json();
    handleApiError(error);
  } catch (error) {
    console.error("Network error:", error);
    showError("Connection error. Please check your internet.");
  }
}

function handleApiError(error: ApiError): void {
  const { code, user_message, details } = error.error;

  switch (code) {
    case "PSI-RATE-4002":
      showUpgradeModal(details.limit, details.reset_at);
      break;
    case "PSI-AUTH-1005":
      refreshToken().then(() => retryRequest());
      break;
    case "PSI-IMG-7002":
      showRetakePhotoPrompt();
      break;
    default:
      if (details.retryable) {
        retryWithBackoff();
      } else {
        showErrorToast(user_message || error.error.message);
      }
  }
}
```

---

## Rate Limiting

The Psi API implements rate limiting to ensure fair usage and system stability.

### Rate Limits by Tier

| Tier | Food Analysis | Fridge Detection | Wellness Checks | Notes |
|------|---------------|------------------|-----------------|-------|
| **Free** | 3/day | 3/day | Unlimited | Resets at midnight UTC |
| **Premium** | Unlimited | Unlimited | Unlimited | No restrictions |

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1699660800
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": {
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

**Best Practices**:
1. Check `X-RateLimit-Remaining` before making requests
2. Cache results when possible
3. Implement exponential backoff for retries
4. Consider upgrading to Premium for unlimited access

---

## Response Formats

### Standard Success Response

```json
{
  "status": "success",
  "data": {
    ...response data
  }
}
```

### Pagination

For endpoints that return lists:

```json
{
  "data": [...items],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 47,
    "has_more": true
  }
}
```

### Timestamps

All timestamps are in ISO 8601 format (UTC):
```
2025-11-10T14:30:00Z
```

---

## Code Examples

### cURL Examples

#### Register User
```bash
curl -X POST https://api.psi.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

#### Upload Food Image
```bash
curl -X POST https://api.psi.com/api/v1/food/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@food.jpg" \
  -F "hrv=65.5" \
  -F "heart_rate=72"
```

#### Get Wellness History
```bash
curl -X GET "https://api.psi.com/api/v1/wellness/history?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Python SDK Example

```python
import requests
from typing import Optional

class PsiAPIClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.psi.com/api/v1"
        self.token = api_key
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def register(self, email: str, password: str, full_name: str):
        """Register a new user"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        return response.json()

    def upload_food_image(
        self,
        image_path: str,
        hrv: Optional[float] = None,
        heart_rate: Optional[int] = None
    ):
        """Upload food image for analysis"""
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {}
            if hrv:
                data["hrv"] = hrv
            if heart_rate:
                data["heart_rate"] = heart_rate

            response = requests.post(
                f"{self.base_url}/food/upload",
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data
            )
        return response.json()

    def get_wellness_check(
        self,
        hrv: Optional[float] = None,
        heart_rate: Optional[int] = None
    ):
        """Perform wellness check"""
        params = {}
        if hrv:
            params["hrv"] = hrv
        if heart_rate:
            params["heart_rate"] = heart_rate

        response = requests.get(
            f"{self.base_url}/wellness/check",
            headers=self.headers,
            params=params
        )
        return response.json()

# Usage
client = PsiAPIClient("your_token_here")

# Upload food image
result = client.upload_food_image(
    image_path="food.jpg",
    hrv=65.5,
    heart_rate=72
)
print(f"Detected: {result['food_items']}")
print(f"Total calories: {result['total_nutrition']['calories']}")
```

---

### JavaScript/TypeScript SDK Example

```typescript
class PsiAPIClient {
  private baseUrl = "https://api.psi.com/api/v1";
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${this.token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error);
    }

    return response.json();
  }

  async register(
    email: string,
    password: string,
    fullName: string
  ): Promise<any> {
    return this.request("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });
  }

  async uploadFoodImage(
    file: File,
    hrv?: number,
    heartRate?: number
  ): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    if (hrv) formData.append("hrv", hrv.toString());
    if (heartRate) formData.append("heart_rate", heartRate.toString());

    return this.request("/food/upload", {
      method: "POST",
      body: formData,
    });
  }

  async getWellnessCheck(
    hrv?: number,
    heartRate?: number
  ): Promise<any> {
    const params = new URLSearchParams();
    if (hrv) params.append("hrv", hrv.toString());
    if (heartRate) params.append("heart_rate", heartRate.toString());

    return this.request(`/wellness/check?${params}`);
  }
}

// Usage
const client = new PsiAPIClient("your_token_here");

// Upload food image
const result = await client.uploadFoodImage(fileInput.files[0], 65.5, 72);
console.log(`Detected: ${result.food_items.map(f => f.name).join(", ")}`);
```

---

## Webhooks

_(Coming soon)_

Psi API will support webhooks for real-time notifications of:
- Recipe recommendations
- Wellness alerts
- Achievement unlocks
- Subscription changes

---

## Changelog

### Version 1.0.0 (2025-11-10)
- ✅ Initial API release
- ✅ Authentication with JWT tokens
- ✅ Mode 1: Food Analysis (YOLO v8 detection)
- ✅ Mode 2: Fridge & Recipes (emotion-based recommendations)
- ✅ Mode 3: Wellness Hub (comprehensive emotion monitoring)
- ✅ Standardized error codes (70+ codes across 12 categories)
- ✅ Rate limiting (3 requests/day free tier)
- ✅ Complete API documentation

---

## Support & Resources

- **API Status**: https://status.psi.com
- **Documentation**: https://docs.psi.com
- **Support Email**: support@psi.com
- **Developer Forum**: https://community.psi.com
- **GitHub Issues**: https://github.com/psi/api/issues

---

## Terms of Service

By using the Psi API, you agree to our [Terms of Service](https://psi.com/terms) and [Privacy Policy](https://psi.com/privacy).

---

**Last Updated**: 2025-11-10
**API Version**: 1.0.0
**Documentation Version**: 1.0.0
