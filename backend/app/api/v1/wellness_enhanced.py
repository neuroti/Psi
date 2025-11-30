"""
Wellness API Routes - Enhanced Implementation
Mode 3: Comprehensive emotion wellness hub with analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import verify_token
from app.core.exceptions import PsiException
from app.models.emotion import WellnessResponse, EmotionAnalysisResult
from app.services.emotion_analysis import EmotionAnalysisService
from app.services.database_service import DatabaseService
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class WellnessService:
    """Complete wellness monitoring and analytics service"""

    def __init__(self):
        self.emotion_service = EmotionAnalysisService()
        self.db_service = DatabaseService()

    def calculate_wellness_score(
        self,
        hrv: float,
        heart_rate: int,
        emotion_score: int
    ) -> int:
        """
        Calculate overall wellness score (0-100)

        Args:
            hrv: Heart Rate Variability
            heart_rate: Heart rate in bpm
            emotion_score: Emotion confidence score

        Returns:
            Wellness score from 0-100
        """
        # HRV component (40 points)
        # Higher HRV = better wellness
        # Typical range: 20-100ms
        hrv_score = min(40, (hrv / 100) * 40)

        # Heart rate component (40 points)
        # Optimal resting HR: 60-80 bpm
        # Score decreases as HR deviates from optimal
        optimal_hr = 70
        hr_deviation = abs(heart_rate - optimal_hr)
        hr_score = max(0, 40 - (hr_deviation * 0.5))

        # Emotion component (20 points)
        # Based on emotion confidence
        emotion_component = (emotion_score / 100) * 20

        total = hrv_score + hr_score + emotion_component
        return min(100, max(0, int(total)))

    def generate_recommendations(
        self,
        emotion_type: str,
        wellness_score: int,
        user_history: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Generate personalized recommendations

        Args:
            emotion_type: Current emotion state
            wellness_score: Overall wellness score
            user_history: User's emotion history

        Returns:
            Dictionary with food, exercise, and content recommendations
        """
        # Base recommendations by emotion type
        base_recommendations = {
            'stress': {
                'food': [
                    'Green tea for L-theanine (calming)',
                    'Dark chocolate (70%+ cacao) for mood',
                    'Almonds and walnuts (magnesium)',
                    'Blueberries (antioxidants)',
                    'Salmon (omega-3 fatty acids)'
                ],
                'exercise': [
                    'Yoga (20-30 minutes)',
                    'Walking in nature',
                    'Stretching routine',
                    'Deep breathing exercises (4-7-8 technique)',
                    'Progressive muscle relaxation'
                ],
                'content': [
                    'Meditation guide (10 minutes)',
                    'Calming nature sounds',
                    'Stress management techniques',
                    'Mindfulness exercises',
                    'Guided imagery sessions'
                ]
            },
            'fatigue': {
                'food': [
                    'Protein-rich breakfast (eggs, greek yogurt)',
                    'Iron-rich foods (spinach, lean beef)',
                    'Complex carbohydrates (oatmeal, quinoa)',
                    'Bananas (potassium and B6)',
                    'Water (stay hydrated)'
                ],
                'exercise': [
                    'Light walking (15 minutes)',
                    'Gentle stretching',
                    'Tai chi',
                    'Easy yoga poses',
                    'Fresh air break'
                ],
                'content': [
                    'Power nap guide (20 minutes)',
                    'Energy-boosting tips',
                    'Sleep hygiene practices',
                    'Recovery strategies',
                    'Motivation podcasts'
                ]
            },
            'anxiety': {
                'food': [
                    'Chamomile tea',
                    'Omega-3 rich foods (salmon, chia seeds)',
                    'Whole grains (brown rice)',
                    'Probiotic foods (yogurt, kefir)',
                    'Magnesium-rich foods (pumpkin seeds)'
                ],
                'exercise': [
                    'Deep breathing (box breathing)',
                    'Progressive muscle relaxation',
                    'Gentle walking',
                    'Yoga for anxiety',
                    'Tai chi'
                ],
                'content': [
                    'Grounding techniques (5-4-3-2-1)',
                    'Anxiety management strategies',
                    'Cognitive restructuring exercises',
                    'Mindfulness meditation',
                    'Relaxation music'
                ]
            },
            'happiness': {
                'food': [
                    'Balanced, colorful meals',
                    'Fresh fruits and vegetables',
                    'Dark berries (antioxidants)',
                    'Fermented foods (gut health)',
                    'Enjoy your favorite healthy treat'
                ],
                'exercise': [
                    'Dancing',
                    'Social sports activities',
                    'Hiking with friends',
                    'Group fitness class',
                    'Try something new!'
                ],
                'content': [
                    'Gratitude journaling',
                    'Social activities',
                    'Creative projects',
                    'Uplifting music',
                    'Comedy or light entertainment'
                ]
            },
            'excitement': {
                'food': [
                    'Protein-balanced meals',
                    'Hydrating foods (cucumber, watermelon)',
                    'Nuts for sustained energy',
                    'Whole grain snacks',
                    'Green smoothie'
                ],
                'exercise': [
                    'Cardio workout',
                    'HIIT training',
                    'Team sports',
                    'Rock climbing',
                    'High-energy activities'
                ],
                'content': [
                    'Challenge yourself',
                    'Learn new skills',
                    'Adventure planning',
                    'Goal setting',
                    'Energizing playlists'
                ]
            },
            'calmness': {
                'food': [
                    'Mindful eating practice',
                    'Fresh seasonal foods',
                    'Herbal tea',
                    'Light, wholesome meals',
                    'Mediterranean diet foods'
                ],
                'exercise': [
                    'Tai chi',
                    'Swimming',
                    'Nature walks',
                    'Gentle yoga',
                    'Pilates'
                ],
                'content': [
                    'Reading',
                    'Art and creativity',
                    'Journaling',
                    'Classical music',
                    'Contemplative practices'
                ]
            },
            'focus': {
                'food': [
                    'Brain foods (blueberries)',
                    'Nuts and seeds',
                    'Fatty fish (salmon)',
                    'Green tea (L-theanine)',
                    'Dark chocolate (small amount)'
                ],
                'exercise': [
                    'Yoga for concentration',
                    'Pilates',
                    'Balance exercises',
                    'Mindful movement',
                    'Short walk breaks'
                ],
                'content': [
                    'Deep work sessions (Pomodoro)',
                    'Problem-solving activities',
                    'Learning new concepts',
                    'Strategic planning',
                    'Focus music (binaural beats)'
                ]
            },
            'apathy': {
                'food': [
                    'Colorful, vibrant meals',
                    'Spicy foods (capsaicin)',
                    'Citrus fruits',
                    'Crunchy vegetables',
                    'Protein-rich breakfast'
                ],
                'exercise': [
                    'Group fitness classes',
                    'Outdoor activities',
                    'Dance classes',
                    'Social sports',
                    'Try something new'
                ],
                'content': [
                    'Motivational content',
                    'Social engagement',
                    'Goal-setting exercises',
                    'Upbeat music',
                    'Connect with friends'
                ]
            }
        }

        recommendations = base_recommendations.get(
            emotion_type,
            base_recommendations['calmness']
        )

        # Adjust based on wellness score
        if wellness_score < 50:
            # Add recovery-focused recommendations
            recommendations['food'].insert(0, 'Prioritize hydration and rest')
            recommendations['exercise'].insert(0, 'Light movement only - listen to your body')

        return recommendations

    def get_daily_tip(
        self,
        emotion_type: str,
        time_of_day: str = 'morning'
    ) -> str:
        """
        Get psychology-based daily tip

        Args:
            emotion_type: Current emotion
            time_of_day: Time of day (morning/afternoon/evening)

        Returns:
            Personalized daily tip
        """
        tips = {
            'stress': [
                "Take 5 deep breaths. Inhale for 4 counts, hold for 4, exhale for 4. Repeat 5 times.",
                "Stress is your body's way of rising to a challenge. Use it as energy, not a burden.",
                "Write down 3 things you're worried about. Next to each, write one small action you can take.",
                "Remember: This feeling is temporary. You've handled stress before and grown from it.",
                "Schedule a 5-minute worry break. Set a timer, acknowledge your concerns, then move on."
            ],
            'fatigue': [
                "Energy dips are natural. Listen to your body and rest when needed.",
                "Take a 20-minute power nap if possible. Set an alarm to avoid grogginess.",
                "Step outside for 5 minutes. Natural light helps regulate your circadian rhythm.",
                "Dehydration mimics fatigue. Drink a glass of water and wait 10 minutes.",
                "Do 10 jumping jacks. Sometimes movement creates energy, not the other way around."
            ],
            'anxiety': [
                "Ground yourself with the 5-4-3-2-1 technique: 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.",
                "Anxiety is fear of the future. Bring yourself back to this moment. What's actually happening right now?",
                "Place your hand on your heart. Breathe deeply and say: 'I am safe. This is temporary.'",
                "Write your anxious thoughts on paper. Seeing them outside your mind makes them more manageable.",
                "Ask yourself: Is this thought true? Is it helpful? Can I let it go?"
            ],
            'happiness': [
                "Savor this positive moment. Write down 3 things you're grateful for today.",
                "Happiness shared is happiness multiplied. Reach out to someone you care about.",
                "Take a mental snapshot of this feeling. You can return to it when you need it.",
                "Notice what contributed to your happiness today. How can you create more of this?",
                "This is a great time to tackle a challenge. Positive emotions fuel creativity and problem-solving."
            ],
            'excitement': [
                "Channel your energy into something productive or creative!",
                "Your enthusiasm is contagious. Share it with others and inspire them.",
                "Remember to breathe. Even positive energy needs grounding to be sustainable.",
                "Document this feeling. What sparked it? How can you create it again?",
                "Balance excitement with planning. Your energy is most powerful when it's directed."
            ],
            'calmness': [
                "This is a perfect time for reflection and planning. What matters most to you?",
                "Calmness is a superpower. Notice how clearly you can think right now.",
                "Use this peaceful state to journal or meditate. It will recharge you deeply.",
                "Your calm energy can help others. Be present for someone who needs you.",
                "Savor this feeling. Calmness is the foundation of sustainable well-being."
            ],
            'focus': [
                "You're in the flow state. Minimize distractions and dive deep.",
                "This is prime time for important work. Protect this focused energy.",
                "Your brain is at peak performance. Tackle your most challenging task now.",
                "Notice what created this focus. Can you replicate these conditions?",
                "Take a short break every hour. Sustainable focus requires rest too."
            ],
            'apathy': [
                "Small actions create momentum. Start with just 5 minutes of something you enjoy.",
                "Apathy is often a sign you need rest or a change. What would feel refreshing right now?",
                "Move your body. Even a short walk can shift your emotional state.",
                "Connect with someone. Social energy can reignite your own.",
                "Be gentle with yourself. This feeling will pass. Do one small thing you'll thank yourself for later."
            ]
        }

        emotion_tips = tips.get(emotion_type, tips['calmness'])

        # Rotate tips based on time
        import random
        random.seed(datetime.now().day)  # Same tip for the day
        return random.choice(emotion_tips)

    async def analyze_emotion_trends(
        self,
        user_id: str,
        days: int = 7
    ) -> Dict:
        """
        Analyze emotion trends over time

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Trend analysis with insights
        """
        history = await self.db_service.get_emotion_history(user_id, days)

        if not history:
            return {
                "message": "Not enough data for trend analysis",
                "recommendation": "Keep tracking your emotions for personalized insights"
            }

        # Calculate emotion distribution
        emotions = [record['emotion_type'] for record in history]
        emotion_counts = Counter(emotions)

        # Find dominant emotion
        dominant_emotion = emotion_counts.most_common(1)[0]

        # Calculate average wellness metrics
        avg_hrv = sum(r['hrv'] for r in history) / len(history)
        avg_hr = sum(r['heart_rate'] for r in history) / len(history)
        avg_score = sum(r['emotion_score'] for r in history) / len(history)

        # Identify patterns
        hourly_emotions = defaultdict(list)
        for record in history:
            hour = datetime.fromisoformat(record['timestamp']).hour
            hourly_emotions[hour].append(record['emotion_type'])

        # Find time-based patterns
        stress_hours = []
        for hour, emotions_at_hour in hourly_emotions.items():
            stress_count = emotions_at_hour.count('stress') + emotions_at_hour.count('anxiety')
            if stress_count / len(emotions_at_hour) > 0.5:
                stress_hours.append(hour)

        insights = {
            "period_days": days,
            "total_readings": len(history),
            "dominant_emotion": {
                "type": dominant_emotion[0],
                "percentage": round((dominant_emotion[1] / len(history)) * 100, 1)
            },
            "emotion_distribution": dict(emotion_counts),
            "average_metrics": {
                "hrv": round(avg_hrv, 1),
                "heart_rate": round(avg_hr, 1),
                "emotion_confidence": round(avg_score, 1)
            },
            "patterns": {
                "high_stress_hours": stress_hours,
                "best_time_of_day": self._get_best_time(hourly_emotions)
            },
            "recommendations": self._generate_trend_recommendations(
                dominant_emotion[0],
                stress_hours
            )
        }

        return insights

    def _get_best_time(self, hourly_emotions: Dict) -> str:
        """Get the time of day with best emotional state"""
        positive_emotions = ['happiness', 'excitement', 'calmness', 'focus']

        best_hour = None
        best_score = 0

        for hour, emotions in hourly_emotions.items():
            positive_count = sum(1 for e in emotions if e in positive_emotions)
            score = positive_count / len(emotions)

            if score > best_score:
                best_score = score
                best_hour = hour

        if best_hour is not None:
            if best_hour < 12:
                return f"Morning ({best_hour}:00)"
            elif best_hour < 18:
                return f"Afternoon ({best_hour}:00)"
            else:
                return f"Evening ({best_hour}:00)"

        return "No clear pattern yet"

    def _generate_trend_recommendations(
        self,
        dominant_emotion: str,
        stress_hours: List[int]
    ) -> List[str]:
        """Generate recommendations based on trends"""
        recommendations = []

        if dominant_emotion in ['stress', 'anxiety']:
            recommendations.append(
                "Consider scheduling regular breaks and stress-reduction activities"
            )
            recommendations.append(
                "Your dominant emotion is stress. Explore stress management techniques."
            )

        if stress_hours:
            recommendations.append(
                f"High stress typically occurs around {min(stress_hours)}:00-{max(stress_hours)}:00. "
                f"Schedule relaxation activities before these times."
            )

        if dominant_emotion == 'fatigue':
            recommendations.append(
                "Consistent fatigue detected. Consider improving sleep hygiene and nutrition."
            )

        return recommendations


