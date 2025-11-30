"""
Food Record Data Models
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional


class FoodItem(BaseModel):
    """Individual food item"""
    name: str
    confidence: float
    grams: float
    calories: float
    nutrition: Dict[str, float]


class EmotionState(BaseModel):
    """Emotion state"""
    type: str
    score: int
    hrv: float
    heart_rate: int


class FoodAnalysisRequest(BaseModel):
    """Request for food analysis"""
    hrv: Optional[float] = None
    heart_rate: Optional[int] = None


class FoodAnalysisResponse(BaseModel):
    """Response from food analysis"""
    food_items: List[FoodItem]
    total_calories: float
    nutrition: Dict[str, float]
    emotion: Optional[EmotionState] = None
    recommendation: str
    xp_gained: int


class FoodRecord(BaseModel):
    """Food record stored in database"""
    record_id: str
    user_id: str
    image_url: str
    foods: List[FoodItem]
    total_calories: float
    nutrition: Dict[str, float]
    emotion_state: Optional[str] = None
    emotion_score: Optional[int] = None
    created_at: datetime
