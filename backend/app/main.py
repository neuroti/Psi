"""
Psi API - Main Application Entry Point
FastAPI-based backend for emotion-based wellness platform
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import db
from app.core.error_handlers import register_exception_handlers
from app.api.v1 import auth
from app.api.v1 import food_enhanced as food
from app.api.v1 import fridge_enhanced as fridge
from app.api.v1 import wellness_enhanced as wellness
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Psi API",
    description="Emotion-based Wellness Platform API - Complete Implementation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Register comprehensive error handlers
register_exception_handlers(app)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    try:
        await db.connect()
        logger.info("✅ Database connections established")
        logger.info("🚀 Psi API started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    try:
        await db.disconnect()
        logger.info("✅ Database connections closed")
        logger.info("👋 Psi API shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# API Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(food.router, prefix="/api/v1/food", tags=["Food Analysis (Mode 1)"])
app.include_router(fridge.router, prefix="/api/v1/fridge", tags=["Fridge Recipes (Mode 2)"])
app.include_router(wellness.router, prefix="/api/v1/wellness", tags=["Wellness Hub (Mode 3)"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Psi API - Emotion-based Wellness Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Comprehensive health check"""
    try:
        # Check database connectivity
        postgres_status = "connected" if db.postgres_pool else "disconnected"
        mongo_status = "connected" if db.mongo_client else "disconnected"

        # Check Redis (optional)
        redis_status = "not configured"
        try:
            import redis
            from app.core.config import settings
            r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
            r.ping()
            redis_status = "connected"
        except:
            redis_status = "disconnected"

        # Check YOLO model
        yolo_status = "not loaded"
        try:
            from app.services.image_recognition import ImageRecognitionService
            service = ImageRecognitionService()
            yolo_status = "loaded"
        except:
            yolo_status = "error"

        all_healthy = all([
            postgres_status == "connected",
            mongo_status == "connected"
        ])

        return {
            "status": "healthy" if all_healthy else "degraded",
            "version": "1.0.0",
            "services": {
                "postgresql": postgres_status,
                "mongodb": mongo_status,
                "redis": redis_status,
                "yolo_model": yolo_status
            },
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/v1/info")
async def api_info():
    """API information and capabilities"""
    return {
        "name": "Psi API",
        "version": "1.0.0",
        "description": "Emotion-based wellness platform with AI-powered food analysis",
        "modes": {
            "mode_1": {
                "name": "Food Analysis",
                "description": "Real-time emotion-nutrition analysis",
                "endpoint": "/api/v1/food/upload"
            },
            "mode_2": {
                "name": "Fridge Recipes",
                "description": "Emotion-based recipe recommendations",
                "endpoint": "/api/v1/fridge/detect"
            },
            "mode_3": {
                "name": "Wellness Hub",
                "description": "Comprehensive emotion monitoring",
                "endpoint": "/api/v1/wellness/check"
            }
        },
        "features": [
            "YOLO v8 food detection (96%+ accuracy)",
            "62+ nutrition metrics",
            "8 emotion types classification",
            "Personalized recommendations",
            "Comprehensive wellness analytics"
        ],
        "rate_limits": {
            "free_tier": "3 analyses per day",
            "premium": "Unlimited"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