# Dependency injection for service
def get_wellness_service() -> WellnessService:
    """Get a new WellnessService instance per request"""
    return WellnessService()


@router.get("/check", response_model=WellnessResponse)
async def wellness_check(
    hrv: Optional[float] = Query(None, ge=10.0, le=200.0, description="Heart Rate Variability in ms"),
    heart_rate: Optional[int] = Query(None, ge=30, le=220, description="Heart rate in bpm"),
    user_id: str = Depends(verify_token),
    wellness_service: WellnessService = Depends(get_wellness_service)
):
    """
    Check current wellness status with comprehensive analysis

    **Mode 3: Emotion wellness hub**

    This endpoint provides:
    1. Real-time emotion classification (8 types)
    2. Comprehensive wellness score (0-100)
    3. Personalized recommendations (food, exercise, content)
    4. Psychology-based daily tips
    5. Trend analysis and insights

    **Parameters:**
    - hrv: Heart Rate Variability from wearable (optional)
    - heart_rate: Heart rate in bpm from wearable (optional)

    **Returns:**
    - Current emotion analysis with confidence scores
    - Overall wellness score
    - Personalized recommendations
    - Daily wellness tip
    - Emotion spectrum breakdown

    **Emotion Types:**
    1. Stress - High arousal, negative valence
    2. Fatigue - Low arousal, negative valence
    3. Anxiety - Unstable HRV, elevated HR
    4. Happiness - Balanced metrics, positive state
    5. Excitement - Elevated HR, positive valence
    6. Calmness - High HRV, low HR
    7. Focus - Balanced metrics, high coherence
    8. Apathy - Low metrics across the board
    """
    try:
        # Default values if no wearable data
        if not hrv or not heart_rate:
            # Try to get latest from database
            emotion_history = await wellness_service.db_service.get_emotion_history(
                user_id,
                days=1
            )

            if emotion_history:
                latest = emotion_history[0]
                hrv = hrv or latest['hrv']
                heart_rate = heart_rate or latest['heart_rate']
            else:
                # Use defaults
                hrv = hrv or 60.0
                heart_rate = heart_rate or 75

        # Analyze current emotion
        current_emotion = await wellness_service.emotion_service.classify_emotion(
            hrv,
            heart_rate
        )

        # Calculate wellness score
        wellness_score = wellness_service.calculate_wellness_score(
            hrv=hrv,
            heart_rate=heart_rate,
            emotion_score=current_emotion.score
        )

        # Get user history for personalized recommendations
        user_history = await wellness_service.db_service.get_emotion_history(
            user_id,
            days=7
        )

        # Generate recommendations
        recommendations = wellness_service.generate_recommendations(
            emotion_type=current_emotion.type,
            wellness_score=wellness_score,
            user_history=user_history
        )

        # Get daily tip
        hour = datetime.now().hour
        time_of_day = 'morning' if hour < 12 else 'afternoon' if hour < 18 else 'evening'
        daily_tip = wellness_service.get_daily_tip(current_emotion.type, time_of_day)

        # Save emotion data
        await wellness_service.db_service.save_emotion_data(
            user_id=user_id,
            hrv=hrv,
            heart_rate=heart_rate,
            coherence=0.5,  # TODO: Calculate from HRV variability
            emotion_type=current_emotion.type,
            emotion_score=current_emotion.score
        )

        return WellnessResponse(
            current_emotion=current_emotion,
            wellness_score=wellness_score,
            recommendations=recommendations,
            daily_tip=daily_tip
        )

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Wellness check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze wellness status"
        )


