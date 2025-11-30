# Psi Operations Manual

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Target Audience**: DevOps Engineers, SREs, Backend Developers
**Status**: Production

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Deployment](#3-deployment)
4. [Monitoring](#4-monitoring)
5. [Troubleshooting](#5-troubleshooting)
6. [Maintenance](#6-maintenance)
7. [Incident Response](#7-incident-response)
8. [Backup & Recovery](#8-backup--recovery)
9. [Scaling](#9-scaling)
10. [Security Operations](#10-security-operations)
11. [Runbooks](#11-runbooks)
12. [Appendix](#12-appendix)

---

## 1. Overview

### 1.1 Purpose

This operations manual provides comprehensive guidance for deploying, monitoring, troubleshooting, and maintaining the Psi platform in production environments.

### 1.2 System Description

**Psi** is an emotion-based wellness platform that combines:
- AI-powered food analysis (YOLO v8 + Claude Vision)
- Real-time emotion monitoring from wearable devices
- Neuroscience-based wellness recommendations
- Comprehensive nutrition tracking (62+ nutrients)

### 1.3 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend API** | FastAPI | 0.109.0 | REST API server |
| **Runtime** | Python | 3.11+ | Application runtime |
| **Primary Database** | PostgreSQL | 15+ | ACID transactions, user data |
| **Document Store** | MongoDB | 7.0+ | Flexible schemas, time series |
| **Cache** | Redis | 7+ | Session management, rate limiting |
| **AI/ML** | YOLO v8, Claude API | Latest | Food detection, vision analysis |
| **Web Server** | Uvicorn | 0.27.0 | ASGI server |
| **Containerization** | Docker | 24.0+ | Container runtime |
| **Orchestration** | Docker Compose / K8s | - | Container orchestration |

### 1.4 Key Metrics & SLAs

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| **Uptime** | 99.9% | < 99% |
| **API Response Time (p95)** | < 500ms | > 2s |
| **API Response Time (p99)** | < 1s | > 5s |
| **Error Rate** | < 0.1% | > 1% |
| **Crash-Free Rate** | > 99.5% | < 98% |
| **Database Query Time (p95)** | < 100ms | > 500ms |
| **YOLO Inference Time** | < 2s | > 5s |
| **Memory Usage (per instance)** | < 2GB | > 3GB |
| **CPU Usage** | < 70% | > 90% |

### 1.5 On-Call & Escalation

**On-Call Schedule**: 24/7 rotation (1 week shifts)

**Escalation Path**:
1. **L1**: On-call DevOps Engineer (responds in < 15 min)
2. **L2**: Senior Backend Engineer (responds in < 30 min)
3. **L3**: CTO/Tech Lead (responds in < 1 hour)
4. **L4**: CEO (critical incidents only)

**Contact Information**: See [Appendix A](#appendix-a-contact-information)

---

## 2. Architecture

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (ALB/NLB)                 │
│                    SSL Termination (443)                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│               Backend API (FastAPI) - Auto-scaled            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Instance 1 │  │  Instance 2 │  │  Instance N │         │
│  │  Uvicorn    │  │  Uvicorn    │  │  Uvicorn    │         │
│  │  Port 8000  │  │  Port 8000  │  │  Port 8000  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────┬───────────────┬───────────────┬──────────────────┘
           │               │               │
           ▼               ▼               ▼
┌──────────────────┐  ┌────────────┐  ┌──────────────┐
│   PostgreSQL     │  │  MongoDB   │  │    Redis     │
│   (Primary DB)   │  │  (NoSQL)   │  │   (Cache)    │
│   Port 5432      │  │  Port 27017│  │   Port 6379  │
└──────────────────┘  └────────────┘  └──────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  - Claude API (Anthropic)                                    │
│  - AWS S3 (Image Storage)                                    │
│  - USDA FoodData API                                         │
│  - HealthKit / Google Health Connect                         │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Network Architecture

**Ports**:
- `80` - HTTP (redirects to 443)
- `443` - HTTPS (production traffic)
- `8000` - Backend API (internal only)
- `5432` - PostgreSQL (internal only)
- `27017` - MongoDB (internal only)
- `6379` - Redis (internal only)

**Security Groups** (AWS example):
```
Load Balancer SG:
  Inbound: 0.0.0.0/0 → 443 (HTTPS)
  Outbound: Backend SG → 8000

Backend SG:
  Inbound: Load Balancer SG → 8000
  Outbound: Database SG → 5432, 27017, 6379
  Outbound: 0.0.0.0/0 → 443 (external APIs)

Database SG:
  Inbound: Backend SG → 5432, 27017, 6379
  Outbound: None
```

### 2.3 Data Flow

**Food Analysis Request**:
```
1. Mobile App → POST /api/v1/food/upload (+ image)
2. API Gateway → JWT validation (Redis cache check)
3. Backend → Rate limit check (Redis)
4. Backend → YOLO inference (2s)
5. Backend → Claude Vision API (1s)
6. Backend → USDA nutrition lookup (local SQLite + API)
7. Backend → Store in PostgreSQL (user history)
8. Backend → Return response (JSON)
```

**Average Latency**: 3-4 seconds (dominated by AI inference)

### 2.4 Database Schema Overview

**PostgreSQL** (Relational):
- `users` - User accounts, credentials
- `food_history` - Uploaded food analyses
- `wellness_scores` - Daily wellness metrics
- `subscriptions` - Premium tier management

**MongoDB** (NoSQL):
- `user_preferences` - Flexible user settings
- `emotion_time_series` - HRV/heart rate data
- `recipe_ratings` - User-generated ratings

**Redis** (Key-Value):
- `session:{token}` - JWT token validation
- `rate_limit:{user_id}:{window}` - Rate limiting
- `cache:{endpoint}:{params}` - Response caching

---

## 3. Deployment

### 3.1 Deployment Environments

| Environment | Purpose | URL | Auto-deploy |
|-------------|---------|-----|-------------|
| **Development** | Local development | http://localhost:8000 | No |
| **Staging** | Pre-production testing | https://staging-api.psi-app.com | Yes (main branch) |
| **Production** | Live user traffic | https://api.psi-app.com | Manual approval |

### 3.2 Pre-Deployment Checklist

Before every deployment, verify:

- [ ] All tests pass: `pytest tests/ -v --cov=app`
- [ ] Code review approved (minimum 2 reviewers)
- [ ] Database migrations tested on staging
- [ ] Environment variables configured
- [ ] Security scan passed (`npm audit`, `pip-audit`)
- [ ] Load testing completed (staging)
- [ ] Rollback plan documented
- [ ] On-call engineer notified
- [ ] Status page updated (if major changes)

### 3.3 Local Development Deployment

#### 3.3.1 Prerequisites

```bash
# Verify installations
python --version  # 3.11+
docker --version  # 24.0+
docker-compose --version  # 2.0+
node --version  # 18+ (for mobile app)
```

#### 3.3.2 Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/psi.git
cd psi

# 2. Set up environment variables
cd backend
cp .env.example .env

# Edit .env with your local configuration
# Required: SECRET_KEY, CLAUDE_API_KEY
nano .env

# 3. Start databases with Docker Compose
cd ../deployment/docker
docker-compose up -d postgres mongodb redis

# Wait for health checks to pass (30 seconds)
docker-compose ps  # All should show "healthy"

# 4. Run database migrations
cd ../../backend
pip install alembic
alembic upgrade head

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Verify API is running
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# 8. Access API documentation
# Open browser: http://localhost:8000/docs
```

#### 3.3.3 Common Local Issues

**Issue**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in the backend/ directory
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Issue**: `Connection refused` to database
```bash
# Solution: Wait for containers to be healthy
docker-compose ps
docker-compose logs postgres  # Check for errors
```

**Issue**: `YOLO model not found`
```bash
# Solution: Download YOLO model
mkdir -p data/models
# Contact team for psi_food_best.pt file
# Or train from scratch: python scripts/train_yolo.py
```

### 3.4 Docker Deployment

#### 3.4.1 Build Docker Image

```bash
# Navigate to deployment directory
cd deployment/docker

# Build backend image
docker build -t psi-backend:latest \
  -f Dockerfile.backend \
  ../../backend/

# Verify image
docker images | grep psi-backend

# Test image locally
docker run -p 8000:8000 \
  -e SECRET_KEY=test-secret-key \
  -e CLAUDE_API_KEY=your-key \
  psi-backend:latest
```

#### 3.4.2 Docker Compose Deployment (All Services)

```bash
# Start all services
cd deployment/docker
docker-compose up -d

# Verify all containers are healthy
docker-compose ps

# Expected output:
# NAME           STATUS              PORTS
# psi_backend    Up (healthy)        0.0.0.0:8000->8000/tcp
# psi_postgres   Up (healthy)        0.0.0.0:5432->5432/tcp
# psi_mongodb    Up (healthy)        0.0.0.0:27017->27017/tcp
# psi_redis      Up (healthy)        0.0.0.0:6379->6379/tcp

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Clean up (WARNING: deletes all data)
docker-compose down -v
```

#### 3.4.3 Production Docker Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: registry.example.com/psi-backend:${VERSION}
    restart: always
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - POSTGRES_SERVER=${POSTGRES_HOST}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - ENVIRONMENT=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3.5 Cloud Deployment (AWS Example)

#### 3.5.1 AWS Infrastructure Setup

```bash
# 1. Create VPC and Subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24  # Public
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24  # Private

# 2. Create RDS PostgreSQL Instance
aws rds create-db-instance \
  --db-instance-identifier psi-db-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username psi_admin \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 100 \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted

# 3. Create DocumentDB (MongoDB-compatible)
aws docdb create-db-cluster \
  --db-cluster-identifier psi-docdb-prod \
  --engine docdb \
  --master-username psi_admin \
  --master-user-password ${DOCDB_PASSWORD} \
  --backup-retention-period 7

# 4. Create ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id psi-redis-prod \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --num-cache-nodes 1

# 5. Create ECR Repository for Docker images
aws ecr create-repository --repository-name psi-backend

# 6. Push Docker image to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ${ECR_URL}
docker tag psi-backend:latest ${ECR_URL}/psi-backend:1.0.0
docker push ${ECR_URL}/psi-backend:1.0.0

# 7. Create ECS Cluster
aws ecs create-cluster --cluster-name psi-prod

# 8. Create ECS Task Definition (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 9. Create ECS Service with ALB
aws ecs create-service \
  --cluster psi-prod \
  --service-name psi-backend \
  --task-definition psi-backend:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --load-balancers targetGroupArn=${TG_ARN},containerName=backend,containerPort=8000
```

#### 3.5.2 ECS Task Definition Example

`task-definition.json`:
```json
{
  "family": "psi-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ECR_URL}/psi-backend:1.0.0",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "POSTGRES_SERVER", "value": "${RDS_ENDPOINT}"}
      ],
      "secrets": [
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "CLAUDE_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/psi-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 3.6 Kubernetes Deployment

#### 3.6.1 Kubernetes Manifests

`k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: psi-backend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: psi-backend
  template:
    metadata:
      labels:
        app: psi-backend
    spec:
      containers:
      - name: backend
        image: registry.example.com/psi-backend:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POSTGRES_SERVER
          valueFrom:
            secretKeyRef:
              name: psi-secrets
              key: postgres-host
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: psi-secrets
              key: secret-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: psi-backend
  namespace: production
spec:
  selector:
    app: psi-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: psi-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.psi-app.com
    secretName: psi-tls
  rules:
  - host: api.psi-app.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: psi-backend
            port:
              number: 80
```

#### 3.6.2 Deploy to Kubernetes

```bash
# 1. Create namespace
kubectl create namespace production

# 2. Create secrets
kubectl create secret generic psi-secrets \
  --from-literal=secret-key=${SECRET_KEY} \
  --from-literal=postgres-host=${POSTGRES_HOST} \
  --from-literal=claude-api-key=${CLAUDE_API_KEY} \
  -n production

# 3. Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 4. Verify deployment
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production

# 5. View logs
kubectl logs -f deployment/psi-backend -n production

# 6. Rolling update
kubectl set image deployment/psi-backend \
  backend=registry.example.com/psi-backend:1.0.1 \
  -n production

# 7. Rollback if needed
kubectl rollout undo deployment/psi-backend -n production
```

### 3.7 Database Migrations

#### 3.7.1 Creating Migrations

```bash
# Ensure you're in backend/ directory
cd backend

# Create a new migration
alembic revision -m "add_user_subscription_table"

# Edit generated file in alembic/versions/xxxxx_add_user_subscription_table.py
# Add upgrade() and downgrade() logic

# Test migration locally
alembic upgrade head

# Test rollback
alembic downgrade -1
```

#### 3.7.2 Running Migrations in Production

```bash
# CRITICAL: Always backup before migrations
./scripts/backup_database.sh

# Staging: Test migration first
alembic upgrade head --sql > migration.sql  # Preview SQL
alembic upgrade head

# Production: Execute with care
# Option 1: Direct execution (small migrations)
alembic upgrade head

# Option 2: Generate SQL and review (large migrations)
alembic upgrade head --sql > prod_migration.sql
# Review prod_migration.sql
psql -h $POSTGRES_HOST -U psi_user -d psi_db < prod_migration.sql

# Verify migration
alembic current
alembic history

# If issues occur, rollback
alembic downgrade -1
```

#### 3.7.3 Zero-Downtime Migration Strategy

For large migrations that may cause downtime:

```bash
# Step 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN new_field VARCHAR(255) NULL;

# Step 2: Deploy code that writes to both old and new fields
# ... deploy v1.1 ...

# Step 3: Backfill data (batch processing)
UPDATE users SET new_field = old_field WHERE new_field IS NULL;

# Step 4: Make column NOT NULL
ALTER TABLE users ALTER COLUMN new_field SET NOT NULL;

# Step 5: Deploy code that only uses new field
# ... deploy v1.2 ...

# Step 6: Drop old column
ALTER TABLE users DROP COLUMN old_field;
```

### 3.8 Deployment Verification

After every deployment, verify:

```bash
# 1. Health check
curl https://api.psi-app.com/health
# Expected: {"status": "healthy", "database": "connected", ...}

# 2. API documentation accessible
curl https://api.psi-app.com/docs
# Expected: HTML response (OpenAPI docs)

# 3. Authentication works
curl -X POST https://api.psi-app.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'
# Expected: {"access_token": "...", ...}

# 4. Rate limiting enforced
for i in {1..10}; do
  curl https://api.psi-app.com/api/v1/food/upload
done
# Expected: 429 Too Many Requests after threshold

# 5. Error handling works
curl https://api.psi-app.com/api/v1/food/invalid-endpoint
# Expected: {"error": {"code": "PSI-RES-3001", ...}}

# 6. Check metrics
# Datadog: https://app.datadoghq.com/dashboard/psi-prod
# New Relic: https://one.newrelic.com/psi-app
```

### 3.9 Deployment Rollback

If issues are detected post-deployment:

#### 3.9.1 Docker Rollback

```bash
# Tag previous version as :rollback
docker tag registry.example.com/psi-backend:1.0.0 \
  registry.example.com/psi-backend:rollback

# Update service to use rollback tag
docker service update --image registry.example.com/psi-backend:rollback \
  psi_backend
```

#### 3.9.2 Kubernetes Rollback

```bash
# Quick rollback to previous version
kubectl rollout undo deployment/psi-backend -n production

# Rollback to specific revision
kubectl rollout history deployment/psi-backend -n production
kubectl rollout undo deployment/psi-backend --to-revision=5 -n production

# Verify rollback
kubectl rollout status deployment/psi-backend -n production
```

#### 3.9.3 Database Rollback

```bash
# Check current version
alembic current

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Verify
alembic current
```

---

## 4. Monitoring

### 4.1 Monitoring Stack

**Recommended Tools**:
- **APM**: Datadog, New Relic, or Dynatrace
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch
- **Metrics**: Prometheus + Grafana
- **Uptime**: Pingdom, UptimeRobot
- **Error Tracking**: Sentry
- **Distributed Tracing**: Jaeger or Zipkin

### 4.2 Key Metrics to Monitor

#### 4.2.1 Application Metrics

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| **Request Rate** | Counter | - |
| **Response Time (p50, p95, p99)** | Histogram | p95 > 1s, p99 > 2s |
| **Error Rate** | Counter | > 1% |
| **Request Success Rate** | Gauge | < 99% |
| **Active Requests** | Gauge | > 1000 |
| **JWT Token Validation Time** | Histogram | > 100ms |
| **YOLO Inference Time** | Histogram | > 5s |
| **Claude API Latency** | Histogram | > 3s |
| **Database Query Time** | Histogram | > 500ms |

#### 4.2.2 Infrastructure Metrics

| Metric | Alert Threshold |
|--------|----------------|
| **CPU Usage** | > 80% for 5 min |
| **Memory Usage** | > 90% for 5 min |
| **Disk Usage** | > 85% |
| **Network I/O** | > 1 Gbps |
| **Open File Descriptors** | > 80% of limit |
| **Thread Count** | > 500 |

#### 4.2.3 Database Metrics

**PostgreSQL**:
- Active connections (alert if > 80% of max_connections)
- Long-running queries (alert if > 10s)
- Deadlocks (alert on any)
- Replication lag (alert if > 10s)
- Table bloat (alert if > 30%)

**MongoDB**:
- Connection pool utilization (alert if > 80%)
- Query execution time (alert if > 1s p95)
- Replica set lag (alert if > 10s)
- Disk I/O (alert if > 80%)

**Redis**:
- Memory usage (alert if > 90%)
- Hit rate (alert if < 80%)
- Evicted keys (alert on any)
- Blocked clients (alert on any)

### 4.3 Logging

#### 4.3.1 Log Levels

```python
# Configured in app/main.py
logging.basicConfig(
    level=logging.INFO,  # Production: INFO, Development: DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Log Levels**:
- **DEBUG**: Detailed diagnostic information (development only)
- **INFO**: General informational messages (default in production)
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (handled exceptions)
- **CRITICAL**: Critical errors (unhandled exceptions, system failures)

#### 4.3.2 Structured Logging

Implement structured JSON logging for easier parsing:

```python
# Example: backend/app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

#### 4.3.3 Log Aggregation

**ELK Stack Example**:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

**Logstash Pipeline** (`logstash/pipeline/logstash.conf`):
```
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "psi-logs-%{+YYYY.MM.dd}"
  }
}
```

#### 4.3.4 Log Retention Policy

| Environment | Retention Period | Storage |
|-------------|-----------------|---------|
| **Production** | 90 days | S3 Glacier (archive) |
| **Staging** | 30 days | S3 Standard |
| **Development** | 7 days | Local disk |

### 4.4 Alerting

#### 4.4.1 Alert Severity Levels

| Severity | Response Time | Notification |
|----------|--------------|--------------|
| **P0 - Critical** | < 15 minutes | PagerDuty, SMS, Phone call |
| **P1 - High** | < 1 hour | PagerDuty, Slack |
| **P2 - Medium** | < 4 hours | Slack, Email |
| **P3 - Low** | Next business day | Email |

#### 4.4.2 Critical Alerts (P0)

- API uptime < 99% (5-minute window)
- Error rate > 5%
- Database connection failures
- All backend instances down
- Security breach detected
- Payment processing failures
- Data loss detected

#### 4.4.3 High Priority Alerts (P1)

- API response time p95 > 2s
- Error rate > 1%
- Database replication lag > 60s
- Memory usage > 95%
- CPU usage > 90% for 10 minutes
- Disk space < 10%
- SSL certificate expiry < 7 days

#### 4.4.4 Alert Configuration Examples

**Datadog Alert** (API response time):
```yaml
name: "High API Response Time"
type: metric alert
query: "avg(last_5m):avg:psi.api.response_time.p95{env:production} > 2"
message: |
  **P1 Alert**: API response time p95 is {{value}}s (threshold: 2s)

  Dashboard: https://app.datadoghq.com/dashboard/psi-prod
  Runbook: https://docs.psi-app.com/runbooks/high-latency

  @pagerduty-psi-oncall
escalation_message: "@oncall-manager API latency still high after 15 minutes"
```

**Prometheus Alert** (High error rate):
```yaml
groups:
- name: api_alerts
  interval: 30s
  rules:
  - alert: HighErrorRate
    expr: |
      rate(http_requests_total{status=~"5.."}[5m])
      / rate(http_requests_total[5m]) > 0.01
    for: 5m
    labels:
      severity: P1
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
```

### 4.5 Dashboards

#### 4.5.1 Primary Dashboard (Grafana Example)

**Panels**:
1. **Request Rate** (time series) - Requests per second
2. **Response Time** (time series) - p50, p95, p99
3. **Error Rate** (gauge) - Percentage of 5xx errors
4. **Active Users** (gauge) - Current authenticated users
5. **Database Connections** (time series) - Active, idle
6. **YOLO Inference Time** (histogram) - AI processing latency
7. **Cache Hit Rate** (gauge) - Redis cache effectiveness
8. **Top Errors** (table) - Most frequent error codes

#### 4.5.2 Infrastructure Dashboard

**Panels**:
1. **CPU Usage** (per instance)
2. **Memory Usage** (per instance)
3. **Disk I/O** (per instance)
4. **Network Traffic** (ingress/egress)
5. **Container Health** (healthy, unhealthy)
6. **Auto-scaling Events** (scale up/down events)

#### 4.5.3 Business Metrics Dashboard

**Panels**:
1. **Daily Active Users (DAU)**
2. **Food Uploads** (per hour/day)
3. **Premium Conversions** (per day)
4. **API Usage by Endpoint** (pie chart)
5. **User Retention** (cohort analysis)
6. **Revenue** (daily/monthly)

### 4.6 Health Checks

#### 4.6.1 Application Health Endpoint

`backend/app/api/v1/health.py`:
```python
from fastapi import APIRouter, Depends
from app.core.database import db
from app.core.cache import redis_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint
    Returns 200 if all systems operational, 503 otherwise
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check PostgreSQL
    try:
        await db.postgres_pool.execute("SELECT 1")
        health_status["checks"]["postgres"] = "connected"
    except Exception as e:
        health_status["checks"]["postgres"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check MongoDB
    try:
        await db.mongodb_client.admin.command('ping')
        health_status["checks"]["mongodb"] = "connected"
    except Exception as e:
        health_status["checks"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        await redis_client.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check YOLO model loaded
    try:
        from app.services.yolo_service import yolo_model
        health_status["checks"]["yolo"] = "loaded" if yolo_model else "not loaded"
    except Exception as e:
        health_status["checks"]["yolo"] = f"error: {str(e)}"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

#### 4.6.2 Liveness vs Readiness Probes

**Liveness Probe** (is application alive?):
- Endpoint: `/health`
- Failure action: Restart container
- Use case: Detect deadlocks, infinite loops

**Readiness Probe** (is application ready to serve traffic?):
- Endpoint: `/health/ready`
- Failure action: Remove from load balancer
- Use case: Detect database connection issues, during startup

```python
@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - checks if app can serve traffic
    """
    # More stringent checks than liveness
    # Must have all database connections ready
    # Must have loaded all ML models
    # ...
```

---

## 5. Troubleshooting

### 5.1 Common Issues & Solutions

#### 5.1.1 API Not Responding

**Symptoms**:
- Health check failing
- HTTP 502/503 errors
- Timeouts

**Diagnosis**:
```bash
# 1. Check if container is running
docker ps | grep psi_backend
# or
kubectl get pods -n production | grep psi-backend

# 2. Check container logs
docker logs psi_backend --tail=100
# or
kubectl logs deployment/psi-backend -n production --tail=100

# 3. Check application logs
tail -f /var/log/psi/app.log

# 4. Check system resources
docker stats psi_backend
# or
kubectl top pod -n production
```

**Common Causes**:

**A. Out of Memory (OOM)**
```bash
# Symptoms in logs:
# "Killed" or "Container exited with code 137"

# Solution:
# Increase memory limit in Docker/K8s config
resources:
  limits:
    memory: 4Gi  # Increased from 2Gi
```

**B. Database Connection Exhaustion**
```bash
# Symptoms:
# "FATAL: sorry, too many clients already"

# Solution 1: Increase PostgreSQL max_connections
ALTER SYSTEM SET max_connections = 200;  -- Default: 100
SELECT pg_reload_conf();

# Solution 2: Implement connection pooling
# In app/core/database.py:
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,  # Max connections per instance
    max_overflow=20,  # Additional connections when pool full
    pool_pre_ping=True  # Verify connections before use
)
```

**C. Deadlock**
```bash
# Symptoms:
# Application hangs, no error logs

# Diagnosis:
# Attach to running container and check processes
docker exec -it psi_backend python -c "import threading; print(threading.enumerate())"

# Solution:
# Force restart container
docker restart psi_backend
# or
kubectl rollout restart deployment/psi-backend -n production
```

#### 5.1.2 High API Latency

**Symptoms**:
- Response times > 2s
- Slow user experience
- Timeouts

**Diagnosis**:
```bash
# 1. Check response time breakdown
curl -w "@curl-format.txt" -o /dev/null -s https://api.psi-app.com/api/v1/food/upload

# curl-format.txt:
#   time_namelookup:  %{time_namelookup}s\n
#   time_connect:     %{time_connect}s\n
#   time_appconnect:  %{time_appconnect}s\n
#   time_pretransfer: %{time_pretransfer}s\n
#   time_starttransfer: %{time_starttransfer}s\n
#   time_total:       %{time_total}s\n

# 2. Check database query performance
# Connect to PostgreSQL:
psql -h $POSTGRES_HOST -U psi_user -d psi_db

# Find slow queries:
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

# 3. Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public' AND tablename = 'food_history'
ORDER BY abs(correlation) DESC;
```

**Common Causes**:

**A. Missing Database Index**
```sql
-- Symptom: Sequential scan on large table
EXPLAIN ANALYZE SELECT * FROM food_history WHERE user_id = 'xxx';

-- Solution: Add index
CREATE INDEX idx_food_history_user_id ON food_history(user_id);
CREATE INDEX idx_food_history_created_at ON food_history(created_at DESC);
```

**B. N+1 Query Problem**
```python
# Bad: N+1 queries
users = await db.fetch("SELECT * FROM users")
for user in users:
    foods = await db.fetch("SELECT * FROM food_history WHERE user_id = $1", user['id'])

# Good: Single query with JOIN
users_with_foods = await db.fetch("""
    SELECT u.*, json_agg(f.*) as foods
    FROM users u
    LEFT JOIN food_history f ON f.user_id = u.id
    GROUP BY u.id
""")
```

**C. YOLO Model Inference Slow**
```bash
# Symptom: YOLO inference > 5s

# Solution 1: Use smaller model
YOLO_MODEL_PATH=data/models/psi_food_nano.pt  # Faster but less accurate

# Solution 2: Enable GPU
docker run --gpus all psi-backend:latest

# Solution 3: Batch processing (if multiple images)
# Process images in batches instead of one-by-one
```

#### 5.1.3 Database Connection Errors

**Symptoms**:
- "could not connect to server: Connection refused"
- "FATAL: password authentication failed"
- "could not translate host name to address"

**Diagnosis**:
```bash
# 1. Verify database is running
docker ps | grep postgres
# or
aws rds describe-db-instances --db-instance-identifier psi-db-prod

# 2. Test connection manually
psql -h $POSTGRES_HOST -U psi_user -d psi_db -c "SELECT 1"

# 3. Check network connectivity
ping $POSTGRES_HOST
telnet $POSTGRES_HOST 5432

# 4. Check security groups (AWS)
aws ec2 describe-security-groups --group-ids sg-xxx
```

**Solutions**:

**A. Incorrect Credentials**
```bash
# Verify environment variables
echo $POSTGRES_PASSWORD

# Update secret in Kubernetes
kubectl create secret generic psi-secrets \
  --from-literal=postgres-password=${CORRECT_PASSWORD} \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/psi-backend -n production
```

**B. Network Firewall Rules**
```bash
# AWS: Add security group rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-backend \
  --protocol tcp \
  --port 5432 \
  --source-group sg-database
```

**C. Connection Pool Exhausted**
```python
# Increase pool size
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Increased from 10
    max_overflow=40,  # Increased from 20
)
```

#### 5.1.4 Rate Limiting Issues

**Symptoms**:
- Users complaining about "429 Too Many Requests"
- Free tier users hitting limits unexpectedly

**Diagnosis**:
```bash
# Check rate limit for specific user
redis-cli GET rate_limit:user:123:day
# Output: 3 (3 requests used today)

# Check rate limit window
redis-cli TTL rate_limit:user:123:day
# Output: 3600 (1 hour remaining until reset)

# Check all rate limit keys
redis-cli KEYS "rate_limit:*" | wc -l
```

**Solutions**:

**A. Legitimate High Usage (Upgrade User)**
```python
# Update user to premium tier
await db.execute("""
    UPDATE users
    SET subscription_tier = 'premium'
    WHERE user_id = $1
""", user_id)

# Clear rate limit
await redis_client.delete(f"rate_limit:user:{user_id}:day")
```

**B. Rate Limit Too Restrictive**
```python
# Increase free tier limit
# In backend/.env:
FREE_TIER_DAILY_LIMIT=5  # Increased from 3
```

**C. Bot/Scraper Abuse**
```bash
# Block IP in firewall
iptables -A INPUT -s 192.168.1.100 -j DROP

# Or use Cloudflare bot protection
```

#### 5.1.5 Authentication Errors

**Symptoms**:
- "Invalid token" errors
- Users logged out unexpectedly
- JWT validation failures

**Diagnosis**:
```bash
# 1. Check if token is in Redis (token revocation)
redis-cli GET session:${TOKEN_ID}

# 2. Decode JWT to check expiry
# Install jwt-cli: https://github.com/mike-engel/jwt-cli
jwt decode ${JWT_TOKEN}

# 3. Check SECRET_KEY matches
# On backend:
echo $SECRET_KEY

# If mismatched, all existing tokens invalid
```

**Solutions**:

**A. Token Expired**
```python
# Increase token expiry (if appropriate)
# In backend/.env:
ACCESS_TOKEN_EXPIRE_HOURS=24  # Increased from 1
```

**B. SECRET_KEY Mismatch**
```bash
# If SECRET_KEY changed, all users must re-login
# Notify users via email/push notification

# Invalidate all sessions in Redis
redis-cli FLUSHDB
```

**C. Token Revocation Not Working**
```python
# Verify Redis connection
await redis_client.ping()

# Manually revoke token
await redis_client.setex(f"session:{token_id}", 3600, "revoked")
```

### 5.2 Performance Debugging

#### 5.2.1 Profiling Python Application

**CPU Profiling**:
```python
# Add to specific endpoint for profiling
import cProfile
import pstats

@app.post("/api/v1/food/upload")
async def upload_food(request: Request):
    profiler = cProfile.Profile()
    profiler.enable()

    # Your code here
    result = await process_food_image(image)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime')
    stats.print_stats(20)  # Top 20 functions

    return result
```

**Memory Profiling**:
```bash
# Install memory_profiler
pip install memory_profiler

# Add decorator to functions
from memory_profiler import profile

@profile
def process_large_dataset(data):
    # ...

# Run with:
python -m memory_profiler app/services/food_service.py
```

#### 5.2.2 Database Query Optimization

```sql
-- Enable query logging (PostgreSQL)
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries > 100ms
SELECT pg_reload_conf();

-- View slow queries
SELECT query, calls, total_time, mean_time, stddev_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC
LIMIT 20;

-- Analyze specific query
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM food_history WHERE user_id = 'xxx' ORDER BY created_at DESC LIMIT 10;

-- Check table statistics
SELECT schemaname, tablename, n_live_tup, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;

-- Manually vacuum if needed
VACUUM ANALYZE food_history;
```

### 5.3 Log Analysis

#### 5.3.1 Finding Errors in Logs

```bash
# Docker logs
docker logs psi_backend --since 1h | grep ERROR

# Kubernetes logs
kubectl logs deployment/psi-backend -n production --since=1h | grep ERROR

# Search for specific error code
kubectl logs deployment/psi-backend -n production | grep "PSI-DB-6002"

# Count error occurrences
kubectl logs deployment/psi-backend -n production | grep ERROR | wc -l

# Find most common errors
kubectl logs deployment/psi-backend -n production | grep ERROR | \
  awk -F'"error_code": "' '{print $2}' | cut -d'"' -f1 | sort | uniq -c | sort -rn
```

#### 5.3.2 Tracing Specific Request

```bash
# Add request ID to logs (middleware)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    logger.info(f"[{request_id}] {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"[{request_id}] Response: {response.status_code}")

    return response

# Search logs by request ID
kubectl logs deployment/psi-backend -n production | grep "abc-123-def-456"
```

---

## 6. Maintenance

### 6.1 Routine Maintenance Tasks

| Task | Frequency | Owner | Estimated Time |
|------|-----------|-------|---------------|
| Database backups verification | Daily | Automated + On-call | 10 min |
| Log rotation | Daily | Automated | - |
| Security updates | Weekly | DevOps | 2 hours |
| Database vacuum | Weekly | Automated + DBA | 30 min |
| Certificate renewal check | Monthly | DevOps | 15 min |
| Dependency updates | Monthly | Backend team | 4 hours |
| Disaster recovery drill | Quarterly | All | 4 hours |
| Security audit | Quarterly | Security team | 1 week |
| Capacity planning | Quarterly | DevOps + Product | 4 hours |

### 6.2 Database Maintenance

#### 6.2.1 PostgreSQL Maintenance

**Daily Tasks**:
```bash
# Automated backup (cron job)
0 2 * * * /usr/local/bin/backup_postgres.sh

# backup_postgres.sh:
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="psi_db_backup_${DATE}.sql.gz"
pg_dump -h $POSTGRES_HOST -U psi_user psi_db | gzip > /backups/${BACKUP_FILE}
# Upload to S3
aws s3 cp /backups/${BACKUP_FILE} s3://psi-backups/postgres/
# Delete local backup older than 7 days
find /backups -name "*.sql.gz" -mtime +7 -delete
```

**Weekly Tasks**:
```sql
-- Vacuum and analyze tables (Sunday 3 AM)
VACUUM ANALYZE food_history;
VACUUM ANALYZE users;
VACUUM ANALYZE wellness_scores;

-- Check for bloat
SELECT schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Reindex if needed
REINDEX TABLE food_history;
```

**Monthly Tasks**:
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC
LIMIT 20;

-- Drop unused indexes (if idx_scan = 0 for > 30 days)
-- DROP INDEX IF EXISTS idx_unused_index;

-- Update statistics
ANALYZE VERBOSE;
```

#### 6.2.2 MongoDB Maintenance

```javascript
// Connect to MongoDB
mongosh mongodb://psi_admin:password@mongodb:27017

// Compact collections (reduces disk space)
db.runCommand({ compact: 'user_preferences' })
db.runCommand({ compact: 'emotion_time_series' })

// Rebuild indexes
db.user_preferences.reIndex()

// Check database stats
db.stats()

// Backup (using mongodump)
mongodump --uri="mongodb://psi_admin:password@mongodb:27017/psi" --out=/backups/mongodb_$(date +%Y%m%d)
```

#### 6.2.3 Redis Maintenance

```bash
# Check memory usage
redis-cli INFO memory

# Check hit rate
redis-cli INFO stats | grep hit

# Flush expired keys manually (if needed)
redis-cli --scan --pattern "rate_limit:*" | xargs redis-cli DEL

# Backup Redis (RDB snapshot)
redis-cli BGSAVE

# Monitor real-time commands
redis-cli MONITOR
```

### 6.3 Security Updates

#### 6.3.1 OS Security Patches

```bash
# For Ubuntu/Debian
apt update
apt list --upgradable
apt upgrade -y

# For Alpine (Docker images)
apk update
apk upgrade

# Reboot if kernel updated
reboot
```

#### 6.3.2 Python Dependency Updates

```bash
# Check for vulnerabilities
pip-audit

# Update specific package
pip install --upgrade anthropic

# Update all packages (TEST IN STAGING FIRST)
pip install --upgrade -r requirements.txt

# Generate new requirements.txt with updated versions
pip freeze > requirements.txt

# Run tests after updates
pytest tests/ -v --cov=app
```

#### 6.3.3 Docker Image Updates

```bash
# Pull latest base images
docker pull python:3.11-slim

# Rebuild images with updated base
docker build -t psi-backend:1.0.1 -f Dockerfile.backend .

# Test locally
docker run -p 8000:8000 psi-backend:1.0.1

# Push to registry
docker push registry.example.com/psi-backend:1.0.1

# Deploy to staging first
kubectl set image deployment/psi-backend backend=registry.example.com/psi-backend:1.0.1 -n staging

# Monitor for issues (24 hours)
# Then deploy to production
kubectl set image deployment/psi-backend backend=registry.example.com/psi-backend:1.0.1 -n production
```

### 6.4 Certificate Management

#### 6.4.1 SSL Certificate Renewal

**Let's Encrypt (Automated with Cert-Manager)**:
```yaml
# cert-manager.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: devops@psi-app.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

**Manual Renewal** (if not using cert-manager):
```bash
# Check certificate expiry
echo | openssl s_client -connect api.psi-app.com:443 2>/dev/null | openssl x509 -noout -dates

# Renew with certbot
certbot renew

# Reload Nginx
nginx -s reload
```

#### 6.4.2 Alert for Expiring Certificates

```bash
# Monitor certificate expiry (cron job)
#!/bin/bash
EXPIRY_DATE=$(echo | openssl s_client -connect api.psi-app.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "${EXPIRY_DATE}" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
  echo "Certificate expires in ${DAYS_LEFT} days!" | mail -s "URGENT: SSL Certificate Expiring" devops@psi-app.com
fi
```

### 6.5 Capacity Planning

#### 6.5.1 Growth Metrics to Track

| Metric | Current | 3-Month Projection | Action If Exceeded |
|--------|---------|-------------------|--------------------|
| **DAU** | 10,000 | 15,000 | Scale backend instances |
| **API Requests/Day** | 100,000 | 150,000 | Increase rate limits |
| **Database Size** | 50 GB | 75 GB | Add storage |
| **Image Storage** | 100 GB | 200 GB | Upgrade S3 plan |
| **CDN Bandwidth** | 500 GB/month | 1 TB/month | Optimize images |

#### 6.5.2 Scaling Triggers

**Auto-Scaling Rules** (Kubernetes HPA):
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: psi-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: psi-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
    scaleUp:
      stabilizationWindowSeconds: 60   # Scale up quickly
```

---

## 7. Incident Response

### 7.1 Incident Response Process

```mermaid
graph TD
    A[Incident Detected] --> B[Acknowledge Alert]
    B --> C[Assess Severity]
    C --> D{Critical?}
    D -->|Yes| E[Page On-Call Engineer]
    D -->|No| F[Create Ticket]
    E --> G[Start War Room]
    F --> G
    G --> H[Diagnose Issue]
    H --> I[Implement Fix]
    I --> J{Resolved?}
    J -->|No| H
    J -->|Yes| K[Monitor]
    K --> L[Post-Mortem]
```

### 7.2 Incident Severity Matrix

| Severity | Impact | Examples | Response |
|----------|--------|----------|----------|
| **P0** | Total outage, data loss | API down, database corrupted | Immediate, all hands |
| **P1** | Significant degradation | High latency, some features down | < 1 hour, on-call + L2 |
| **P2** | Minor degradation | Single feature broken | < 4 hours, normal hours |
| **P3** | No user impact | Monitoring alert, low disk | Next business day |

### 7.3 Incident Communication

**Status Page Updates** (status.psi-app.com):
- Update within 15 minutes of detection
- Provide ETA for resolution
- Post-resolution: Root cause summary

**Example Status Update**:
```
🔴 Major Outage - API Unavailable
Posted: 2025-11-10 14:32 UTC

We are currently investigating an issue causing API requests to fail.
Our engineering team is actively working on a resolution.

ETA: 30 minutes

Updates:
14:45 UTC - Root cause identified: Database connection pool exhausted
14:52 UTC - Fix deployed, monitoring recovery
15:10 UTC - Service restored, monitoring stability
```

### 7.4 Post-Mortem Template

**Document**: `incidents/YYYY-MM-DD-incident-name.md`

```markdown
# Incident Post-Mortem: [Title]

**Date**: 2025-11-10
**Duration**: 38 minutes (14:32 - 15:10 UTC)
**Severity**: P0
**Impact**: 100% of API requests failed

## Summary
Brief description of what happened.

## Timeline (UTC)
- 14:32 - Monitoring alert: API error rate > 50%
- 14:35 - On-call engineer paged
- 14:40 - War room initiated
- 14:45 - Root cause identified: Database connection pool exhausted
- 14:52 - Fix deployed: Increased connection pool from 10 to 30
- 15:10 - Service fully restored, monitoring stable

## Root Cause
Sudden traffic spike (5x normal) caused all database connections to be consumed.
New connections timed out, causing cascading failures.

## Resolution
1. Increased PostgreSQL max_connections from 100 to 200
2. Increased application connection pool from 10 to 30
3. Enabled connection pooling in PgBouncer

## Impact
- 50,000 failed API requests
- 10,000 users affected
- No data loss

## Action Items
- [ ] Implement auto-scaling based on connection pool usage (@devops, due: 2025-11-15)
- [ ] Add alert for connection pool > 80% (@devops, due: 2025-11-12)
- [ ] Load test to validate new limits (@backend, due: 2025-11-17)
- [ ] Document connection pool tuning (@tech-lead, due: 2025-11-14)

## Lessons Learned
**What Went Well**:
- Fast detection (< 3 minutes)
- Quick root cause identification
- Effective communication to users

**What Could Be Improved**:
- Connection pool limits not monitored
- No load testing for traffic spikes
- Alerting threshold too high (50% error rate)

**Lucky Breaks**:
- Incident during business hours (faster response)
```

---

## 8. Backup & Recovery

### 8.1 Backup Strategy

| Data Store | Backup Frequency | Retention | Method | Location |
|------------|------------------|-----------|--------|----------|
| **PostgreSQL** | Daily (2 AM UTC) | 30 days | pg_dump + WAL archiving | AWS S3 |
| **MongoDB** | Daily (3 AM UTC) | 30 days | mongodump | AWS S3 |
| **Redis** | Every 6 hours | 7 days | RDB snapshot | Local + S3 |
| **Images (S3)** | Continuous | 90 days | S3 versioning | S3 Glacier |
| **Application Code** | On every commit | Indefinite | Git | GitHub |

### 8.2 Backup Scripts

#### 8.2.1 PostgreSQL Backup

`scripts/backup_postgres.sh`:
```bash
#!/bin/bash
set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
BACKUP_FILE="psi_db_${DATE}.sql.gz"
S3_BUCKET="s3://psi-backups/postgres"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Dump database
pg_dump -h ${POSTGRES_HOST} \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_DB} \
  --no-owner --no-acl \
  | gzip > ${BACKUP_DIR}/${BACKUP_FILE}

# Verify backup
if [ -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
  echo "Backup created: ${BACKUP_FILE}"

  # Upload to S3
  aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE} ${S3_BUCKET}/${BACKUP_FILE}

  # Verify S3 upload
  if aws s3 ls ${S3_BUCKET}/${BACKUP_FILE}; then
    echo "Backup uploaded to S3"

    # Delete local backup older than 7 days
    find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete

    # Send success notification
    echo "PostgreSQL backup completed successfully" | \
      mail -s "Backup Success: ${BACKUP_FILE}" devops@psi-app.com
  else
    echo "ERROR: S3 upload failed" | \
      mail -s "Backup FAILED: S3 Upload" devops@psi-app.com
    exit 1
  fi
else
  echo "ERROR: Backup file not created" | \
    mail -s "Backup FAILED: File Creation" devops@psi-app.com
  exit 1
fi
```

#### 8.2.2 WAL Archiving (Point-in-Time Recovery)

Enable continuous archiving in PostgreSQL:
```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://psi-backups/postgres/wal/%f'
archive_timeout = 300  -- Archive every 5 minutes
```

### 8.3 Restore Procedures

#### 8.3.1 PostgreSQL Full Restore

```bash
# 1. Stop application (prevent writes)
kubectl scale deployment psi-backend --replicas=0 -n production

# 2. Download backup from S3
aws s3 cp s3://psi-backups/postgres/psi_db_20251110_020000.sql.gz /tmp/

# 3. Drop existing database (DANGEROUS!)
psql -h ${POSTGRES_HOST} -U postgres -c "DROP DATABASE psi_db;"
psql -h ${POSTGRES_HOST} -U postgres -c "CREATE DATABASE psi_db OWNER psi_user;"

# 4. Restore backup
gunzip -c /tmp/psi_db_20251110_020000.sql.gz | \
  psql -h ${POSTGRES_HOST} -U psi_user -d psi_db

# 5. Verify restore
psql -h ${POSTGRES_HOST} -U psi_user -d psi_db -c "SELECT COUNT(*) FROM users;"

# 6. Restart application
kubectl scale deployment psi-backend --replicas=3 -n production
```

#### 8.3.2 Point-in-Time Recovery (PITR)

```bash
# Restore to specific time (e.g., before accidental DELETE)
# 1. Restore base backup
gunzip -c /tmp/psi_db_20251110_020000.sql.gz | psql ...

# 2. Create recovery.conf
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'aws s3 cp s3://psi-backups/postgres/wal/%f %p'
recovery_target_time = '2025-11-10 14:30:00 UTC'
recovery_target_action = 'promote'
EOF

# 3. Restart PostgreSQL
pg_ctl restart

# 4. PostgreSQL will replay WAL logs until 14:30:00
```

### 8.4 Disaster Recovery Plan

#### 8.4.1 DR Scenarios

| Scenario | RPO | RTO | Procedure |
|----------|-----|-----|-----------|
| **Single instance failure** | 0 | 5 min | Auto-scaling replaces instance |
| **Database corruption** | 24 hours | 1 hour | Restore from daily backup |
| **Accidental data deletion** | 5 min | 30 min | Point-in-time recovery |
| **Region outage (AWS)** | 24 hours | 4 hours | Failover to DR region |
| **Complete data loss** | 24 hours | 8 hours | Full rebuild from backups |

**RPO** (Recovery Point Objective): Maximum data loss acceptable
**RTO** (Recovery Time Objective): Maximum downtime acceptable

#### 8.4.2 DR Drill Procedure (Quarterly)

```bash
# 1. Schedule maintenance window
# Notify users: "Scheduled maintenance 2025-12-01 02:00-06:00 UTC"

# 2. Create test environment
kubectl create namespace dr-test

# 3. Restore databases from backup
./scripts/restore_postgres.sh dr-test psi_db_20251110_020000.sql.gz
./scripts/restore_mongodb.sh dr-test mongodb_20251110

# 4. Deploy application to dr-test namespace
kubectl apply -f k8s/deployment.yaml -n dr-test

# 5. Run smoke tests
pytest tests/integration/test_full_system.py --namespace=dr-test

# 6. Verify data integrity
python scripts/verify_data_integrity.py --namespace=dr-test

# 7. Document results
# - Time to restore: ____ minutes
# - Data loss: ____ records
# - Issues encountered: ________

# 8. Clean up
kubectl delete namespace dr-test

# 9. Update DR plan based on learnings
```

---

## 9. Scaling

### 9.1 Vertical Scaling (Scale Up)

**When to Scale Up**:
- CPU usage consistently > 70%
- Memory usage > 85%
- Single-threaded workloads (YOLO inference)

**Backend Instance Sizing**:
| Tier | vCPUs | Memory | Cost/month | Use Case |
|------|-------|--------|------------|----------|
| **Small** | 1 | 2 GB | $50 | Development |
| **Medium** | 2 | 4 GB | $100 | Staging |
| **Large** | 4 | 8 GB | $200 | Production (current) |
| **XLarge** | 8 | 16 GB | $400 | High traffic |

**Scaling Procedure**:
```bash
# AWS ECS: Update task definition
aws ecs register-task-definition --family psi-backend --cpu 2048 --memory 4096 ...

# Kubernetes: Update deployment
kubectl set resources deployment/psi-backend \
  --limits=cpu=2,memory=4Gi \
  --requests=cpu=1,memory=2Gi \
  -n production

# Rolling update (zero downtime)
kubectl rollout status deployment/psi-backend -n production
```

### 9.2 Horizontal Scaling (Scale Out)

**When to Scale Out**:
- Request rate increasing
- Multi-threaded workloads
- Geographic distribution

**Auto-Scaling Configuration**:
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: psi-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: psi-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

**Manual Scaling**:
```bash
# Scale to 10 replicas
kubectl scale deployment/psi-backend --replicas=10 -n production

# Verify
kubectl get pods -n production | grep psi-backend | wc -l
```

### 9.3 Database Scaling

#### 9.3.1 PostgreSQL Read Replicas

```bash
# AWS RDS: Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier psi-db-replica-1 \
  --source-db-instance-identifier psi-db-prod \
  --db-instance-class db.t3.large

# Update application to use read replica for SELECT queries
# In app/core/database.py:
READ_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{READ_REPLICA_HOST}:5432/{POSTGRES_DB}"
read_engine = create_async_engine(READ_DATABASE_URL)
```

#### 9.3.2 MongoDB Sharding

```javascript
// Enable sharding on database
sh.enableSharding("psi")

// Shard collection by user_id
sh.shardCollection("psi.emotion_time_series", { "user_id": 1 })

// Verify sharding status
sh.status()
```

#### 9.3.3 Redis Clustering

```bash
# Create Redis cluster (6 nodes: 3 masters, 3 replicas)
redis-cli --cluster create \
  redis-1:6379 redis-2:6379 redis-3:6379 \
  redis-4:6379 redis-5:6379 redis-6:6379 \
  --cluster-replicas 1
```

### 9.4 CDN & Caching Strategy

**CloudFlare / CloudFront Configuration**:
```nginx
# Cache static assets
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
  expires 7d;
  add_header Cache-Control "public, immutable";
}

# Cache API responses (if appropriate)
location /api/v1/food/stats {
  proxy_cache api_cache;
  proxy_cache_valid 200 5m;
  proxy_cache_key "$request_uri";
}
```

---

## 10. Security Operations

### 10.1 Security Monitoring

**Tools**:
- **SIEM**: Splunk, Datadog Security Monitoring
- **Vulnerability Scanning**: Snyk, Trivy
- **WAF**: Cloudflare, AWS WAF
- **DDoS Protection**: Cloudflare, AWS Shield

**Alerts to Configure**:
- Failed login attempts > 10 in 5 minutes
- Unusual API access patterns
- Database query failures
- Privilege escalation attempts
- File system changes
- New IP addresses accessing admin endpoints

### 10.2 Access Control

#### 10.2.1 SSH Access

```bash
# Disable password authentication, use SSH keys only
# /etc/ssh/sshd_config:
PasswordAuthentication no
PubkeyAuthentication yes

# Rotate SSH keys quarterly
ssh-keygen -t ed25519 -C "devops@psi-app.com"

# Use bastion host for production access
ssh -J bastion.psi-app.com production-backend-1
```

#### 10.2.2 Database Access

```sql
-- Create read-only user for analytics
CREATE USER analyst WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE psi_db TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;

-- Revoke unnecessary privileges
REVOKE ALL PRIVILEGES ON DATABASE psi_db FROM PUBLIC;
```

#### 10.2.3 Kubernetes RBAC

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: production
subjects:
- kind: User
  name: developer@psi-app.com
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

### 10.3 Secrets Management

#### 10.3.1 AWS Secrets Manager

```bash
# Store secret
aws secretsmanager create-secret \
  --name psi/prod/secret-key \
  --secret-string "${SECRET_KEY}"

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id psi/prod/secret-key \
  --query SecretString \
  --output text

# Rotate secret
aws secretsmanager rotate-secret \
  --secret-id psi/prod/secret-key
```

#### 10.3.2 Kubernetes Secrets

```bash
# Create secret from file
kubectl create secret generic psi-secrets \
  --from-file=secret-key=./secret.txt \
  --from-literal=db-password="${DB_PASSWORD}" \
  -n production

# Encrypt secrets at rest
kubectl create secret generic psi-secrets --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml
```

### 10.4 Security Incident Response

**Security Incident Types**:
1. **Data Breach**: Unauthorized access to user data
2. **DDoS Attack**: Service degradation from traffic flood
3. **SQL Injection**: Malicious database queries
4. **Credential Compromise**: Leaked API keys or passwords

**Response Procedure**:
```markdown
1. **Contain** (0-15 min)
   - Isolate affected systems
   - Block malicious IPs
   - Revoke compromised credentials

2. **Investigate** (15-60 min)
   - Review logs for intrusion vector
   - Identify scope of breach
   - Preserve evidence

3. **Eradicate** (1-4 hours)
   - Patch vulnerabilities
   - Remove malware/backdoors
   - Reset all passwords

4. **Recover** (4-24 hours)
   - Restore from clean backups
   - Verify system integrity
   - Resume normal operations

5. **Report** (24-72 hours)
   - Notify affected users (GDPR requirement)
   - File regulatory reports (if required)
   - Post-mortem analysis
```

---

## 11. Runbooks

### 11.1 Runbook: High API Latency

**Symptoms**: API response time p95 > 2s

**1. Quick Diagnosis**:
```bash
# Check current latency
curl -w "@curl-format.txt" -o /dev/null -s https://api.psi-app.com/health

# Check backend instances
kubectl top pods -n production | grep psi-backend

# Check database performance
psql -h $POSTGRES_HOST -U psi_user -d psi_db -c "
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"
```

**2. Common Causes & Fixes**:

**A. Database Slow Queries**
```sql
-- Find slow queries
SELECT query, mean_time FROM pg_stat_statements WHERE mean_time > 1000 ORDER BY mean_time DESC;

-- Add missing index
CREATE INDEX CONCURRENTLY idx_food_history_user_created ON food_history(user_id, created_at DESC);
```

**B. YOLO Model Overloaded**
```bash
# Scale up backend instances
kubectl scale deployment/psi-backend --replicas=10 -n production

# Or: Use smaller YOLO model
kubectl set env deployment/psi-backend YOLO_MODEL_PATH=data/models/psi_food_nano.pt -n production
```

**C. External API Timeout (Claude)**
```bash
# Check Claude API status
curl https://status.anthropic.com/api/v2/status.json

# Increase timeout temporarily
kubectl set env deployment/psi-backend CLAUDE_TIMEOUT=30 -n production
```

**3. Escalation**:
If latency persists > 30 minutes, escalate to L2 (Senior Backend Engineer).

---

### 11.2 Runbook: Database Connection Failures

**Symptoms**: "could not connect to server" errors

**1. Verify Database Status**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# or
aws rds describe-db-instances --db-instance-identifier psi-db-prod | jq '.DBInstances[0].DBInstanceStatus'

# Test connection
psql -h $POSTGRES_HOST -U psi_user -d psi_db -c "SELECT 1"
```

**2. Check Connection Pool**:
```sql
-- Check active connections
SELECT COUNT(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- Kill long-running idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';
```

**3. Firewall Rules**:
```bash
# AWS: Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx | jq '.SecurityGroups[0].IpPermissions'

# Test network connectivity
telnet $POSTGRES_HOST 5432
```

**4. Emergency Fix**:
```bash
# Restart PostgreSQL (last resort)
docker restart psi_postgres
# or
aws rds reboot-db-instance --db-instance-identifier psi-db-prod

# Restart backend instances to reset connections
kubectl rollout restart deployment/psi-backend -n production
```

---

### 11.3 Runbook: High Error Rate

**Symptoms**: Error rate > 1%

**1. Identify Error Type**:
```bash
# Check recent errors
kubectl logs deployment/psi-backend -n production --tail=100 | grep ERROR

# Group by error code
kubectl logs deployment/psi-backend -n production --since=1h | \
  grep "error_code" | \
  jq -r '.error_code' | \
  sort | uniq -c | sort -rn
```

**2. Common Error Codes & Fixes**:

**PSI-DB-6002** (Database query failed)
```bash
# Check database health
psql -h $POSTGRES_HOST -U psi_user -d psi_db -c "SELECT 1"

# Check disk space
df -h | grep postgres
```

**PSI-RATE-4002** (Daily limit exceeded)
```bash
# Check if legitimate traffic spike
redis-cli KEYS "rate_limit:*" | wc -l

# Temporarily increase limits (if approved)
kubectl set env deployment/psi-backend FREE_TIER_DAILY_LIMIT=10 -n production
```

**PSI-IMG-7002** (No food detected)
```bash
# Check YOLO model status
kubectl exec -it deployment/psi-backend -n production -- python -c "from app.services.yolo_service import yolo_model; print('Model loaded' if yolo_model else 'Model not loaded')"

# Reload YOLO model (if needed)
kubectl rollout restart deployment/psi-backend -n production
```

**3. Escalation**:
If error rate persists > 15 minutes, page L2 engineer.

---

### 11.4 Runbook: Out of Memory (OOM)

**Symptoms**: Containers restarting with exit code 137

**1. Confirm OOM**:
```bash
# Check exit codes
kubectl get pods -n production | grep Error

# Check events
kubectl describe pod psi-backend-xxx -n production | grep -A 10 Events

# Expected: "OOMKilled" or "Killed"
```

**2. Immediate Fix**:
```bash
# Increase memory limit
kubectl set resources deployment/psi-backend \
  --limits=memory=4Gi \
  --requests=memory=2Gi \
  -n production

# Verify
kubectl rollout status deployment/psi-backend -n production
```

**3. Root Cause Analysis**:
```bash
# Check memory usage before crash (if monitoring enabled)
# Datadog: https://app.datadoghq.com/dashboard/psi-memory

# Common causes:
# - YOLO model too large (try nano model)
# - Memory leak (check with memory_profiler)
# - Too many concurrent requests (reduce)
```

---

### 11.5 Runbook: SSL Certificate Expired

**Symptoms**: "certificate has expired" errors

**1. Verify Expiry**:
```bash
echo | openssl s_client -connect api.psi-app.com:443 2>/dev/null | openssl x509 -noout -dates
```

**2. Renew Certificate**:

**Let's Encrypt (Cert-Manager)**:
```bash
# Force renewal
kubectl delete certificate psi-tls -n production
# Cert-manager will automatically create new one
```

**Manual (Certbot)**:
```bash
certbot renew --force-renewal
nginx -s reload
```

**3. Update in Kubernetes**:
```bash
# If manually renewed
kubectl create secret tls psi-tls \
  --cert=/etc/letsencrypt/live/api.psi-app.com/fullchain.pem \
  --key=/etc/letsencrypt/live/api.psi-app.com/privkey.pem \
  --dry-run=client -o yaml | kubectl apply -f - -n production
```

---

## 12. Appendix

### Appendix A: Contact Information

| Role | Name | Email | Phone | Slack |
|------|------|-------|-------|-------|
| **On-Call DevOps** | [Name] | devops@psi-app.com | +1-555-0100 | @oncall |
| **CTO / Tech Lead** | [Name] | cto@psi-app.com | +1-555-0101 | @cto |
| **Senior Backend Engineer** | [Name] | backend@psi-app.com | +1-555-0102 | @backend-lead |
| **DBA** | [Name] | dba@psi-app.com | +1-555-0103 | @dba |
| **Security Lead** | [Name] | security@psi-app.com | +1-555-0104 | @security |
| **CEO** | [Name] | ceo@psi-app.com | +1-555-0105 | @ceo |

**PagerDuty**: https://psi-app.pagerduty.com

### Appendix B: Useful Commands

```bash
# Docker
docker ps                              # List running containers
docker logs -f psi_backend             # Follow logs
docker exec -it psi_backend bash       # Shell into container
docker stats                           # Resource usage
docker-compose up -d                   # Start all services
docker-compose down                    # Stop all services

# Kubernetes
kubectl get pods -n production         # List pods
kubectl logs -f deploy/psi-backend -n production  # Follow logs
kubectl exec -it deploy/psi-backend -n production -- bash  # Shell
kubectl describe pod psi-backend-xxx -n production  # Pod details
kubectl top pods -n production         # Resource usage
kubectl get events -n production --sort-by='.lastTimestamp'  # Recent events

# Database
psql -h $POSTGRES_HOST -U psi_user -d psi_db  # Connect to PostgreSQL
mongosh mongodb://$MONGO_HOST:27017    # Connect to MongoDB
redis-cli -h $REDIS_HOST               # Connect to Redis

# Logs
tail -f /var/log/psi/app.log           # Follow application logs
grep ERROR /var/log/psi/app.log        # Search for errors
journalctl -u psi-backend -f           # Systemd logs (if applicable)

# Performance
top                                    # System resources
htop                                   # Better top
iostat -x 5                            # Disk I/O
netstat -tulpn                         # Network connections
ss -tulpn                              # Socket statistics (modern)
```

### Appendix C: Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Production API** | https://api.psi-app.com | Live API |
| **Staging API** | https://staging-api.psi-app.com | Testing |
| **API Docs** | https://api.psi-app.com/docs | OpenAPI docs |
| **Status Page** | https://status.psi-app.com | Public status |
| **Monitoring (Datadog)** | https://app.datadoghq.com/dashboard/psi-prod | Metrics |
| **Logs (Kibana)** | https://logs.psi-app.com | Log aggregation |
| **Error Tracking (Sentry)** | https://sentry.io/psi | Error monitoring |
| **CI/CD (GitHub Actions)** | https://github.com/yourusername/psi/actions | Build pipeline |
| **AWS Console** | https://console.aws.amazon.com | Cloud resources |
| **PagerDuty** | https://psi-app.pagerduty.com | On-call alerts |

### Appendix D: Acronyms

| Acronym | Full Term |
|---------|-----------|
| **APM** | Application Performance Monitoring |
| **CDN** | Content Delivery Network |
| **DAU** | Daily Active Users |
| **DR** | Disaster Recovery |
| **ELK** | Elasticsearch, Logstash, Kibana |
| **HPA** | Horizontal Pod Autoscaler (Kubernetes) |
| **JWT** | JSON Web Token |
| **MAU** | Monthly Active Users |
| **OOM** | Out of Memory |
| **PITR** | Point-in-Time Recovery |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |
| **SLA** | Service Level Agreement |
| **SRE** | Site Reliability Engineering |
| **WAF** | Web Application Firewall |
| **WAL** | Write-Ahead Log (PostgreSQL) |

### Appendix E: Configuration Files Reference

```
psi/
├── backend/
│   ├── .env.example              # Environment variable template
│   ├── alembic.ini               # Database migration config
│   └── app/
│       └── core/
│           └── config.py         # Application settings
├── deployment/
│   ├── docker/
│   │   ├── docker-compose.yml    # Local development setup
│   │   └── Dockerfile.backend    # Backend container image
│   └── kubernetes/
│       ├── deployment.yaml       # K8s deployment manifest
│       ├── service.yaml          # K8s service manifest
│       └── ingress.yaml          # K8s ingress manifest
└── docs/
    ├── API_DOCUMENTATION.md      # API reference
    ├── DEPLOYMENT_CHECKLIST.md   # Pre-deployment checklist
    └── OPERATIONS_MANUAL.md      # This document
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-10
**Next Review**: 2026-02-10 (Quarterly)
**Maintained By**: DevOps Team

---

## Feedback & Improvements

This operations manual is a living document. If you encounter issues or have suggestions for improvement:

1. **Create Issue**: https://github.com/yourusername/psi/issues/new?template=ops-manual
2. **Slack**: #ops-manual-feedback
3. **Email**: devops@psi-app.com

**Change Log**:
- 2025-11-10: Initial version (v1.0.0)

---

**Thank you for keeping Psi operational! 🚀**
