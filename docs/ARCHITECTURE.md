# Psi Architecture Document

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Status**: Living Document
**Authors**: Engineering Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Design](#2-system-design)
3. [Data Model](#3-data-model)
4. [API Design](#4-api-design)
5. [Security Architecture](#5-security-architecture)
6. [Infrastructure](#6-infrastructure)
7. [Scalability](#7-scalability)
8. [Decision Records](#8-decision-records)

---

## 1. Introduction

### 1.1 Purpose

This document describes the technical architecture of Psi, an emotion-based wellness platform that combines AI-powered food analysis with real-time biometric emotion tracking to provide personalized nutrition recommendations.

### 1.2 Scope

This document covers:
- High-level system architecture and component interactions
- Database schemas and data modeling decisions
- API design patterns and RESTful conventions
- Security architecture and threat models
- Infrastructure and deployment strategies
- Scalability considerations

### 1.3 Audience

- **Software Engineers**: Understand system design for implementation
- **DevOps Engineers**: Infrastructure and deployment planning
- **Security Engineers**: Security review and hardening
- **Product Managers**: Technical constraints and capabilities
- **Architects**: System evolution and design reviews

### 1.4 Architecture Goals

| Goal | Description | Status |
|------|-------------|--------|
| **Scalability** | Handle 100K+ concurrent users | 🟡 In Progress |
| **Reliability** | 99.9% uptime SLA | 🟡 In Progress |
| **Performance** | < 500ms API response (p95) | ✅ Achieved |
| **Security** | GDPR/CCPA compliant, encrypted data | 🟡 In Progress |
| **Maintainability** | Clean architecture, well-documented | ✅ Achieved |
| **Extensibility** | Easy to add new features/integrations | ✅ Achieved |

---

## 2. System Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐            │
│  │   iOS Application    │      │  Android Application │            │
│  │   (React Native)     │      │   (React Native)     │            │
│  │                      │      │                      │            │
│  │  • Redux Store       │      │  • Redux Store       │            │
│  │  • Async Storage     │      │  • Async Storage     │            │
│  │  • HealthKit         │      │  • Health Connect    │            │
│  │  • Camera/Gallery    │      │  • Camera/Gallery    │            │
│  └──────────┬───────────┘      └──────────┬───────────┘            │
│             │                              │                         │
│             └──────────────┬───────────────┘                         │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │ HTTPS/TLS 1.3
                             │ REST API (JSON)
┌────────────────────────────▼─────────────────────────────────────────┐
│                      GATEWAY TIER                                    │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              Load Balancer (AWS ALB / GCP LB)             │      │
│  │  • SSL Termination                                        │      │
│  │  • Health Checks                                          │      │
│  │  • Traffic Distribution (Round Robin)                     │      │
│  │  • WAF (Web Application Firewall)                         │      │
│  └───────────────────────────┬───────────────────────────────┘      │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────┐
│                     APPLICATION TIER                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │          FastAPI Backend (Python 3.11+)                      │   │
│  │  ┌────────────────────────────────────────────────────┐     │   │
│  │  │  API Layer (app/api/v1/)                           │     │   │
│  │  │  • Routing & Endpoint Definitions                  │     │   │
│  │  │  • Request Validation (Pydantic)                   │     │   │
│  │  │  • Authentication Middleware (JWT)                 │     │   │
│  │  │  • Rate Limiting Middleware                        │     │   │
│  │  │  • Error Handling Middleware                       │     │   │
│  │  └────────────────┬───────────────────────────────────┘     │   │
│  │                   │                                          │   │
│  │  ┌────────────────▼───────────────────────────────────┐     │   │
│  │  │  Service Layer (app/services/)                     │     │   │
│  │  │  • Business Logic                                  │     │   │
│  │  │  • YOLO Service (Food Detection)                   │     │   │
│  │  │  • Claude Service (Vision Analysis)                │     │   │
│  │  │  • Nutrition Service (USDA Lookup)                 │     │   │
│  │  │  • Emotion Service (HRV Analysis)                  │     │   │
│  │  │  • Recipe Service (TF-IDF Matching)                │     │   │
│  │  └────────────────┬───────────────────────────────────┘     │   │
│  │                   │                                          │   │
│  │  ┌────────────────▼───────────────────────────────────┐     │   │
│  │  │  Data Access Layer (app/core/database.py)          │     │   │
│  │  │  • SQLAlchemy ORM                                  │     │   │
│  │  │  • Connection Pooling                              │     │   │
│  │  │  • Query Optimization                              │     │   │
│  │  └────────────────┬───────────────────────────────────┘     │   │
│  └───────────────────┼──────────────────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────────┐
│                       DATA TIER                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │ PostgreSQL   │   │  MongoDB     │   │    Redis     │            │
│  │   (Primary)  │   │  (NoSQL)     │   │   (Cache)    │            │
│  │              │   │              │   │              │            │
│  │ • Users      │   │ • Preferences│   │ • Sessions   │            │
│  │ • Food Hist  │   │ • Emotions   │   │ • Cache      │            │
│  │ • Wellness   │   │ • Recipes    │   │ • Rate Limit │            │
│  │              │   │              │   │              │            │
│  │ ACID         │   │ Flexible     │   │ In-Memory    │            │
│  │ Transactions │   │ Schema       │   │ Key-Value    │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │ Claude API   │   │  USDA API    │   │  AWS S3      │            │
│  │ (Anthropic)  │   │  (Optional)  │   │  (Images)    │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Pattern: Layered Architecture

We employ a **Layered Architecture** pattern with clear separation of concerns:

#### 2.2.1 Presentation Layer (API Layer)
- **Responsibility**: Handle HTTP requests/responses, authentication, validation
- **Components**: FastAPI routers, middleware, Pydantic schemas
- **Location**: `backend/app/api/v1/`

**Key Decisions**:
- ✅ FastAPI for async support and auto-generated docs
- ✅ Pydantic for request/response validation
- ✅ Dependency injection for testability

#### 2.2.2 Business Logic Layer (Service Layer)
- **Responsibility**: Core business logic, algorithms, external API calls
- **Components**: Service classes, business rules, transformations
- **Location**: `backend/app/services/`

**Key Decisions**:
- ✅ Service classes (not functions) for state management
- ✅ Single Responsibility Principle (each service has one purpose)
- ✅ Dependency injection for mocking in tests

#### 2.2.3 Data Access Layer
- **Responsibility**: Database operations, ORM, caching
- **Components**: SQLAlchemy models, repository pattern, Redis client
- **Location**: `backend/app/core/database.py`, `backend/app/models/`

**Key Decisions**:
- ✅ SQLAlchemy ORM for type safety and query building
- ✅ Async database drivers (asyncpg, motor)
- ✅ Connection pooling for efficiency

### 2.3 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Mobile App (React Native)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Screens    │  │  Components  │  │  Navigation  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
│         └─────────────────┼──────────────────┘                  │
│                           │                                     │
│         ┌─────────────────▼────────────────┐                   │
│         │      Redux Store                 │                   │
│         │  • Auth Slice                    │                   │
│         │  • Food Slice                    │                   │
│         │  • Wellness Slice                │                   │
│         └─────────────────┬────────────────┘                   │
│                           │                                     │
│         ┌─────────────────▼────────────────┐                   │
│         │      API Services                │                   │
│         │  • authApi.ts                    │                   │
│         │  • foodApi.ts                    │                   │
│         │  • wellnessApi.ts                │                   │
│         └─────────────────┬────────────────┘                   │
└───────────────────────────┼──────────────────────────────────────┘
                            │ Axios HTTP Client
                            │ Authorization: Bearer <JWT>
┌───────────────────────────▼──────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Middleware Stack                                        │   │
│  │  1. CORS Middleware                                      │   │
│  │  2. Authentication Middleware (JWT verification)         │   │
│  │  3. Rate Limiting Middleware (Redis)                     │   │
│  │  4. Request Timing Middleware                            │   │
│  │  5. Error Handler Middleware                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │  API Routes (/api/v1/)                                   │   │
│  │  • auth.py      → AuthenticationService                  │   │
│  │  • food.py      → FoodAnalysisService, YOLOService       │   │
│  │  • fridge.py    → RecipeService, FridgeService           │   │
│  │  • wellness.py  → EmotionService, WellnessService        │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │  Services (Business Logic)                               │   │
│  │  ┌───────────────────┐  ┌───────────────────┐           │   │
│  │  │ YOLOService       │  │ ClaudeService     │           │   │
│  │  │ • detect_food()   │  │ • analyze_image() │           │   │
│  │  └───────────────────┘  └───────────────────┘           │   │
│  │  ┌───────────────────┐  ┌───────────────────┐           │   │
│  │  │ NutritionService  │  │ EmotionService    │           │   │
│  │  │ • get_nutrition() │  │ • analyze_hrv()   │           │   │
│  │  └───────────────────┘  └───────────────────┘           │   │
│  │  ┌───────────────────┐  ┌───────────────────┐           │   │
│  │  │ RecipeService     │  │ AuthService       │           │   │
│  │  │ • match_recipes() │  │ • create_token()  │           │   │
│  │  └───────────────────┘  └───────────────────┘           │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │  Data Access (SQLAlchemy + Motor + Redis)               │   │
│  │  • PostgreSQL: CRUD operations, transactions             │   │
│  │  • MongoDB: Document operations, aggregations            │   │
│  │  • Redis: Cache get/set, rate limit counters            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.4 Data Flow Patterns

#### 2.4.1 Synchronous Request-Response

Most API endpoints follow this pattern:

```
Client → API Gateway → Backend → Database → Backend → API Gateway → Client
```

**Example: GET /api/v1/food/history**
```
1. Mobile app sends GET request with JWT token
2. Load balancer forwards to available backend instance
3. Authentication middleware verifies JWT
4. Rate limiting middleware checks limits (Redis)
5. Handler function called
6. Service layer queries PostgreSQL
7. Response formatted with Pydantic schema
8. JSON returned to client
```

**Latency**: ~50-100ms

#### 2.4.2 Asynchronous Processing

Long-running operations (e.g., food analysis) use async processing:

```
Client → API → Queue → Worker → Database → Client (polling/webhook)
```

**Example: POST /api/v1/food/upload**
```
1. Mobile app uploads image (multipart/form-data)
2. Backend saves image to temporary storage
3. Async job dispatched to YOLO service (2-3s)
4. Async job dispatched to Claude API (1-2s)
5. Results aggregated and stored in database
6. Response returned with analysis_id
7. Client polls GET /api/v1/food/analysis/{id} for results
```

**Current**: Synchronous (acceptable for MVP)
**Future**: Async with WebSocket updates for real-time progress

#### 2.4.3 Caching Strategy

```
┌────────────────────────────────────────────────────────┐
│               Cache-Aside Pattern                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Client requests data                               │
│  2. Check Redis cache                                  │
│     ├─ Cache HIT → Return cached data                  │
│     └─ Cache MISS:                                     │
│        a. Query database                               │
│        b. Store result in Redis (with TTL)             │
│        c. Return data                                  │
│                                                        │
│  Cache TTL by Data Type:                               │
│  • Nutrition data: 7 days (rarely changes)             │
│  • Recipe data: 1 day (updated nightly)                │
│  • User sessions: 1 hour (JWT expiry)                  │
│  • Rate limit counters: 24 hours (daily reset)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2.5 Technology Stack Rationale

#### 2.5.1 Why FastAPI?

| Criterion | FastAPI | Django | Flask |
|-----------|---------|--------|-------|
| **Async Support** | ✅ Native | ❌ Limited | ❌ No |
| **Performance** | ✅ Fast (Starlette) | 🟡 Medium | 🟡 Medium |
| **Type Safety** | ✅ Pydantic | ❌ No | ❌ No |
| **Auto Docs** | ✅ OpenAPI | ❌ Manual | ❌ Manual |
| **Learning Curve** | 🟡 Medium | 🔴 High | ✅ Low |
| **Ecosystem** | ✅ Growing | ✅ Mature | ✅ Mature |

**Decision**: FastAPI for async, performance, and developer experience.

#### 2.5.2 Why PostgreSQL + MongoDB + Redis?

**Polyglot Persistence**: Different data stores for different needs.

| Database | Use Case | Why |
|----------|----------|-----|
| **PostgreSQL** | Users, food history, wellness scores | ACID transactions, referential integrity, complex queries |
| **MongoDB** | User preferences, emotion time series, recipes | Flexible schema, fast writes, horizontal scaling |
| **Redis** | Sessions, cache, rate limiting | In-memory speed, atomic operations, TTL support |

**Alternative Considered**: Single database (PostgreSQL only)
**Rejected**: JSONB fields don't scale well for high-write time series data

#### 2.5.3 Why React Native?

| Criterion | React Native | Flutter | Native (Swift/Kotlin) |
|-----------|--------------|---------|----------------------|
| **Code Reuse** | ✅ 90%+ | ✅ 90%+ | ❌ 0% |
| **Performance** | ✅ Good | ✅ Good | ✅ Excellent |
| **Developer Pool** | ✅ Large (JS/TS) | 🟡 Growing (Dart) | 🟡 Separate teams |
| **Ecosystem** | ✅ Mature | ✅ Growing | ✅ Mature |
| **Expo Tools** | ✅ Yes | ❌ No | ❌ No |
| **Time to Market** | ✅ Fast | ✅ Fast | 🔴 Slow |

**Decision**: React Native + Expo for rapid development and code sharing.

### 2.6 Design Principles

#### 2.6.1 SOLID Principles

- **Single Responsibility**: Each class/service has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Many specific interfaces > one general interface
- **Dependency Inversion**: Depend on abstractions, not concrete classes

**Example**:
```python
# Good: Single Responsibility
class YOLOService:
    """Only responsible for YOLO model inference"""
    def detect_food(self, image_path: str) -> List[Detection]:
        pass

class ClaudeService:
    """Only responsible for Claude API calls"""
    def analyze_image(self, image_path: str) -> str:
        pass

class FoodAnalysisService:
    """Orchestrates YOLOService + ClaudeService"""
    def __init__(self, yolo: YOLOService, claude: ClaudeService):
        self.yolo = yolo
        self.claude = claude

    def analyze_food(self, image_path: str) -> FoodAnalysis:
        detections = self.yolo.detect_food(image_path)
        description = self.claude.analyze_image(image_path)
        return FoodAnalysis(detections, description)
```

#### 2.6.2 DRY (Don't Repeat Yourself)

- Shared utilities in `backend/app/core/` and `mobile/src/utils/`
- Reusable components in `mobile/src/components/common/`
- Base exception classes in `backend/app/core/exceptions.py`

#### 2.6.3 KISS (Keep It Simple, Stupid)

- Favor simple solutions over clever ones
- Avoid premature optimization
- Code should be readable by junior developers

#### 2.6.4 YAGNI (You Aren't Gonna Need It)

- Don't build features "just in case"
- Wait for actual requirements before adding complexity
- Example: No microservices until we hit scale limits

---

## 3. Data Model

### 3.1 Database Schema Overview

We use **polyglot persistence** with three databases:

1. **PostgreSQL**: Structured, relational data (ACID compliance)
2. **MongoDB**: Semi-structured, flexible schema data
3. **Redis**: Ephemeral, cached data

### 3.2 PostgreSQL Schema

#### 3.2.1 Entity-Relationship Diagram

```
┌──────────────────┐         ┌──────────────────┐
│      users       │         │  subscriptions   │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │────┐    │ id (PK)          │
│ email (unique)   │    │    │ user_id (FK)     │
│ password_hash    │    │    │ tier             │
│ name             │    │    │ starts_at        │
│ subscription_tier│    │    │ ends_at          │
│ created_at       │    │    │ status           │
│ updated_at       │    │    └──────────────────┘
└──────────────────┘    │
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│  food_history    │         │ wellness_scores  │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ user_id (FK)     │         │ user_id (FK)     │
│ image_url        │         │ date (unique)    │
│ detected_foods   │         │ wellness_score   │
│ nutrition (JSONB)│         │ hrv_avg          │
│ confidence_score │         │ heart_rate_avg   │
│ created_at       │         │ dominant_emotion │
└──────────────────┘         │ created_at       │
                             └──────────────────┘
```

#### 3.2.2 Table Definitions

**users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free'
        CHECK (subscription_tier IN ('free', 'premium', 'admin')),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**food_history**
```sql
CREATE TABLE food_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_url VARCHAR(500),  -- S3 URL or null if deleted
    detected_foods JSONB NOT NULL,  -- Array of detected items with confidence
    nutrition JSONB NOT NULL,  -- Complete nutrition breakdown
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    analysis_duration_ms INTEGER,  -- For performance monitoring
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_food_history_user_id ON food_history(user_id);
CREATE INDEX idx_food_history_created_at ON food_history(created_at DESC);
CREATE INDEX idx_food_history_user_created ON food_history(user_id, created_at DESC);

-- GIN index for JSONB queries
CREATE INDEX idx_food_history_detected_foods ON food_history USING GIN (detected_foods);

-- Example JSONB structure:
-- detected_foods: [
--   {"food": "apple", "confidence": 0.95, "quantity": 1},
--   {"food": "banana", "confidence": 0.88, "quantity": 2}
-- ]
-- nutrition: {
--   "calories": 150, "protein": 2, "carbs": 35, "fat": 0.5,
--   "vitamins": {"vitamin_c": 15}, "minerals": {"potassium": 450}
-- }
```

**wellness_scores**
```sql
CREATE TABLE wellness_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    wellness_score INTEGER CHECK (wellness_score BETWEEN 0 AND 100),
    hrv_avg FLOAT,  -- Heart Rate Variability (ms)
    heart_rate_avg FLOAT,  -- Beats per minute
    dominant_emotion VARCHAR(50),  -- calm, stressed, anxious, happy, sad, etc.
    emotion_confidence FLOAT,
    data_points INTEGER DEFAULT 0,  -- Number of biometric readings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)  -- One score per day per user
);

CREATE INDEX idx_wellness_scores_user_id ON wellness_scores(user_id);
CREATE INDEX idx_wellness_scores_date ON wellness_scores(date DESC);
CREATE INDEX idx_wellness_scores_user_date ON wellness_scores(user_id, date DESC);
```

**subscriptions**
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('free', 'premium')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at TIMESTAMP WITH TIME ZONE,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);
```

#### 3.2.3 Data Relationships

**Cardinality**:
- One User → Many Food History records (1:N)
- One User → Many Wellness Scores (1:N)
- One User → One or Zero Active Subscription (1:0..1)

**Referential Integrity**:
- `ON DELETE CASCADE`: When user deleted, all related data deleted
- Foreign keys enforced at database level
- Use soft deletes (`deleted_at`) for user accounts (compliance)

### 3.3 MongoDB Collections

#### 3.3.1 user_preferences

```javascript
{
  _id: ObjectId("..."),
  user_id: "uuid-from-postgresql",  // Link to PostgreSQL
  dietary_restrictions: ["vegetarian", "gluten-free", "dairy-free"],
  allergens: ["peanuts", "shellfish", "tree_nuts"],
  disliked_foods: ["olives", "cilantro"],
  preferred_cuisines: ["korean", "italian", "japanese"],
  wellness_goals: ["improve_sleep", "reduce_stress", "weight_loss"],
  notification_preferences: {
    meal_reminders: true,
    wellness_tips: true,
    recipe_suggestions: false,
    time_preferences: {
      breakfast: "08:00",
      lunch: "12:00",
      dinner: "19:00"
    }
  },
  ui_preferences: {
    theme: "light",  // or "dark"
    language: "en",
    units: "metric"  // or "imperial"
  },
  created_at: ISODate("2025-11-10T12:00:00Z"),
  updated_at: ISODate("2025-11-10T14:30:00Z")
}
```

**Indexes**:
```javascript
db.user_preferences.createIndex({ user_id: 1 }, { unique: true });
db.user_preferences.createIndex({ dietary_restrictions: 1 });
```

#### 3.3.2 emotion_time_series

```javascript
{
  _id: ObjectId("..."),
  user_id: "uuid",
  timestamp: ISODate("2025-11-10T14:30:00Z"),
  heart_rate: 72,  // bpm
  hrv: 65,  // ms
  emotion: "calm",  // Derived from HRV/HR
  confidence: 0.85,
  source: "apple_watch",  // or "fitbit", "garmin", etc.
  raw_data: {  // Original data for auditing
    sdnn: 50,
    rmssd: 40,
    pnn50: 20
  }
}
```

**Indexes**:
```javascript
db.emotion_time_series.createIndex({ user_id: 1, timestamp: -1 });
db.emotion_time_series.createIndex({ timestamp: -1 });

// TTL index: Auto-delete after 90 days
db.emotion_time_series.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 7776000 }  // 90 days
);
```

**Time Series Optimization**:
- Use MongoDB time series collections (5.0+) for better compression
- Downsample to hourly aggregates after 30 days
- Delete raw data after 90 days (GDPR compliance)

#### 3.3.3 recipe_ratings

```javascript
{
  _id: ObjectId("..."),
  user_id: "uuid",
  recipe_id: "recipe-123",
  rating: 5,  // 1-5 stars
  comment: "Delicious and easy to make!",
  tags: ["quick", "healthy", "family-friendly"],
  preparation_time_actual: 25,  // minutes (vs recipe estimate)
  difficulty_actual: "easy",  // vs recipe difficulty
  created_at: ISODate("2025-11-10T19:00:00Z"),
  updated_at: ISODate("2025-11-10T19:00:00Z")
}
```

**Indexes**:
```javascript
db.recipe_ratings.createIndex({ recipe_id: 1 });
db.recipe_ratings.createIndex({ user_id: 1 });
db.recipe_ratings.createIndex({ user_id: 1, recipe_id: 1 }, { unique: true });
```

### 3.4 Redis Key Patterns

#### 3.4.1 Session Management

```
Key Pattern: session:{token_id}
Value: JSON string with user info
TTL: 3600 seconds (1 hour)

Example:
Key: session:abc123def456
Value: {"user_id": "uuid", "email": "user@example.com", "tier": "premium"}
TTL: 3600
```

```python
# Set session
await redis.setex(
    f"session:{token_id}",
    3600,
    json.dumps({"user_id": user_id, "email": email, "tier": tier})
)

# Get session
session_data = await redis.get(f"session:{token_id}")
if session_data:
    user_info = json.loads(session_data)
```

#### 3.4.2 Rate Limiting

```
Key Pattern: rate_limit:{user_id}:{window}
Value: Integer (request count)
TTL: 86400 seconds (24 hours for daily limit)

Example:
Key: rate_limit:user123:2025-11-10
Value: 3
TTL: 86400 (resets at midnight)
```

```python
# Check rate limit
key = f"rate_limit:{user_id}:{date.today()}"
count = await redis.incr(key)

if count == 1:
    # First request of the day, set TTL
    await redis.expire(key, 86400)

if count > FREE_TIER_DAILY_LIMIT:
    raise RateLimitError("Daily limit exceeded")
```

#### 3.4.3 Cache

```
Key Pattern: cache:{endpoint}:{params_hash}
Value: JSON response
TTL: Varies by data type

Examples:
- cache:nutrition:apple → 604800 (7 days)
- cache:recipes:korean_chicken → 86400 (1 day)
- cache:wellness:user123:today → 3600 (1 hour)
```

#### 3.4.4 Token Revocation (Blacklist)

```
Key Pattern: revoked:{token_id}
Value: "1" (or any value, existence is what matters)
TTL: Same as original token expiry

Example:
Key: revoked:abc123def456
Value: "1"
TTL: 3600 (matches token expiry)
```

### 3.5 Data Modeling Best Practices

#### 3.5.1 When to Use PostgreSQL

✅ **Use PostgreSQL when**:
- Data has complex relationships (foreign keys)
- ACID transactions required
- Complex queries with JOINs
- Data integrity is critical

**Examples**: User accounts, payments, food history with user relationship

#### 3.5.2 When to Use MongoDB

✅ **Use MongoDB when**:
- Schema varies frequently
- High write throughput needed
- Data is hierarchical/nested
- Horizontal scaling required

**Examples**: User preferences (flexible), emotion time series (high writes), recipe ratings

#### 3.5.3 When to Use Redis

✅ **Use Redis when**:
- Data is temporary/ephemeral
- Sub-millisecond access required
- Atomic operations needed
- TTL (time-to-live) required

**Examples**: Sessions, rate limiting, caching, pub/sub

### 3.6 Data Versioning

**Problem**: API evolves, client apps can't always update immediately

**Solution**: Version database schemas and maintain compatibility

```python
# In SQLAlchemy models
class FoodHistory(Base):
    __tablename__ = "food_history"

    schema_version = Column(Integer, default=1)  # Track schema version

    # V1: detected_foods as simple array
    # V2: detected_foods with confidence scores
    # V3: detected_foods with quantities
```

**Migration Strategy**:
1. Add new fields as nullable
2. Backfill old records with default values
3. Update application code to use new fields
4. Make fields non-nullable after backfill
5. Remove old fields in next major version

---

## 4. API Design

### 4.1 RESTful Principles

We follow REST (Representational State Transfer) principles:

| Principle | Implementation |
|-----------|---------------|
| **Resource-based** | URLs represent resources (nouns), not actions |
| **HTTP Methods** | GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove) |
| **Stateless** | Each request contains all necessary information (JWT token) |
| **Cacheable** | Responses marked as cacheable where appropriate |
| **Layered** | Client doesn't know if connected directly to backend or intermediary |

### 4.2 API Versioning

**URL Versioning**: `/api/v1/resource`

**Why URL versioning**:
- ✅ Simple and explicit
- ✅ Easy to route different versions to different servers
- ✅ Visible in browser/logs

**Alternatives Considered**:
- Header versioning (`Accept: application/vnd.psi.v1+json`) - Rejected: Less visible
- Query parameter (`/api/resource?version=1`) - Rejected: Pollutes URL

**Backward Compatibility Promise**:
- V1 API remains stable (no breaking changes)
- New fields added as optional
- Deprecated fields marked in docs but still functional
- V2 API introduced when breaking changes needed

### 4.3 Endpoint Design Patterns

#### 4.3.1 Resource Naming Conventions

**Rules**:
1. Use plural nouns for collections (`/users`, not `/user`)
2. Use kebab-case for multi-word resources (`/food-items`, not `/foodItems`)
3. Nest resources logically (max 2 levels)

**Examples**:
```
✅ GET  /api/v1/users/{user_id}
✅ GET  /api/v1/users/{user_id}/food-history
✅ POST /api/v1/food/upload
❌ GET  /api/v1/getUser/{user_id}  # Don't use verbs
❌ GET  /api/v1/users/{user_id}/food-history/{food_id}/nutrition/{nutrient_id}  # Too deep
```

#### 4.3.2 HTTP Method Usage

| Method | Purpose | Idempotent | Safe | Example |
|--------|---------|------------|------|---------|
| **GET** | Retrieve resource(s) | ✅ | ✅ | GET /users/{id} |
| **POST** | Create resource | ❌ | ❌ | POST /users |
| **PUT** | Replace resource | ✅ | ❌ | PUT /users/{id} |
| **PATCH** | Update resource partially | ❌ | ❌ | PATCH /users/{id} |
| **DELETE** | Remove resource | ✅ | ❌ | DELETE /users/{id} |

**Idempotent**: Multiple identical requests have same effect as single request
**Safe**: Request doesn't modify server state

#### 4.3.3 Status Code Usage

| Code | Meaning | When to Use |
|------|---------|-------------|
| **200 OK** | Success | GET, PUT, PATCH with response body |
| **201 Created** | Resource created | POST success |
| **204 No Content** | Success, no body | DELETE success, PUT with no response |
| **400 Bad Request** | Invalid input | Validation errors |
| **401 Unauthorized** | Missing/invalid auth | No token or expired token |
| **403 Forbidden** | Insufficient permissions | Valid token but no access |
| **404 Not Found** | Resource doesn't exist | GET/PUT/PATCH/DELETE non-existent resource |
| **409 Conflict** | Resource conflict | Email already exists |
| **422 Unprocessable Entity** | Semantic errors | Valid JSON but business logic failure |
| **429 Too Many Requests** | Rate limit exceeded | Free tier daily limit hit |
| **500 Internal Server Error** | Server error | Unhandled exceptions |
| **503 Service Unavailable** | Temporary unavailability | Database down, maintenance mode |

### 4.4 Request/Response Formats

#### 4.4.1 Request Format

**Authentication**:
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Authenticated Request**:
```
GET /api/v1/food/history
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**File Upload**:
```
POST /api/v1/food/upload
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="food.jpg"
Content-Type: image/jpeg

[binary image data]
------WebKitFormBoundary--
```

#### 4.4.2 Response Format

**Success Response**:
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "subscription_tier": "premium"
  },
  "meta": {
    "timestamp": "2025-11-10T14:30:00Z"
  }
}
```

**List Response with Pagination**:
```json
{
  "data": [
    {"id": "1", "name": "Item 1"},
    {"id": "2", "name": "Item 2"}
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "first": "/api/v1/food/history?page=1",
    "prev": null,
    "next": "/api/v1/food/history?page=2",
    "last": "/api/v1/food/history?page=8"
  }
}
```

**Error Response** (Standardized):
```json
{
  "error": {
    "code": "PSI-AUTH-1002",
    "message": "Invalid credentials",
    "user_message": "The email or password you entered is incorrect.",
    "type": "AuthenticationError",
    "details": {
      "field": "email",
      "retryable": true
    }
  },
  "meta": {
    "timestamp": "2025-11-10T14:30:00Z",
    "request_id": "abc-123-def"
  }
}
```

### 4.5 Pagination

**Query Parameters**:
```
GET /api/v1/food/history?page=2&per_page=20&sort=-created_at
```

**Parameters**:
- `page`: Page number (1-indexed, default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `sort`: Sort field (prefix `-` for descending)

**Implementation**:
```python
from fastapi import Query

@router.get("/food/history")
async def get_food_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at"),
    current_user: User = Depends(verify_token)
):
    offset = (page - 1) * per_page

    query = select(FoodHistory).where(FoodHistory.user_id == current_user.id)

    # Sorting
    if sort.startswith("-"):
        query = query.order_by(desc(getattr(FoodHistory, sort[1:])))
    else:
        query = query.order_by(asc(getattr(FoodHistory, sort)))

    # Pagination
    query = query.offset(offset).limit(per_page)

    results = await db.execute(query)
    items = results.scalars().all()

    # Count total
    count_query = select(func.count()).where(FoodHistory.user_id == current_user.id)
    total = await db.scalar(count_query)

    return {
        "data": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    }
```

### 4.6 Filtering & Searching

**Query Parameters**:
```
GET /api/v1/food/history?food=apple&min_calories=100&max_calories=500&date_from=2025-11-01
```

**Implementation**:
```python
@router.get("/food/history")
async def get_food_history(
    food: Optional[str] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(verify_token)
):
    query = select(FoodHistory).where(FoodHistory.user_id == current_user.id)

    # Food filter (JSONB query)
    if food:
        query = query.where(
            FoodHistory.detected_foods.op('@>')(
                f'[{{"food": "{food}"}}]'
            )
        )

    # Calorie range filter (JSONB query)
    if min_calories:
        query = query.where(
            FoodHistory.nutrition['calories'].astext.cast(Integer) >= min_calories
        )

    if max_calories:
        query = query.where(
            FoodHistory.nutrition['calories'].astext.cast(Integer) <= max_calories
        )

    # Date range filter
    if date_from:
        query = query.where(FoodHistory.created_at >= date_from)

    if date_to:
        query = query.where(FoodHistory.created_at <= date_to)

    results = await db.execute(query)
    return {"data": results.scalars().all()}
```

### 4.7 Rate Limiting

**Headers**:
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 1
X-RateLimit-Reset: 1699632000
```

**When Exceeded**:
```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 86400

{
  "error": {
    "code": "PSI-RATE-4002",
    "message": "Daily limit exceeded",
    "user_message": "You've reached your daily limit of 3 analyses. Upgrade to Premium for unlimited access!",
    "details": {
      "limit": 3,
      "reset_time": "2025-11-11T00:00:00Z",
      "upgrade_url": "/premium"
    }
  }
}
```

### 4.8 API Documentation

**Tools**:
- FastAPI automatic OpenAPI generation
- Swagger UI at `/docs`
- ReDoc at `/redoc`

**Enhanced with**:
```python
@router.post(
    "/food/upload",
    response_model=FoodAnalysisResponse,
    status_code=201,
    summary="Upload and analyze food image",
    description="""
    Upload a food image for AI-powered analysis.

    **Process**:
    1. Image validated (max 10MB, JPG/PNG only)
    2. YOLO detects food items (2-3 seconds)
    3. Claude provides detailed description
    4. Nutrition looked up in USDA database
    5. Analysis saved to history

    **Rate Limits**:
    - Free tier: 3 analyses per day
    - Premium: Unlimited
    """,
    responses={
        201: {"description": "Analysis successful", "model": FoodAnalysisResponse},
        400: {"description": "Invalid image format"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "AI service unavailable"}
    },
    tags=["Food Analysis"]
)
async def upload_food(
    file: UploadFile = File(..., description="Food image (JPG/PNG, max 10MB)"),
    current_user: User = Depends(verify_token)
):
    pass
```

---

## 5. Security Architecture

### 5.1 Threat Model

#### 5.1.1 Assets to Protect

| Asset | Confidentiality | Integrity | Availability |
|-------|----------------|-----------|--------------|
| **User Credentials** | Critical | Critical | High |
| **Health Data (HRV, HR)** | Critical | High | Medium |
| **Food Images** | Medium | Low | Medium |
| **API Keys** | Critical | Critical | High |
| **Database** | Critical | Critical | Critical |

#### 5.1.2 Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| **Script Kiddie** | Low | Curiosity, bragging rights |
| **Competitor** | Medium | Steal data/algorithms |
| **Organized Crime** | High | Financial gain (sell health data) |
| **Nation State** | Very High | Espionage, disruption |

#### 5.1.3 Attack Vectors

```
┌─────────────────────────────────────────────────────────┐
│                 STRIDE Threat Model                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Spoofing Identity                                      │
│  • Attacker impersonates legitimate user               │
│  • Mitigation: JWT authentication, 2FA (future)        │
│                                                         │
│  Tampering with Data                                    │
│  • Attacker modifies food history, wellness scores     │
│  • Mitigation: HTTPS, input validation, HMAC           │
│                                                         │
│  Repudiation                                            │
│  • User denies action (e.g., deleting account)         │
│  • Mitigation: Audit logs, database triggers           │
│                                                         │
│  Information Disclosure                                 │
│  • Attacker accesses sensitive health data             │
│  • Mitigation: Encryption, access controls, RBAC       │
│                                                         │
│  Denial of Service                                      │
│  • Attacker overwhelms API with requests               │
│  • Mitigation: Rate limiting, DDoS protection, WAF     │
│                                                         │
│  Elevation of Privilege                                 │
│  • Attacker gains admin access                         │
│  • Mitigation: RBAC, principle of least privilege      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Authentication & Authorization

#### 5.2.1 Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│              JWT Authentication Flow                    │
└─────────────────────────────────────────────────────────┘

1. User Registration
   ─────────────────
   Client                    Backend                Database
     │                         │                      │
     │ POST /auth/register     │                      │
     │ {email, password}       │                      │
     ├────────────────────────>│                      │
     │                         │ Hash password        │
     │                         │ (bcrypt, cost=12)    │
     │                         │                      │
     │                         │ INSERT INTO users    │
     │                         ├─────────────────────>│
     │                         │                      │
     │                         │<─────────────────────┤
     │ 201 Created             │                      │
     │ {user_id, email}        │                      │
     │<────────────────────────┤                      │
     │                         │                      │

2. User Login
   ─────────────
   Client                    Backend                Database        Redis
     │                         │                      │               │
     │ POST /auth/login        │                      │               │
     │ {email, password}       │                      │               │
     ├────────────────────────>│                      │               │
     │                         │ SELECT * FROM users  │               │
     │                         ├─────────────────────>│               │
     │                         │<─────────────────────┤               │
     │                         │                      │               │
     │                         │ Verify password      │               │
     │                         │ (bcrypt.verify)      │               │
     │                         │                      │               │
     │                         │ Generate JWT         │               │
     │                         │ (HS256, 1h expiry)   │               │
     │                         │                      │               │
     │                         │ Store session        │               │
     │                         ├─────────────────────────────────────>│
     │                         │ SET session:{token_id} {user_info}  │
     │                         │ EX 3600              │               │
     │                         │                      │               │
     │ 200 OK                  │                      │               │
     │ {access_token, ...}     │                      │               │
     │<────────────────────────┤                      │               │
     │                         │                      │               │

3. Authenticated Request
   ─────────────────────
   Client                    Backend                Redis
     │                         │                      │
     │ GET /food/history       │                      │
     │ Authorization: Bearer   │                      │
     │  eyJhbGciOiJIUzI1...    │                      │
     ├────────────────────────>│                      │
     │                         │ Verify JWT signature │
     │                         │ (HMAC-SHA256)        │
     │                         │                      │
     │                         │ Check expiry         │
     │                         │ (exp claim)          │
     │                         │                      │
     │                         │ Check revocation     │
     │                         ├─────────────────────>│
     │                         │ GET revoked:{token}  │
     │                         │<─────────────────────┤
     │                         │                      │
     │                         │ Extract user_id      │
     │                         │ from JWT payload     │
     │                         │                      │
     │                         │ [Process request]    │
     │                         │                      │
     │ 200 OK                  │                      │
     │ {data: [...]}           │                      │
     │<────────────────────────┤                      │
     │                         │                      │

4. Logout (Token Revocation)
   ──────────────────────────
   Client                    Backend                Redis
     │                         │                      │
     │ POST /auth/logout       │                      │
     │ Authorization: Bearer   │                      │
     ├────────────────────────>│                      │
     │                         │ Extract token_id     │
     │                         │ and expiry from JWT  │
     │                         │                      │
     │                         │ Add to blacklist     │
     │                         ├─────────────────────>│
     │                         │ SET revoked:{token}  │
     │                         │ EX {remaining_ttl}   │
     │                         │<─────────────────────┤
     │                         │                      │
     │ 204 No Content          │                      │
     │<────────────────────────┤                      │
     │                         │                      │
```

#### 5.2.2 JWT Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "tier": "premium",
    "iat": 1699632000,
    "exp": 1699635600,
    "jti": "token-unique-id"
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

**Claims**:
- `sub` (subject): User ID
- `email`: User email (for convenience)
- `tier`: Subscription tier (free, premium, admin)
- `iat` (issued at): Token creation timestamp
- `exp` (expiry): Token expiration timestamp (1 hour from `iat`)
- `jti` (JWT ID): Unique token ID (for revocation)

#### 5.2.3 Role-Based Access Control (RBAC)

```python
from enum import Enum
from fastapi import Depends, HTTPException

class Role(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

def require_role(*allowed_roles: Role):
    """Dependency to check if user has required role"""
    def role_checker(current_user: User = Depends(verify_token)):
        if current_user.subscription_tier not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": {
                        "code": "PSI-AUTH-1007",
                        "message": "Insufficient permissions",
                        "user_message": "This feature requires a Premium subscription."
                    }
                }
            )
        return current_user
    return role_checker

# Usage:
@router.get("/premium-feature", dependencies=[Depends(require_role(Role.PREMIUM, Role.ADMIN))])
async def premium_feature():
    return {"message": "This is a premium feature"}
```

### 5.3 Data Security

#### 5.3.1 Encryption at Rest

| Data Type | Encryption Method | Key Management |
|-----------|-------------------|---------------|
| **Database** | AES-256 (transparent encryption) | AWS RDS managed keys |
| **Passwords** | bcrypt (cost factor 12) | N/A (one-way hash) |
| **API Keys** | AES-256-GCM | AWS Secrets Manager |
| **Images (S3)** | AES-256 | AWS S3 managed keys (SSE-S3) |

**Implementation**:
```python
# Password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # bcrypt with automatic salt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 5.3.2 Encryption in Transit

- **HTTPS/TLS 1.3**: All API traffic encrypted
- **Certificate**: Let's Encrypt or commercial CA
- **HSTS**: Enforce HTTPS (Strict-Transport-Security header)
- **Database Connections**: SSL/TLS required

**Nginx Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.psi-app.com;

    # SSL/TLS
    ssl_certificate /etc/letsencrypt/live/api.psi-app.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.psi-app.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Other security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    location / {
        proxy_pass http://backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 5.3.3 Data Minimization

**Principle**: Collect only what's necessary

| Data | Necessary? | Reason |
|------|-----------|--------|
| Email | ✅ | Authentication, communication |
| Name | ✅ | Personalization |
| Password (hashed) | ✅ | Authentication |
| Phone Number | ❌ | Not required (future: 2FA) |
| Date of Birth | ❌ | Not required (age verification in future) |
| HRV, Heart Rate | ✅ | Core feature (emotion tracking) |
| GPS Location | ❌ | Not required |

### 5.4 Input Validation

#### 5.4.1 Request Validation (Pydantic)

```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserRegistration(BaseModel):
    email: EmailStr  # Validates email format
    password: constr(min_length=8, max_length=100)  # Length constraints
    name: constr(min_length=1, max_length=255)

    @validator('password')
    def password_strength(cls, v):
        """Ensure password has minimum complexity"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v
```

**Automatic Validation**:
- Type checking (string, int, float, datetime, etc.)
- Format validation (email, URL, UUID, etc.)
- Range validation (min, max, ge, le)
- Custom validators (regex, business rules)

#### 5.4.2 SQL Injection Prevention

✅ **Always use parameterized queries**:
```python
# Safe: Parameterized query
query = "SELECT * FROM users WHERE email = $1"
result = await db.fetch_one(query, email)

# Unsafe: String concatenation (NEVER DO THIS)
query = f"SELECT * FROM users WHERE email = '{email}'"  # ❌ VULNERABLE
```

✅ **Use ORM (SQLAlchemy)**:
```python
# Safe: SQLAlchemy automatically parameterizes
query = select(User).where(User.email == email)
result = await db.execute(query)
```

#### 5.4.3 XSS Prevention

- **Input Sanitization**: Strip HTML tags from user input
- **Output Encoding**: Encode special characters in responses
- **Content-Security-Policy**: Restrict script sources

```python
import bleach

def sanitize_html(text: str) -> str:
    """Remove all HTML tags"""
    return bleach.clean(text, tags=[], strip=True)

# Usage:
user_comment = sanitize_html(request_data['comment'])
```

#### 5.4.4 CSRF Prevention

**Token-based CSRF protection** (for web):
- Double-submit cookie pattern
- SameSite cookie attribute

```python
from fastapi import Cookie, HTTPException

@router.post("/api/v1/action")
async def action(
    csrf_token: str = Cookie(...),
    csrf_header: str = Header(..., alias="X-CSRF-Token")
):
    if csrf_token != csrf_header:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # Process request
```

**Note**: Mobile apps use JWT in Authorization header, not cookies, so CSRF doesn't apply.

### 5.5 Rate Limiting

**Implementation**:
```python
from fastapi import Request, HTTPException
from app.core.cache import redis_client

async def rate_limit_middleware(request: Request, call_next):
    """
    Global rate limiting middleware
    """
    # Skip for non-API endpoints
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    # Get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)

    if user:
        # Per-user rate limit
        key = f"rate_limit:user:{user.id}:minute"
        count = await redis_client.incr(key)

        if count == 1:
            await redis_client.expire(key, 60)  # 1 minute window

        if count > 100:  # 100 requests per minute
            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "code": "PSI-RATE-4001",
                        "message": "Rate limit exceeded",
                        "user_message": "Too many requests. Please try again in a minute."
                    }
                }
            )
    else:
        # Per-IP rate limit (for unauthenticated requests)
        client_ip = request.client.host
        key = f"rate_limit:ip:{client_ip}:minute"
        count = await redis_client.incr(key)

        if count == 1:
            await redis_client.expire(key, 60)

        if count > 20:  # 20 requests per minute per IP
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(100 - count)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

    return response
```

### 5.6 Secrets Management

**Never commit secrets to Git**:
```bash
# .gitignore
.env
.env.local
.env.production
secrets/
*.pem
*.key
credentials.json
```

**Production Secrets Management**:
```python
# AWS Secrets Manager
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage:
secrets = get_secret('psi/prod/database')
DATABASE_URL = f"postgresql://{secrets['username']}:{secrets['password']}@{secrets['host']}/{secrets['database']}"
```

### 5.7 Compliance

#### 5.7.1 GDPR (EU Users)

**Requirements**:
1. ✅ **Consent**: Users must explicitly consent to data collection
2. ✅ **Right to Access**: Users can download their data
3. ✅ **Right to Deletion**: Users can delete their account and all data
4. ✅ **Data Portability**: Users can export data in machine-readable format (JSON)
5. ✅ **Privacy Policy**: Clear explanation of data usage
6. ✅ **Data Breach Notification**: Must notify within 72 hours

**Implementation**:
```python
@router.get("/users/me/data-export")
async def export_user_data(current_user: User = Depends(verify_token)):
    """
    GDPR Article 20: Right to data portability
    """
    user_data = {
        "user": {...},
        "food_history": [...],
        "wellness_scores": [...],
        "preferences": {...}
    }

    return JSONResponse(content=user_data, headers={
        "Content-Disposition": f"attachment; filename=psi_data_{current_user.id}.json"
    })

@router.delete("/users/me")
async def delete_account(current_user: User = Depends(verify_token)):
    """
    GDPR Article 17: Right to erasure
    """
    # Soft delete (mark as deleted, anonymize data)
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(
            deleted_at=datetime.utcnow(),
            email=f"deleted_{current_user.id}@deleted.local",
            password_hash="DELETED",
            name="Deleted User"
        )
    )

    # Hard delete after 30 days (cron job)
    return {"message": "Account deletion scheduled"}
```

#### 5.7.2 CCPA (California Users)

**Requirements**:
1. ✅ **Notice**: Inform users what data is collected
2. ✅ **Opt-Out**: Users can opt-out of data sale (N/A: we don't sell data)
3. ✅ **Deletion**: Users can request deletion
4. ✅ **Non-Discrimination**: Can't discriminate against users who exercise rights

#### 5.7.3 HIPAA (Health Data)

**Note**: Psi is NOT HIPAA-compliant by default.

**Why**: HIPAA requires:
- Business Associate Agreement (BAA) with cloud providers
- Extensive audit logging
- Encryption everywhere
- Physical security controls
- Regular risk assessments

**Disclaimer in App**:
```
⚠️ IMPORTANT: Psi is a wellness app and NOT a medical device.
The information provided is for informational purposes only
and is not intended to diagnose, treat, cure, or prevent any
disease. Always consult with a qualified healthcare provider
before making any health-related decisions.
```

---

## 6. Infrastructure

### 6.1 Deployment Architecture (AWS)

```
┌──────────────────────────────────────────────────────────┐
│                     Route 53 (DNS)                        │
│              api.psi-app.com → CloudFront                 │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│              CloudFront (CDN) + WAF                       │
│  • SSL Termination                                        │
│  • DDoS Protection (AWS Shield)                           │
│  • WAF Rules (SQL injection, XSS blocking)                │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│         Application Load Balancer (ALB)                   │
│  • Health Checks (/health endpoint)                       │
│  • Traffic Distribution (Round Robin)                     │
│  • Sticky Sessions (disabled for stateless API)           │
└───────────┬────────────────────────┬──────────────────────┘
            │                        │
     ┌──────▼──────┐         ┌───────▼─────┐
     │ Availability │         │ Availability│
     │   Zone 1a    │         │   Zone 1b   │
     └──────┬───────┘         └───────┬─────┘
            │                         │
┌───────────▼─────────────┬───────────▼───────────────┐
│  ECS Fargate Cluster    │   ECS Fargate Cluster     │
│  ┌──────────────────┐   │   ┌──────────────────┐    │
│  │  Backend Task 1  │   │   │  Backend Task 3  │    │
│  │  (2 vCPU, 4GB)   │   │   │  (2 vCPU, 4GB)   │    │
│  └──────────────────┘   │   └──────────────────┘    │
│  ┌──────────────────┐   │   ┌──────────────────┐    │
│  │  Backend Task 2  │   │   │  Backend Task 4  │    │
│  └──────────────────┘   │   └──────────────────┘    │
└─────────────┬───────────┴───────────┬───────────────┘
              │                       │
       ┌──────▼───────────────────────▼──────┐
       │    VPC (Virtual Private Cloud)      │
       │                                      │
       │  ┌──────────────────────────────┐   │
       │  │   Private Subnet (Data Tier)  │   │
       │  │                               │   │
       │  │  ┌─────────────────────────┐ │   │
       │  │  │  RDS PostgreSQL         │ │   │
       │  │  │  (Multi-AZ, db.t3.large)│ │   │
       │  │  └─────────────────────────┘ │   │
       │  │                               │   │
       │  │  ┌─────────────────────────┐ │   │
       │  │  │  DocumentDB (MongoDB)   │ │   │
       │  │  │  (3-node cluster)       │ │   │
       │  │  └─────────────────────────┘ │   │
       │  │                               │   │
       │  │  ┌─────────────────────────┐ │   │
       │  │  │  ElastiCache (Redis)    │ │   │
       │  │  │  (cache.t3.medium)      │ │   │
       │  │  └─────────────────────────┘ │   │
       │  └──────────────────────────────┘   │
       └──────────────────────────────────────┘
                        │
       ┌────────────────▼────────────────┐
       │   S3 (Image Storage)            │
       │   • Versioning enabled          │
       │   • Lifecycle: Glacier after 90d│
       └─────────────────────────────────┘
```

### 6.2 Container Architecture

**Dockerfile Multi-Stage Build**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app /app/app

# Create directories for data
RUN mkdir -p /app/data/models /app/data/usda

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Image Size Optimization**:
- Multi-stage build: 1.2 GB → 450 MB
- Slim base image: 300 MB smaller
- No cache: `--no-cache-dir` flag

---

## 7. Scalability

### 7.1 Horizontal Scaling Strategy

**Auto-Scaling Rules**:
```yaml
# ECS Service Auto-Scaling
TargetTrackingScalingPolicy:
  TargetValue: 70.0
  ScaleInCooldown: 300  # 5 minutes
  ScaleOutCooldown: 60  # 1 minute
  PredefinedMetricType: ECSServiceAverageCPUUtilization

MinCapacity: 2  # Always at least 2 instances
MaxCapacity: 20  # Scale up to 20 during peak
```

**Load Testing Results** (JMeter, 10K concurrent users):
| Metric | 2 Instances | 5 Instances | 10 Instances |
|--------|-------------|-------------|--------------|
| Throughput | 500 req/s | 1250 req/s | 2500 req/s |
| Response Time (p95) | 800ms | 450ms | 350ms |
| Error Rate | 2% | 0.1% | 0% |

**Conclusion**: Sweet spot at 5-7 instances for cost/performance balance

### 7.2 Database Scaling

#### 7.2.1 Read Replicas (PostgreSQL)

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Primary (Write) │─────>│  Replica 1 (Read)│      │  Replica 2 (Read)│
│  us-east-1a      │      │  us-east-1b      │      │  us-east-1c      │
└──────────────────┘      └──────────────────┘      └──────────────────┘
       │                          │                          │
       │ All Writes               │ Read-only                │ Read-only
       │                          │ queries                  │ queries
       │                          │                          │
       ▼                          ▼                          ▼
   Backend tasks            Backend tasks            Backend tasks
   (writes)                 (reads)                  (reads)
```

**Read/Write Split**:
```python
from sqlalchemy import create_engine

# Write (Primary)
write_engine = create_engine(WRITE_DATABASE_URL, pool_size=10)

# Read (Replicas)
read_engines = [
    create_engine(READ_REPLICA_1_URL, pool_size=20),
    create_engine(READ_REPLICA_2_URL, pool_size=20)
]

def get_read_engine():
    """Round-robin load balancing across read replicas"""
    return random.choice(read_engines)
```

#### 7.2.2 Caching Strategy

**Cache Layers**:
1. **Application Cache** (Redis): Short-lived, frequently accessed data
2. **CDN Cache** (CloudFront): Static assets, API responses (when appropriate)
3. **Browser Cache**: Client-side caching (Cache-Control headers)

**Cache Invalidation**:
```python
# Write-through cache
async def update_user_preferences(user_id: str, preferences: dict):
    # 1. Update database
    await db.execute(
        update(UserPreferences)
        .where(UserPreferences.user_id == user_id)
        .values(**preferences)
    )

    # 2. Invalidate cache
    cache_key = f"user_preferences:{user_id}"
    await redis.delete(cache_key)

    # 3. Optionally pre-warm cache
    await redis.setex(cache_key, 3600, json.dumps(preferences))
```

### 7.3 Bottleneck Analysis

**Current Bottlenecks** (as of MVP):
1. **YOLO Inference**: 2-3 seconds per image (CPU-bound)
2. **Claude API**: 1-2 seconds per request (network-bound)
3. **Database Queries**: 50-100ms (acceptable)

**Mitigation Strategies**:
- YOLO: GPU instances (T4, V100) or batching
- Claude: Parallel requests, caching common analyses
- Database: Read replicas, connection pooling, query optimization

---

## 8. Decision Records

### ADR-001: Use FastAPI for Backend

**Status**: Accepted
**Date**: 2025-10-01

**Context**: Need to choose a Python web framework for the backend API.

**Decision**: Use FastAPI

**Rationale**:
- Native async/await support (critical for AI API calls)
- Automatic OpenAPI documentation
- Type safety with Pydantic
- High performance (benchmarks show 2-3x faster than Flask)

**Consequences**:
- ✅ Faster development with auto-generated docs
- ✅ Better type safety catches bugs early
- ❌ Smaller ecosystem than Django
- ❌ Learning curve for developers unfamiliar with async

---

### ADR-002: Polyglot Persistence (PostgreSQL + MongoDB + Redis)

**Status**: Accepted
**Date**: 2025-10-05

**Context**: Need to choose database(s) for different data types.

**Decision**: Use PostgreSQL for structured data, MongoDB for semi-structured data, Redis for caching.

**Rationale**:
- PostgreSQL: ACID transactions for users, food history
- MongoDB: Flexible schema for emotion time series (high write volume)
- Redis: In-memory speed for sessions, rate limiting

**Consequences**:
- ✅ Optimal performance for each data type
- ✅ Easier to scale horizontally (MongoDB sharding)
- ❌ Increased operational complexity (3 databases to maintain)
- ❌ Need to manage data consistency across databases

---

### ADR-003: React Native + Expo for Mobile

**Status**: Accepted
**Date**: 2025-10-08

**Context**: Need to build iOS and Android apps with limited team resources.

**Decision**: Use React Native with Expo

**Rationale**:
- 90%+ code reuse across iOS and Android
- Large developer pool (JavaScript/TypeScript)
- Expo simplifies build and deployment

**Consequences**:
- ✅ Faster time to market (single codebase)
- ✅ Easier to find developers
- ❌ Performance slightly worse than native (acceptable for our use case)
- ❌ Limited access to some native APIs (workaround: eject from Expo if needed)

---

### ADR-004: JWT Authentication (not sessions)

**Status**: Accepted
**Date**: 2025-10-12

**Context**: Need to implement authentication for mobile app + API.

**Decision**: Use JWT tokens (stored in secure storage on mobile)

**Rationale**:
- Stateless (easier to scale horizontally)
- Works well with mobile apps (no cookies needed)
- Can be validated without database lookup (Redis for revocation only)

**Consequences**:
- ✅ Easy to scale (no session storage on servers)
- ✅ Works seamlessly with mobile apps
- ❌ Cannot invalidate tokens immediately (use Redis blacklist)
- ❌ Tokens can be large (include claims in payload)

---

## 9. Appendix

### 9.1 Glossary

| Term | Definition |
|------|------------|
| **ACID** | Atomicity, Consistency, Isolation, Durability (database properties) |
| **ALB** | Application Load Balancer (AWS service) |
| **CDN** | Content Delivery Network |
| **CORS** | Cross-Origin Resource Sharing |
| **CSRF** | Cross-Site Request Forgery |
| **HRV** | Heart Rate Variability |
| **JWT** | JSON Web Token |
| **ORM** | Object-Relational Mapping |
| **RBAC** | Role-Based Access Control |
| **REST** | Representational State Transfer |
| **SLA** | Service Level Agreement |
| **TF-IDF** | Term Frequency-Inverse Document Frequency |
| **TTL** | Time To Live |
| **WAF** | Web Application Firewall |
| **YOLO** | You Only Look Once (object detection algorithm) |

### 9.2 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GDPR Guidelines](https://gdpr.eu/)
- [HIPAA Guidelines](https://www.hhs.gov/hipaa/)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-10
**Next Review**: 2026-02-10 (Quarterly)
**Maintained By**: Engineering Team

---

## Feedback

This is a living document. To suggest changes:
1. Create an issue: https://github.com/yourusername/psi/issues
2. Submit a PR: Modify this document and create a pull request
3. Email: architecture@psi-app.com

**Change Log**:
- 2025-11-10: Initial version (v1.0.0)
