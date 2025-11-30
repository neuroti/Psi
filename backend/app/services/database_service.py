"""
Database Service
High-level database operations for food records, users, and emotions
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging
from app.core.database import db

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    async def save_food_record(
        self,
        user_id: str,
        image_url: str,
        foods: List[Dict],
        total_calories: float,
        nutrition: Dict,
        emotion_state: Optional[str] = None,
        emotion_score: Optional[int] = None
    ) -> str:
        """
        Save food record to PostgreSQL

        Args:
            user_id: User ID
            image_url: URL of uploaded image
            foods: List of detected foods
            total_calories: Total calories
            nutrition: Nutrition breakdown
            emotion_state: Current emotion type
            emotion_score: Emotion confidence score

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        query = """
            INSERT INTO food_records (
                record_id, user_id, image_url, foods, total_calories,
                nutrition, emotion_state, emotion_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING record_id
        """

        try:
            import json
            result = await db.execute_one(
                query,
                record_id,
                user_id,
                image_url,
                json.dumps(foods),
                total_calories,
                json.dumps(nutrition),
                emotion_state,
                emotion_score,
                datetime.utcnow()
            )

            logger.info(f"Saved food record: {record_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to save food record: {e}")
            raise

    async def get_food_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get user's food history

        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            List of food records
        """
        query = """
            SELECT record_id, image_url, foods, total_calories,
                   nutrition, emotion_state, emotion_score, created_at
            FROM food_records
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """

        try:
            rows = await db.execute_query(query, user_id, limit, offset)

            return [
                {
                    'record_id': str(row['record_id']),
                    'image_url': row['image_url'],
                    'foods': row['foods'],
                    'total_calories': float(row['total_calories']),
                    'nutrition': row['nutrition'],
                    'emotion_state': row['emotion_state'],
                    'emotion_score': row['emotion_score'],
                    'created_at': row['created_at'].isoformat()
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get food history: {e}")
            return []

    async def save_emotion_data(
        self,
        user_id: str,
        hrv: float,
        heart_rate: int,
        coherence: float,
        emotion_type: str,
        emotion_score: int
    ) -> str:
        """
        Save emotion data to PostgreSQL

        Args:
            user_id: User ID
            hrv: Heart Rate Variability
            heart_rate: Heart rate in bpm
            coherence: Coherence score
            emotion_type: Detected emotion type
            emotion_score: Confidence score

        Returns:
            Emotion data ID
        """
        emotion_id = str(uuid.uuid4())

        query = """
            INSERT INTO emotion_data (
                emotion_id, user_id, hrv, heart_rate, coherence,
                emotion_type, emotion_score, timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING emotion_id
        """

        try:
            result = await db.execute_one(
                query,
                emotion_id,
                user_id,
                hrv,
                heart_rate,
                coherence,
                emotion_type,
                emotion_score,
                datetime.utcnow()
            )

            logger.info(f"Saved emotion data: {emotion_id}")
            return emotion_id

        except Exception as e:
            logger.error(f"Failed to save emotion data: {e}")
            raise

    async def get_emotion_history(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Get user's emotion history

        Args:
            user_id: User ID
            days: Number of days to retrieve

        Returns:
            List of emotion records
        """
        query = """
            SELECT emotion_id, hrv, heart_rate, coherence,
                   emotion_type, emotion_score, timestamp
            FROM emotion_data
            WHERE user_id = $1
              AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """ % days

        try:
            rows = await db.execute_query(query, user_id)

            return [
                {
                    'emotion_id': str(row['emotion_id']),
                    'hrv': float(row['hrv']),
                    'heart_rate': row['heart_rate'],
                    'coherence': float(row['coherence']) if row['coherence'] else None,
                    'emotion_type': row['emotion_type'],
                    'emotion_score': row['emotion_score'],
                    'timestamp': row['timestamp'].isoformat()
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get emotion history: {e}")
            return []

    # Whitelisted usage types to prevent SQL injection
    ALLOWED_USAGE_TYPES = {'food_analyses', 'fridge_analyses', 'wellness_checks'}

    async def check_daily_usage(
        self,
        user_id: str,
        usage_type: str = 'food_analyses'
    ) -> int:
        """
        Check daily usage for free tier limits

        Args:
            user_id: User ID
            usage_type: Type of usage to check (must be in ALLOWED_USAGE_TYPES)

        Returns:
            Current usage count

        Raises:
            ValueError: If usage_type is not in whitelist
            ServiceUnavailableError: If database query fails (fail closed)
        """
        # Validate usage_type to prevent SQL injection
        if usage_type not in self.ALLOWED_USAGE_TYPES:
            raise ValueError(f"Invalid usage type: {usage_type}. Must be one of {self.ALLOWED_USAGE_TYPES}")

        today = datetime.utcnow().date()

        # Now safe to use f-string with whitelisted value
        query = f"""
            SELECT {usage_type} FROM daily_usage
            WHERE user_id = $1 AND date = $2
        """

        try:
            row = await db.execute_one(query, user_id, today)
            return row[usage_type] if row else 0

        except Exception as e:
            logger.error(f"Failed to check daily usage: {e}", exc_info=True)
            # SECURITY: Fail closed - on error, assume limit is reached
            # This prevents database errors from granting unlimited access
            from app.core.exceptions import ServiceUnavailableError
            raise ServiceUnavailableError(
                service="rate_limiter",
                message="Unable to check rate limits. Please try again later.",
                retry_after=60,
                details={"user_id": user_id, "usage_type": usage_type}
            )

    async def increment_daily_usage(
        self,
        user_id: str,
        usage_type: str = 'food_analyses'
    ) -> int:
        """
        Increment daily usage counter atomically

        Args:
            user_id: User ID
            usage_type: Type of usage to increment (must be in ALLOWED_USAGE_TYPES)

        Returns:
            New usage count after increment

        Raises:
            ValueError: If usage_type is not in whitelist
            DatabaseError: If increment operation fails
        """
        # Validate usage_type to prevent SQL injection
        if usage_type not in self.ALLOWED_USAGE_TYPES:
            raise ValueError(f"Invalid usage type: {usage_type}. Must be one of {self.ALLOWED_USAGE_TYPES}")

        today = datetime.utcnow().date()
        usage_id = str(uuid.uuid4())

        # Now safe to use f-string with whitelisted value
        # RETURNING clause ensures we get the new count
        query = f"""
            INSERT INTO daily_usage (usage_id, user_id, date, {usage_type})
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (user_id, date)
            DO UPDATE SET {usage_type} = daily_usage.{usage_type} + 1
            RETURNING {usage_type}
        """

        try:
            row = await db.execute_one(query, usage_id, user_id, today)
            new_count = row[usage_type]
            logger.info(f"Incremented {usage_type} for user {user_id}: {new_count}")
            return new_count

        except Exception as e:
            logger.error(f"Failed to increment daily usage: {e}", exc_info=True)
            # Don't silently fail - raise error so caller knows increment didn't happen
            from app.core.exceptions import DatabaseError
            raise DatabaseError(
                operation="increment_daily_usage",
                message=f"Failed to track usage for {usage_type}",
                original_error=e,
                details={"user_id": user_id, "usage_type": usage_type}
            )

    async def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """
        Get user preferences from MongoDB

        Args:
            user_id: User ID

        Returns:
            User preferences dictionary
        """
        try:
            preferences = await db.mongo_db.user_preferences.find_one(
                {'user_id': user_id}
            )

            if preferences:
                preferences['_id'] = str(preferences['_id'])

            return preferences

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return None

    async def save_user_preferences(
        self,
        user_id: str,
        preferences: Dict
    ):
        """
        Save user preferences to MongoDB

        Args:
            user_id: User ID
            preferences: Preferences dictionary
        """
        try:
            await db.mongo_db.user_preferences.update_one(
                {'user_id': user_id},
                {'$set': {**preferences, 'updated_at': datetime.utcnow()}},
                upsert=True
            )

            logger.info(f"Saved preferences for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
