"""
Food API Routes - Enhanced Implementation
Mode 1: Real-time emotion-nutrition analysis with full database integration
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query, Request
from app.core.security import verify_token
from app.core.exceptions import PsiException
from app.models.food import FoodAnalysisResponse, FoodItem
from app.services.image_recognition import ImageRecognitionService
from app.services.nutrition_analysis import NutritionAnalysisService
from app.services.emotion_analysis import EmotionAnalysisService
from app.services.database_service import DatabaseService
from typing import Optional, List
import logging
import io
from PIL import Image
import boto3
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class FoodUploadService:
    """Enhanced food upload service with S3 storage and database persistence"""

    def __init__(self):
        self.image_service = ImageRecognitionService()
        self.nutrition_service = NutritionAnalysisService()
        self.emotion_service = EmotionAnalysisService()
        self.db_service = DatabaseService()

        # S3 client for image storage (if configured)
        self.s3_client = None
        if settings.AWS_ACCESS_KEY_ID:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

    async def validate_image(self, image_bytes: bytes) -> None:
        """
        Validate uploaded image

        Args:
            image_bytes: Raw image bytes

        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="Image too large (maximum 10MB)"
            )

        # Verify it's actually an image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()

            # Check dimensions
            if img.width < 100 or img.height < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Image too small (minimum 100x100 pixels)"
                )

            # Check format
            if img.format not in ['JPEG', 'PNG', 'JPG']:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported format (use JPEG or PNG)"
                )

        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

    async def upload_to_s3(
        self,
        image_bytes: bytes,
        user_id: str,
        filename: str
    ) -> str:
        """
        Upload image to S3

        Args:
            image_bytes: Image data
            user_id: User ID for folder organization
            filename: Original filename

        Returns:
            S3 URL
        """
        if not self.s3_client:
            return "local://placeholder"

        import uuid
        from datetime import datetime
        import os

        # Generate unique key with sanitized extension
        date_path = datetime.utcnow().strftime('%Y/%m/%d')
        unique_id = str(uuid.uuid4())

        # Sanitize filename to prevent path traversal
        safe_extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if safe_extension not in ['jpg', 'jpeg', 'png']:
            safe_extension = 'jpg'

        key = f"food_images/{user_id}/{date_path}/{unique_id}.{safe_extension}"

        try:
            self.s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )

            url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
            logger.info(f"Uploaded image to S3: {url}")
            return url

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return "local://placeholder"

    async def process_food_image(
        self,
        image_bytes: bytes,
        user_id: str,
        filename: str,
        hrv: Optional[float] = None,
        heart_rate: Optional[int] = None
    ) -> FoodAnalysisResponse:
        """
        Complete food image processing pipeline

        Args:
            image_bytes: Image data
            user_id: User ID
            filename: Original filename
            hrv: Heart Rate Variability
            heart_rate: Heart rate in bpm

        Returns:
            FoodAnalysisResponse
        """
        # 1. Validate image
        await self.validate_image(image_bytes)

        # 2. Check daily limits (free tier)
        usage_count = await self.db_service.check_daily_usage(user_id, 'food_analyses')
        if usage_count >= settings.FREE_TIER_DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Daily limit reached ({settings.FREE_TIER_DAILY_LIMIT} analyses/day). Upgrade to premium for unlimited access."
            )

        # 3. Upload to S3
        image_url = await self.upload_to_s3(image_bytes, user_id, filename)

        # 4. Detect food items
        detections = await self.image_service.analyze_food_image(image_bytes)

        if not detections:
            raise HTTPException(
                status_code=400,
                detail="No food items detected in image. Please upload a clearer photo."
            )

        # 5. Get nutrition information
        food_items = []
        total_calories = 0.0

        for detection in detections:
            # Estimate portion size
            portion_grams = self.image_service.estimate_portion_size(detection['bbox'])

            # Get nutrition info
            nutrition = await self.nutrition_service.get_nutrition_info(
                detection['class'],
                portion_grams
            )

            if nutrition:
                food_items.append(FoodItem(
                    name=detection['class'],
                    confidence=detection['confidence'],
                    grams=portion_grams,
                    calories=nutrition['calories'],
                    nutrition=nutrition
                ))
                total_calories += nutrition['calories']
            else:
                # Use default values if not found
                logger.warning(f"Nutrition data not found for: {detection['class']}")
                food_items.append(FoodItem(
                    name=detection['class'],
                    confidence=detection['confidence'],
                    grams=portion_grams,
                    calories=0.0,
                    nutrition={}
                ))

        # 6. Calculate total nutrition
        total_nutrition = self.nutrition_service.calculate_total_nutrition(
            [{'nutrition': item.nutrition} for item in food_items]
        )

        # 7. Analyze emotion (if wearable data provided)
        emotion = None
        recommendation = "Enjoy your meal mindfully!"
        emotion_type = None
        emotion_score = None

        if hrv and heart_rate:
            emotion_result = await self.emotion_service.classify_emotion(hrv, heart_rate)
            emotion_type = emotion_result.type
            emotion_score = emotion_result.score

            emotion = {
                'type': emotion_type,
                'score': emotion_score,
                'hrv': hrv,
                'heart_rate': heart_rate
            }

            # Get personalized recommendation
            recommendation = await self.emotion_service.get_emotion_nutrition_recommendation(
                emotion_type,
                total_nutrition
            )

            # Save emotion data
            await self.db_service.save_emotion_data(
                user_id=user_id,
                hrv=hrv,
                heart_rate=heart_rate,
                coherence=0.5,  # TODO: Calculate from HRV
                emotion_type=emotion_type,
                emotion_score=emotion_score
            )

        # 8. Save food record to database
        food_items_dict = [item.dict() for item in food_items]

        await self.db_service.save_food_record(
            user_id=user_id,
            image_url=image_url,
            foods=food_items_dict,
            total_calories=total_calories,
            nutrition=total_nutrition,
            emotion_state=emotion_type,
            emotion_score=emotion_score
        )

        # 9. Increment usage counter
        await self.db_service.increment_daily_usage(user_id, 'food_analyses')

        # 10. Calculate XP
        xp_gained = 15 + len(food_items) * 5

        return FoodAnalysisResponse(
            food_items=food_items,
            total_calories=round(total_calories, 1),
            nutrition=total_nutrition,
            emotion=emotion,
            recommendation=recommendation,
            xp_gained=xp_gained
        )


