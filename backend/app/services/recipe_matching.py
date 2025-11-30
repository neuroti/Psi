"""
레시피 매칭 서비스
Recipe Matching Service

TF-IDF 알고리즘 기반 레시피 매칭 및 감정 점수 계산
- 보유 재료로 만들 수 있는 레시피 검색 (70% 이상 매칭)
- 현재 감정 상태에 맞는 조리 시간/난이도 추천
- 부족한 재료 자동 추출 (쇼핑 리스트)

TF-IDF based recipe matching with emotion scoring
- Search recipes that can be made with available ingredients (70%+ match)
- Recommend cooking time/difficulty based on current emotion
- Automatic extraction of missing ingredients (shopping list)
"""
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import json


class RecipeMatchingService:
    """
    레시피 매칭 서비스
    Service for matching recipes based on ingredients and emotion

    냉장고에 있는 재료와 현재 감정 상태를 고려하여
    최적의 레시피를 추천합니다.

    매칭 알고리즘:
    1. 재료 매칭: TF-IDF로 재료 유사도 계산
    2. 감정 점수: 조리 시간 + 난이도가 감정에 적합한지
    3. 최종 점수: (재료 매칭 + 감정 점수) / 2

    감정별 선호 레시피:
    - Stress: 간단한 요리 (5-15분, easy)
    - Happiness: 복잡한 요리 (20-40분, medium)
    - Fatigue: 빠른 요리 (10-20분, easy)
    """

    def __init__(self):
        """
        레시피 매칭 서비스 초기화
        Initialize vectorizer and load recipes

        초기화 항목:
        1. TF-IDF Vectorizer 초기화 (재료 매칭용)
        2. 레시피 데이터베이스 로드 (MongoDB)
        """
        # TF-IDF 벡터라이저 (텍스트 유사도 계산)
        # TF-IDF vectorizer for text similarity calculation
        self.vectorizer = TfidfVectorizer()

        # 레시피 목록 (MongoDB에서 로드)
        # Recipe list (loaded from MongoDB)
        self.recipes = []
        self._load_recipes()

    def _load_recipes(self):
        """Load recipes from database or file"""
        # Placeholder: Load from MongoDB or JSON file
        # In production, this would load from the recipes database
        self.recipes = [
            {
                'recipe_id': '1',
                'name': 'Simple Pasta',
                'ingredients': ['pasta', 'tomato', 'garlic', 'olive oil'],
                'cooking_time': 15,
                'difficulty': 'easy',
                'emotion_types': ['stress', 'fatigue']
            },
            # More recipes...
        ]

    async def match_recipes(
        self,
        ingredients: List[str],
        emotion_type: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        재료와 감정 기반 레시피 매칭
        Match recipes based on available ingredients and emotion

        냉장고에 있는 재료와 현재 감정을 고려하여
        만들 수 있는 최적의 레시피를 추천합니다.

        매칭 프로세스:
        1. 70% 이상 재료가 일치하는 레시피 검색
        2. 각 레시피에 대해 감정 점수 계산
        3. 재료 매칭 점수 계산 (보유 재료 / 필요 재료)
        4. 최종 점수 = (재료 점수 + 감정 점수) / 2
        5. 상위 k개 레시피 반환

        Args:
            ingredients: 보유 재료 목록 (예: ["tomato", "onion", "garlic"])
            emotion_type: 현재 감정 유형 (8가지 중 하나)
            top_k: 반환할 레시피 개수 (기본값 5개)

        Returns:
            List[Dict]: 추천 레시피 목록 (점수 내림차순 정렬)
                각 항목: {
                    'recipe_id': str,
                    'name': str - 레시피 이름,
                    'ingredients': List[str] - 필요한 재료,
                    'cooking_time': int - 조리 시간 (분),
                    'difficulty': str - 난이도,
                    'emotion_score': float - 감정 적합도 (0-1),
                    'ingredient_match': float - 재료 매칭률 (0-1),
                    'available_ingredients': int - 보유 재료 수,
                    'total_ingredients': int - 전체 필요 재료 수
                }

        예제:
            >>> ingredients = ["tomato", "pasta", "garlic", "olive oil"]
            >>> recipes = await service.match_recipes(ingredients, "stress", top_k=3)
            >>> for recipe in recipes:
            >>>     print(f"{recipe['name']}: {recipe['ingredient_match']*100}% match")
            Simple Pasta: 100% match
            Garlic Bread: 75% match
            Tomato Soup: 80% match
        """
        # 재료를 텍스트로 변환 (TF-IDF 입력용)
        # Convert ingredients to text for TF-IDF
        ingredient_text = ' '.join(ingredients)

        # === 1단계: 재료 기반 레시피 검색 ===
        # Stage 1: Search recipes based on ingredients
        # 70% 이상 재료가 일치하는 레시피만 선택
        # Select only recipes with 70%+ ingredient match
        candidates = self._search_recipes(ingredients)

        # === 2단계: 점수 계산 ===
        # Stage 2: Calculate scores
        for recipe in candidates:
            # 감정 적합도 점수 (조리 시간 + 난이도)
            # Emotion fit score (cooking time + difficulty)
            recipe['emotion_score'] = self._score_by_emotion(recipe, emotion_type)

            # 재료 매칭률 (보유 재료 / 필요 재료)
            # Ingredient match rate (available / required)
            recipe['ingredient_match'] = self._calculate_ingredient_match(
                ingredients,
                recipe['ingredients']
            )

        # === 3단계: 최종 점수로 정렬 ===
        # Stage 3: Sort by final score
        # 최종 점수 = (감정 점수 + 재료 점수) / 2
        # Final score = (emotion score + ingredient score) / 2
        candidates.sort(
            key=lambda x: (x['emotion_score'] + x['ingredient_match']) / 2,
            reverse=True
        )

        # 상위 k개 레시피 반환
        # Return top k recipes
        return candidates[:top_k]

    def _search_recipes(self, ingredients: List[str]) -> List[Dict]:
        """
        Search recipes that can be made with available ingredients

        Args:
            ingredients: Available ingredients

        Returns:
            List of feasible recipes
        """
        candidates = []
        ingredient_set = set(ing.lower() for ing in ingredients)

        for recipe in self.recipes:
            recipe_ingredients = set(ing.lower() for ing in recipe['ingredients'])

            # Calculate match percentage
            match_count = len(ingredient_set & recipe_ingredients)
            total_needed = len(recipe_ingredients)

            # Only include if we have 70%+ of ingredients
            if match_count / total_needed >= 0.7:
                candidates.append({
                    **recipe,
                    'available_ingredients': match_count,
                    'total_ingredients': total_needed
                })

        return candidates

    def _calculate_ingredient_match(
        self,
        available: List[str],
        required: List[str]
    ) -> float:
        """Calculate ingredient match score (0-1)"""
        available_set = set(ing.lower() for ing in available)
        required_set = set(ing.lower() for ing in required)

        if not required_set:
            return 0.0

        match_count = len(available_set & required_set)
        return match_count / len(required_set)

    def _score_by_emotion(self, recipe: Dict, emotion_type: str) -> float:
        """
        Score recipe based on emotion fit

        Args:
            recipe: Recipe dictionary
            emotion_type: Current emotion

        Returns:
            Emotion fit score (0-1)
        """
        base_score = 0.5

        emotion_preferences = {
            'stress': {'cooking_time': (5, 15), 'difficulty': 'easy'},
            'fatigue': {'cooking_time': (10, 20), 'difficulty': 'easy'},
            'anxiety': {'cooking_time': (5, 10), 'difficulty': 'easy'},
            'happiness': {'cooking_time': (20, 40), 'difficulty': 'medium'},
            'excitement': {'cooking_time': (15, 30), 'difficulty': 'medium'},
            'calmness': {'cooking_time': (20, 40), 'difficulty': 'medium'},
            'focus': {'cooking_time': (25, 45), 'difficulty': 'hard'},
            'apathy': {'cooking_time': (5, 15), 'difficulty': 'easy'},
        }

        prefs = emotion_preferences.get(emotion_type, {})

        # Cooking time preference
        if 'cooking_time' in prefs:
            target_min, target_max = prefs['cooking_time']
            actual = recipe.get('cooking_time', 15)
            target_avg = (target_min + target_max) / 2

            time_diff = abs(actual - target_avg)
            time_score = max(0, 1 - time_diff / 30)
            base_score += time_score * 0.25

        # Difficulty preference
        if 'difficulty' in prefs:
            if recipe.get('difficulty') == prefs['difficulty']:
                base_score += 0.25

        return min(1.0, base_score)

    async def generate_shopping_list(
        self,
        available: List[str],
        recipe: Dict
    ) -> List[str]:
        """
        Generate shopping list for missing ingredients

        Args:
            available: Available ingredients
            recipe: Selected recipe

        Returns:
            List of missing ingredients
        """
        available_set = set(ing.lower() for ing in available)
        required_set = set(ing.lower() for ing in recipe['ingredients'])

        missing = required_set - available_set
        return list(missing)
