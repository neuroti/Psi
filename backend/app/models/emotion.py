"""
Emotion Data Models
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List


class EmotionType:
    """8 emotion types supported"""
    STRESS = "stress"
    FATIGUE = "fatigue"
    ANXIETY = "anxiety"
    HAPPINESS = "happiness"
    EXCITEMENT = "excitement"
    CALMNESS = "calmness"
    FOCUS = "focus"
    APATHY = "apathy"


class EmotionData(BaseModel):
    """Emotion data from wearables"""
    emotion_id: str
    user_id: str
    hrv: float
    heart_rate: int
    coherence: float
    emotion_type: str
    emotion_score: int
    timestamp: datetime


class EmotionAnalysisResult(BaseModel):
    """Result of emotion analysis"""
    type: str
    score: int
    all_emotions: Dict[str, float]
    hrv: float
    heart_rate: int


class WellnessScore(BaseModel):
    """Daily wellness score"""
    date: datetime
    score: int  # 0-100
    emotion_distribution: Dict[str, int]
    recommendations: Dict[str, str]


class WellnessResponse(BaseModel):
    """Response for wellness check"""
    current_emotion: EmotionAnalysisResult
    wellness_score: int
    recommendations: Dict[str, List[str]]
    daily_tip: str
