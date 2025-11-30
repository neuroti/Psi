# Getting Started with Psi

Welcome to Psi! This guide will help you get the project up and running in minutes.

## 🎯 What You Have

Your Psi project is now fully structured with:

✅ **Backend (FastAPI)** - 19 Python files
✅ **Frontend (React Native)** - 11 TypeScript/JavaScript files
✅ **Database Schemas** - PostgreSQL, MongoDB, Redis
✅ **ML Pipeline** - YOLO v8 training scripts
✅ **Docker Setup** - Multi-container orchestration
✅ **Documentation** - Complete API & setup guides
✅ **CI/CD** - GitHub Actions workflow

**Total**: 37+ source files + configuration

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../mobile
npm install
```

### Step 2: Start Databases

```bash
cd ../deployment/docker
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- MongoDB on port 27017
- Redis on port 6379

### Step 3: Configure Environment

```bash
cd ../../backend
cp .env.example .env

# Edit .env and add:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - CLAUDE_API_KEY (from https://console.anthropic.com/)
```

### Step 4: Initialize Databases

```bash
# PostgreSQL will auto-initialize via docker-compose
# Or manually run:
docker-compose exec postgres psql -U psi_user -d psi_db -f /docker-entrypoint-initdb.d/init.sql
```

### Step 5: Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs for interactive API documentation

### Step 6: Start Mobile App

```bash
cd ../mobile
npm start
```

Scan QR code with Expo Go app on your phone!

## 📱 3 Main Features

### Mode 1: Food Analysis
Upload food photos → Get instant nutrition analysis + emotion-based recommendations

**Try it**:
- Open mobile app → Food tab
- Take photo or upload from gallery
- See calories, nutrients, and personalized tips

### Mode 2: Fridge Recipes
Scan your fridge → Get recipe suggestions based on ingredients + emotion

**Try it**:
- Open mobile app → Recipes tab
- Upload up to 5 fridge photos
- Get personalized recipes with shopping lists

### Mode 3: Wellness Hub
Real-time emotion monitoring → Daily wellness score + recommendations

**Try it**:
- Open mobile app → Wellness tab
- See current emotion state
- Get food, exercise, and content recommendations

## 📊 Project Structure Overview

```
Psi/
├── backend/          # FastAPI server (Python)
├── mobile/           # React Native app (TypeScript)
├── data/             # ML models & datasets
├── deployment/       # Docker & Kubernetes
└── docs/             # Documentation
```

**Key Files**:
- `backend/app/main.py` - Backend entry point
- `mobile/App.tsx` - Mobile app entry point
- `deployment/docker/docker-compose.yml` - Full stack setup
- `docs/SETUP.md` - Detailed setup guide
- `docs/API.md` - Complete API reference

## 🛠️ Development Workflow

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload  # Auto-reload on code changes
```

### Frontend Development
```bash
cd mobile
npm start                       # Expo dev server
npm run ios                     # iOS simulator
npm run android                 # Android emulator
```

### Testing
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd mobile
npm test
```

## 🎓 Next Steps

1. **Read the Documentation**
   - [Complete Setup Guide](docs/SETUP.md)
   - [API Documentation](docs/API.md)
   - [Project Structure](PROJECT_STRUCTURE.md)

2. **Download ML Models**
   ```bash
   cd data/models
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
   ```

3. **Configure Wearables** (Optional)
   - iOS: Enable HealthKit in Xcode
   - Android: Configure Google Fit API

4. **Customize for Your Needs**
   - Add more food categories
   - Train on your own dataset
   - Customize emotion rules
   - Add new API endpoints

## 🐛 Troubleshooting

**Backend won't start?**
- Check `.env` file exists and has required variables
- Verify databases are running: `docker-compose ps`
- Check Python version: `python --version` (should be 3.11+)

**Frontend won't start?**
- Delete `node_modules` and run `npm install` again
- Clear Expo cache: `npm start -- --clear`
- Check Node version: `node --version` (should be 18+)

**Database connection failed?**
- Restart Docker containers: `docker-compose restart`
- Check ports not in use: `lsof -i :5432` (macOS/Linux)
- View Docker logs: `docker-compose logs postgres`

## 📚 Learning Resources

**FastAPI**:
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: Build a backend API

**React Native**:
- Official Docs: https://reactnative.dev/
- Expo Docs: https://docs.expo.dev/

**YOLO v8**:
- Ultralytics Docs: https://docs.ultralytics.com/
- Training Guide: Fine-tune on custom data

**Database**:
- PostgreSQL: https://www.postgresql.org/docs/
- MongoDB: https://docs.mongodb.com/

## 💡 Development Tips

1. **Use Hot Reload**: Both backend and frontend support auto-reload
2. **API Testing**: Use Swagger UI at http://localhost:8000/docs
3. **Debugging**: Add breakpoints in VS Code or PyCharm
4. **Logging**: Check console output for errors
5. **Git Workflow**: Create feature branches for new features

## 🎯 Milestones

- [ ] **Week 1**: Set up development environment
- [ ] **Week 2**: Backend API working locally
- [ ] **Week 3**: Mobile app UI complete
- [ ] **Week 4**: Integration testing
- [ ] **Month 2**: YOLO fine-tuning
- [ ] **Month 3**: Beta release on TestFlight/Play Store

## 🤝 Need Help?

- 📖 Check [docs/SETUP.md](docs/SETUP.md) for detailed setup
- 🐛 Found a bug? Open an issue on GitHub
- 💬 Questions? Join our Discord community
- 📧 Email: support@psi-app.com

## 🎉 You're Ready!

Your Psi platform is now ready for development. Start building your emotion-based wellness app!

**Recommended first tasks**:
1. ✅ Get backend running
2. ✅ Get mobile app running
3. ✅ Test food upload API
4. ✅ Customize emotion rules
5. ✅ Add your own recipes

Happy coding! 🚀