@router.get("/history")
async def get_wellness_history(
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve"),
    user_id: str = Depends(verify_token),
    wellness_service: WellnessService = Depends(get_wellness_service)
):
    """
    Get wellness history with daily summaries

    **Parameters:**
    - days: Number of days to retrieve (1-90)

    **Returns:**
    - Daily emotion summaries
    - Wellness score trends
    - Emotion distribution over time
    """
    try:
        history = await wellness_service.db_service.get_emotion_history(user_id, days)

        # Group by date
        daily_summary = defaultdict(list)
        for record in history:
            date = datetime.fromisoformat(record['timestamp']).date()
            daily_summary[date].append(record)

        # Calculate daily stats
        daily_stats = []
        for date, records in sorted(daily_summary.items(), reverse=True):
            emotions = [r['emotion_type'] for r in records]
            emotion_counts = Counter(emotions)
            dominant = emotion_counts.most_common(1)[0] if emotion_counts else ('unknown', 0)

            avg_hrv = sum(r['hrv'] for r in records) / len(records)
            avg_hr = sum(r['heart_rate'] for r in records) / len(records)
            avg_score = sum(r['emotion_score'] for r in records) / len(records)

            wellness_score = wellness_service.calculate_wellness_score(
                hrv=avg_hrv,
                heart_rate=avg_hr,
                emotion_score=avg_score
            )

            daily_stats.append({
                'date': date.isoformat(),
                'wellness_score': wellness_score,
                'dominant_emotion': dominant[0],
                'emotion_distribution': dict(emotion_counts),
                'readings_count': len(records),
                'average_metrics': {
                    'hrv': round(avg_hrv, 1),
                    'heart_rate': round(avg_hr, 1)
                }
            })

        return {
            "period_days": days,
            "daily_summary": daily_stats,
            "total_readings": len(history)
        }

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Failed to get wellness history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve wellness history"
        )


