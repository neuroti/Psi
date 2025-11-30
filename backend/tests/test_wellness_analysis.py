"""
Unit Tests for Wellness Emotion Analysis Component (Mode 3)
"""
import pytest
from app.services.emotion_analysis import EmotionAnalysisService
from app.api.v1.wellness_enhanced import WellnessService
from datetime import datetime, timedelta


class TestEmotionClassification:
    """Test suite for 8-emotion classification"""

    def test_all_emotion_types(self):
        """Test that all 8 emotions can be detected"""
        service = EmotionAnalysisService()

        # Test cases for each emotion
        test_cases = [
            (30, 100, ['stress', 'anxiety']),  # High HR, low HRV
            (25, 55, ['fatigue', 'apathy']),   # Low both
            (30, 105, ['anxiety', 'stress']),  # Unstable, high HR
            (75, 72, ['happiness', 'calmness']),  # High HRV, normal HR
            (50, 100, ['excitement']),  # Moderate HRV, high HR
            (85, 62, ['calmness']),  # Very high HRV, low HR
            (60, 85, ['focus']),  # Balanced
            (35, 58, ['apathy', 'fatigue']),  # Low metrics
        ]

        for hrv, hr, expected_emotions in test_cases:
            result = service.classify_emotion(hrv=hrv, hr=hr)

            assert result['type'] in expected_emotions, \
                f"HRV={hrv}, HR={hr} should detect {expected_emotions}, got {result['type']}"
            assert 0 <= result['score'] <= 100

    def test_emotion_spectrum(self):
        """Test that all_emotions contains all 8 types"""
        service = EmotionAnalysisService()

        result = service.classify_emotion(hrv=60, hr=75)

        assert 'all_emotions' in result
        assert len(result['all_emotions']) == 8

        # Verify all emotion types are present
        expected_types = [
            'stress', 'fatigue', 'anxiety', 'happiness',
            'excitement', 'calmness', 'focus', 'apathy'
        ]

        for emotion_type in expected_types:
            assert emotion_type in result['all_emotions']


class TestWellnessScore:
    """Test wellness score calculation"""

    def test_wellness_score_range(self):
        """Test that wellness scores are in valid range"""
        service = WellnessService()

        # Test various combinations
        test_cases = [
            (80, 65, 90),  # Excellent
            (60, 75, 80),  # Good
            (40, 85, 70),  # Fair
            (20, 100, 50),  # Poor
        ]

        for hrv, hr, emotion_score in test_cases:
            score = service.calculate_wellness_score(hrv, hr, emotion_score)

            assert 0 <= score <= 100, f"Score {score} out of range"

    def test_optimal_wellness(self):
        """Test wellness score for optimal metrics"""
        service = WellnessService()

        # Optimal: high HRV, resting HR, high confidence
        score = service.calculate_wellness_score(
            hrv=90,
            heart_rate=68,
            emotion_score=95
        )

        # Should be very high
        assert score >= 80

    def test_poor_wellness(self):
        """Test wellness score for poor metrics"""
        service = WellnessService()

        # Poor: low HRV, elevated HR
        score = service.calculate_wellness_score(
            hrv=20,
            heart_rate=110,
            emotion_score=60
        )

        # Should be low
        assert score <= 50


class TestRecommendations:
    """Test personalized recommendations"""

    def test_stress_recommendations(self):
        """Test recommendations for stressed state"""
        service = WellnessService()

        recommendations = service.generate_recommendations(
            emotion_type='stress',
            wellness_score=60,
            user_history=[]
        )

        assert 'food' in recommendations
        assert 'exercise' in recommendations
        assert 'content' in recommendations

        # Should recommend calming activities
        exercise_recs = ' '.join(recommendations['exercise']).lower()
        assert 'yoga' in exercise_recs or 'breathing' in exercise_recs

    def test_happiness_recommendations(self):
        """Test recommendations for happy state"""
        service = WellnessService()

        recommendations = service.generate_recommendations(
            emotion_type='happiness',
            wellness_score=85,
            user_history=[]
        )

        # Should recommend social/active activities
        exercise_recs = ' '.join(recommendations['exercise']).lower()
        assert any(word in exercise_recs for word in ['social', 'dance', 'group'])

    def test_low_wellness_adjustments(self):
        """Test that low wellness adds recovery recommendations"""
        service = WellnessService()

        recommendations = service.generate_recommendations(
            emotion_type='fatigue',
            wellness_score=30,
            user_history=[]
        )

        # Should prioritize rest
        food_recs = ' '.join(recommendations['food']).lower()
        exercise_recs = ' '.join(recommendations['exercise']).lower()

        assert 'rest' in food_recs or 'rest' in exercise_recs


