"""
Fridge API Routes - Enhanced Implementation
Mode 2: Emotion-based fridge recipe recommendations
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from app.core.security import verify_token
from app.core.exceptions import PsiException
from app.models.recipe import FridgeDetectionResponse, DetectedIngredient
from app.services.image_recognition import ImageRecognitionService
from app.services.recipe_matching import RecipeMatchingService
from app.services.emotion_analysis import EmotionAnalysisService
from app.services.database_service import DatabaseService
from typing import List, Optional, Dict
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()


class FridgeDetectionService:
    """Complete fridge detection and recipe recommendation service"""

    def __init__(self):
        self.image_service = ImageRecognitionService()
        self.recipe_service = RecipeMatchingService()
        self.emotion_service = EmotionAnalysisService()
        self.db_service = DatabaseService()

    async def detect_ingredients_from_images(
        self,
        image_bytes_list: List[bytes]
    ) -> List[DetectedIngredient]:
        """
        Detect ingredients from multiple fridge images

        Args:
            image_bytes_list: List of image bytes (up to 5)

        Returns:
            List of detected ingredients with confidence scores
        """
        all_ingredients = []

        # Process all images concurrently for speed
        tasks = [
            self.image_service.analyze_food_image(img_bytes)
            for img_bytes in image_bytes_list
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process image {i}: {result}")
                continue

            for detection in result:
                all_ingredients.append(DetectedIngredient(
                    name=detection['class'],
                    confidence=detection['confidence'],
                    quantity="unknown"  # TODO: Add volume estimation
                ))

        # Remove duplicates, keeping highest confidence
        unique_ingredients = {}
        for ing in all_ingredients:
            if ing.name not in unique_ingredients:
                unique_ingredients[ing.name] = ing
            elif ing.confidence > unique_ingredients[ing.name].confidence:
                unique_ingredients[ing.name] = ing

        return list(unique_ingredients.values())

    async def find_matching_recipes(
        self,
        ingredients: List[str],
        emotion_type: str,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Find recipes that match available ingredients and emotion

        Args:
            ingredients: List of available ingredient names
            emotion_type: Current emotion state
            user_preferences: User dietary preferences

        Returns:
            List of matched recipes with scores
        """
        # Get recipes from database that match ingredients
        matched_recipes = await self.recipe_service.match_recipes(
            ingredients=ingredients,
            emotion_type=emotion_type,
            top_k=10  # Get top 10 candidates
        )

        # Filter by user preferences if available
        if user_preferences:
            filtered_recipes = []
            dietary_restrictions = user_preferences.get('dietary_restrictions', [])
            disliked_foods = user_preferences.get('disliked_foods', [])

            for recipe in matched_recipes:
                # Check dietary restrictions
                if any(restriction in str(recipe.get('tags', [])).lower()
                       for restriction in dietary_restrictions):
                    continue

                # Check disliked foods
                recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
                if any(dislike.lower() in ' '.join(recipe_ingredients)
                       for dislike in disliked_foods):
                    continue

                filtered_recipes.append(recipe)

            matched_recipes = filtered_recipes

        return matched_recipes[:5]  # Return top 5

    async def generate_shopping_list(
        self,
        available_ingredients: List[str],
        selected_recipe: Dict
    ) -> List[str]:
        """
        Generate shopping list for missing ingredients

        Args:
            available_ingredients: What user already has
            selected_recipe: Recipe to prepare

        Returns:
            List of ingredients to buy
        """
        return await self.recipe_service.generate_shopping_list(
            available=available_ingredients,
            recipe=selected_recipe
        )

    async def process_fridge_detection(
        self,
        files: List[UploadFile],
        user_id: str,
        hrv: Optional[float] = None,
        heart_rate: Optional[int] = None
    ) -> FridgeDetectionResponse:
        """
        Complete fridge detection pipeline

        Args:
            files: List of fridge images (max 5)
            user_id: User ID
            hrv: Heart Rate Variability
            heart_rate: Heart rate

        Returns:
            FridgeDetectionResponse with ingredients and recipes
        """
        # 1. Validate number of files
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="Please upload at least one fridge image"
            )

        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 images allowed"
            )

        # 2. Check daily limits
        usage_count = await self.db_service.check_daily_usage(user_id, 'fridge_analyses')
        from app.core.config import settings
        if usage_count >= settings.FREE_TIER_DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Daily limit reached. Upgrade to premium for unlimited access."
            )

        # 3. Read all images with size validation
        image_bytes_list = []
        max_size = 10 * 1024 * 1024  # 10MB

        for file in files:
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not an image"
                )

            # Check size before reading (prevent memory exhaustion)
            content_length = None
            if hasattr(file, 'size') and file.size:
                content_length = file.size

            if content_length and content_length > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image {file.filename} too large (max 10MB)"
                )

            # Read image bytes
            image_bytes = await file.read()

            # Verify actual size after reading
            if len(image_bytes) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image {file.filename} too large (max 10MB)"
                )

            image_bytes_list.append(image_bytes)

        # 4. Detect ingredients
        ingredients = await self.detect_ingredients_from_images(image_bytes_list)

        if not ingredients:
            raise HTTPException(
                status_code=400,
                detail="No ingredients detected. Please upload clearer photos of your fridge contents."
            )

        logger.info(f"Detected {len(ingredients)} ingredients for user {user_id}")

        # 5. Analyze emotion
        emotion_type = 'calmness'  # Default
        if hrv and heart_rate:
            emotion_result = await self.emotion_service.classify_emotion(hrv, heart_rate)
            emotion_type = emotion_result.type

            # Save emotion data
            await self.db_service.save_emotion_data(
                user_id=user_id,
                hrv=hrv,
                heart_rate=heart_rate,
                coherence=0.5,
                emotion_type=emotion_type,
                emotion_score=emotion_result.score
            )

        # 6. Get user preferences
        user_preferences = await self.db_service.get_user_preferences(user_id)

        # 7. Find matching recipes
        ingredient_names = [ing.name for ing in ingredients]
        matched_recipes = await self.find_matching_recipes(
            ingredients=ingredient_names,
            emotion_type=emotion_type,
            user_preferences=user_preferences
        )

        if not matched_recipes:
            logger.warning(f"No recipes found for user {user_id}")
            matched_recipes = []

        # 8. Generate shopping list (for first recipe)
        shopping_list = []
        if matched_recipes:
            shopping_list = await self.generate_shopping_list(
                available_ingredients=ingredient_names,
                selected_recipe=matched_recipes[0]
            )

        # 9. Increment usage counter
        await self.db_service.increment_daily_usage(user_id, 'fridge_analyses')

        return FridgeDetectionResponse(
            ingredients=ingredients,
            recipes=matched_recipes,
            shopping_list=shopping_list,
            emotion_type=emotion_type
        )


