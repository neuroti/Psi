# Psi Project Structure

Complete directory structure for the Psi emotion-based wellness platform.

```
Psi/
│
├── backend/                          # FastAPI Backend (Python)
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py          # Authentication routes
│   │   │       ├── food.py          # Mode 1: Food analysis
│   │   │       ├── fridge.py        # Mode 2: Fridge recipes
│   │   │       └── wellness.py      # Mode 3: Wellness hub
│   │   ├── core/
│   │   │   ├── config.py            # App configuration
│   │   │   └── security.py          # JWT & password hashing
│   │   ├── models/
│   │   │   ├── user.py              # User data models
│   │   │   ├── food.py              # Food record models
│   │   │   ├── emotion.py           # Emotion data models
│   │   │   └── recipe.py            # Recipe models
│   │   ├── services/
│   │   │   ├── image_recognition.py # YOLO v8 integration
│   │   │   ├── nutrition_analysis.py # USDA nutrition lookup
│   │   │   ├── emotion_analysis.py   # 8-emotion classification
│   │   │   └── recipe_matching.py    # TF-IDF recipe matching
│   │   ├── utils/                    # Utility functions
│   │   └── main.py                   # FastAPI app entry point
│   ├── scripts/
│   │   ├── init_postgres.sql         # PostgreSQL initialization
│   │   ├── init_mongodb.js           # MongoDB initialization
│   │   └── train_yolo.py             # YOLO training script
│   ├── tests/                        # Backend tests
│   ├── requirements.txt              # Python dependencies
│   ├── pyproject.toml               # Poetry configuration
│   └── .env.example                 # Environment variables template
│
├── mobile/                           # React Native Mobile App
│   ├── src/
│   │   ├── screens/
│   │   │   ├── FoodAnalysisScreen.tsx   # Mode 1 UI
│   │   │   ├── FridgeRecipeScreen.tsx   # Mode 2 UI
│   │   │   ├── WellnessHubScreen.tsx    # Mode 3 UI
│   │   │   └── ProfileScreen.tsx        # User profile
│   │   ├── components/                   # Reusable components
│   │   ├── navigation/
│   │   │   └── AppNavigator.tsx         # Tab navigation
│   │   ├── services/
│   │   │   └── api.ts                   # API client
│   │   ├── store/
│   │   │   ├── index.ts                 # Redux store config
│   │   │   └── slices/
│   │   │       ├── authSlice.ts         # Auth state
│   │   │       ├── foodSlice.ts         # Food state
│   │   │       └── wellnessSlice.ts     # Wellness state
│   │   ├── utils/                       # Utility functions
│   │   ├── hooks/                       # Custom React hooks
│   │   ├── contexts/                    # React contexts
│   │   ├── constants/                   # App constants
│   │   └── assets/                      # Images & icons
│   ├── __tests__/                       # Frontend tests
│   ├── App.tsx                          # App entry point
│   ├── package.json                     # npm dependencies
│   └── app.json                         # Expo configuration
│
├── data/                             # ML Models & Datasets
│   ├── models/
│   │   ├── psi_food_best.pt         # Fine-tuned YOLO model
│   │   ├── yolov8m.pt               # Base YOLO v8 model
│   │   └── README.md                # Model documentation
│   └── datasets/
│       ├── food/
│       │   ├── train/               # Training data (80%)
│       │   │   ├── images/
│       │   │   └── labels/
│       │   ├── val/                 # Validation data (10%)
│       │   │   ├── images/
│       │   │   └── labels/
│       │   ├── test/                # Test data (10%)
│       │   │   ├── images/
│       │   │   └── labels/
│       │   └── data.yaml            # Dataset configuration
│       └── README.md                # Dataset documentation
│
├── deployment/                       # Deployment Configurations
│   ├── docker/
│   │   ├── docker-compose.yml       # Multi-container orchestration
│   │   └── Dockerfile.backend       # Backend container
│   └── kubernetes/                   # K8s configs (future)
│       ├── backend-deployment.yaml
│       ├── postgres-statefulset.yaml
│       └── ingress.yaml
│
├── docs/                             # Documentation
│   ├── API.md                        # API reference
│   ├── SETUP.md                      # Setup guide
│   ├── DEVELOPMENT.md                # Development guide
│   └── CONTRIBUTING.md               # Contributing guidelines
│
├── .github/                          # GitHub Actions
│   └── workflows/
│       └── ci.yml                    # CI/CD pipeline
│
├── .gitignore                        # Git ignore rules
├── README.md                         # Project overview
├── LICENSE                           # MIT License
├── Psi_PRD_LLD_PLAN                 # Original planning document
└── PROJECT_STRUCTURE.md             # This file
```

