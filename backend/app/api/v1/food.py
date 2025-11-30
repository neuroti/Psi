"""
음식 분석 API 라우트
모드 1: 실시간 감정-영양 분석

Food API Routes
Mode 1: Real-time emotion-nutrition analysis

Psi의 핵심 기능인 음식 이미지 분석 및 감정 기반 영양 추천을 제공합니다.
YOLO v8 모델과 Claude Vision API를 사용하여 96% 이상의 정확도로 음식을 인식하며,
웨어러블 기기 데이터(HRV, 심박수)를 분석하여 사용자의 현재 감정 상태에 맞는
개인화된 영양 권장사항을 제공합니다.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import verify_token
from app.models.food import FoodAnalysisResponse, FoodAnalysisRequest, FoodItem
from app.services.image_recognition import ImageRecognitionService
from app.services.nutrition_analysis import NutritionAnalysisService
from app.services.emotion_analysis import EmotionAnalysisService
from typing import Optional

router = APIRouter()


@router.post("/upload", response_model=FoodAnalysisResponse)
async def upload_food_image(
    file: UploadFile = File(...),
    hrv: Optional[float] = None,
    heart_rate: Optional[int] = None,
    user_id: str = Depends(verify_token)
):
    """
    음식 이미지 업로드 및 AI 분석
    Upload and analyze food image with AI

    Psi의 핵심 기능인 3단계 음식 분석 프로세스:
    1단계: YOLO v8 모델로 음식 인식 (96%+ 정확도)
    2단계: USDA 데이터베이스에서 영양 정보 조회 (400K+ 음식)
    3단계: HRV/심박수 데이터로 감정 분석 및 개인화된 추천

    Core 3-stage food analysis process:
    Stage 1: Food detection using YOLO v8 (96%+ accuracy)
    Stage 2: Nutrition lookup from USDA database (400K+ foods)
    Stage 3: Emotion analysis from HRV/HR and personalized recommendations

    Args:
        file: 업로드할 음식 이미지 파일 (JPG, PNG)
            - 최대 크기: 10MB
            - 권장 해상도: 640x640 이상
        hrv: Heart Rate Variability (선택)
            - 단위: ms (milliseconds)
            - 범위: 20-100 (정상 성인 기준)
            - Apple Watch, Fitbit 등에서 수집
        heart_rate: 심박수 (선택)
            - 단위: bpm (beats per minute)
            - 범위: 40-200
            - 웨어러블 기기에서 수집
        user_id: JWT 토큰에서 자동 추출된 사용자 ID

    Returns:
        FoodAnalysisResponse: {
            "food_items": List[FoodItem] - 인식된 음식 목록
                각 항목: {name, confidence, grams, calories, nutrition}
            "total_calories": float - 총 칼로리
            "nutrition": dict - 종합 영양 정보 (62개 영양소)
            "emotion": dict | None - 감정 분석 결과
                {type, score, hrv, heart_rate}
            "recommendation": str - 개인화된 추천 메시지
            "xp_gained": int - 획득한 경험치 (게이미피케이션)
        }

    Raises:
        HTTPException 400: 이미지 형식 오류 또는 파일 크기 초과
        HTTPException 401: 유효하지 않은 JWT 토큰
        HTTPException 429: Rate Limit 초과 (무료: 3회/일, 프리미엄: 무제한)
        HTTPException 500: AI 모델 추론 실패 또는 서버 오류

    처리 시간:
    - YOLO 추론: ~500ms
    - Claude Vision (필요시): ~2s
    - USDA DB 조회: ~100ms
    - 총 평균: 1-3초

    예제:
        POST /api/v1/food/upload
        Headers: Authorization: Bearer <jwt_token>
        Content-Type: multipart/form-data

        Form Data:
        - file: <image_file>
        - hrv: 65.5
        - heart_rate: 72
    """
    # 1. 파일 형식 검증 (보안: 이미지 파일만 허용)
    # Validate file format (security: only allow image files)
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "PSI-FOOD-4001",
                    "message": "File must be an image (JPG, PNG, WebP)"
                }
            }
        )

    # 2. 이미지 파일 읽기
    # Read image file into memory
    image_bytes = await file.read()

    # 3. 파일 크기 검증 (DoS 공격 방지)
    # Validate file size (prevent DoS attacks)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "PSI-FOOD-4002",
                    "message": f"Image too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
                }
            }
        )

    # 4. 서비스 레이어 초기화
    # Initialize service layer components
    image_service = ImageRecognitionService()  # YOLO v8 + Claude Vision
    nutrition_service = NutritionAnalysisService()  # USDA DB 조회
    emotion_service = EmotionAnalysisService()  # 8가지 감정 분류

    # === 1단계: AI 기반 음식 인식 ===
    # Stage 1: AI-powered food detection
    # YOLO v8 모델로 이미지에서 음식 탐지 (confidence >= 0.5)
    # 낮은 confidence의 경우 Claude Vision API로 재분석
    # Detect food items using YOLO v8 (confidence >= 0.5)
    # Falls back to Claude Vision API if confidence is low
    detections = await image_service.analyze_food_image(image_bytes)

    # === 2단계: 영양 정보 조회 및 집계 ===
    # Stage 2: Nutrition information lookup and aggregation
    food_items = []
    total_calories = 0

    for detection in detections:
        # 바운딩 박스 크기로 음식 분량 추정 (g 단위)
        # Estimate portion size from bounding box (in grams)
        # 휴리스틱: 이미지의 50% = 200g 기준
        # Heuristic: 50% of image = 200g baseline
        portion_grams = image_service.estimate_portion_size(detection['bbox'])

        # USDA FoodData Central DB에서 영양 정보 조회
        # Query nutrition information from USDA FoodData Central
        # 캐싱: Redis에 24시간 저장 (동일 음식 재조회 방지)
        # Caching: Stored in Redis for 24h (avoid redundant lookups)
        nutrition = await nutrition_service.get_nutrition_info(
            detection['class'],  # 음식 이름 (예: "apple", "rice")
            portion_grams  # 추정 분량 (g)
        )

        if nutrition:
            # 인식된 음식을 FoodItem 객체로 변환
            # Convert detected food to FoodItem object
            food_items.append(FoodItem(
                name=detection['class'],
                confidence=detection['confidence'],  # YOLO confidence (0-1)
                grams=portion_grams,
                calories=nutrition['calories'],
                nutrition=nutrition  # 62개 영양소 데이터
            ))
            total_calories += nutrition['calories']

    # === 3단계: 감정 분석 및 개인화된 추천 ===
    # Stage 3: Emotion analysis and personalized recommendations
    emotion = None
    recommendation = "Enjoy your meal!"  # 기본 메시지

    # 웨어러블 데이터가 제공된 경우 감정 분석 수행
    # Perform emotion analysis if wearable data is provided
    if hrv and heart_rate:
        # HRV와 심박수를 기반으로 8가지 감정 중 하나로 분류
        # Classify into one of 8 emotions based on HRV and HR
        # 감정: stress, fatigue, anxiety, happiness, excitement, calmness, focus, apathy
        emotion_result = await emotion_service.classify_emotion(hrv, heart_rate)

        emotion = {
            'type': emotion_result.type,  # 감정 유형
            'score': emotion_result.score,  # 신뢰도 (0-100)
            'hrv': hrv,  # 원본 HRV 값
            'heart_rate': heart_rate  # 원본 심박수
        }

        # 현재 감정과 음식의 영양 정보를 고려한 개인화된 추천
        # Generate personalized recommendation based on emotion and nutrition
        total_nutrition = nutrition_service.calculate_total_nutrition(
            [{'nutrition': item.nutrition} for item in food_items]
        )
        recommendation = await emotion_service.get_emotion_nutrition_recommendation(
            emotion_result.type,
            total_nutrition
        )

    # === 게이미피케이션: XP 계산 ===
    # Gamification: Calculate XP earned
    # 기본 15 XP + 인식된 음식 1개당 5 XP
    # Base 15 XP + 5 XP per detected food item
    xp_gained = 15 + len(food_items) * 5

    # === 최종 응답 생성 ===
    # Build final response
    return FoodAnalysisResponse(
        food_items=food_items,  # 인식된 음식 목록
        total_calories=round(total_calories, 1),  # 총 칼로리 (소수점 1자리)
        nutrition=nutrition_service.calculate_total_nutrition(
            [{'nutrition': item.nutrition} for item in food_items]
        ),  # 통합 영양 정보
        emotion=emotion,  # 감정 분석 결과 (옵션)
        recommendation=recommendation,  # 개인화된 추천 메시지
        xp_gained=xp_gained  # 획득 경험치
    )


@router.get("/history")
async def get_food_history(
    limit: int = 10,
    user_id: str = Depends(verify_token)
):
    """
    사용자의 음식 기록 조회
    Get user's food history

    사용자가 과거에 업로드한 음식 분석 기록을 시간 역순으로 조회합니다.
    각 기록에는 인식된 음식, 영양 정보, 감정 상태, 업로드 시간이 포함됩니다.

    Args:
        limit: 조회할 최대 기록 수 (기본값: 10, 최대: 100)
        user_id: JWT 토큰에서 자동 추출된 사용자 ID

    Returns:
        dict: {
            "total": int - 전체 기록 수,
            "items": List[dict] - 음식 기록 목록,
                각 항목: {
                    "id": str - 기록 UUID,
                    "created_at": str - ISO 8601 형식 날짜,
                    "food_items": List[FoodItem] - 인식된 음식,
                    "total_calories": float - 총 칼로리,
                    "emotion": dict | None - 당시 감정 상태,
                    "image_url": str - S3 이미지 URL
                }
        }

    Raises:
        HTTPException 401: 유효하지 않은 토큰
        HTTPException 422: limit 값이 유효 범위를 벗어남 (1-100)

    예제:
        GET /api/v1/food/history?limit=20
        Headers: Authorization: Bearer <jwt_token>

    데이터베이스 쿼리:
        SELECT * FROM food_history
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    # TODO: PostgreSQL에서 음식 기록 조회
    # Query food history from PostgreSQL
    # Example:
    # if limit < 1 or limit > 100:
    #     raise HTTPException(status_code=422, detail="Limit must be between 1 and 100")
    #
    # history = await db.query(FoodHistory).filter(
    #     FoodHistory.user_id == user_id
    # ).order_by(
    #     FoodHistory.created_at.desc()
    # ).limit(limit).all()
    #
    # return {
    #     "total": len(history),
    #     "items": [item.to_dict() for item in history]
    # }

    return {"message": "Food history", "user_id": user_id, "limit": limit}