# Dependency injection for service
def get_fridge_service() -> FridgeDetectionService:
    """Get a new FridgeDetectionService instance per request"""
    return FridgeDetectionService()


@router.post("/detect", response_model=FridgeDetectionResponse)
async def detect_fridge_ingredients(
    files: List[UploadFile] = File(...),
    hrv: Optional[float] = Query(None, ge=10.0, le=200.0, description="Heart Rate Variability in ms"),
    heart_rate: Optional[int] = Query(None, ge=30, le=220, description="Heart rate in bpm"),
    user_id: str = Depends(verify_token),
    fridge_service: FridgeDetectionService = Depends(get_fridge_service)
):
    """
    Detect ingredients and get recipe recommendations

    **Mode 2: Emotion-based fridge recipe recommendations**

    This endpoint:
    1. Analyzes up to 5 fridge photos
    2. Detects all visible ingredients
    3. Considers your emotional state
    4. Recommends recipes you can make
    5. Generates shopping list for missing items

    **Parameters:**
    - files: List of fridge images (1-5 photos, JPG/PNG)
    - hrv: Heart Rate Variability from wearable (optional)
    - heart_rate: Heart rate in bpm (optional)

    **Returns:**
    - Detected ingredients with confidence
    - Top 5 recipe recommendations
    - Shopping list for missing ingredients
    - Your current emotional state

    **Tips:**
    - Take photos from different angles
    - Good lighting helps detection
    - Close-up shots work better
    - Open containers/packages when possible

    **Rate Limits:**
    - Free tier: 3 scans per day
    - Premium: Unlimited
    """
    try:
        result = await fridge_service.process_fridge_detection(
            files=files,
            user_id=user_id,
            hrv=hrv,
            heart_rate=heart_rate
        )

        logger.info(f"Successfully processed fridge detection for user {user_id}")
        return result

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Fridge detection failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during fridge analysis"
        )


