# Psi Developer Guide

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Target Audience**: Backend Developers, Frontend Developers, New Contributors
**Project**: Psi - Emotion-Based Wellness Platform

---

## Table of Contents

1. [Welcome](#1-welcome)
2. [Setup](#2-setup)
3. [Installation](#3-installation)
4. [Development](#4-development)
5. [Testing](#5-testing)
6. [Debugging](#6-debugging)
7. [Contributing](#7-contributing)
8. [Architecture Deep Dive](#8-architecture-deep-dive)
9. [API Development](#9-api-development)
10. [Mobile Development](#10-mobile-development)
11. [Best Practices](#11-best-practices)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Welcome

### 1.1 About Psi

**Psi** (사이, pronounced "sigh") is an innovative emotion-based wellness platform that combines:

- 🍽️ **AI-Powered Food Analysis** - YOLO v8 + Claude Vision for 96%+ accuracy
- ❤️ **Real-Time Emotion Monitoring** - HRV and heart rate analysis from wearables
- 🧠 **Neuroscience-Based Recommendations** - Psychology-backed wellness insights
- 📊 **Comprehensive Nutrition Tracking** - 62+ nutrients tracked

### 1.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI (Python 3.11+) | REST API server |
| **Mobile** | React Native (0.73) + Expo | iOS & Android apps |
| **Databases** | PostgreSQL 15, MongoDB 7, Redis 7 | Data persistence & caching |
| **AI/ML** | YOLO v8, Claude API | Food detection & vision analysis |
| **Infrastructure** | Docker, Kubernetes | Containerization & orchestration |

### 1.3 Repository Structure

```
Psi/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API routes (auth, food, fridge, wellness)
│   │   ├── core/              # Configuration, security, database
│   │   ├── models/            # SQLAlchemy & Pydantic models
│   │   ├── services/          # Business logic (YOLO, Claude, nutrition)
│   │   └── main.py            # Application entry point
│   ├── tests/                 # Backend tests (unit, integration)
│   ├── scripts/               # Utility scripts (train YOLO, etc.)
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   ├── pytest.ini             # Test configuration
│   └── .env.example           # Environment variable template
│
├── mobile/                    # React Native app
│   ├── src/
│   │   ├── screens/           # App screens (Login, FoodUpload, etc.)
│   │   ├── components/        # Reusable UI components
│   │   ├── services/          # API client & business logic
│   │   ├── store/             # Redux state management
│   │   ├── navigation/        # React Navigation config
│   │   └── theme/             # Design system (colors, typography)
│   ├── App.tsx                # App entry point
│   ├── package.json           # Node dependencies
│   └── app.json               # Expo configuration
│
├── data/                      # Data & ML models
│   ├── models/                # YOLO model files (*.pt)
│   ├── datasets/              # Training data
│   └── usda/                  # USDA nutrition database (SQLite)
│
├── deployment/                # Deployment configurations
│   ├── docker/                # Dockerfiles & docker-compose
│   └── kubernetes/            # K8s manifests (future)
│
├── docs/                      # Documentation
│   ├── API_DOCUMENTATION.md   # API reference
│   ├── DEPLOYMENT_CHECKLIST.md # Pre-deployment checklist
│   ├── OPERATIONS_MANUAL.md   # Operations guide
│   └── DEVELOPER_GUIDE.md     # This document
│
├── .gitignore                 # Git ignore rules
└── README.md                  # Project overview
```

### 1.4 Quick Links

- **GitHub Repository**: https://github.com/yourusername/psi
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Issue Tracker**: https://github.com/yourusername/psi/issues
- **Slack Channel**: #psi-dev
- **Design Figma**: https://figma.com/psi-design

---

## 2. Setup

### 2.1 Prerequisites

Before you begin, ensure you have the following installed:

#### 2.1.1 Required Software

| Software | Version | Download | Purpose |
|----------|---------|----------|---------|
| **Python** | 3.11+ | https://www.python.org/downloads/ | Backend runtime |
| **Node.js** | 18+ (LTS) | https://nodejs.org/ | Mobile app development |
| **Git** | 2.30+ | https://git-scm.com/downloads | Version control |
| **Docker** | 24.0+ | https://www.docker.com/get-started | Containerization |
| **Docker Compose** | 2.0+ | Included with Docker Desktop | Multi-container orchestration |

**Verify installations**:
```bash
python --version      # Should show 3.11.x or higher
node --version        # Should show v18.x.x or higher
npm --version         # Should show 9.x.x or higher
git --version         # Should show 2.30.x or higher
docker --version      # Should show 24.0.x or higher
docker-compose --version  # Should show 2.x.x or higher
```

#### 2.1.2 Optional but Recommended

| Tool | Purpose | Installation |
|------|---------|--------------|
| **VS Code** | Recommended IDE | https://code.visualstudio.com/ |
| **Postman** | API testing | https://www.postman.com/downloads/ |
| **pgAdmin** | PostgreSQL GUI | https://www.pgadmin.org/download/ |
| **MongoDB Compass** | MongoDB GUI | https://www.mongodb.com/products/compass |
| **Redis Commander** | Redis GUI | `npm install -g redis-commander` |

#### 2.1.3 VS Code Extensions (Recommended)

Install these extensions for the best development experience:

```json
{
  "recommendations": [
    "ms-python.python",               // Python IntelliSense
    "ms-python.vscode-pylance",       // Python language server
    "ms-python.black-formatter",      // Python formatter
    "charliermarsh.ruff",             // Python linter
    "ms-azuretools.vscode-docker",    // Docker support
    "cweijan.vscode-postgresql-client2",  // PostgreSQL client
    "dsznajder.es7-react-js-snippets",    // React snippets
    "esbenp.prettier-vscode",         // Code formatter
    "dbaeumer.vscode-eslint",         // JavaScript linter
    "ms-vscode.makefile-tools"        // Makefile support
  ]
}
```

### 2.2 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 8 GB | 16+ GB |
| **Disk Space** | 20 GB free | 50+ GB free |
| **OS** | Windows 10, macOS 10.15, Ubuntu 20.04 | Latest stable |

### 2.3 Account Setup

#### 2.3.1 Required Accounts

1. **GitHub Account**
   - Sign up: https://github.com/join
   - Fork the repository: https://github.com/yourusername/psi
   - Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
   - Add to GitHub: Settings → SSH and GPG keys

2. **Claude API Key** (Anthropic)
   - Sign up: https://console.anthropic.com/
   - Generate API key: Settings → API Keys
   - Pricing: Free tier available, then pay-as-you-go

#### 2.3.2 Optional Accounts

3. **AWS Account** (for S3 image storage in production)
   - Sign up: https://aws.amazon.com/
   - Create IAM user with S3 access
   - Generate access key and secret

### 2.4 Code Editor Configuration

#### 2.4.1 VS Code Settings

Create `.vscode/settings.json` in project root:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true,
    "**/node_modules": true
  }
}
```

#### 2.4.2 EditorConfig

`.editorconfig`:
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{py,js,ts,tsx,json,yml,yaml}]
indent_style = space
indent_size = 4

[*.{js,ts,tsx,json}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

---

## 3. Installation

### 3.1 Clone Repository

```bash
# Clone your fork
git clone git@github.com:YOUR_USERNAME/psi.git
cd psi

# Add upstream remote (to sync with main repo)
git remote add upstream git@github.com:original-owner/psi.git

# Verify remotes
git remote -v
# origin    git@github.com:YOUR_USERNAME/psi.git (fetch)
# origin    git@github.com:YOUR_USERNAME/psi.git (push)
# upstream  git@github.com:original-owner/psi.git (fetch)
# upstream  git@github.com:original-owner/psi.git (push)
```

### 3.2 Backend Setup

#### 3.2.1 Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# Verify activation (should show path to venv)
which python  # macOS/Linux
where python  # Windows
```

#### 3.2.2 Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list

# Install development dependencies (optional)
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

**Common Dependencies** (from `requirements.txt`):
```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Databases
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pymongo==4.6.1
redis==5.0.1

# AI/ML
anthropic==0.18.0
ultralytics==8.1.0
opencv-python==4.9.0.80
numpy==1.26.3

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

#### 3.2.3 Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required `.env` Configuration**:
```bash
# API Settings
SECRET_KEY=your-random-secret-key-min-32-chars-long-abc123xyz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# PostgreSQL Database (local development)
POSTGRES_SERVER=localhost
POSTGRES_USER=psi_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=psi_db

# MongoDB (local development)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=psi

# Redis (local development)
REDIS_HOST=localhost
REDIS_PORT=6379

# External APIs
CLAUDE_API_KEY=sk-ant-api-your-actual-key-here
USDA_API_KEY=  # Optional, using local DB

# YOLO Model
YOLO_MODEL_PATH=data/models/psi_food_best.pt
YOLO_CONFIDENCE_THRESHOLD=0.5

# CORS Origins
ALLOWED_ORIGINS=http://localhost:3000,exp://localhost:19000

# Rate Limiting
FREE_TIER_DAILY_LIMIT=3
```

**Generate SECRET_KEY**:
```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Using online generator
# https://generate-secret.vercel.app/32
```

#### 3.2.4 Start Databases with Docker

```bash
# Navigate to deployment directory
cd ../deployment/docker

# Start PostgreSQL, MongoDB, and Redis
docker-compose up -d postgres mongodb redis

# Verify containers are running
docker-compose ps
# Should show:
#   psi_postgres   Up (healthy)
#   psi_mongodb    Up (healthy)
#   psi_redis      Up (healthy)

# View logs
docker-compose logs -f postgres
# Press Ctrl+C to stop following logs

# Wait for health checks to pass (30 seconds)
sleep 30
docker-compose ps  # All should show "healthy"
```

#### 3.2.5 Initialize Databases

```bash
cd ../../backend

# Create PostgreSQL database and tables
psql -h localhost -U psi_user -d psi_db

# If psql not installed, use Docker:
docker exec -it psi_postgres psql -U psi_user -d psi_db

# In psql prompt:
\l  # List databases
\dt  # List tables (should be empty initially)
\q  # Quit
```

#### 3.2.6 Run Database Migrations

```bash
# Initialize Alembic (if not already initialized)
alembic init alembic  # Skip if alembic/ already exists

# Run migrations
alembic upgrade head

# Verify
alembic current
# Should show: <revision_id> (head)

# View migration history
alembic history
```

#### 3.2.7 Download YOLO Model

The YOLO model is not included in the repository (large file). You need to:

**Option 1: Use Pre-trained Model**
```bash
# Create models directory
mkdir -p ../data/models

# Download from team (ask in Slack #psi-dev)
# Or use a placeholder for testing
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O ../data/models/psi_food_best.pt
```

**Option 2: Train Your Own** (Advanced)
```bash
python scripts/train_yolo.py --epochs 100 --data food_dataset.yaml
```

### 3.3 Frontend (Mobile) Setup

#### 3.3.1 Install Node Dependencies

```bash
cd ../mobile

# Install dependencies
npm install

# Or use Yarn
yarn install

# Verify installation
npm list --depth=0
```

**Key Dependencies** (from `package.json`):
```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.73.0",
    "expo": "~50.0.0",
    "@react-navigation/native": "^6.1.9",
    "@reduxjs/toolkit": "^2.0.1",
    "axios": "^1.6.5",
    "react-native-image-picker": "^7.1.0",
    "expo-secure-store": "~12.8.1"
  }
}
```

#### 3.3.2 Configure Environment

Create `mobile/.env`:
```bash
# API Endpoint
API_BASE_URL=http://localhost:8000/api/v1

# For iOS Simulator, use localhost
# For Android Emulator, use 10.0.2.2 instead of localhost
# For physical device, use your computer's local IP (e.g., 192.168.1.100)

# API Keys
SENTRY_DSN=  # Optional, for error tracking
ANALYTICS_KEY=  # Optional, for analytics
```

#### 3.3.3 iOS Setup (macOS only)

```bash
# Install CocoaPods
sudo gem install cocoapods

# Navigate to iOS directory
cd ios

# Install iOS dependencies
pod install

# Return to mobile root
cd ..
```

#### 3.3.4 Android Setup

```bash
# Install Android Studio (if not already)
# Download: https://developer.android.com/studio

# Set ANDROID_HOME environment variable
# Add to ~/.bashrc or ~/.zshrc:
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

### 3.4 Verify Installation

#### 3.4.1 Backend Health Check

```bash
cd backend

# Start backend server
uvicorn app.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "mongodb": "connected"
}

# Open API documentation in browser
# http://localhost:8000/docs
```

#### 3.4.2 Frontend Health Check

```bash
cd mobile

# Start Expo development server
npm start

# Expected output:
› Metro waiting on exp://localhost:19000
› Scan the QR code above with Expo Go (Android) or Camera (iOS)

# Press 'w' to open web version
# Press 'i' to open iOS simulator
# Press 'a' to open Android emulator
```

### 3.5 Troubleshooting Installation

#### Issue: `ModuleNotFoundError`

```bash
# Ensure virtual environment is activated
which python  # Should show path to venv

# Reinstall requirements
pip install -r requirements.txt

# Clear pip cache if needed
pip cache purge
```

#### Issue: Database connection refused

```bash
# Check if Docker containers are running
docker-compose ps

# Restart containers
docker-compose down
docker-compose up -d

# Check logs for errors
docker-compose logs postgres
```

#### Issue: Port already in use

```bash
# Find process using port 8000
# macOS/Linux:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

## 4. Development

### 4.1 Development Workflow

#### 4.1.1 Starting Development

```bash
# 1. Update your fork with latest changes
git checkout main
git pull upstream main
git push origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Start Docker services
cd deployment/docker
docker-compose up -d

# 4. Start backend
cd ../../backend
source venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. (In new terminal) Start frontend
cd mobile
npm start
```

#### 4.1.2 Daily Development Cycle

```bash
# Morning: Sync with main branch
git checkout main
git pull upstream main
git checkout feature/your-feature-name
git merge main  # Or rebase: git rebase main

# Development: Make changes
# ... edit code ...

# Run tests frequently
pytest tests/test_your_feature.py -v

# Check code style
black app/ tests/
flake8 app/ tests/

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# End of day: Open pull request (if ready)
# Go to GitHub and create PR from your fork to main repo
```

### 4.2 Code Style & Conventions

#### 4.2.1 Python Code Style (PEP 8)

We use **Black** for code formatting and **Flake8** for linting.

```bash
# Format all Python files
black backend/app backend/tests

# Check linting
flake8 backend/app backend/tests

# Type checking
mypy backend/app
```

**Naming Conventions**:
```python
# Variables and functions: snake_case
user_id = 123
def calculate_wellness_score():
    pass

# Classes: PascalCase
class UserModel:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

**Imports Order**:
```python
# 1. Standard library imports
import os
import sys
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends
from sqlalchemy import Column, Integer

# 3. Local application imports
from app.core.config import settings
from app.models.user import User
```

**Docstrings** (Google Style):
```python
def analyze_food_image(image_path: str, user_id: str) -> dict:
    """
    Analyze food image using YOLO and Claude Vision.

    Args:
        image_path: Path to uploaded image file
        user_id: Unique identifier for user

    Returns:
        dict: Analysis results containing:
            - detected_foods: List of detected food items
            - nutrition: Nutritional breakdown
            - confidence: Detection confidence score

    Raises:
        ImageProcessingError: If image cannot be processed
        APIError: If Claude API fails

    Example:
        >>> result = analyze_food_image("/tmp/food.jpg", "user_123")
        >>> print(result['detected_foods'])
        ['apple', 'banana']
    """
    # Implementation
    pass
```

#### 4.2.2 JavaScript/TypeScript Code Style

We use **Prettier** for formatting and **ESLint** for linting.

```bash
# Format all JS/TS files
npm run format

# Check linting
npm run lint

# Auto-fix linting errors
npm run lint:fix
```

**Naming Conventions**:
```typescript
// Variables and functions: camelCase
const userId = "123";
function calculateWellnessScore() {}

// Components: PascalCase
const FoodUploadScreen = () => {};

// Constants: UPPER_SNAKE_CASE
const MAX_UPLOAD_SIZE = 10 * 1024 * 1024;

// Private methods: _leadingUnderscore (or use # for true private)
function _internalHelper() {}
```

### 4.3 Git Commit Conventions

We follow **Conventional Commits** specification.

**Format**: `<type>(<scope>): <subject>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `ci`: CI/CD changes

**Examples**:
```bash
# Good commits
git commit -m "feat(auth): add token refresh mechanism"
git commit -m "fix(food): correct nutrition calculation for liquids"
git commit -m "docs(api): update food upload endpoint examples"
git commit -m "test(wellness): add emotion analysis unit tests"
git commit -m "perf(yolo): optimize model inference time"

# Bad commits (avoid these)
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdfasdf"
```

**Multi-line Commit** (for complex changes):
```bash
git commit -m "feat(auth): implement RBAC system

- Add role-based access control middleware
- Create admin, premium, and free user roles
- Update endpoint decorators with @require_role
- Add database migration for user roles

Closes #123"
```

### 4.4 Branch Strategy

```
main
  ├── develop (integration branch)
  │   ├── feature/food-analysis-v2
  │   ├── feature/emotion-tracking
  │   └── feature/premium-subscription
  ├── hotfix/security-patch
  └── release/v1.0.0
```

**Branch Naming**:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `release/vX.Y.Z` - Release branches
- `docs/description` - Documentation updates

### 4.5 Code Review Process

#### 4.5.1 Creating Pull Request

```bash
# 1. Push your branch
git push origin feature/your-feature

# 2. Go to GitHub and create PR
# Title: "feat(scope): Brief description"
# Description template:

## Summary
Brief overview of changes

## Changes
- Bullet point list of changes
- Another change

## Testing
- How to test these changes
- Expected behavior

## Screenshots (if UI changes)
[Attach screenshots]

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

Closes #<issue_number>
```

#### 4.5.2 Review Checklist (for Reviewers)

- [ ] Code follows project conventions
- [ ] Tests are included and passing
- [ ] No security vulnerabilities introduced
- [ ] Performance considerations addressed
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] No hardcoded secrets or credentials

### 4.6 Local Development Tips

#### 4.6.1 Using Makefile

Create `Makefile` in project root:
```makefile
.PHONY: help install start test lint format clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd mobile && npm install

start:  ## Start all services
	docker-compose -f deployment/docker/docker-compose.yml up -d
	cd backend && uvicorn app.main:app --reload &
	cd mobile && npm start

test:  ## Run all tests
	cd backend && pytest tests/ -v

lint:  ## Run linters
	cd backend && flake8 app/ tests/
	cd mobile && npm run lint

format:  ## Format code
	cd backend && black app/ tests/
	cd mobile && npm run format

clean:  ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache backend/htmlcov
```

**Usage**:
```bash
make help     # Show available commands
make install  # Install all dependencies
make start    # Start development environment
make test     # Run tests
make lint     # Check code style
make format   # Auto-format code
make clean    # Clean build artifacts
```

#### 4.6.2 Hot Reloading

**Backend (FastAPI)**:
```bash
# --reload flag enables hot reloading
uvicorn app.main:app --reload

# Watch specific directories
uvicorn app.main:app --reload --reload-dir app
```

**Frontend (React Native)**:
```bash
# Expo has hot reloading by default
npm start

# Fast Refresh: Edit code and save
# Changes appear immediately in simulator/device
```

#### 4.6.3 Environment Switching

```bash
# Use different .env files
cp .env .env.development
cp .env .env.production

# Load specific environment
export ENV_FILE=.env.development
uvicorn app.main:app --reload

# Or use python-dotenv in code
from dotenv import load_dotenv
load_dotenv('.env.development')
```

---

## 5. Testing

### 5.1 Testing Philosophy

We follow the **Testing Pyramid**:

```
      /\
     /  \    E2E Tests (10%)
    /────\
   /      \  Integration Tests (30%)
  /────────\
 /          \ Unit Tests (60%)
/────────────\
```

**Guidelines**:
- Write tests BEFORE fixing bugs (TDD for bug fixes)
- Aim for 80%+ code coverage
- Fast unit tests (< 1s each)
- Slower integration tests (< 10s each)
- Minimal E2E tests (most expensive)

### 5.2 Backend Testing (pytest)

#### 5.2.1 Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_auth.py                   # Authentication tests
├── test_food_analysis.py          # Food analysis tests
├── test_wellness_analysis.py      # Wellness tests
├── test_error_codes.py            # Error code tests
└── integration/
    └── test_full_system.py        # End-to-end tests
```

#### 5.2.2 Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_login_success

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests (fast)
pytest -m "unit"

# Run only integration tests
pytest -m "integration"

# Skip slow tests
pytest -m "not slow"

# Run failed tests from last run
pytest --lf

# Stop on first failure
pytest -x

# Run in parallel (faster)
pytest -n auto
```

#### 5.2.3 Writing Unit Tests

**Example: Testing Food Analysis Service**

`tests/test_food_service.py`:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.food_service import FoodAnalysisService
from app.core.exceptions import ImageProcessingError

class TestFoodAnalysisService:
    """Unit tests for FoodAnalysisService"""

    @pytest.fixture
    def food_service(self):
        """Create FoodAnalysisService instance"""
        return FoodAnalysisService()

    @pytest.fixture
    def sample_image_path(self, tmp_path):
        """Create sample image file"""
        image_file = tmp_path / "test_food.jpg"
        # Create a dummy image file
        image_file.write_bytes(b"fake image data")
        return str(image_file)

    def test_detect_food_success(self, food_service, sample_image_path):
        """Test successful food detection"""
        # Arrange
        with patch('app.services.yolo_service.detect_objects') as mock_yolo:
            mock_yolo.return_value = [
                {"label": "apple", "confidence": 0.95},
                {"label": "banana", "confidence": 0.88}
            ]

            # Act
            result = food_service.detect_food(sample_image_path)

            # Assert
            assert len(result) == 2
            assert result[0]["label"] == "apple"
            assert result[0]["confidence"] > 0.9
            mock_yolo.assert_called_once_with(sample_image_path)

    def test_detect_food_no_food_found(self, food_service, sample_image_path):
        """Test when no food is detected"""
        # Arrange
        with patch('app.services.yolo_service.detect_objects') as mock_yolo:
            mock_yolo.return_value = []

            # Act & Assert
            with pytest.raises(ImageProcessingError) as exc_info:
                food_service.detect_food(sample_image_path)

            assert "No food detected" in str(exc_info.value)

    @pytest.mark.parametrize("confidence,expected", [
        (0.95, "high"),
        (0.75, "medium"),
        (0.55, "low")
    ])
    def test_confidence_levels(self, food_service, confidence, expected):
        """Test confidence level classification"""
        result = food_service.classify_confidence(confidence)
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_analyze_food(self, food_service, sample_image_path):
        """Test async food analysis"""
        result = await food_service.analyze_food_async(sample_image_path)
        assert "nutrition" in result
        assert "detected_foods" in result
```

#### 5.2.4 Writing Integration Tests

**Example: Testing Full Food Upload Flow**

`tests/integration/test_food_upload.py`:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.integration
class TestFoodUploadFlow:
    """Integration tests for complete food upload workflow"""

    @pytest.fixture
    async def authenticated_client(self):
        """Create authenticated API client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register and login
            register_response = await client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "name": "Test User"
            })
            assert register_response.status_code == 201

            login_response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "SecurePass123!"
            })
            token = login_response.json()["access_token"]

            # Set auth header
            client.headers["Authorization"] = f"Bearer {token}"
            yield client

    @pytest.mark.asyncio
    async def test_complete_food_upload_flow(self, authenticated_client):
        """Test complete food upload and analysis flow"""
        # 1. Upload food image
        with open("tests/fixtures/apple.jpg", "rb") as image:
            files = {"file": ("apple.jpg", image, "image/jpeg")}
            upload_response = await authenticated_client.post(
                "/api/v1/food/upload",
                files=files
            )

        assert upload_response.status_code == 200
        data = upload_response.json()

        # 2. Verify response structure
        assert "analysis_id" in data
        assert "detected_foods" in data
        assert len(data["detected_foods"]) > 0
        assert "nutrition" in data

        # 3. Check nutrition data
        nutrition = data["nutrition"]
        assert "calories" in nutrition
        assert nutrition["calories"] > 0
        assert "protein" in nutrition
        assert "carbohydrates" in nutrition

        # 4. Retrieve food history
        history_response = await authenticated_client.get("/api/v1/food/history")
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) >= 1
        assert history[0]["analysis_id"] == data["analysis_id"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self, authenticated_client):
        """Test free tier rate limiting"""
        # Upload 3 images (free tier limit)
        for i in range(3):
            response = await authenticated_client.post("/api/v1/food/upload", ...)
            assert response.status_code == 200

        # 4th upload should be rate limited
        response = await authenticated_client.post("/api/v1/food/upload", ...)
        assert response.status_code == 429
        assert "PSI-RATE-4002" in response.json()["error"]["code"]
```

#### 5.2.5 Test Fixtures

`tests/conftest.py`:
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """Create test database session"""
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_pass@localhost/test_db",
        echo=True
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User",
        "subscription_tier": "free"
    }

@pytest.fixture
def mock_yolo_service(monkeypatch):
    """Mock YOLO service for faster tests"""
    def mock_detect(image_path):
        return [{"label": "apple", "confidence": 0.95}]

    monkeypatch.setattr("app.services.yolo_service.detect_objects", mock_detect)
```

### 5.3 Frontend Testing (Jest + React Testing Library)

#### 5.3.1 Running Frontend Tests

```bash
cd mobile

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Update snapshots
npm test -- -u
```

#### 5.3.2 Writing Component Tests

**Example: Testing FoodUploadScreen**

`mobile/src/screens/__tests__/FoodUploadScreen.test.tsx`:
```typescript
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import FoodUploadScreen from '../FoodUploadScreen';

const mockStore = configureStore([]);

describe('FoodUploadScreen', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      auth: { token: 'fake-token', user: { id: '123' } },
      food: { uploading: false, analysis: null }
    });
  });

  it('renders correctly', () => {
    const { getByText, getByTestId } = render(
      <Provider store={store}>
        <FoodUploadScreen />
      </Provider>
    );

    expect(getByText('Upload Food Photo')).toBeTruthy();
    expect(getByTestId('camera-button')).toBeTruthy();
    expect(getByTestId('gallery-button')).toBeTruthy();
  });

  it('opens camera when camera button pressed', () => {
    const { getByTestId } = render(
      <Provider store={store}>
        <FoodUploadScreen />
      </Provider>
    );

    const cameraButton = getByTestId('camera-button');
    fireEvent.press(cameraButton);

    // Verify camera picker was called
    // (requires mocking react-native-image-picker)
  });

  it('displays loading state during upload', () => {
    store = mockStore({
      auth: { token: 'fake-token' },
      food: { uploading: true, analysis: null }
    });

    const { getByTestId } = render(
      <Provider store={store}>
        <FoodUploadScreen />
      </Provider>
    );

    expect(getByTestId('loading-spinner')).toBeTruthy();
  });

  it('displays analysis results after successful upload', async () => {
    const mockAnalysis = {
      detected_foods: ['apple', 'banana'],
      nutrition: { calories: 150, protein: 2 }
    };

    store = mockStore({
      auth: { token: 'fake-token' },
      food: { uploading: false, analysis: mockAnalysis }
    });

    const { getByText } = render(
      <Provider store={store}>
        <FoodUploadScreen />
      </Provider>
    );

    await waitFor(() => {
      expect(getByText('apple')).toBeTruthy();
      expect(getByText('banana')).toBeTruthy();
      expect(getByText('150 cal')).toBeTruthy();
    });
  });
});
```

### 5.4 Test Coverage

#### 5.4.1 Checking Coverage

```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Frontend coverage
cd mobile
npm test -- --coverage

# Open coverage report
open coverage/lcov-report/index.html
```

#### 5.4.2 Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| **Backend Core** | 90%+ | TBD |
| **Backend Services** | 85%+ | TBD |
| **Backend API Routes** | 80%+ | TBD |
| **Frontend Components** | 75%+ | TBD |
| **Frontend Screens** | 70%+ | TBD |

**Exclusions**:
- Migration scripts
- Configuration files
- `__init__.py` files
- Third-party integrations (mocked)

### 5.5 Continuous Integration (CI)

**GitHub Actions Workflow** (`.github/workflows/test.yml`):
```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        env:
          POSTGRES_SERVER: localhost
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
          REDIS_HOST: localhost
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd mobile
          npm ci

      - name: Run tests
        run: |
          cd mobile
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./mobile/coverage/lcov.info
```

---

## 6. Debugging

### 6.1 Backend Debugging

#### 6.1.1 Using Python Debugger (pdb)

```python
# Insert breakpoint in code
import pdb; pdb.set_trace()

# Or use Python 3.7+ built-in
breakpoint()

# Debugger commands:
# n - next line
# s - step into function
# c - continue execution
# p variable - print variable
# pp variable - pretty print
# l - list code around current line
# w - where (stack trace)
# q - quit debugger
```

**Example**:
```python
@router.post("/food/upload")
async def upload_food(file: UploadFile):
    # Set breakpoint here
    breakpoint()

    # Debug file processing
    contents = await file.read()
    print(f"File size: {len(contents)}")

    # Step through food detection
    detected_foods = detect_food(contents)
    return {"foods": detected_foods}
```

#### 6.1.2 VS Code Debugging

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v"
      ],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

**Usage**:
1. Set breakpoints by clicking left of line numbers
2. Press F5 or click "Run and Debug"
3. Select configuration (e.g., "Python: FastAPI")
4. Use debug controls: Continue (F5), Step Over (F10), Step Into (F11), Step Out (Shift+F11)

#### 6.1.3 Logging for Debugging

```python
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Use different log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Error with stack trace")  # Use in except blocks

# Example in endpoint
@router.post("/food/upload")
async def upload_food(file: UploadFile):
    logger.info(f"Received upload request: {file.filename}")

    try:
        result = await process_image(file)
        logger.debug(f"Processing result: {result}")
        return result
    except Exception as e:
        logger.exception("Failed to process image")
        raise
```

**View logs**:
```bash
# Docker logs
docker logs -f psi_backend

# Kubernetes logs
kubectl logs -f deploy/psi-backend -n production

# Filter logs by level
docker logs psi_backend 2>&1 | grep ERROR
```

#### 6.1.4 API Debugging with Swagger UI

1. Start backend: `uvicorn app.main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click "Authorize" and enter JWT token
4. Try endpoints with different inputs
5. View request/response details

**Using curl for debugging**:
```bash
# Test health endpoint
curl -v http://localhost:8000/health

# Test authenticated endpoint
TOKEN="your-jwt-token"
curl -v -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/food/history

# Test file upload
curl -v -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/food.jpg" \
  http://localhost:8000/api/v1/food/upload

# Pretty print JSON response
curl -s http://localhost:8000/health | jq .
```

### 6.2 Frontend Debugging

#### 6.2.1 React Native Debugger

```bash
# Install React Native Debugger (standalone app)
# Download: https://github.com/jhen0409/react-native-debugger/releases

# Or use Chrome DevTools (built-in)
# In simulator/emulator, press:
# iOS: Cmd+D (Shake gesture on device)
# Android: Cmd+M or Ctrl+M (Shake gesture on device)
# Select "Debug" from menu
```

**Using console.log**:
```typescript
// Add debug logging
console.log('User data:', userData);
console.warn('Warning: Invalid input');
console.error('Error uploading image:', error);

// View logs in terminal
# Logs appear in Metro bundler terminal
# Or in React Native Debugger console
```

#### 6.2.2 Redux DevTools

```bash
# Install Redux DevTools Extension
# Chrome: https://chrome.google.com/webstore (search "Redux DevTools")

# Enable in code (mobile/src/store/index.ts)
import { configureStore } from '@reduxjs/toolkit';

const store = configureStore({
  reducer: rootReducer,
  devTools: __DEV__,  // Enable in development only
});
```

**Usage**:
1. Open React Native Debugger
2. Click "Redux" tab
3. View state changes in real-time
4. Time-travel debugging (replay actions)
5. Inspect action payloads

#### 6.2.3 React DevTools

```bash
# Install React DevTools (standalone app)
npm install -g react-devtools

# Run
react-devtools

# Connect from app
# App should auto-connect when running in development
```

**Features**:
- Inspect component tree
- View props and state
- Edit props/state in real-time
- Highlight component updates
- Profiler for performance analysis

#### 6.2.4 Network Debugging

**Using Reactotron**:
```bash
# Install Reactotron (desktop app)
# Download: https://github.com/infinitered/reactotron/releases

# Install in project
npm install --save-dev reactotron-react-native reactotron-redux

# Configure (mobile/src/config/ReactotronConfig.ts)
import Reactotron from 'reactotron-react-native';
import { reactotronRedux } from 'reactotron-redux';

const reactotron = Reactotron
  .configure({ name: 'Psi Mobile' })
  .use(reactotronRedux())
  .useReactNative()
  .connect();

export default reactotron;
```

**Features**:
- Monitor API requests/responses
- View Redux actions
- Log custom events
- Benchmark API calls
- Inspect AsyncStorage

### 6.3 Database Debugging

#### 6.3.1 PostgreSQL Query Debugging

```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Explain query execution plan
EXPLAIN ANALYZE
SELECT * FROM food_history WHERE user_id = '123' ORDER BY created_at DESC;

-- Check active connections
SELECT pid, usename, application_name, client_addr, state, query
FROM pg_stat_activity
WHERE state = 'active';

-- Kill long-running query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

#### 6.3.2 MongoDB Query Debugging

```javascript
// Enable profiling
db.setProfilingLevel(2);  // Log all queries

// View slow queries
db.system.profile.find().sort({millis: -1}).limit(10);

// Explain query
db.user_preferences.find({user_id: "123"}).explain("executionStats");

// Check current operations
db.currentOp();

// Kill operation
db.killOp(<opid>);
```

#### 6.3.3 Redis Debugging

```bash
# Monitor all commands in real-time
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# View all keys (WARNING: slow on large databases)
redis-cli KEYS "*"

# Better: Use SCAN for large databases
redis-cli --scan --pattern "rate_limit:*"

# Check specific key
redis-cli GET "session:abc123"

# Check TTL
redis-cli TTL "rate_limit:user:123:day"

# View slow log
redis-cli SLOWLOG GET 10
```

### 6.4 Performance Debugging

#### 6.4.1 Backend Performance Profiling

```python
# Profile endpoint performance
import cProfile
import pstats
from io import StringIO

@router.post("/food/upload")
async def upload_food(file: UploadFile):
    profiler = cProfile.Profile()
    profiler.enable()

    # Your code here
    result = await process_image(file)

    profiler.disable()
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumtime')
    ps.print_stats(20)  # Top 20 functions
    logger.debug(f"Profile:\n{s.getvalue()}")

    return result
```

**Using py-spy (sampling profiler)**:
```bash
# Install
pip install py-spy

# Profile running process
py-spy top --pid <pid>

# Generate flame graph
py-spy record -o profile.svg --pid <pid>

# Open in browser
open profile.svg
```

#### 6.4.2 Frontend Performance Profiling

```typescript
// React Native Performance Monitor
import { PerformanceObserver, performance } from 'react-native-performance';

// Measure component render time
const measure = (componentName: string) => {
  performance.mark(`${componentName}-start`);

  return () => {
    performance.mark(`${componentName}-end`);
    performance.measure(
      componentName,
      `${componentName}-start`,
      `${componentName}-end`
    );
  };
};

// Usage in component
const FoodUploadScreen = () => {
  useEffect(() => {
    const endMeasure = measure('FoodUploadScreen');
    return () => endMeasure();
  }, []);

  // Component code...
};
```

**Using Flipper (React Native debugging tool)**:
```bash
# Install Flipper
# Download: https://fbflipper.com/

# Connect to app (automatic in development)
# Features:
# - Network inspector
# - Layout inspector
# - Redux inspector
# - AsyncStorage inspector
# - Performance monitoring
```

---

## 7. Contributing

### 7.1 How to Contribute

We welcome contributions! Here's how to get started:

1. **Find an issue** or create one
   - Check [GitHub Issues](https://github.com/yourusername/psi/issues)
   - Look for issues labeled `good first issue` or `help wanted`

2. **Comment on the issue** to claim it
   - Say "I'd like to work on this"
   - Wait for approval before starting

3. **Fork and clone**
   ```bash
   git clone git@github.com:YOUR_USERNAME/psi.git
   ```

4. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make changes**
   - Follow code style guidelines
   - Write tests
   - Update documentation

6. **Test thoroughly**
   ```bash
   pytest tests/
   npm test
   ```

7. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to GitHub and create PR
   - Fill out PR template
   - Wait for review

### 7.2 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Welcome newcomers
- Report violations to conduct@psi-app.com

### 7.3 Getting Help

- **Slack**: #psi-dev
- **GitHub Discussions**: https://github.com/yourusername/psi/discussions
- **Email**: dev@psi-app.com
- **Office Hours**: Tuesdays 2-4 PM UTC (Zoom link in Slack)

---

## 8. Architecture Deep Dive

### 8.1 Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (api/v1/)                                 │   │
│  │  - auth.py      (Authentication endpoints)           │   │
│  │  - food.py      (Food analysis endpoints)            │   │
│  │  - fridge.py    (Fridge & recipes endpoints)         │   │
│  │  - wellness.py  (Wellness hub endpoints)             │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Service Layer (services/)                           │   │
│  │  - food_service.py        (Food analysis logic)      │   │
│  │  - yolo_service.py        (YOLO model inference)     │   │
│  │  - claude_service.py      (Claude API integration)   │   │
│  │  - nutrition_service.py   (USDA database lookup)     │   │
│  │  - emotion_service.py     (Emotion analysis)         │   │
│  │  - recipe_service.py      (Recipe matching)          │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Data Layer (models/ & core/database.py)             │   │
│  │  - SQLAlchemy models (PostgreSQL)                    │   │
│  │  - Pydantic schemas (validation)                     │   │
│  │  - MongoDB collections                               │   │
│  │  - Redis cache                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Request Flow

**Example: Food Upload Request**

```
1. Mobile App → POST /api/v1/food/upload (image file)
   ↓
2. API Layer (food.py)
   - Validate JWT token (dependency injection)
   - Check rate limit (Redis)
   - Validate file type and size
   ↓
3. Service Layer (food_service.py)
   - Save image to temporary storage
   ↓
4. YOLO Service (yolo_service.py)
   - Run YOLO inference on image
   - Detect food items (apple, banana, etc.)
   - Return confidence scores
   ↓
5. Claude Service (claude_service.py)
   - Send image to Claude Vision API
   - Get detailed food descriptions
   ↓
6. Nutrition Service (nutrition_service.py)
   - Look up nutrition data in USDA database (SQLite)
   - Calculate total nutrition for detected foods
   ↓
7. Database (PostgreSQL)
   - Save food analysis to food_history table
   - Associate with user account
   ↓
8. Cache (Redis)
   - Increment user's daily usage counter
   - Cache nutrition data for future lookups
   ↓
9. Response
   - Return JSON with detected foods, nutrition, analysis ID
```

### 8.3 Database Schemas

#### 8.3.1 PostgreSQL Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Food history table
CREATE TABLE food_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    image_url VARCHAR(500),
    detected_foods JSONB NOT NULL,  -- Array of detected items
    nutrition JSONB NOT NULL,       -- Nutritional breakdown
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_food_history_user_id ON food_history(user_id);
CREATE INDEX idx_food_history_created_at ON food_history(created_at DESC);

-- Wellness scores table
CREATE TABLE wellness_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    wellness_score INTEGER CHECK (wellness_score BETWEEN 0 AND 100),
    hrv_avg FLOAT,
    heart_rate_avg FLOAT,
    dominant_emotion VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

#### 8.3.2 MongoDB Collections

```javascript
// user_preferences collection
{
  _id: ObjectId("..."),
  user_id: "uuid-from-postgresql",
  dietary_restrictions: ["vegetarian", "gluten-free"],
  allergens: ["peanuts", "shellfish"],
  preferred_cuisines: ["korean", "italian"],
  wellness_goals: ["improve_sleep", "reduce_stress"],
  updated_at: ISODate("2025-11-10T...")
}

// emotion_time_series collection
{
  _id: ObjectId("..."),
  user_id: "uuid",
  timestamp: ISODate("2025-11-10T14:30:00Z"),
  heart_rate: 72,
  hrv: 65,
  emotion: "calm",
  confidence: 0.85,
  source: "apple_watch"
}

// recipe_ratings collection
{
  _id: ObjectId("..."),
  user_id: "uuid",
  recipe_id: "recipe-123",
  rating: 5,
  comment: "Delicious and easy to make!",
  created_at: ISODate("...")
}
```

### 8.4 Authentication Flow

```
1. User Registration
   POST /api/v1/auth/register
   - Hash password with bcrypt
   - Save user to PostgreSQL
   - Return user ID

2. User Login
   POST /api/v1/auth/login
   - Verify email/password
   - Generate JWT token (expires in 24 hours)
   - Return access_token

3. Authenticated Request
   GET /api/v1/food/history
   - Header: Authorization: Bearer <token>
   - Verify JWT signature
   - Check token expiration
   - Check token revocation (Redis blacklist)
   - Extract user_id from token
   - Process request

4. Token Refresh (if implemented)
   POST /api/v1/auth/refresh
   - Verify refresh token
   - Generate new access token
   - Return new access_token

5. Logout (if token revocation implemented)
   POST /api/v1/auth/logout
   - Add token to Redis blacklist
   - Set TTL to token expiry time
```

---

## 9. API Development

### 9.1 Creating New Endpoint

**Step-by-step guide to add a new API endpoint:**

#### Step 1: Define Pydantic Models

`backend/app/models/recipe.py`:
```python
from pydantic import BaseModel
from typing import List, Optional

class RecipeBase(BaseModel):
    """Base recipe model"""
    name: str
    cuisine: str
    difficulty: str  # easy, medium, hard
    prep_time: int  # minutes
    ingredients: List[str]
    instructions: List[str]

class RecipeCreate(RecipeBase):
    """Recipe creation model"""
    pass

class RecipeResponse(RecipeBase):
    """Recipe response model"""
    id: str
    rating: Optional[float] = None
    user_rating: Optional[int] = None

    class Config:
        orm_mode = True
```

#### Step 2: Create Service Logic

`backend/app/services/recipe_service.py`:
```python
from typing import List
from app.models.recipe import RecipeResponse
from app.core.exceptions import ResourceNotFoundError

class RecipeService:
    """Recipe business logic"""

    async def get_recipe_by_id(self, recipe_id: str) -> RecipeResponse:
        """
        Get recipe by ID

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            RecipeResponse object

        Raises:
            ResourceNotFoundError: If recipe not found
        """
        # Query database
        recipe = await db.fetch_one(
            "SELECT * FROM recipes WHERE id = $1", recipe_id
        )

        if not recipe:
            raise ResourceNotFoundError("Recipe", recipe_id)

        return RecipeResponse(**recipe)

    async def search_recipes(
        self,
        ingredients: List[str],
        cuisine: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[RecipeResponse]:
        """
        Search recipes by ingredients and filters

        Args:
            ingredients: List of available ingredients
            cuisine: Optional cuisine filter
            difficulty: Optional difficulty filter

        Returns:
            List of matching recipes
        """
        # Implement recipe matching logic
        # (TF-IDF, vector similarity, etc.)
        pass

recipe_service = RecipeService()
```

#### Step 3: Create API Endpoint

`backend/app/api/v1/recipes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.recipe import RecipeResponse
from app.services.recipe_service import recipe_service
from app.core.security import verify_token

router = APIRouter()

@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get recipe by ID

    - **recipe_id**: Unique recipe identifier

    Returns:
        Recipe details including ingredients, instructions, and rating
    """
    try:
        recipe = await recipe_service.get_recipe_by_id(recipe_id)
        return recipe
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/recipes/search", response_model=List[RecipeResponse])
async def search_recipes(
    ingredients: List[str] = Query(..., description="Available ingredients"),
    cuisine: Optional[str] = Query(None, description="Cuisine type"),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(verify_token)
):
    """
    Search recipes by ingredients and filters

    - **ingredients**: List of available ingredients
    - **cuisine**: Optional cuisine filter (e.g., "korean", "italian")
    - **difficulty**: Optional difficulty filter (easy, medium, hard)
    - **limit**: Maximum number of results (1-100)

    Returns:
        List of matching recipes sorted by match score
    """
    recipes = await recipe_service.search_recipes(
        ingredients=ingredients,
        cuisine=cuisine,
        difficulty=difficulty
    )
    return recipes[:limit]
```

#### Step 4: Register Router

`backend/app/main.py`:
```python
from app.api.v1 import recipes

# Add to existing imports and router registration
app.include_router(
    recipes.router,
    prefix="/api/v1/recipes",
    tags=["Recipes"]
)
```

#### Step 5: Write Tests

`backend/tests/test_recipes.py`:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_recipe_success():
    """Test successful recipe retrieval"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Arrange
        recipe_id = "recipe-123"
        token = "valid-jwt-token"

        # Act
        response = await client.get(
            f"/api/v1/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe_id
        assert "name" in data
        assert "ingredients" in data

@pytest.mark.asyncio
async def test_get_recipe_not_found():
    """Test recipe not found error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/recipes/nonexistent",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 404
        assert "Recipe not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_recipes_by_ingredients():
    """Test recipe search by ingredients"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/recipes/search",
            params={
                "ingredients": ["chicken", "rice", "vegetables"],
                "cuisine": "korean",
                "limit": 5
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        assert all("ingredients" in recipe for recipe in data)
```

#### Step 6: Update API Documentation

`docs/API_DOCUMENTATION.md`:
```markdown
## Recipe Endpoints

### GET /api/v1/recipes/{recipe_id}

Get recipe details by ID.

**Authentication**: Required (Bearer token)

**Parameters**:
- `recipe_id` (path, required): Recipe ID

**Response** (200 OK):
\`\`\`json
{
  "id": "recipe-123",
  "name": "Korean Bibimbap",
  "cuisine": "korean",
  "difficulty": "medium",
  "prep_time": 45,
  "ingredients": ["rice", "beef", "vegetables", "gochujang"],
  "instructions": ["Cook rice", "Prepare toppings", "Mix with sauce"],
  "rating": 4.5,
  "user_rating": 5
}
\`\`\`

**Errors**:
- 404: Recipe not found (PSI-RES-3012)
```

### 9.2 Error Handling

Always use standardized error codes:

```python
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    AuthenticationError,
    RateLimitError
)
from app.core.error_codes import ErrorCode

# Example: Resource not found
raise ResourceNotFoundError(
    resource="Recipe",
    identifier=recipe_id,
    error_code=ErrorCode.RES_RECIPE_NOT_FOUND
)

# Example: Validation error
raise ValidationError(
    message="Invalid ingredients list",
    error_code=ErrorCode.VAL_INVALID_INPUT,
    details={"field": "ingredients", "issue": "cannot be empty"}
)

# Example: Rate limit exceeded
raise RateLimitError(
    message="Daily limit exceeded",
    error_code=ErrorCode.RATE_DAILY_LIMIT_EXCEEDED,
    details={"limit": 3, "reset_time": "2025-11-11T00:00:00Z"}
)
```

---

## 10. Mobile Development

### 10.1 Project Structure

```
mobile/src/
├── screens/           # Full-screen components
│   ├── auth/
│   │   ├── LoginScreen.tsx
│   │   └── RegisterScreen.tsx
│   ├── food/
│   │   ├── FoodUploadScreen.tsx
│   │   └── FoodHistoryScreen.tsx
│   └── wellness/
│       └── WellnessHubScreen.tsx
│
├── components/        # Reusable UI components
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── LoadingSpinner.tsx
│   ├── food/
│   │   ├── FoodCard.tsx
│   │   └── NutritionChart.tsx
│   └── wellness/
│       └── EmotionBadge.tsx
│
├── services/          # API clients & business logic
│   ├── api/
│   │   ├── authApi.ts
│   │   ├── foodApi.ts
│   │   └── wellnessApi.ts
│   └── storage/
│       └── secureStorage.ts
│
├── store/             # Redux state management
│   ├── slices/
│   │   ├── authSlice.ts
│   │   ├── foodSlice.ts
│   │   └── wellnessSlice.ts
│   └── index.ts
│
├── navigation/        # React Navigation
│   ├── AppNavigator.tsx
│   ├── AuthNavigator.tsx
│   └── MainNavigator.tsx
│
├── theme/             # Design system
│   ├── colors.ts
│   ├── typography.ts
│   └── spacing.ts
│
├── hooks/             # Custom React hooks
│   ├── useAuth.ts
│   ├── useFoodUpload.ts
│   └── useWellness.ts
│
└── utils/             # Helper functions
    ├── validators.ts
    └── formatters.ts
```

### 10.2 Creating New Screen

**Example: Creating a Recipe Detail Screen**

#### Step 1: Create Screen Component

`mobile/src/screens/recipe/RecipeDetailScreen.tsx`:
```typescript
import React, { useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { fetchRecipeById } from '../../store/slices/recipeSlice';
import { RootState } from '../../store';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Button from '../../components/common/Button';

type RecipeDetailRouteProp = RouteProp<
  { RecipeDetail: { recipeId: string } },
  'RecipeDetail'
>;

const RecipeDetailScreen = () => {
  const route = useRoute<RecipeDetailRouteProp>();
  const dispatch = useDispatch();
  const { recipe, loading, error } = useSelector(
    (state: RootState) => state.recipe
  );

  useEffect(() => {
    dispatch(fetchRecipeById(route.params.recipeId));
  }, [dispatch, route.params.recipeId]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Button
          title="Try Again"
          onPress={() => dispatch(fetchRecipeById(route.params.recipeId))}
        />
      </View>
    );
  }

  if (!recipe) {
    return null;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{recipe.name}</Text>
      <Text style={styles.cuisine}>{recipe.cuisine}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ingredients</Text>
        {recipe.ingredients.map((ingredient, index) => (
          <Text key={index} style={styles.ingredient}>
            • {ingredient}
          </Text>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Instructions</Text>
        {recipe.instructions.map((step, index) => (
          <Text key={index} style={styles.instruction}>
            {index + 1}. {step}
          </Text>
        ))}
      </View>

      <Button
        title="Start Cooking"
        onPress={() => {/* Navigate to cooking mode */}}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  cuisine: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 12,
  },
  ingredient: {
    fontSize: 16,
    marginBottom: 8,
  },
  instruction: {
    fontSize: 16,
    marginBottom: 12,
    lineHeight: 24,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#f00',
    marginBottom: 16,
    textAlign: 'center',
  },
});

export default RecipeDetailScreen;
```

#### Step 2: Create Redux Slice

`mobile/src/store/slices/recipeSlice.ts`:
```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { recipeApi } from '../../services/api/recipeApi';

interface Recipe {
  id: string;
  name: string;
  cuisine: string;
  ingredients: string[];
  instructions: string[];
  rating?: number;
}

interface RecipeState {
  recipe: Recipe | null;
  recipes: Recipe[];
  loading: boolean;
  error: string | null;
}

const initialState: RecipeState = {
  recipe: null,
  recipes: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchRecipeById = createAsyncThunk(
  'recipe/fetchById',
  async (recipeId: string, { rejectWithValue }) => {
    try {
      const response = await recipeApi.getRecipeById(recipeId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch recipe');
    }
  }
);

export const searchRecipes = createAsyncThunk(
  'recipe/search',
  async (params: { ingredients: string[]; cuisine?: string }, { rejectWithValue }) => {
    try {
      const response = await recipeApi.searchRecipes(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search recipes');
    }
  }
);

// Slice
const recipeSlice = createSlice({
  name: 'recipe',
  initialState,
  reducers: {
    clearRecipe(state) {
      state.recipe = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch by ID
      .addCase(fetchRecipeById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecipeById.fulfilled, (state, action) => {
        state.loading = false;
        state.recipe = action.payload;
      })
      .addCase(fetchRecipeById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Search
      .addCase(searchRecipes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchRecipes.fulfilled, (state, action) => {
        state.loading = false;
        state.recipes = action.payload;
      })
      .addCase(searchRecipes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearRecipe } = recipeSlice.actions;
export default recipeSlice.reducer;
```

#### Step 3: Create API Client

`mobile/src/services/api/recipeApi.ts`:
```typescript
import axios from 'axios';
import { getToken } from '../storage/secureStorage';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const recipeApi = {
  getRecipeById: (recipeId: string) => {
    return api.get(`/recipes/${recipeId}`);
  },

  searchRecipes: (params: { ingredients: string[]; cuisine?: string }) => {
    return api.get('/recipes/search', { params });
  },

  rateRecipe: (recipeId: string, rating: number) => {
    return api.post(`/recipes/${recipeId}/rate`, { rating });
  },
};
```

#### Step 4: Add Navigation

`mobile/src/navigation/MainNavigator.tsx`:
```typescript
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import RecipeListScreen from '../screens/recipe/RecipeListScreen';
import RecipeDetailScreen from '../screens/recipe/RecipeDetailScreen';

export type MainStackParamList = {
  RecipeList: undefined;
  RecipeDetail: { recipeId: string };
};

const Stack = createStackNavigator<MainStackParamList>();

const MainNavigator = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="RecipeList"
        component={RecipeListScreen}
        options={{ title: 'Recipes' }}
      />
      <Stack.Screen
        name="RecipeDetail"
        component={RecipeDetailScreen}
        options={{ title: 'Recipe' }}
      />
    </Stack.Navigator>
  );
};

export default MainNavigator;
```

---

## 11. Best Practices

### 11.1 Security Best Practices

- ✅ **Never commit secrets** to Git (.env files, API keys)
- ✅ **Use environment variables** for sensitive configuration
- ✅ **Validate all user input** (Pydantic for backend, Yup for frontend)
- ✅ **Sanitize database queries** (use parameterized queries)
- ✅ **Hash passwords** (bcrypt, never store plaintext)
- ✅ **Implement rate limiting** (prevent abuse)
- ✅ **Use HTTPS** in production (enforce TLS 1.2+)
- ✅ **Set short JWT expiry** (1 hour access token, 7 days refresh)
- ✅ **Implement CORS properly** (whitelist specific origins)
- ✅ **Keep dependencies updated** (run `npm audit`, `pip-audit`)

### 11.2 Performance Best Practices

- ✅ **Index database queries** (add indexes on frequently queried columns)
- ✅ **Cache expensive operations** (use Redis for API responses)
- ✅ **Optimize images** (compress before upload, use WebP)
- ✅ **Paginate large results** (limit default to 20-50 items)
- ✅ **Use connection pooling** (PostgreSQL, MongoDB)
- ✅ **Lazy load images** (React Native lazy loading)
- ✅ **Minimize bundle size** (code splitting, tree shaking)
- ✅ **Profile before optimizing** (measure, don't guess)

### 11.3 Code Quality Best Practices

- ✅ **Write self-documenting code** (clear variable names, docstrings)
- ✅ **Keep functions small** (< 50 lines, single responsibility)
- ✅ **Don't repeat yourself** (DRY principle)
- ✅ **Write tests first** (TDD for bug fixes)
- ✅ **Use type hints** (Python type hints, TypeScript)
- ✅ **Handle errors gracefully** (try/except, proper error messages)
- ✅ **Log appropriately** (info for events, error for failures)
- ✅ **Review your own code** (before requesting review)

---

## 12. Troubleshooting

### 12.1 Common Development Issues

| Issue | Solution |
|-------|----------|
| **Port 8000 already in use** | `lsof -i :8000` then `kill -9 <PID>` |
| **Database connection refused** | Check Docker containers: `docker-compose ps` |
| **Module not found** | Activate venv: `source venv/bin/activate` |
| **YOLO model not loading** | Check `YOLO_MODEL_PATH` in `.env` |
| **JWT token expired** | Login again to get new token |
| **Rate limit exceeded** | Wait for reset or upgrade to premium in code |
| **CORS error** | Add origin to `ALLOWED_ORIGINS` in `.env` |
| **Slow tests** | Run with `-m "not slow"` to skip slow tests |

### 12.2 Getting Help

1. **Check documentation** (this guide, API docs)
2. **Search GitHub Issues** (may already be reported)
3. **Ask in Slack** (#psi-dev channel)
4. **Create GitHub Issue** (with reproduction steps)
5. **Email dev team** (dev@psi-app.com)

---

## Appendix

### A. Useful Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React Native**: https://reactnative.dev/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **MongoDB**: https://docs.mongodb.com/
- **Redis**: https://redis.io/documentation
- **YOLO**: https://docs.ultralytics.com/
- **Claude API**: https://docs.anthropic.com/

### B. Keyboard Shortcuts

**VS Code**:
- `Cmd+P` / `Ctrl+P` - Quick open file
- `Cmd+Shift+P` / `Ctrl+Shift+P` - Command palette
- `F5` - Start debugging
- `Cmd+B` / `Ctrl+B` - Toggle sidebar

**Terminal**:
- `Ctrl+C` - Stop running process
- `Ctrl+D` - Exit shell
- `↑` / `↓` - Navigate command history

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-10
**Next Review**: 2026-01-10

**Questions? Contact**: dev@psi-app.com

**Happy Coding! 🚀**