@router.get("/trends")
async def get_emotion_trends(
    period: str = Query('week', regex='^(week|month|year)$'),
    user_id: str = Depends(verify_token),
    wellness_service: WellnessService = Depends(get_wellness_service)
):
    """
    Get emotion trends and insights

    **Parameters:**
    - period: Analysis period (week/month/year)

    **Returns:**
    - Emotion distribution patterns
    - Time-based insights
    - Personalized recommendations
    - Wellness trajectory
    """
    days_map = {'week': 7, 'month': 30, 'year': 365}
    days = days_map[period]

    try:
        trends = await wellness_service.analyze_emotion_trends(user_id, days)

        return trends

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Failed to analyze trends: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze emotion trends"
        )


@router.get("/insights")
async def get_wellness_insights(
    user_id: str = Depends(verify_token),
    wellness_service: WellnessService = Depends(get_wellness_service)
):
    """
    Get AI-powered wellness insights

    **Returns:**
    - Personalized insights based on your data
    - Progress tracking
    - Goal suggestions
    - Improvement areas
    """
    try:
        # Get trends
        trends = await wellness_service.analyze_emotion_trends(user_id, days=30)

        # Generate insights
        insights = {
            "summary": trends,
            "progress": {
                "message": "Keep tracking your emotions for personalized progress insights"
            },
            "goals": [
                "Maintain wellness score above 70",
                "Reduce stress episodes",
                "Improve sleep quality",
                "Build consistent routines"
            ]
        }

        return insights

    except HTTPException:
        raise
    except PsiException:
        # Let custom exceptions propagate to global handler
        raise
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate wellness insights"
        )
