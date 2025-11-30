"""
User Data Models
PostgreSQL and Pydantic models for users
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class SubscriptionType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserLogin(UserBase):
    """User login schema"""
    password: str


class UserResponse(UserBase):
    """User response schema"""
    user_id: str
    subscription_type: SubscriptionType
    profile_pic_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """User preferences stored in MongoDB"""
    user_id: str
    liked_foods: list[str] = []
    disliked_foods: list[str] = []
    dietary_restrictions: list[str] = []
    notification_enabled: bool = True
    wellness_goals: list[str] = []
