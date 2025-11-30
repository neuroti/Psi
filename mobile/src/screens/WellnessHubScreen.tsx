/**
 * Mode 3: Wellness Hub Screen
 * Real-time emotion monitoring and wellness recommendations
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { wellnessApi } from '../services/api';

export default function WellnessHubScreen() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchWellnessData();
  }, []);

  const fetchWellnessData = async () => {
    try {
      setLoading(true);
      const response = await wellnessApi.check();
      setData(response.data);
    } catch (error) {
      console.error('Error fetching wellness data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={fetchWellnessData} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Wellness Hub</Text>
        <Text style={styles.subtitle}>Your emotional wellness dashboard</Text>
      </View>

      {/* Wellness Score */}
      <View style={styles.scoreCard}>
        <Text style={styles.scoreLabel}>Wellness Score</Text>
        <Text style={styles.scoreValue}>{data.wellness_score}/100</Text>
        <View style={styles.scoreBar}>
          <View
            style={[
              styles.scoreBarFill,
              { width: `${data.wellness_score}%` },
            ]}
          />
        </View>
      </View>

      {/* Current Emotion */}
      <View style={styles.emotionCard}>
        <Text style={styles.sectionTitle}>Current Emotion</Text>
        <Text style={styles.emotionType}>{data.current_emotion.type}</Text>
        <Text style={styles.emotionScore}>
          Confidence: {data.current_emotion.score}%
        </Text>

        <View style={styles.vitalSigns}>
          <View style={styles.vitalItem}>
            <Text style={styles.vitalLabel}>HRV</Text>
            <Text style={styles.vitalValue}>
              {data.current_emotion.hrv.toFixed(1)} ms
            </Text>
          </View>
          <View style={styles.vitalItem}>
            <Text style={styles.vitalLabel}>Heart Rate</Text>
            <Text style={styles.vitalValue}>
              {data.current_emotion.heart_rate} bpm
            </Text>
          </View>
        </View>
      </View>

      {/* Daily Tip */}
      <View style={styles.tipCard}>
        <Text style={styles.tipIcon}>💡</Text>
        <Text style={styles.tipTitle}>Daily Wellness Tip</Text>
        <Text style={styles.tipText}>{data.daily_tip}</Text>
      </View>

      {/* Recommendations */}
      <View style={styles.recommendationsCard}>
        <Text style={styles.sectionTitle}>Personalized Recommendations</Text>

        <View style={styles.recommendationSection}>
          <Text style={styles.recommendationCategory}>🍎 Food</Text>
          {data.recommendations.food.map((item: string, index: number) => (
            <Text key={index} style={styles.recommendationItem}>
              • {item}
            </Text>
          ))}
        </View>

        <View style={styles.recommendationSection}>
          <Text style={styles.recommendationCategory}>🏃 Exercise</Text>
          {data.recommendations.exercise.map((item: string, index: number) => (
            <Text key={index} style={styles.recommendationItem}>
              • {item}
            </Text>
          ))}
        </View>

        <View style={styles.recommendationSection}>
          <Text style={styles.recommendationCategory}>📚 Content</Text>
          {data.recommendations.content.map((item: string, index: number) => (
            <Text key={index} style={styles.recommendationItem}>
              • {item}
            </Text>
          ))}
        </View>
      </View>

      {/* All Emotions */}
      <View style={styles.allEmotionsCard}>
        <Text style={styles.sectionTitle}>Emotion Spectrum</Text>
        {Object.entries(data.current_emotion.all_emotions).map(
          ([emotion, score]: [string, any]) => (
            <View key={emotion} style={styles.emotionBar}>
              <Text style={styles.emotionBarLabel}>{emotion}</Text>
              <View style={styles.emotionBarContainer}>
                <View
                  style={[styles.emotionBarFill, { width: `${score}%` }]}
                />
              </View>
              <Text style={styles.emotionBarValue}>{score.toFixed(0)}%</Text>
            </View>
          )
        )}
      </View>

      <TouchableOpacity
        style={styles.refreshButton}
        onPress={fetchWellnessData}
      >
        <Text style={styles.refreshButtonText}>Refresh Data</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#FF6B9D',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  scoreCard: {
    margin: 20,
    marginBottom: 0,
    backgroundColor: 'white',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginBottom: 16,
  },
  scoreBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#F0F0F0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    backgroundColor: '#FF6B9D',
  },
  emotionCard: {
    margin: 20,
    marginBottom: 0,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  emotionType: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF6B9D',
    textTransform: 'capitalize',
    marginBottom: 8,
  },
  emotionScore: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
  },
  vitalSigns: {
    flexDirection: 'row',
    gap: 16,
  },
  vitalItem: {
    flex: 1,
    backgroundColor: '#F8F8F8',
    padding: 12,
    borderRadius: 8,
  },
  vitalLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  vitalValue: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  tipCard: {
    margin: 20,
    marginBottom: 0,
    backgroundColor: '#FFF9E6',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  tipIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  tipText: {
    fontSize: 15,
    lineHeight: 22,
    textAlign: 'center',
    color: '#666',
  },
  recommendationsCard: {
    margin: 20,
    marginBottom: 0,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
  },
  recommendationSection: {
    marginBottom: 16,
  },
  recommendationCategory: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  recommendationItem: {
    fontSize: 15,
    lineHeight: 24,
    color: '#666',
    paddingLeft: 8,
  },
  allEmotionsCard: {
    margin: 20,
    marginBottom: 0,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
  },
  emotionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  emotionBarLabel: {
    width: 80,
    fontSize: 14,
    color: '#666',
    textTransform: 'capitalize',
  },
  emotionBarContainer: {
    flex: 1,
    height: 6,
    backgroundColor: '#F0F0F0',
    borderRadius: 3,
    overflow: 'hidden',
    marginHorizontal: 8,
  },
  emotionBarFill: {
    height: '100%',
    backgroundColor: '#FF6B9D',
  },
  emotionBarValue: {
    width: 45,
    fontSize: 12,
    color: '#666',
    textAlign: 'right',
  },
  refreshButton: {
    margin: 20,
    backgroundColor: '#FF6B9D',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