## Key Components

### Backend (FastAPI)

**Purpose**: REST API server with ML inference and business logic

**Technology Stack**:
- FastAPI (Python web framework)
- YOLO v8 (food detection)
- Claude Vision API (advanced image analysis)
- PostgreSQL (relational data)
- MongoDB (flexible schemas)
- Redis (caching)
- SQLite (local USDA database)

**Key Features**:
- JWT authentication
- Image recognition (96%+ accuracy)
- Nutrition analysis (62+ nutrients)
- Emotion classification (8 types)
- Recipe matching (TF-IDF)

### Frontend (React Native)

**Purpose**: Cross-platform mobile app for iOS and Android

**Technology Stack**:
- React Native 0.73
- Expo 50
- Redux Toolkit (state management)
- React Navigation (routing)
- Axios (HTTP client)
- Apple HealthKit & Google Fit (wearables)

**3 Main Modes**:
1. **Food Analysis**: Upload food photos for instant nutrition analysis
2. **Fridge Recipes**: Get personalized recipes from fridge ingredients
3. **Wellness Hub**: Real-time emotion monitoring and recommendations

### Data Layer

**Databases**:
1. **PostgreSQL**: Users, food records, emotion data (ACID)
2. **MongoDB**: User preferences, time series, RLHF data
3. **Redis**: Caching layer (detection results, nutrition data)
4. **SQLite**: Local USDA nutrition database (400K+ items)

### ML Models

**YOLO v8**:
- Base model: yolov8m.pt (medium)
- Custom fine-tuned: psi_food_best.pt
- Training data: 10K+ Korean & international foods
- Accuracy: 96%+
- Inference: 0.5s (GPU) / 1-2s (CPU)

## File Count Summary

- **Backend**: ~30 Python files
- **Frontend**: ~40 TypeScript/JavaScript files
- **Documentation**: 6 markdown files
- **Configuration**: 10+ config files
- **Total**: ~90 files (excluding datasets/models)

## Size Estimates

- **Backend code**: ~5 MB
- **Frontend code**: ~3 MB (excluding node_modules)
- **Dependencies**:
  - Python packages: ~500 MB
  - Node modules: ~400 MB
- **ML Models**:
  - YOLO v8: ~50 MB
  - Training datasets: ~5 GB
- **Databases** (empty): ~100 MB

## Development Workflow

1. **Backend**: Edit in `backend/app/` → Run `uvicorn` → Test at http://localhost:8000/docs
2. **Frontend**: Edit in `mobile/src/` → Run `npm start` → Test on Expo Go
3. **Database**: Run `docker-compose up -d` → Databases ready
4. **ML**: Train in `backend/scripts/` → Save to `data/models/`

## Production Deployment

```bash
# Build all services
docker-compose -f deployment/docker/docker-compose.yml build

# Start production stack
docker-compose -f deployment/docker/docker-compose.yml up -d

# Mobile app: Build with EAS
cd mobile
eas build --platform all
```

## Next Steps

1. Clone the repository
2. Follow [docs/SETUP.md](docs/SETUP.md) for installation
3. Read [docs/API.md](docs/API.md) for API reference
4. Check [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for dev guidelines
5. Start building! 🚀