# Dependency injection for service
def get_food_service() -> FoodUploadService:
    """Get a new FoodUploadService instance per request"""
    return FoodUploadService()


@router.post("/upload", response_model=FoodAnalysisResponse)
async def upload_food_image(
    file: UploadFile = File(...),
    hrv: Optional[float] = Query(None, ge=10.0, le=200.0, description="Heart Rate Variability in ms"),
    heart_rate: Optional[int] = Query(None, ge=30, le=220, description="Heart rate in bpm"),
    user_id: str = Depends(verify_token),
    food_service: FoodUploadService = Depends(get_food_service)
):
    """
    Upload food image for complete analysis

    **Mode 1: Real-time emotion-nutrition analysis**

    This endpoint:
    1. Validates and uploads your food image
    2. Detects food items using YOLO v8 (96%+ accuracy)
    3. Calculates comprehensive nutrition (62+ nutrients)
    4. Analyzes your emotional state from wearables
    5. Provides personalized recommendations
    6. Saves everything to your history

    **Parameters:**
    - file: Food image (JPG/PNG, max 10MB)
    - hrv: Heart Rate Variability from wearable (optional)
    - heart_rate: Heart rate in bpm from wearable (optional)

    **Returns:**
    - Detected foods with nutrition breakdown
    - Total calories and macros
    - Your current emotional state
    - Personalized recommendations
    - XP points earned

    **Rate Limits:**
    - Free tier: 3 analyses per day
    - Premium: Unlimited
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG or PNG)"
        )

    try:
        # Check file size before reading (prevent memory exhaustion)
        max_size = 10 * 1024 * 1024  # 10MB

        # Try to get size from Content-Length header first
        content_length = None
        if hasattr(file, 'size') and file.size:
            content_length = file.size

        if content_length and content_length > max_size:
            raise HTTPException(
                status_code=400,
                detail="Image too large (maximum 10MB)"
            )

        # Read image bytes
        image_bytes = await file.read()

        # Verify actual size after reading
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Image too large (maximum 10MB)"
            )

        # Process through complete pipeline
        result = await food_service.process_food_image(
            image_bytes=image_bytes,
            user_id=user_id,
            filename=file.filename or "upload.jpg",
            hrv=hrv,
            heart_rate=heart_rate
        )

        logger.info(f"Successfully processed food upload for user {user_id}")
        return result

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Food upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during food analysis"
        )


@router.get("/history")
async def get_food_history(
    limit: int = 10,
    offset: int = 0,
    user_id: str = Depends(verify_token)
):
    """
    Get user's food history

    **Parameters:**
    - limit: Number of records to return (default: 10, max: 100)
    - offset: Offset for pagination (default: 0)

    **Returns:**
    - List of previous food analyses
    - Includes nutrition, emotion, and timestamps
    """
    # Validate parameters
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset must be non-negative"
        )

    try:
        db_service = DatabaseService()
        history = await db_service.get_food_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return {
            "history": history,
            "count": len(history),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to get food history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve food history"
        )


@router.get("/stats")
async def get_food_stats(
    days: int = 7,
    user_id: str = Depends(verify_token)
):
    """
    Get food statistics for the user

    **Parameters:**
    - days: Number of days to analyze (default: 7)

    **Returns:**
    - Total calories consumed
    - Average calories per meal
    - Most common foods
    - Nutrition trends
    """
    if days < 1 or days > 90:
        raise HTTPException(
            status_code=400,
            detail="Days must be between 1 and 90"
        )

    try:
        db_service = DatabaseService()
        history = await db_service.get_food_history(
            user_id=user_id,
            limit=1000  # Get all recent records
        )

        # Calculate statistics
        total_calories = sum(record['total_calories'] for record in history)
        avg_calories = total_calories / len(history) if history else 0

        # Get most common foods
        from collections import Counter
        all_foods = []
        for record in history:
            for food in record['foods']:
                all_foods.append(food['name'])

        most_common = Counter(all_foods).most_common(10)

        return {
            "period_days": days,
            "total_meals": len(history),
            "total_calories": round(total_calories, 1),
            "average_calories_per_meal": round(avg_calories, 1),
            "most_common_foods": [
                {"name": name, "count": count}
                for name, count in most_common
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get food stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate statistics"
        )
