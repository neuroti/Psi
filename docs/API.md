# Psi API Documentation

Complete API reference for the Psi platform.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.psi-app.com/api/v1
```

## Authentication

All protected endpoints require JWT authentication.

### Get Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

### Use Token

```http
GET /wellness/check
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

---

### Food Analysis (Mode 1)

#### Upload Food Image

**Endpoint:** `POST /food/upload`

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Parameters:**
- `file` (required): Image file (JPG, PNG, max 10MB)
- `hrv` (optional): Heart Rate Variability in ms
- `heart_rate` (optional): Heart rate in bpm

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/food/upload?hrv=65.5&heart_rate=75" \
  -H "Authorization: Bearer <token>" \
  -F "file=@food.jpg"
```

**Response:**
```json
{
  "food_items": [
    {
      "name": "Bibimbap",
      "confidence": 0.95,
      "grams": 350.0,
      "calories": 560.0,
      "nutrition": {
        "protein": 25.0,
        "carbs": 82.0,
        "fat": 15.0,
        "fiber": 8.0,
        ...
      }
    }
  ],
  "total_calories": 560.0,
  "nutrition": {
    "calories": 560.0,
    "protein": 25.0,
    "carbs": 82.0,
    "fat": 15.0,
    ...
  },
  "emotion": {
    "type": "focus",
    "score": 85,
    "hrv": 65.5,
    "heart_rate": 75
  },
  "recommendation": "Excellent choice for maintaining your focused state!",
  "xp_gained": 20
}
```

#### Get Food History

**Endpoint:** `GET /food/history`

**Parameters:**
- `limit` (optional, default: 10): Number of records to return

**Response:**
```json
{
  "history": [
    {
      "record_id": "uuid",
      "foods": [...],
      "total_calories": 560.0,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Fridge Recipes (Mode 2)

#### Detect Ingredients

**Endpoint:** `POST /fridge/detect`

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Parameters:**
- `files` (required): Up to 5 fridge images
- `hrv` (optional): Heart Rate Variability
- `heart_rate` (optional): Heart rate

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/fridge/detect?hrv=60&heart_rate=72" \
  -H "Authorization: Bearer <token>" \
  -F "files=@fridge1.jpg" \
  -F "files=@fridge2.jpg"
```

**Response:**
```json
{
  "ingredients": [
    {
      "name": "eggs",
      "confidence": 0.92,
      "quantity": "unknown"
    },
    {
      "name": "milk",
      "confidence": 0.88,
      "quantity": "unknown"
    }
  ],
  "recipes": [
    {
      "recipe_id": "uuid",
      "name": "Simple Omelette",
      "cooking_time": 10,
      "difficulty": "easy",
      "emotion_score": 0.85,
      "ingredient_match": 0.9,
      "available_ingredients": 4,
      "total_ingredients": 5
    }
  ],
  "shopping_list": ["butter", "salt"],
  "emotion_type": "calmness"
}
```

---

### Wellness Hub (Mode 3)

#### Check Wellness Status

**Endpoint:** `GET /wellness/check`

**Parameters:**
- `hrv` (optional): Current HRV value
- `heart_rate` (optional): Current heart rate

**Example:**
```bash
curl "http://localhost:8000/api/v1/wellness/check?hrv=70&heart_rate=68" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "current_emotion": {
    "type": "calmness",
    "score": 90,
    "all_emotions": {
      "stress": 15,
      "fatigue": 20,
      "anxiety": 10,
      "happiness": 75,
      "excitement": 40,
      "calmness": 90,
      "focus": 65,
      "apathy": 5
    },
    "hrv": 70.0,
    "heart_rate": 68
  },
  "wellness_score": 85,
  "recommendations": {
    "food": ["Mindful eating", "Fresh seasonal foods"],
    "exercise": ["Tai chi", "Swimming", "Nature walks"],
    "content": ["Reading", "Art", "Journaling"]
  },
  "daily_tip": "This is a great time for reflection and planning."
}
```

#### Get Wellness History

**Endpoint:** `GET /wellness/history`

**Parameters:**
- `days` (optional, default: 7): Number of days to retrieve

**Response:**
```json
{
  "history": [
    {
      "date": "2024-01-15",
      "wellness_score": 85,
      "dominant_emotion": "calmness",
      "emotion_distribution": {
        "stress": 2,
        "calmness": 12,
        "happiness": 6,
        ...
      }
    }
  ]
}
```

---

## Error Responses

All endpoints return standard HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "detail": "File must be an image"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

### Free Tier
- 3 analyses per day
- 100 requests per minute

### Premium Tier
- Unlimited analyses
- 1000 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252800
```

## Webhooks (Coming Soon)

Subscribe to events:
- `food.analyzed`
- `emotion.changed`
- `wellness.score.updated`

## SDK Libraries

### Python
```python
from psi_sdk import PsiClient

client = PsiClient(api_key="your-api-key")
result = client.food.upload("food.jpg", hrv=65, heart_rate=75)
```

### JavaScript
```javascript
import { PsiClient } from 'psi-sdk';

const client = new PsiClient({ apiKey: 'your-api-key' });
const result = await client.food.upload(file, { hrv: 65, heartRate: 75 });
```

## Pagination

Use `limit` and `offset` for paginated endpoints:

```http
GET /food/history?limit=20&offset=40
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 40,
    "has_more": true
  }
}
```
