"""
감정 분석 서비스
Emotion Analysis Service

웨어러블 기기 데이터(HRV, 심박수)를 분석하여 8가지 감정으로 분류
- 스트레스, 피로, 불안, 행복, 흥분, 평온, 집중, 무기력
- 심리학 및 심박수 변이도(HRV) 연구 기반 분류 규칙
- 실시간 감정 모니터링 및 개인화된 추천 제공

Wearable data analysis for 8-emotion classification
- Stress, Fatigue, Anxiety, Happiness, Excitement, Calmness, Focus, Apathy
- Classification rules based on psychology and HRV research
- Real-time emotion monitoring and personalized recommendations
"""
from typing import Dict, Tuple
from app.models.emotion import EmotionType, EmotionAnalysisResult


class EmotionAnalysisService:
    """
    감정 분류 서비스
    Service for emotion classification from wearable data

    웨어러블 기기에서 수집한 HRV(심박수 변이도)와 심박수를 분석하여
    사용자의 현재 감정 상태를 8가지 유형 중 하나로 분류합니다.

    8가지 감정 유형:
    1. Stress (스트레스): 낮은 HRV, 높은 심박수
    2. Fatigue (피로): 낮은 HRV, 낮은 심박수
    3. Anxiety (불안): 불안정한 HRV, 높은 심박수
    4. Happiness (행복): 높은 HRV, 적정 심박수
    5. Excitement (흥분): 중간 HRV, 높은 심박수
    6. Calmness (평온): 높은 HRV, 낮은 심박수
    7. Focus (집중): 중간 HRV, 적정 심박수
    8. Apathy (무기력): 낮은 HRV, 낮은 심박수

    분류 방법:
    - HRV 범위 체크 (40점)
    - 심박수 범위 체크 (40점)
    - 일관성 점수 (20점)
    - 총 100점 만점 스코어링
    """

    # HRV와 심박수 기반 감정 분류 규칙
    # Emotion classification rules based on HRV and Heart Rate
    EMOTION_RULES = {
        EmotionType.STRESS: {
            'hrv': (20, 50),
            'hr': (85, 120),
            'coherence': (0, 0.5)
        },
        EmotionType.FATIGUE: {
            'hrv': (20, 40),
            'hr': (50, 70),
            'coherence': (0, 0.3)
        },
        EmotionType.ANXIETY: {
            'hrv': 'unstable',  # High variability
            'hr': (85, 120),
            'coherence': (0, 0.3)
        },
        EmotionType.HAPPINESS: {
            'hrv': (60, 100),
            'hr': (70, 85),
            'coherence': (0.8, 1.0)
        },
        EmotionType.EXCITEMENT: {
            'hrv': (40, 60),
            'hr': (90, 110),
            'coherence': (0.6, 0.9)
        },
        EmotionType.CALMNESS: {
            'hrv': (70, 100),
            'hr': (55, 70),
            'coherence': (0.8, 1.0)
        },
        EmotionType.FOCUS: {
            'hrv': (50, 70),
            'hr': (80, 95),
            'coherence': (0.9, 1.0)
        },
        EmotionType.APATHY: {
            'hrv': (30, 50),
            'hr': (50, 65),
            'coherence': (0.3, 0.6)
        }
    }

    async def classify_emotion(self, hrv: float, hr: int, coherence: float = 0.5) -> EmotionAnalysisResult:
        """
        웨어러블 데이터 기반 감정 분류
        Classify emotion based on wearable data

        HRV, 심박수, 일관성 점수를 종합하여 8가지 감정 중
        가장 적합한 감정을 분류하고 신뢰도 점수를 반환합니다.

        분류 알고리즘:
        1. 각 감정에 대해 0-100 점수 계산
           - HRV 범위 일치도: 40점
           - 심박수 범위 일치도: 40점
           - 일관성 점수: 20점
        2. 가장 높은 점수의 감정 선택
        3. 모든 감정의 점수 분포 반환

        Args:
            hrv: Heart Rate Variability (ms)
                - 정상 범위: 20-100ms
                - 높을수록 스트레스 회복력 좋음
            hr: Heart Rate (bpm, beats per minute)
                - 정상 안정 심박수: 60-100 bpm
            coherence: 일관성 점수 (0-1, 기본값 0.5)
                - HRV의 일관성을 나타내는 지표

        Returns:
            EmotionAnalysisResult: {
                type: str - 분류된 감정 유형,
                score: int - 신뢰도 점수 (0-100),
                all_emotions: dict - 모든 감정의 점수 분포,
                hrv: float - 입력된 HRV,
                heart_rate: int - 입력된 심박수
            }

        예제:
            >>> result = await service.classify_emotion(hrv=65, hr=72)
            >>> print(f"{result.type}: {result.score}%")
            calmness: 85%
        """
        emotions = []

        # 모든 감정 유형에 대해 점수 계산
        # Calculate score for all emotion types
        for emotion_type, rules in self.EMOTION_RULES.items():
            score = self._calculate_emotion_score(hrv, hr, coherence, rules)
            emotions.append((emotion_type, score))

        # 점수로 정렬하여 최고 점수의 감정 선택
        # Sort by score and select top emotion
        emotions.sort(key=lambda x: x[1], reverse=True)
        top_emotion, top_score = emotions[0]

        # 결과 객체 생성
        # Build result object
        return EmotionAnalysisResult(
            type=top_emotion,
            score=int(top_score),
            all_emotions={emotion: score for emotion, score in emotions},
            hrv=hrv,
            heart_rate=hr
        )

    def _calculate_emotion_score(
        self,
        hrv: float,
        hr: int,
        coherence: float,
        rules: Dict
    ) -> float:
        """
        Calculate emotion score (0-100) based on rules

        Args:
            hrv: Heart Rate Variability
            hr: Heart Rate
            coherence: Coherence score
            rules: Emotion rules

        Returns:
            Score from 0-100
        """
        score = 0.0

        # HRV scoring (40 points)
        if isinstance(rules['hrv'], tuple):
            hrv_min, hrv_max = rules['hrv']
            if hrv_min <= hrv <= hrv_max:
                score += 40
            else:
                # Gradual decrease
                distance = min(abs(hrv - hrv_min), abs(hrv - hrv_max))
                score += max(0, 40 - distance * 0.5)

        # HR scoring (40 points)
        if isinstance(rules['hr'], tuple):
            hr_min, hr_max = rules['hr']
            if hr_min <= hr <= hr_max:
                score += 40
            else:
                distance = min(abs(hr - hr_min), abs(hr - hr_max))
                score += max(0, 40 - distance * 0.5)

        # Coherence scoring (20 points)
        if isinstance(rules['coherence'], tuple):
            coh_min, coh_max = rules['coherence']
            if coh_min <= coherence <= coh_max:
                score += 20
            else:
                distance = min(abs(coherence - coh_min), abs(coherence - coh_max))
                score += max(0, 20 - distance * 20)

        return min(100, score)

    async def get_emotion_nutrition_recommendation(
        self,
        emotion_type: str,
        nutrition: Dict
    ) -> str:
        """
        Generate nutrition recommendation based on emotion

        Args:
            emotion_type: Current emotion type
            nutrition: Nutrition information

        Returns:
            Personalized recommendation string
        """
        recommendations = {
            EmotionType.STRESS: "Consider foods rich in magnesium and B vitamins to help manage stress.",
            EmotionType.FATIGUE: "Your meal is good, but consider adding iron-rich foods for energy.",
            EmotionType.ANXIETY: "Foods with omega-3 and tryptophan can help promote calmness.",
            EmotionType.HAPPINESS: "Great choice! This meal aligns well with your positive state.",
            EmotionType.EXCITEMENT: "Good energy! Consider balancing with some protein.",
            EmotionType.CALMNESS: "Perfect meal for maintaining your peaceful state.",
            EmotionType.FOCUS: "Excellent choice for sustained concentration.",
            EmotionType.APATHY: "Try adding colorful vegetables to boost motivation."
        }

        return recommendations.get(emotion_type, "Enjoy your meal mindfully!")
