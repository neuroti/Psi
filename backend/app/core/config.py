"""
Application Configuration
Environment variables and settings management
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Psi API"

    # Security
    SECRET_KEY: str = "test-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "psi_db"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "psi"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # External APIs
    CLAUDE_API_KEY: str = "test-api-key"
    USDA_API_KEY: str = ""  # Optional, using local DB

    # YOLO Settings
    YOLO_MODEL_PATH: str = "data/models/psi_food_best.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    YOLO_HIGH_CONFIDENCE_THRESHOLD: float = 0.8

    # AWS S3 (for image storage)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "exp://localhost:19000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Free Tier Limits
    FREE_TIER_DAILY_LIMIT: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


try:
    settings = Settings()
except Exception as e:
    # If .env file doesn't exist or there are validation errors, use defaults
    import os
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    settings = Settings()
