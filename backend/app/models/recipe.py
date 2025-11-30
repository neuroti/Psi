"""
Recipe Data Models
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict


class Ingredient(BaseModel):
    """Recipe ingredient"""
    name: str
    quantity: str
    unit: str


class RecipeStep(BaseModel):
    """Cooking step"""
    step_number: int
    instruction: str
    duration_minutes: int


class Recipe(BaseModel):
    """Recipe model"""
    recipe_id: str
    name: str
    ingredients: List[Ingredient]
    instructions: List[RecipeStep]
    cooking_time: int
    difficulty: str  # easy, medium, hard
    emotion_type: str
    nutrition: Dict[str, float]
    image_url: str = ""
    created_at: datetime


class FridgeDetectionRequest(BaseModel):
    """Request for fridge detection"""
    pass  # Images sent as multipart/form-data


class DetectedIngredient(BaseModel):
    """Detected ingredient from fridge"""
    name: str
    confidence: float
    quantity: str


class FridgeDetectionResponse(BaseModel):
    """Response from fridge detection"""
    ingredients: List[DetectedIngredient]
    recipes: List[Dict]
    shopping_list: List[str]
    emotion_type: str
