"""
웰니스 허브 API 라우트
모드 3: 감정 웰니스 허브

Wellness API Routes
Mode 3: Emotion wellness hub

실시간 감정 모니터링 및 일일 웰니스 점수를 제공하며,
개인화된 추천 (음식, 운동, 콘텐츠)과 심리학 기반 데일리 팁을 제공합니다.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import verify_token
from app.models.emotion import WellnessResponse, EmotionAnalysisResult
from app.services.emotion_analysis import EmotionAnalysisService
from typing import Optional

router = APIRouter()


@router.get("/check", response_model=WellnessResponse)
async def wellness_check(
    hrv: Optional[float] = None,
    heart_rate: Optional[int] = None,
    user_id: str = Depends(verify_token)
):
    """
    현재 웰니스 상태 확인
    Check current wellness status

    모드 3의 핵심 기능: 실시간 감정 모니터링 및 맞춤형 웰니스 추천
    - 웨어러블 데이터(HRV, 심박수)로 현재 감정 분석
    - 0-100 범위의 일일 웰니스 점수 계산
    - 감정에 맞는 음식, 운동, 콘텐츠 추천
    - 심리학 기반 데일리 팁 제공

    Args:
        hrv: Heart Rate Variability (선택)
            - 단위: ms
            - 미제공 시 DB에서 최근 데이터 조회
        heart_rate: 심박수 (선택)
            - 단위: bpm
            - 미제공 시 DB에서 최근 데이터 조회
        user_id: JWT 토큰에서 자동 추출

    Returns:
        WellnessResponse: {
            "current_emotion": EmotionAnalysisResult - 현재 감정
                {type, score, hrv, heart_rate, all_emotions}
            "wellness_score": int - 웰니스 점수 (0-100)
            "recommendations": dict - 개인화된 추천
                {food: List[str], exercise: List[str], content: List[str]}
            "daily_tip": str - 심리학 기반 데일리 팁
        }

    웰니스 점수 계산 공식:
    - HRV 기여도: (hrv / 100) * 50점 (높을수록 좋음)
    - 심박수 기여도: (100 - |hr - 70|) / 100 * 50점 (70bpm이 최적)
    - 총점 = min(100, HRV 점수 + 심박수 점수)

    예제:
        GET /api/v1/wellness/check?hrv=65&heart_rate=72
        Headers: Authorization: Bearer <jwt_token>

        Response:
        {
            "current_emotion": {
                "type": "calmness",
                "score": 85,
                "hrv": 65.0,
                "heart_rate": 72
            },
            "wellness_score": 82,
            "recommendations": {
                "food": ["Mindful eating", "Fresh seasonal foods"],
                "exercise": ["Tai chi", "Swimming", "Nature walks"],
                "content": ["Reading", "Art", "Journaling"]
            },
            "daily_tip": "This is a great time for reflection and planning."
        }
    """
    # 1. 서비스 레이어 초기화
    # Initialize service layer
    emotion_service = EmotionAnalysisService()

    # 2. 웨어러블 데이터 검증 및 기본값 처리
    # Validate wearable data or use defaults
    if not hrv or not heart_rate:
        # TODO: MongoDB에서 사용자의 최근 웨어러블 데이터 조회
        # Fetch latest wearable data from MongoDB
        # Example:
        # latest_data = await mongo_db.emotion_time_series.find_one(
        #     {"user_id": user_id},
        #     sort=[("timestamp", -1)]
        # )
        # hrv = latest_data.get("hrv", 60.0)
        # heart_rate = latest_data.get("heart_rate", 75)

        # 기본값 사용 (웨어러블 데이터 없는 경우)
        # Use default values if no wearable data
        hrv = 60.0
        heart_rate = 75

    # 3. 현재 감정 분석 (8가지 감정 중 분류)
    # Analyze current emotion (classify into 8 emotions)
    current_emotion = await emotion_service.classify_emotion(hrv, heart_rate)

    # 4. 웰니스 점수 계산 (0-100)
    # Calculate wellness score (0-100)
    # 높은 HRV + 적정 심박수 = 높은 웰니스 점수
    # Higher HRV + moderate HR = better wellness score
    hrv_score = (hrv / 100) * 50  # HRV 기여도 (최대 50점)
    hr_deviation = abs(heart_rate - 70)  # 최적 심박수 70bpm과의 편차
    hr_score = ((100 - hr_deviation) / 100) * 50  # 심박수 기여도 (최대 50점)
    wellness_score = int(min(100, hrv_score + hr_score))

    # 5. 감정에 맞는 개인화된 추천 생성
    # Generate personalized recommendations based on emotion
    recommendations = _generate_recommendations(current_emotion.type)

    # 6. 심리학 기반 데일리 팁 조회
    # Get psychology-based daily tip
    daily_tip = _get_daily_tip(current_emotion.type)

    # 7. 최종 응답 생성
    # Build final response
    return WellnessResponse(
        current_emotion=current_emotion,
        wellness_score=wellness_score,
        recommendations=recommendations,
        daily_tip=daily_tip
    )


@router.get("/history")
async def get_wellness_history(
    days: int = 7,
    user_id: str = Depends(verify_token)
):
    """
    웰니스 기록 조회
    Get wellness history

    지정된 기간 동안의 웰니스 점수 및 감정 변화를 조회합니다.

    Args:
        days: 조회 기간 (일 단위, 기본값: 7일, 최대: 90일)
        user_id: JWT 토큰에서 자동 추출

    Returns:
        dict: {
            "period": str - 조회 기간,
            "data": List[dict] - 일별 웰니스 데이터
                각 항목: {date, wellness_score, emotion_type, hrv, heart_rate}
        }

    예제:
        GET /api/v1/wellness/history?days=30
        Headers: Authorization: Bearer <jwt_token>
    """
    # TODO: MongoDB emotion_time_series 컬렉션에서 조회
    # Query from MongoDB emotion_time_series collection
    return {"message": "Wellness history", "days": days}


@router.get("/trends")
async def get_emotion_trends(
    period: str = "week",
    user_id: str = Depends(verify_token)
):
    """
    감정 트렌드 분석
    Get emotion trends over time

    기간별 감정 패턴 및 트렌드를 분석하여 인사이트를 제공합니다.

    Args:
        period: 분석 기간 (week/month/quarter/year)
        user_id: JWT 토큰에서 자동 추출

    Returns:
        dict: {
            "period": str - 분석 기간,
            "dominant_emotion": str - 가장 많이 나타난 감정,
            "emotion_distribution": dict - 감정별 비율,
            "insights": List[str] - AI 기반 인사이트
        }

    예제:
        GET /api/v1/wellness/trends?period=month
        Headers: Authorization: Bearer <jwt_token>
    """
    # TODO: MongoDB 데이터 집계 및 트렌드 분석
    # Aggregate MongoDB data and analyze trends
    return {"message": "Emotion trends", "period": period}


def _generate_recommendations(emotion_type: str) -> dict:
    """Generate personalized recommendations based on emotion"""
    recommendations = {
        'stress': {
            'food': ['Green tea', 'Dark chocolate', 'Nuts', 'Berries'],
            'exercise': ['Yoga', 'Walking', 'Stretching'],
            'content': ['Meditation guide', 'Breathing exercises', 'Calming music']
        },
        'fatigue': {
            'food': ['Protein-rich meals', 'Iron-rich foods', 'Complex carbs'],
            'exercise': ['Light walking', 'Gentle stretching'],
            'content': ['Power nap guide', 'Energy-boosting tips']
        },
        'anxiety': {
            'food': ['Chamomile tea', 'Omega-3 rich foods', 'Whole grains'],
            'exercise': ['Deep breathing', 'Progressive muscle relaxation'],
            'content': ['Mindfulness exercises', 'Grounding techniques']
        },
        'happiness': {
            'food': ['Balanced meals', 'Colorful vegetables'],
            'exercise': ['Dancing', 'Social sports', 'Hiking'],
            'content': ['Social activities', 'Creative projects']
        },
        'excitement': {
            'food': ['Protein-balanced meals', 'Hydrating foods'],
            'exercise': ['Cardio', 'Team sports', 'High-intensity workouts'],
            'content': ['Challenge yourself', 'Learn new skills']
        },
        'calmness': {
            'food': ['Mindful eating', 'Fresh seasonal foods'],
            'exercise': ['Tai chi', 'Swimming', 'Nature walks'],
            'content': ['Reading', 'Art', 'Journaling']
        },
        'focus': {
            'food': ['Brain foods', 'Nuts', 'Blueberries', 'Fish'],
            'exercise': ['Yoga', 'Pilates', 'Balance exercises'],
            'content': ['Deep work sessions', 'Problem-solving']
        },
        'apathy': {
            'food': ['Colorful meals', 'Spicy foods', 'Citrus'],
            'exercise': ['Group classes', 'Outdoor activities'],
            'content': ['Motivational content', 'Social engagement']
        }
    }

    return recommendations.get(emotion_type, recommendations['calmness'])


def _get_daily_tip(emotion_type: str) -> str:
    """Get psychology-based daily tip"""
    tips = {
        'stress': "Take 5 deep breaths. Inhale for 4 counts, hold for 4, exhale for 4. Repeat.",
        'fatigue': "Energy dips are natural. Listen to your body and rest when needed.",
        'anxiety': "Ground yourself with the 5-4-3-2-1 technique: 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.",
        'happiness': "Savor this positive moment. Write down 3 things you're grateful for today.",
        'excitement': "Channel your energy into something productive or creative!",
        'calmness': "This is a great time for reflection and planning.",
        'focus': "You're in the flow state. Minimize distractions and dive deep.",
        'apathy': "Small actions create momentum. Start with just 5 minutes of something you enjoy."
    }

    return tips.get(emotion_type, "Remember to stay hydrated and move your body today.")