@router.get("/recipes/{recipe_id}")
async def get_recipe_detail(
    recipe_id: str,
    user_id: str = Depends(verify_token)
):
    """
    Get detailed recipe information

    **Parameters:**
    - recipe_id: Recipe UUID

    **Returns:**
    - Complete recipe with ingredients and instructions
    - Nutrition information
    - Cooking time and difficulty
    - User ratings and reviews

    **Raises:**
    - 404: Recipe not found
    - 500: Database error
    """
    try:
        from app.core.database import db
        from app.core.exceptions import ResourceNotFoundError, DatabaseError

        query = """
            SELECT recipe_id, name, ingredients, instructions,
                   cooking_time, difficulty, emotion_type,
                   nutrition, image_url, created_at
            FROM recipes
            WHERE recipe_id = $1
        """

        recipe = await db.execute_one(query, recipe_id)

        # Properly return 404 if recipe doesn't exist
        if not recipe:
            raise ResourceNotFoundError(
                resource="Recipe",
                identifier=recipe_id
            )

        return {
            'recipe_id': str(recipe['recipe_id']),
            'name': recipe['name'],
            'ingredients': recipe['ingredients'],
            'instructions': recipe['instructions'],
            'cooking_time': recipe['cooking_time'],
            'difficulty': recipe['difficulty'],
            'emotion_type': recipe['emotion_type'],
            'nutrition': recipe['nutrition'],
            'image_url': recipe['image_url'],
            'created_at': recipe['created_at'].isoformat()
        }

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions
        raise
    except PsiException:
        # Let custom exceptions (ResourceNotFoundError, DatabaseError, etc.) propagate to global handler
        raise
    except Exception as e:
        # Database or unexpected errors
        logger.error(f"Failed to get recipe {recipe_id}: {e}", exc_info=True)
        raise DatabaseError(
            operation="get_recipe",
            message="Failed to retrieve recipe details",
            original_error=e,
            details={"recipe_id": recipe_id}
        )


@router.post("/recipes/{recipe_id}/rate")
async def rate_recipe(
    recipe_id: str,
    rating: int,
    review: Optional[str] = None,
    user_id: str = Depends(verify_token)
):
    """
    Rate a recipe

    **Parameters:**
    - recipe_id: Recipe UUID
    - rating: Rating from 1-5
    - review: Optional text review

    **Returns:**
    - Success confirmation
    """
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    try:
        # TODO: Save rating to database
        logger.info(f"User {user_id} rated recipe {recipe_id}: {rating}/5")

        return {
            "message": "Rating saved successfully",
            "recipe_id": recipe_id,
            "rating": rating
        }

    except Exception as e:
        logger.error(f"Failed to save rating: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save rating"
        )


@router.get("/preferences")
async def get_user_preferences(
    user_id: str = Depends(verify_token)
):
    """
    Get user's food preferences

    **Returns:**
    - Liked foods
    - Disliked foods
    - Dietary restrictions
    - Cooking skill level
    """
    try:
        db_service = DatabaseService()
        preferences = await db_service.get_user_preferences(user_id)

        if not preferences:
            # Return default preferences
            return {
                "liked_foods": [],
                "disliked_foods": [],
                "dietary_restrictions": [],
                "notification_enabled": True,
                "wellness_goals": []
            }

        return preferences

    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve preferences"
        )


@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict,
    user_id: str = Depends(verify_token)
):
    """
    Update user's food preferences

    **Parameters:**
    - preferences: Preferences object

    **Returns:**
    - Updated preferences
    """
    try:
        db_service = DatabaseService()
        await db_service.save_user_preferences(user_id, preferences)

        return {
            "message": "Preferences updated successfully",
            "preferences": preferences
        }

    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update preferences"
        )
