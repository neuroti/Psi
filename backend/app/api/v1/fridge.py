"""
냉장고 재료 인식 API 라우트
모드 2: 감정 기반 냉장고 레시피 추천

Fridge API Routes
Mode 2: Emotion-based fridge recipe recommendations

냉장고 이미지에서 재료를 자동으로 인식하고,
사용자의 현재 감정 상태에 맞는 레시피를 추천합니다.
TF-IDF 알고리즘을 사용하여 재료 매칭을 수행하며,
부족한 재료는 쇼핑 리스트로 자동 생성됩니다.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import verify_token
from app.models.recipe import FridgeDetectionResponse, DetectedIngredient
from app.services.image_recognition import ImageRecognitionService
from app.services.recipe_matching import RecipeMatchingService
from app.services.emotion_analysis import EmotionAnalysisService
from typing import List, Optional

router = APIRouter()


@router.post("/detect", response_model=FridgeDetectionResponse)
async def detect_fridge_ingredients(
    files: List[UploadFile] = File(...),
    hrv: Optional[float] = None,
    heart_rate: Optional[int] = None,
    user_id: str = Depends(verify_token)
):
    """
    냉장고 이미지에서 재료 인식 및 감정 기반 레시피 추천
    Detect ingredients from fridge images and suggest emotion-based recipes

    4단계 프로세스:
    1단계: 최대 5장의 냉장고 사진에서 재료 인식 (YOLO v8)
    2단계: 중복 제거 및 재료 목록 생성
    3단계: 현재 감정 분석 (HRV + 심박수)
    4단계: TF-IDF 알고리즘으로 레시피 매칭 및 쇼핑 리스트 생성

    4-stage process:
    Stage 1: Detect ingredients from up to 5 fridge images (YOLO v8)
    Stage 2: Deduplicate and compile ingredient list
    Stage 3: Analyze current emotion (HRV + HR)
    Stage 4: Match recipes using TF-IDF and generate shopping list

    Args:
        files: 냉장고 이미지 파일 목록 (최대 5장)
            - 각 파일 최대 크기: 10MB
            - 지원 형식: JPG, PNG, WebP
            - 권장: 냉장고 선반별 촬영
        hrv: Heart Rate Variability (선택)
            - 단위: ms
            - 감정 기반 레시피 추천에 사용
        heart_rate: 심박수 (선택)
            - 단위: bpm
            - 감정 기반 레시피 추천에 사용
        user_id: JWT 토큰에서 자동 추출

    Returns:
        FridgeDetectionResponse: {
            "ingredients": List[DetectedIngredient] - 인식된 재료 목록
                각 항목: {name, confidence, quantity}
            "recipes": List[Recipe] - 추천 레시피 (최대 5개)
                각 항목: {
                    recipe_id, name, ingredients,
                    cooking_time, difficulty,
                    emotion_score, ingredient_match
                }
            "shopping_list": List[str] - 첫 번째 레시피에 필요한 추가 재료
            "emotion_type": str - 분석된 감정 유형
        }

    Raises:
        HTTPException 400: 이미지 수 초과 (5장 제한) 또는 파일 형식 오류
        HTTPException 401: 유효하지 않은 토큰
        HTTPException 413: 파일 크기 초과
        HTTPException 500: AI 모델 오류

    처리 시간:
    - 이미지 1장당 YOLO 추론: ~500ms
    - 레시피 매칭 (TF-IDF): ~200ms
    - 총 평균 (5장): 3-4초

    예제:
        POST /api/v1/fridge/detect
        Headers: Authorization: Bearer <jwt_token>
        Content-Type: multipart/form-data

        Form Data:
        - files: [<image1>, <image2>, <image3>]
        - hrv: 65.5
        - heart_rate: 72

    활용 시나리오:
    1. 스트레스 상태: 간단한 요리 (조리 시간 5-15분) 우선 추천
    2. 행복 상태: 복잡한 요리 (조리 시간 20-40분) 추천
    3. 피로 상태: 에너지 보충 재료가 포함된 레시피 추천
    """
    # 1. 이미지 수 검증 (최대 5장 제한)
    # Validate number of images (max 5 images allowed)
    MAX_IMAGES = 5
    if len(files) > MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "PSI-FRIDGE-4001",
                    "message": f"Maximum {MAX_IMAGES} images allowed. You uploaded {len(files)} images."
                }
            }
        )

    # 2. 서비스 레이어 초기화
    # Initialize service layer components
    image_service = ImageRecognitionService()  # YOLO v8 음식 인식
    recipe_service = RecipeMatchingService()  # TF-IDF 레시피 매칭
    emotion_service = EmotionAnalysisService()  # 8가지 감정 분류

    # === 1단계: 모든 이미지에서 재료 인식 ===
    # Stage 1: Detect ingredients from all images
    all_ingredients = []  # 모든 이미지에서 인식된 재료 통합 리스트

    for idx, file in enumerate(files):
        # 각 파일의 형식 검증
        # Validate each file format
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "PSI-FRIDGE-4002",
                        "message": f"File #{idx + 1} must be an image"
                    }
                }
            )

        # 이미지 파일 읽기
        # Read image file
        image_bytes = await file.read()

        # YOLO v8로 재료 인식 (confidence >= 0.5)
        # Detect ingredients using YOLO v8 (confidence >= 0.5)
        detections = await image_service.analyze_food_image(image_bytes)

        # 인식된 각 재료를 목록에 추가
        # Add each detected ingredient to the list
        for detection in detections:
            all_ingredients.append(DetectedIngredient(
                name=detection['class'],  # 재료 이름 (예: "tomato", "onion")
                confidence=detection['confidence'],  # YOLO confidence (0-1)
                quantity="unknown"  # TODO: 부피 추정 알고리즘으로 개선 가능
            ))

    # === 2단계: 중복 재료 제거 (높은 confidence 우선) ===
    # Stage 2: Remove duplicate ingredients (prioritize higher confidence)
    unique_ingredients = {}
    for ing in all_ingredients:
        if ing.name not in unique_ingredients:
            # 처음 발견된 재료는 바로 추가
            # First occurrence: add directly
            unique_ingredients[ing.name] = ing
        elif ing.confidence > unique_ingredients[ing.name].confidence:
            # 동일 재료가 여러 번 인식된 경우, 더 높은 confidence 선택
            # If ingredient appears multiple times, keep higher confidence
            unique_ingredients[ing.name] = ing

    ingredients = list(unique_ingredients.values())

    # === 3단계: 감정 분석 ===
    # Stage 3: Emotion analysis
    emotion_type = 'calmness'  # 기본 감정 (웨어러블 데이터 없을 때)
    if hrv and heart_rate:
        # HRV + 심박수로 현재 감정 분류
        # Classify current emotion using HRV + HR
        emotion_result = await emotion_service.classify_emotion(hrv, heart_rate)
        emotion_type = emotion_result.type

    # === 4단계: TF-IDF 기반 레시피 매칭 ===
    # Stage 4: TF-IDF based recipe matching
    ingredient_names = [ing.name for ing in ingredients]

    # 재료와 감정 상태를 고려한 최적 레시피 검색 (상위 5개)
    # Find optimal recipes considering ingredients and emotion (top 5)
    # 매칭 알고리즘:
    # - 재료 매칭 점수: 보유 재료 / 필요 재료 (70% 이상만 포함)
    # - 감정 점수: 조리 시간 + 난이도가 감정에 맞는지
    # - 최종 점수 = (재료 매칭 + 감정 점수) / 2
    matched_recipes = await recipe_service.match_recipes(
        ingredient_names,
        emotion_type,
        top_k=5
    )

    # === 5단계: 쇼핑 리스트 생성 (첫 번째 레시피 기준) ===
    # Stage 5: Generate shopping list (for top recipe)
    shopping_list = []
    if matched_recipes:
        # 첫 번째 추천 레시피에 필요하지만 냉장고에 없는 재료 추출
        # Extract missing ingredients for the top recommended recipe
        shopping_list = await recipe_service.generate_shopping_list(
            ingredient_names,
            matched_recipes[0]
        )

    # === 최종 응답 생성 ===
    # Build final response
    return FridgeDetectionResponse(
        ingredients=ingredients,  # 인식된 재료 목록
        recipes=matched_recipes,  # 추천 레시피 (최대 5개)
        shopping_list=shopping_list,  # 부족한 재료 리스트
        emotion_type=emotion_type  # 현재 감정 상태
    )


@router.get("/recipes/{recipe_id}")
async def get_recipe_detail(
    recipe_id: str,
    user_id: str = Depends(verify_token)
):
    """
    레시피 상세 정보 조회
    Get detailed recipe information

    특정 레시피의 전체 정보를 조회합니다 (재료, 조리 방법, 영양 정보 등).

    Args:
        recipe_id: 레시피 UUID
        user_id: JWT 토큰에서 자동 추출

    Returns:
        dict: {
            "recipe_id": str,
            "name": str - 레시피 이름,
            "ingredients": List[str] - 필요한 재료 목록,
            "instructions": List[str] - 단계별 조리 방법,
            "cooking_time": int - 조리 시간 (분),
            "difficulty": str - 난이도 (easy/medium/hard),
            "servings": int - 인분,
            "nutrition": dict - 1인분당 영양 정보,
            "image_url": str - 레시피 이미지,
            "rating": float - 평균 평점 (0-5),
            "reviews_count": int - 리뷰 수
        }

    Raises:
        HTTPException 404: 레시피를 찾을 수 없음

    예제:
        GET /api/v1/fridge/recipes/550e8400-e29b-41d4-a716-446655440000
        Headers: Authorization: Bearer <jwt_token>
    """
    # TODO: MongoDB에서 레시피 상세 정보 조회
    # Query recipe details from MongoDB
    # Example:
    # recipe = await mongo_db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # if not recipe:
    #     raise HTTPException(status_code=404, detail="Recipe not found")
    # return recipe

    return {"message": "Recipe details", "recipe_id": recipe_id}