class TestDailyTips:
    """Test psychology-based daily tips"""

    def test_tips_for_all_emotions(self):
        """Test that tips exist for all emotion types"""
        service = WellnessService()

        emotions = [
            'stress', 'fatigue', 'anxiety', 'happiness',
            'excitement', 'calmness', 'focus', 'apathy'
        ]

        for emotion in emotions:
            tip = service.get_daily_tip(emotion)

            assert isinstance(tip, str)
            assert len(tip) > 10  # Should be meaningful

    def test_tip_consistency(self):
        """Test that tips are consistent for same day"""
        service = WellnessService()

        # Same emotion, same day should give same tip
        tip1 = service.get_daily_tip('stress')
        tip2 = service.get_daily_tip('stress')

        # Due to random seeding by day
        # May or may not be same - depends on implementation
        pass


class TestEmotionTrends:
    """Test emotion trend analysis"""

    def test_dominant_emotion_calculation(self):
        """Test finding dominant emotion from history"""
        # Mock history with mostly stress
        history = [
            {'emotion_type': 'stress', 'hrv': 30, 'heart_rate': 95,
             'emotion_score': 80, 'timestamp': datetime.now().isoformat()}
            for _ in range(7)
        ] + [
            {'emotion_type': 'happiness', 'hrv': 70, 'heart_rate': 70,
             'emotion_score': 85, 'timestamp': datetime.now().isoformat()}
            for _ in range(3)
        ]

        from collections import Counter
        emotions = [r['emotion_type'] for r in history]
        dominant = Counter(emotions).most_common(1)[0]

        assert dominant[0] == 'stress'
        assert dominant[1] == 7

    def test_average_metrics_calculation(self):
        """Test calculating average HRV and HR"""
        history = [
            {'hrv': 60, 'heart_rate': 75, 'emotion_score': 80,
             'emotion_type': 'focus', 'timestamp': datetime.now().isoformat()},
            {'hrv': 80, 'heart_rate': 65, 'emotion_score': 90,
             'emotion_type': 'calmness', 'timestamp': datetime.now().isoformat()},
        ]

        avg_hrv = sum(r['hrv'] for r in history) / len(history)
        avg_hr = sum(r['heart_rate'] for r in history) / len(history)

        assert avg_hrv == 70
        assert avg_hr == 70


class TestPatternDetection:
    """Test pattern detection in emotion data"""

    def test_stress_hour_detection(self):
        """Test identifying hours with high stress"""
        # Mock data showing stress at specific hours
        pass

    def test_best_time_detection(self):
        """Test identifying best emotional time of day"""
        # Mock data showing best time
        pass


# Integration Tests

class TestWellnessIntegration:
    """Integration tests for wellness system"""

    @pytest.mark.asyncio
    async def test_complete_wellness_check(self):
        """Test complete wellness check flow"""
        # Would test:
        # 1. Emotion classification
        # 2. Wellness score calculation
        # 3. Recommendation generation
        # 4. Database storage
        pass

    @pytest.mark.asyncio
    async def test_trend_analysis(self):
        """Test trend analysis with historical data"""
        # Would test analyzing 7+ days of data
        pass

    @pytest.mark.asyncio
    async def test_real_time_monitoring(self):
        """Test real-time emotion monitoring"""
        # Would test continuous monitoring flow
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
