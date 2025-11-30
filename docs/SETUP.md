# Psi Setup Guide

Complete guide to setting up the Psi development environment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Setup](#database-setup)
- [ML Models Setup](#ml-models-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Node.js 18+**
   ```bash
   node --version   # Should be 18 or higher
   npm --version
   ```

3. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

4. **Git**
   ```bash
   git --version
   ```

### Optional but Recommended

- **PyCharm Professional** (Student license available)
- **VS Code** with Python and React Native extensions
- **Expo CLI** for mobile development
  ```bash
  npm install -g expo-cli
  ```

## Backend Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/psi.git
cd psi
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - CLAUDE_API_KEY (from https://console.anthropic.com/)
```

### 5. Database Setup

See [Database Setup](#database-setup) section below.

### 6. Download YOLO Model

```bash
# Download base YOLO v8 model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
mv yolov8m.pt ../data/models/

# Or use curl on Windows:
curl -L -o ../data/models/yolov8m.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### 7. Run Backend

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for API documentation
```

## Frontend Setup

### 1. Navigate to Mobile Directory

```bash
cd mobile
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Install Expo CLI (if not already installed)

```bash
npm install -g expo-cli
```

### 4. Start Development Server

```bash
# Start Expo development server
npm start

# Or specific platforms:
npm run ios      # iOS simulator
npm run android  # Android emulator
npm run web      # Web browser
```

### 5. Install Expo Go App

- **iOS**: Download from App Store
- **Android**: Download from Google Play

Scan the QR code from terminal to run on your device.

## Database Setup

### Option 1: Docker (Recommended)

```bash
cd deployment/docker
docker-compose up -d

# Verify databases are running
docker-compose ps

# Initialize PostgreSQL
docker-compose exec postgres psql -U psi_user -d psi_db -f /docker-entrypoint-initdb.d/init.sql

# Initialize MongoDB
docker-compose exec mongodb mongosh -u psi_admin -p psi_mongo_password --authenticationDatabase admin /docker-entrypoint-initdb.d/init_mongodb.js
```

### Option 2: Manual Installation

#### PostgreSQL

```bash
# Install PostgreSQL 15
# macOS:
brew install postgresql@15

# Ubuntu:
sudo apt install postgresql-15

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo systemctl start postgresql    # Linux

# Create database
psql -U postgres
CREATE DATABASE psi_db;
CREATE USER psi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE psi_db TO psi_user;
\q

# Run initialization script
psql -U psi_user -d psi_db -f backend/scripts/init_postgres.sql
```

#### MongoDB

```bash
# Install MongoDB 7.0
# macOS:
brew tap mongodb/brew
brew install mongodb-community@7.0

# Ubuntu:
# Follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

# Start MongoDB
brew services start mongodb-community@7.0  # macOS
sudo systemctl start mongod                # Linux

# Run initialization script
mongosh < backend/scripts/init_mongodb.js
```

#### Redis

```bash
# Install Redis
# macOS:
brew install redis

# Ubuntu:
sudo apt install redis-server

# Start Redis
brew services start redis           # macOS
sudo systemctl start redis-server   # Linux
```

## ML Models Setup

### 1. Download Base YOLO Model

```bash
cd data/models

# Download YOLOv8 medium model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### 2. Prepare Training Dataset (Optional)

```bash
# Download AI Hub Korean Food Dataset
# Visit: https://aihub.or.kr
# Register and download manually

# Or use Roboflow
cd backend/scripts
python download_roboflow.py
```

### 3. Train Custom Model (Optional)

```bash
cd backend
python scripts/train_yolo.py \
    --data ../data/datasets/food/data.yaml \
    --epochs 100 \
    --batch 16
```

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "yolo": "loaded"
  }
}
```

### Database Connection Test

```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U psi_user -d psi_db

# MongoDB
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# Redis
docker-compose exec redis redis-cli ping
```

### Frontend Test

```bash
cd mobile
npm test
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in the backend directory
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Problem**: Database connection failed
```bash
# Check if databases are running
docker-compose ps

# Restart databases
docker-compose restart postgres mongodb redis
```

**Problem**: YOLO model not found
```bash
# Download model again
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### Frontend Issues

**Problem**: `expo command not found`
```bash
npm install -g expo-cli
```

**Problem**: Metro bundler cache issues
```bash
cd mobile
npm start -- --clear
```

**Problem**: iOS simulator not opening
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### Docker Issues

**Problem**: Port already in use
```bash
# Find and kill process using the port
# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem**: Docker out of disk space
```bash
docker system prune -a
docker volume prune
```

## Next Steps

1. Read the [API Documentation](http://localhost:8000/docs)
2. Review the [Development Guide](DEVELOPMENT.md)
3. Check out [Contributing Guidelines](CONTRIBUTING.md)
4. Join our [Discord Community](https://discord.gg/psi-app)

## Support

- **Email**: support@psi-app.com
- **Issues**: https://github.com/yourusername/psi/issues
- **Discussions**: https://github.com/yourusername/psi/discussions
